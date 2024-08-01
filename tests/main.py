import asyncio
import time

from picwish import PicWish


async def a():
    picwish = PicWish()
    bgremoved = await picwish.remove_background('a.jpg', no_watermark=True)
    await bgremoved.download('output0.jpg')
    bgremoved = await picwish.remove_background('a.jpg', no_watermark=False)
    await bgremoved.download('output1.jpg')
    enhanced = await picwish.enhance('b.jpg', no_watermark=True, enhance_face=True)
    await enhanced.download('output2.jpg')
    enhanced = await picwish.enhance('b.jpg', no_watermark=True, enhance_face=False)
    await enhanced.download('output3.jpg')
    enhanced = await picwish.enhance('b.jpg', no_watermark=False, enhance_face=True)
    await enhanced.download('output4.jpg')
    enhanced = await picwish.enhance('b.jpg', no_watermark=False, enhance_face=False)
    await enhanced.download('output5.jpg')


async def b():
    picwish = PicWish()
    async def process(f, *args, o, **kwargs):
        processed = await f(*args, **kwargs)
        await processed.download(o)

    await asyncio.gather(*[
        asyncio.create_task(c)
        for c in [
            process(picwish.remove_background, 'a.jpg', no_watermark=True, o='output6.jpg'),
            process(picwish.remove_background, 'a.jpg', no_watermark=False, o='output7.jpg'),
            process(picwish.enhance, 'b.jpg', no_watermark=True, enhance_face=True, o='output8.jpg'),
            process(picwish.enhance, 'b.jpg', no_watermark=True, enhance_face=False, o='output9.jpg'),
            process(picwish.enhance, 'b.jpg', no_watermark=False, enhance_face=True, o='output10.jpg'),
            process(picwish.enhance, 'b.jpg', no_watermark=False, enhance_face=False, o='output11.jpg')
        ]
    ])


async def main():
    t1 = time.time()
    await a()
    print(time.time() - t1)
    time.sleep(5)
    t2 = time.time()
    await b()
    print(time.time() - t2)

asyncio.run(main())
