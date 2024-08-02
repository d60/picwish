import asyncio

import picwish
from picwish import PicWish
from picwish.enums import OCRFormat

print(picwish.__version__)

picwish = PicWish()

async def main():
    result = await picwish.ocr('c.jpg', format=OCRFormat.TXT)
    print(await result.text())
    result = await picwish.ocr('c.jpg', format=OCRFormat.PDF)
    print(await result.download('1.pdf'))

asyncio.run(main())
