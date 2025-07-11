"""
PicWish Python
==============
A library designed to provide free and unlimited access to PicWish
services such as AI image generation, image enhancement, image OCR,
and background removal.

Copyright (c) d60 2024

This software is released under the MIT License.
For more details, see https://opensource.org/licenses/MIT.
"""

__version__ = '0.6.0'
__license__ = 'MIT'

import asyncio
import os

from .enums import (
    ImageTranslator,
    OCRFormat,
    OCRLanguage,
    T2IQuality,
    T2ISize,
    T2ITheme,
    TranslateSourceLanguage,
    TranslateTargetLanguage,
    ImageTranslator
)
from .image_models import BackgroundRemovedImage, ColorizeResult, EnhancedImage, OCRResult, T2IResult
from .main import EnhancedImage, PicWish, PicwishError

if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
