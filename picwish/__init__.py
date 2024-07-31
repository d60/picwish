import asyncio
import os

if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from .main import EnhancedImage, Enhancer, PicwishError

__version__ = '0.1.1'
