"""
Flask 主应用
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import config
import logging
import base64
import io
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from PIL import Image
from ocr_service import get_ocr_service

app = Flask(__name__,
            static_folder='static',  # 前端构建产物目录
            static_url_path='')      # 静态文件 URL 前缀为空

# 配置 Flask
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH

# 配置 CORS（允许前端跨域）
CORS(app)

logger = logging.getLogger(__name__)

# 并发控制
semaphore = threading.Semaphore(config.MAX_WORKERS)
executor = ThreadPoolExecutor(max_workers=config.MAX_WORKERS)

# OCR 服务实例（全局单例）
ocr_service = None


def init_ocr_service():
    """
    初始化 OCR 服务（延迟加载）
    """
    global ocr_service
    if ocr_service is None:
        logger.info("Initializing OCR service...")
        ocr_service = get_ocr_service()
        logger.info("OCR service initialized successfully")


def validate_image(image_bytes: bytes) -> None:
    """
    验证图片格式和大小

    Args:
        image_bytes: 图片字节流

    Raises:
        ValueError: 验证失败时抛出
    """
    # 1. 大小验证
    if len(image_bytes) > config.MAX_FILE_SIZE:
        raise ValueError(f"文件大小超过 {config.MAX_FILE_SIZE / 1024 / 1024}MB 限制")

    if len(image_bytes) == 0:
        raise ValueError("文件内容为空")

    # 2. 格式验证（使用 Pillow）
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img_format = img.format.lower() if img.format else None

        if img_format not in config.ALLOWED_FORMATS:
            raise ValueError(f"不支持的图片格式: {img_format}。支持的格式: {', '.join(config.ALLOWED_FORMATS)}")

    except Exception as e:
        if isinstance(e, ValueError):
            raise
        raise ValueError(f"无效的图片文件: {str(e)}")


@app.route('/')
def index():
    """
    前端页面入口（服务静态文件）
    """
    return app.send_static_file('index.html')


@app.route('/health', methods=['GET'])
def health_check():
    """
    健康检查接口
    """
    return jsonify({
        "status": "ok",
        "service": "Web OCR",
        "max_workers": config.MAX_WORKERS
    }), 200


@app.route('/api/ocr', methods=['POST'])
def ocr_endpoint():
    """
    OCR 识别接口
    """
    # 延迟初始化 OCR 服务（避免启动时加载模型）
    init_ocr_service()

    try:
        # 1. 解析请求 JSON
        if not request.is_json:
            return jsonify({"error": "请求必须是 JSON 格式"}), 400

        data = request.get_json()

        if 'image' not in data:
            return jsonify({"error": "缺少 'image' 字段"}), 400

        # 2. 解码 Base64 图片
        try:
            image_b64 = data['image']
            image_bytes = base64.b64decode(image_b64)
        except Exception as e:
            logger.error(f"Base64 decode failed: {e}")
            return jsonify({"error": "Base64 解码失败"}), 400

        # 3. 验证图片
        try:
            validate_image(image_bytes)
        except ValueError as e:
            logger.warning(f"Image validation failed: {e}")
            return jsonify({"error": str(e)}), 400

        # 4. 并发控制（非阻塞获取信号量）
        if not semaphore.acquire(blocking=False):
            logger.warning("Service busy: Max concurrent requests reached")
            return jsonify({"error": "服务繁忙，请稍后重试"}), 429

        # 5. 提交到线程池处理
        try:
            future = executor.submit(ocr_service.recognize, image_bytes)
            result = future.result(timeout=config.OCR_TIMEOUT)
            return jsonify(result), 200

        except TimeoutError:
            logger.error(f"OCR timeout after {config.OCR_TIMEOUT}s")
            return jsonify({"error": "OCR 处理超时"}), 504

        except Exception as e:
            logger.error(f"OCR processing failed: {type(e).__name__} - {str(e)}")
            return jsonify({"error": f"OCR 处理失败: {str(e)}"}), 500

        finally:
            # 释放信号量
            semaphore.release()

    except Exception as e:
        logger.error(f"Unexpected error in ocr_endpoint: {type(e).__name__} - {str(e)}")
        return jsonify({"error": "服务器内部错误"}), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """
    请求体过大错误处理
    """
    return jsonify({"error": "文件大小超过限制"}), 413


@app.errorhandler(500)
def internal_server_error(error):
    """
    服务器内部错误处理
    """
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "服务器内部错误"}), 500


if __name__ == '__main__':
    logger.info("Starting Web OCR service...")
    logger.info(f"Max workers: {config.MAX_WORKERS}")
    logger.info(f"Max file size: {config.MAX_FILE_SIZE / 1024 / 1024}MB")
    app.run(host='0.0.0.0', port=5000, debug=False)
