"""
OCR 服务封装
"""
import io
import time
import numpy as np
from PIL import Image
from paddleocr import PaddleOCR
import config
import logging

logger = logging.getLogger(__name__)


class OCRService:
    """
    OCR 服务类
    """

    def __init__(self):
        """
        初始化 PaddleOCR
        """
        logger.info("Initializing PaddleOCR...")
        try:
            self.ocr = PaddleOCR(
                use_angle_cls=True,  # 启用角度分类器
                lang='ch',            # 中文模型
                use_gpu=False,        # 使用 CPU
                show_log=False        # 不显示详细日志
            )
            logger.info("PaddleOCR initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize PaddleOCR: {e}")
            raise

    def recognize(self, image_bytes: bytes) -> dict:
        """
        识别图片中的文字

        Args:
            image_bytes: 图片字节流

        Returns:
            dict: 格式化的识别结果
            {
                "plain_text": "纯文本结果",
                "detailed": [
                    {
                        "text": "文本",
                        "confidence": 0.98,
                        "box": [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                    }
                ]
            }
        """
        start_time = time.time()

        try:
            # 1. 转换为 PIL Image
            img = Image.open(io.BytesIO(image_bytes))
            img_width, img_height = img.size

            # 2. 转为 numpy array
            img_array = np.array(img)

            logger.info(f"Processing image: {img_width}x{img_height}, size: {len(image_bytes)/1024:.1f}KB")

            # 3. OCR 识别
            result = self.ocr.ocr(img_array, cls=True)

            # 4. 格式化结果
            if not result or not result[0]:
                elapsed = time.time() - start_time
                logger.info(f"OCR completed: No text detected | Time: {elapsed:.2f}s")
                return {
                    "plain_text": "",
                    "detailed": []
                }

            # 提取纯文本（按行拼接）
            plain_text = "\n".join([line[1][0] for line in result[0]])

            # 提取详细结果
            detailed = [
                {
                    "text": line[1][0],
                    "confidence": round(line[1][1], 4),
                    "box": line[0]
                }
                for line in result[0]
            ]

            elapsed = time.time() - start_time
            logger.info(
                f"OCR Success | Size: {len(image_bytes)/1024:.1f}KB | "
                f"Dimension: {img_width}x{img_height} | "
                f"Time: {elapsed:.2f}s | Lines: {len(detailed)}"
            )

            return {
                "plain_text": plain_text,
                "detailed": detailed
            }

        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"OCR Failed | Error: {type(e).__name__} | Message: {str(e)} | Time: {elapsed:.2f}s")
            raise


# 全局单例（避免重复加载模型）
_ocr_service_instance = None

def get_ocr_service() -> OCRService:
    """
    获取 OCR 服务单例
    """
    global _ocr_service_instance
    if _ocr_service_instance is None:
        _ocr_service_instance = OCRService()
    return _ocr_service_instance
