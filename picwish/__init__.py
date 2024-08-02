import asyncio
import os

if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from .enums import OCRFormat, OCRLanguage, T2IQuality, T2ITheme
from .image_models import BackgroundRemovedImage, EnhancedImage
from .main import EnhancedImage, PicWish, PicwishError

__version__ = '0.4.0'
