"""
配置文件
"""
import os
import logging

# 项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 并发配置
MAX_WORKERS = 10  # 最大并发处理数

# 文件限制
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FORMATS = ['jpeg', 'jpg', 'png', 'bmp']  # 支持的图片格式
ALLOWED_MIME_TYPES = ['image/jpeg', 'image/png', 'image/bmp']

# Flask 配置
MAX_CONTENT_LENGTH = 15 * 1024 * 1024  # 15MB（留缓冲）

# OCR 配置
OCR_TIMEOUT = 60  # OCR 任务超时时间（秒）

# 日志配置
LOG_DIR = os.path.join(BASE_DIR, 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'ocr.log')

# 确保日志目录存在
os.makedirs(LOG_DIR, exist_ok=True)

# 配置日志格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()  # 同时输出到控制台
    ]
)

logger = logging.getLogger(__name__)
