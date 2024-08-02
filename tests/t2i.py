import asyncio

import picwish
from picwish import PicWish
from picwish.enums import T2IQuality, T2ITheme

print(picwish.__version__)

picwish = PicWish()


async def generate(output, *args, **kwargs):
    print('Generating: ', args, kwargs)
    results = await picwish.text_to_image(*args, **kwargs)
    for n, i in enumerate(results):
        await i.download(f'{n}_{output}')


async def main():
    # Enhance an image
    prompt = 'A cat'
    await generate('1.jpg', prompt, T2ITheme.GENERAL, 616, 616, quality=T2IQuality.HIGH, batch_size=1)
    # await generate('2.jpg', prompt, T2ITheme.DIGITAL_ART, 616, 616, quality=T2IQuality.HIGH, batch_size=1)
    # await generate('3.jpg', prompt, T2ITheme._3D, 616, 616, quality=T2IQuality.HIGH, batch_size=1)
    # await generate('4.jpg', prompt, T2ITheme.PHOTOGRAPHY, 616, 616, quality=T2IQuality.HIGH, batch_size=1)
    # await generate('5.jpg', prompt, T2ITheme.ANIME, 616, 616, quality=T2IQuality.HIGH, batch_size=1)
    # await generate('6.jpg', prompt, T2ITheme.CYBERPUNK, 616, 616, quality=T2IQuality.HIGH, batch_size=1)
    # await generate('7.jpg', prompt, T2ITheme.PAINTING, 616, 616, quality=T2IQuality.HIGH, batch_size=1)
    # await generate('8.jpg', prompt, T2ITheme.CYBERPUNK, 616, 616, quality=T2IQuality.HIGH, batch_size=1)
    # await generate('9.jpg', prompt, T2ITheme.PAINTING, 616, 616, quality=T2IQuality.HIGH, batch_size=1)
    # await generate('a.jpg', prompt, T2ITheme.PIXEL_ART, 616, 616, quality=T2IQuality.HIGH, batch_size=1)
    # await generate('b.jpg', prompt, T2ITheme.ILLUSTRATION, 616, 616, quality=T2IQuality.HIGH, batch_size=1)
    # await generate('c.jpg', prompt, T2ITheme.SKETCH, 616, 616, quality=T2IQuality.HIGH, batch_size=1)

    await generate('d.jpg', prompt, T2ITheme.GENERAL, 616, 616, quality=T2IQuality.LOW, batch_size=1)
    # await generate('e.jpg', prompt, T2ITheme.DIGITAL_ART, 616, 616, quality=T2IQuality.LOW, batch_size=1)
    # await generate('f.jpg', prompt, T2ITheme._3D, 616, 616, quality=T2IQuality.LOW, batch_size=1)
    # await generate('10.jpg', prompt, T2ITheme.PHOTOGRAPHY, 616, 616, quality=T2IQuality.LOW, batch_size=1)
    # await generate('11.jpg', prompt, T2ITheme.ANIME, 616, 616, quality=T2IQuality.LOW, batch_size=1)
    # await generate('12.jpg', prompt, T2ITheme.CYBERPUNK, 616, 616, quality=T2IQuality.LOW, batch_size=1)
    # await generate('13.jpg', prompt, T2ITheme.PAINTING, 616, 616, quality=T2IQuality.LOW, batch_size=1)
    # await generate('14.jpg', prompt, T2ITheme.CYBERPUNK, 616, 616, quality=T2IQuality.LOW, batch_size=1)
    # await generate('15.jpg', prompt, T2ITheme.PAINTING, 616, 616, quality=T2IQuality.LOW, batch_size=1)
    # await generate('16.jpg', prompt, T2ITheme.PIXEL_ART, 616, 616, quality=T2IQuality.LOW, batch_size=1)
    # await generate('17.jpg', prompt, T2ITheme.ILLUSTRATION, 616, 616, quality=T2IQuality.LOW, batch_size=1)
    # await generate('18.jpg', prompt, T2ITheme.SKETCH, 616, 616, quality=T2IQuality.LOW, batch_size=1)

    await generate('19.jpg', prompt, T2ITheme.GENERAL, 616, 616, quality=T2IQuality.HIGH, batch_size=1, negative_prompt=prompt)
    # await generate('1a.jpg', prompt, T2ITheme.DIGITAL_ART, 616, 616, quality=T2IQuality.LOW, batch_size=1, negative_prompt=prompt)
    # await generate('1b.jpg', prompt, T2ITheme._3D, 616, 616, quality=T2IQuality.HIGH, batch_size=1, negative_prompt=prompt)
    # await generate('1c.jpg', prompt, T2ITheme.PHOTOGRAPHY, 616, 616, quality=T2IQuality.HIGH, batch_size=1, negative_prompt=prompt)
    # await generate('1d.jpg', prompt, T2ITheme.ANIME, 616, 616, quality=T2IQuality.HIGH, batch_size=1, negative_prompt=prompt)
    # await generate('1e.jpg', prompt, T2ITheme.CYBERPUNK, 616, 616, quality=T2IQuality.HIGH, batch_size=1, negative_prompt=prompt)
    # await generate('1f.jpg', prompt, T2ITheme.PAINTING, 616, 616, quality=T2IQuality.HIGH, batch_size=1, negative_prompt=prompt)
    # await generate('20.jpg', prompt, T2ITheme.CYBERPUNK, 616, 616, quality=T2IQuality.HIGH, batch_size=1, negative_prompt=prompt)
    # await generate('21.jpg', prompt, T2ITheme.PAINTING, 616, 616, quality=T2IQuality.HIGH, batch_size=1, negative_prompt=prompt)
    # await generate('23.jpg', prompt, T2ITheme.PIXEL_ART, 616, 616, quality=T2IQuality.HIGH, batch_size=1, negative_prompt=prompt)
    # await generate('24.jpg', prompt, T2ITheme.ILLUSTRATION, 616, 616, quality=T2IQuality.HIGH, batch_size=1, negative_prompt=prompt)
    # await generate('25.jpg', prompt, T2ITheme.SKETCH, 616, 616, quality=T2IQuality.HIGH, batch_size=1, negative_prompt=prompt)

asyncio.run(main())
