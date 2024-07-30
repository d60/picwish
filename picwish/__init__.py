import asyncio
import os

if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from .errors import PicwishError
from .main import EnhancedImage, Enhancer

__version__ = '0.0.1'
