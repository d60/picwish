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