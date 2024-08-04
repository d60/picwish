from dataclasses import dataclass, field
from pathlib import Path

from httpx import AsyncClient

from .enums import OCRFormat


@dataclass
class BaseImage:
    """
    Base class for processed images.
    """
    _http: AsyncClient
    url: str
    _cached_bytes: bytes | None = field(default=None, init=False, repr=False)

    async def get_bytes(self) -> bytes:
        """
        Fetches the image bytes from the URL.

        :return: The content of the image in bytes.
        :rtype: bytes
        """
        if self._cached_bytes is None:
            response = await self._http.get(self.url)
            self._cached_bytes = response.content
        return self._cached_bytes

    async def download(self, output: str) -> None:
        """
        Downloads the image and saves it to the specified file path.

        :param output: The file path where the image will be saved.
        :type output: str
        """
        Path(output).write_bytes(await self.get_bytes())


@dataclass
class EnhancedImage(BaseImage):
    """
    Represents an enhanced image.

    :ivar url: The URL of the enhanced image.
    :type url: str
    :ivar watermark: Indicates whether the image has a watermark.
    :type watermark: bool
    :param face_enhanced: Indicates whether the image has been enhanced for faces.
    :type face_enhanced: bool
    """
    watermark: bool
    face_enhanced: bool


@dataclass
class BackgroundRemovedImage(BaseImage):
    """
    Represents an enhanced image.

    :ivar url: The URL of the enhanced image.
    :type url: str
    :ivar watermark: Indicates whether the image has a watermark.
    :type watermark: bool
    :param mask: The URL of the mask used for background removal.
    :type mask: str
    """
    watermark: bool
    mask: str


@dataclass
class OCRResult(BaseImage):
    """
    Represents an OCR result.

    :ivar url: The URL used to get OCR result.
    :type url: str
    :ivar format: The format of the OCR result.
    :type format: OCRFormat
    """
    format: OCRFormat

    async def text(self, encoding: str = 'utf-8', errors: str = 'ignore') -> str:
        """
        Returns the OCR result as string.
        """
        bytes_ = await self.get_bytes()
        return bytes_.decode(encoding=encoding, errors=errors)


@dataclass
class T2IResult(BaseImage):
    """
    Represents the result of a text-to-image.

    :ivar url: The URL used to get T2I result.
    :type url: str
    :ivar id: The ID of the generated image.
    :type id: str
    """
    id: str


@dataclass
class ColorizeResult(BaseImage):
    """
    Represents the result of a colorization operation.

    :ivar url: The URL used to retrieve the colorization result.
    :type url: str
    """
