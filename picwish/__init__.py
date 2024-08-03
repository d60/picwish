"""
PicWish Python
==============
A library designed to provide free and unlimited access to PicWish
services such as AI image generation, image enhancement, image OCR,
and background removal.

Example
---------
import asyncio
from picwish import PicWish, T2ITheme, T2IQuality, T2ISize

async def main():
    # Initialize the PicWish client
    picwish = PicWish()

    # Generate images from text prompt
    results = await picwish.text_to_image(
        prompt='A Cat',
        theme=T2ITheme.ANIME,
        size=T2ISize.FHD_1_1,
        batch_size=4,
        quality=T2IQuality.HIGH
    )

    # Download the generated images
    for result in results:
        await result.download(f'{result.id}.png')

asyncio.run(main())
"""

__version__ = '0.4.3'
__license__ = 'MIT'

import asyncio
import os
from .enums import OCRFormat, OCRLanguage, T2IQuality, T2ISize, T2ITheme
from .image_models import BackgroundRemovedImage, EnhancedImage
from .main import EnhancedImage, PicWish, PicwishError

if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
