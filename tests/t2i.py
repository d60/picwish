import asyncio

import picwish
from picwish import PicWish
from picwish.enums import T2IQuality, T2ITheme, T2ISize

print(picwish.__version__)

picwish = PicWish()


async def generate(output, *args, **kwargs):
    print('Generating: ', args, kwargs)
    results = await picwish.text_to_image(*args, **kwargs)
    for n, i in enumerate(results):
        await i.download(f'{n}_{output}')


async def main():
    prompt = 'a cat'
    await generate('1.jpg', prompt, theme=T2ITheme.ANIME, size=T2ISize.FHD_16_9, quality=T2IQuality.HIGH, batch_size=1)
    # await generate('2.jpg', prompt, theme=T2ITheme.DIGITAL_ART, size=T2ISize.FHD_16_9, quality=T2IQuality.HIGH, batch_size=1)
    # await generate('3.jpg', prompt, theme=T2ITheme._3D, size=T2ISize.FHD_16_9, quality=T2IQuality.HIGH, batch_size=1)
    # await generate('4.jpg', prompt, theme=T2ITheme.PHOTOGRAPHY, size=T2ISize.FHD_16_9, quality=T2IQuality.HIGH, batch_size=1)
    # await generate('5.jpg', prompt, theme=T2ITheme.ANIME, size=T2ISize.FHD_16_9, quality=T2IQuality.HIGH, batch_size=1)
    # await generate('6.jpg', prompt, theme=T2ITheme.CYBERPUNK, size=T2ISize.FHD_16_9, quality=T2IQuality.HIGH, batch_size=1)
    # await generate('7.jpg', prompt, theme=T2ITheme.PAINTING, size=T2ISize.FHD_16_9, quality=T2IQuality.HIGH, batch_size=1)
    # await generate('8.jpg', prompt, theme=T2ITheme.CYBERPUNK, size=T2ISize.FHD_16_9, quality=T2IQuality.HIGH, batch_size=1)
    # await generate('9.jpg', prompt, theme=T2ITheme.PAINTING, size=T2ISize.FHD_16_9, quality=T2IQuality.HIGH, batch_size=1)
    # await generate('a.jpg', prompt, theme=T2ITheme.PIXEL_ART, size=T2ISize.FHD_16_9, quality=T2IQuality.HIGH, batch_size=1)
    # await generate('b.jpg', prompt, theme=T2ITheme.ILLUSTRATION, size=T2ISize.FHD_16_9, quality=T2IQuality.HIGH, batch_size=1)
    # await generate('c.jpg', prompt, theme=T2ITheme.SKETCH, size=T2ISize.FHD_16_9, quality=T2IQuality.HIGH, batch_size=1)

    await generate('d.jpg', prompt, theme=T2ITheme.GENERAL, size=T2ISize.FHD_16_9, quality=T2IQuality.LOW, batch_size=1)
    # await generate('e.jpg', prompt, theme=T2ITheme.DIGITAL_ART, size=T2ISize.FHD_16_9, quality=T2IQuality.LOW, batch_size=1)
    # await generate('f.jpg', prompt, theme=T2ITheme._3D, size=T2ISize.FHD_16_9, quality=T2IQuality.LOW, batch_size=1)
    # await generate('10.jpg', prompt, theme=T2ITheme.PHOTOGRAPHY, size=T2ISize.FHD_16_9, quality=T2IQuality.LOW, batch_size=1)
    # await generate('11.jpg', prompt, theme=T2ITheme.ANIME, size=T2ISize.FHD_16_9, quality=T2IQuality.LOW, batch_size=1)
    # await generate('12.jpg', prompt, theme=T2ITheme.CYBERPUNK, size=T2ISize.FHD_16_9, quality=T2IQuality.LOW, batch_size=1)
    # await generate('13.jpg', prompt, theme=T2ITheme.PAINTING, size=T2ISize.FHD_16_9, quality=T2IQuality.LOW, batch_size=1)
    # await generate('14.jpg', prompt, theme=T2ITheme.CYBERPUNK, size=T2ISize.FHD_16_9, quality=T2IQuality.LOW, batch_size=1)
    # await generate('15.jpg', prompt, theme=T2ITheme.PAINTING, size=T2ISize.FHD_16_9, quality=T2IQuality.LOW, batch_size=1)
    # await generate('16.jpg', prompt, theme=T2ITheme.PIXEL_ART, size=T2ISize.FHD_16_9, quality=T2IQuality.LOW, batch_size=1)
    # await generate('17.jpg', prompt, theme=T2ITheme.ILLUSTRATION, size=T2ISize.FHD_16_9, quality=T2IQuality.LOW, batch_size=1)
    # await generate('18.jpg', prompt, theme=T2ITheme.SKETCH, size=T2ISize.FHD_16_9, quality=T2IQuality.LOW, batch_size=1)

    await generate('19.jpg', prompt, theme=T2ITheme.GENERAL, size=T2ISize.FHD_16_9, quality=T2IQuality.HIGH, batch_size=1, negative_prompt=prompt)
    # await generate('1a.jpg', prompt, theme=T2ITheme.DIGITAL_ART, size=T2ISize.FHD_16_9, quality=T2IQuality.LOW, batch_size=1, negative_prompt=prompt)
    # await generate('1b.jpg', prompt, theme=T2ITheme._3D, size=T2ISize.FHD_16_9, quality=T2IQuality.HIGH, batch_size=1, negative_prompt=prompt)
    # await generate('1c.jpg', prompt, theme=T2ITheme.PHOTOGRAPHY, size=T2ISize.FHD_16_9, quality=T2IQuality.HIGH, batch_size=1, negative_prompt=prompt)
    # await generate('1d.jpg', prompt, theme=T2ITheme.ANIME, size=T2ISize.FHD_16_9, quality=T2IQuality.HIGH, batch_size=1, negative_prompt=prompt)
    # await generate('1e.jpg', prompt, theme=T2ITheme.CYBERPUNK, size=T2ISize.FHD_16_9, quality=T2IQuality.HIGH, batch_size=1, negative_prompt=prompt)
    # await generate('1f.jpg', prompt, theme=T2ITheme.PAINTING, size=T2ISize.FHD_16_9, quality=T2IQuality.HIGH, batch_size=1, negative_prompt=prompt)
    # await generate('20.jpg', prompt, theme=T2ITheme.CYBERPUNK, size=T2ISize.FHD_16_9, quality=T2IQuality.HIGH, batch_size=1, negative_prompt=prompt)
    # await generate('21.jpg', prompt, theme=T2ITheme.PAINTING, size=T2ISize.FHD_16_9, quality=T2IQuality.HIGH, batch_size=1, negative_prompt=prompt)
    # await generate('23.jpg', prompt, theme=T2ITheme.PIXEL_ART, size=T2ISize.FHD_16_9, quality=T2IQuality.HIGH, batch_size=1, negative_prompt=prompt)
    # await generate('24.jpg', prompt, theme=T2ITheme.ILLUSTRATION, size=T2ISize.FHD_16_9, quality=T2IQuality.HIGH, batch_size=1, negative_prompt=prompt)
    # await generate('25.jpg', prompt, theme=T2ITheme.SKETCH, size=T2ISize.FHD_16_9, quality=T2IQuality.HIGH, batch_size=1, negative_prompt=prompt)

asyncio.run(main())
