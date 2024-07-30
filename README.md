# PicWish Photo Enhancer for Python

Enhance images to high quality **without tokens, accounts, or watermarks**, and enjoy **unlimited usage**!

## Usage

### 1. Install
```
pip install picwish
```

### 2. Write the Code
```python
import asyncio
from picwish import Enhancer

enhancer = Enhancer()

async def main():
    enhanced_image = await enhancer.enhance('/path/to/input.jpg')
    await enhanced_image.download('output.jpg')

asyncio.run(main())
```
