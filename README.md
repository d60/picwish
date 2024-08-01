# PicWish API for Python

Enhance images and remove backgrounds **without tokens, accounts, or watermarks**, and enjoy **unlimited usage**!

## Features
- **Image Enhancement**:   Improve image quality without watermark.
- **Background Removal**:   Remove background from images.

## Usage

### 1. Install
```
pip install picwish
```

### 2. Write the Code
```python
import asyncio
from picwish import PicWish

async def main():
    picwish = PicWish()

    # Enhance an image
    enhanced_image = await picwish.enhance('/path/to/input.jpg')
    await enhanced_image.download('enhanced_output.jpg')

    # Remove background from an image
    background_removed_image = await picwish.remove_background('/path/to/input.jpg')
    await background_removed_image.download('background_removed_output.png')

asyncio.run(main())
```
