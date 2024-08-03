import asyncio

from picwish import PicWish


async def main():
    picwish = PicWish()

    results = await picwish.colorize(
        'd.jpg'
    )
    print(results)
    await results.download('c1.jpg')

asyncio.run(main())
