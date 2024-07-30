# PicWish Photo Enhancer for Python

## Usage

### 1. Install
```
pip install picwish
```

### 2. Obtain Your API Token
- 1 Log in to your PicWish account
- 2 Open the console and enter `localStorage['passport_api_token']`.
- 3 Copy the API token displayed.

### 3. Write the Code
```python
import asyncio
from picwish import Enhancer

# Replace '<Your-token-here>' with your actual API token
enhancer = Enhancer('<Your-token-here>')

async def main():
    enhanced_image = await enhancer.enhance('/path/to/input.jpg')
    await enhanced_image.download('output.jpg')

asyncio.run(main())
```
