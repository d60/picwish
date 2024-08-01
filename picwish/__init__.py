import asyncio
import os

if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from .image_models import BackgroundRemovedImage, EnhancedImage
from .main import EnhancedImage, PicWish, PicwishError

__version__ = '0.3.0'
