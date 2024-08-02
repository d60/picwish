# PicWish API for Python 🎨✨

Enhance, generate, and process images **without tokens, accounts, or watermarks**, and enjoy **unlimited usage**!

## Features
- **Image Enhancement**:   Improve image quality without watermark.
- **Background Removal**:   Remove background from images.

To get started, install the `picwish` package using pip:

```bash
pip install picwish
```


## Quick Examples 🚀

### 1. Text-to-Image Generation
Generate images based on a text prompt with customizable settings:

```python
import asyncio
from picwish import PicWish, T2ITheme, T2IQuality

async def main():
    picwish = PicWish()

    # Generate images from text prompt
    results = await picwish.text_to_image(
        prompt='A girl',
        theme=T2ITheme.ANIME,
        width=616,
        height=616,
        batch_size=4,
        quality=T2IQuality.HIGH
    )

    for result in results:
        await result.download(f'{result.id}.png')

asyncio.run(main())
```


### 2. Image Enhancement
Enhance the quality of an image without a watermark:

```python
import asyncio
from picwish import PicWish

async def main():
    picwish = PicWish()

    # Enhance an image
    enhanced_image = await picwish.enhance('/path/to/input.jpg')
    await enhanced_image.download('enhanced_output.jpg')

asyncio.run(main())
```

### 3. Background Removal
Remove the background from an image:

```python
import asyncio
from picwish import PicWish

async def main():
    picwish = PicWish()

    # Remove background from an image
    background_removed_image = await picwish.remove_background('/path/to/input.jpg')
    await background_removed_image.download('background_removed_output.png')

asyncio.run(main())
```

### 4. OCR (Optical Character Recognition)
Extract text from images with support for multiple languages and output formats:

```python
import asyncio
from picwish import PicWish, OCRFormat

async def main():
    picwish = PicWish()
    ocr_result = await picwish.ocr(
        'input.jpg',
        format=OCRFormat.TXT
    )
    print(await ocr_result.text())

    # -----------------
    # Download as PNG
    ocr_result = await picwish.ocr(
        'input.jpg',
        format=OCRFormat.PDF
    )
    print(await ocr_result.download('result.pdf'))

asyncio.run(main())
```
