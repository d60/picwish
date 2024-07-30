import asyncio
import base64
import json
import mimetypes
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import filetype
from httpx import AsyncClient, Response

from .errors import PicwishError
from .signature import Signature


@dataclass(frozen=True)
class EnhancedImage:
    """
    Represents an enhanced image.

    :param _http: The HTTP client to use for requests.
    :param url: The URL of the enhanced image.
    :param watermark: Indicates whether the image has a watermark.

    :ivar _http: The HTTP client to use for requests.
    :ivar url: The URL of the enhanced image.
    :ivar watermark: Indicates whether the image has a watermark.
    """

    _http: AsyncClient
    url: str
    watermark: bool

    async def get_bytes(self) -> bytes:
        """
        Fetches the image bytes from the url.

        :return: The content of the image in bytes.
        :rtype: bytes
        """
        response = await self._http.get(self.url)
        return response.content

    async def download(self, output: str) -> None:
        """
        Downloads the image and saves it to the specified file path.

        :param output: The path to the file where the image will be saved.
        :type output: str
        """
        bytes_ = await self.get_bytes()
        with open(output, 'wb') as f:
            f.write(bytes_)


class Enhancer:
    """
    Provides methods to enhance images using the Picwish API.

    :param token: The API token for authorization.
    :param kwargs: Optional HTTP client settings.
    """

    _product_id = 482
    _language = 'en'
    _params = {
        'product_id': _product_id,
        'language': _language
    }

    def __init__(self, token: str, **kwargs) -> None:
        """
        Initializes the Enhancer with the provided token and optional HTTP client settings.

        :param token: The API token for authorization.
        :type token: str
        :param kwargs: Optional HTTP client settings.
        """
        self.http = AsyncClient(**kwargs)
        self.token = token

    @property
    def _headers(self) -> dict:
        return {
            'Authorization': f'Bearer {self.token}'
        }

    async def request(self, method: str, url: str, *args, **kwargs) -> tuple[Any, Response]:
        response = await self.http.request(method, url, *args, **kwargs)
        try:
            response_data = response.json()
            if 'status' in response_data and 400 <= response_data['status'] < 600:
                message = f'status: {response_data["status"]} message: {response_data["message"]}'
                raise PicwishError(message)
        except json.JSONDecodeError:
            response_data = response.text
        return response_data, response

    async def get_oss_authorizations(self, filename: str) -> dict:
        """
        Retrieves OSS authorizations for the specified filename.

        :param filename: The name of the file to retrieve authorizations for.
        :type filename: str

        :return: A dictionary containing the OSS authorization data.
        :rtype: dict
        """
        url = 'https://gw.aoscdn.com/app/picwish/authorizations/oss'
        data = {'filenames': [filename]}
        response, _ = await self.request('POST', url, json=data, params=self._params, headers=self._headers)
        return response

    async def _signature(self, filename: str, oss: str) -> tuple[str, dict]:
        """
        Creates the necessary signature for OSS requests.
        Returns the URL and headers.

        :param filename: The name of the file.
        :type filename: str
        :param oss: The OSS authorization data.
        :type oss: dict

        :return: The signed URL and headers.
        :rtype: tuple[str, dict]
        """

        access_key_id = oss['data']['credential']['access_key_id']
        access_key_secret = oss['data']['credential']['access_key_secret']
        security_token = oss['data']['credential']['security_token']
        accelerate = oss['data']['accelerate']
        bucket = oss['data']['bucket']
        object = list(oss['data']['objects'].values())[0]
        GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'

        time = datetime.utcnow().strftime(GMT_FORMAT)
        callback = base64.b64encode(json.dumps({
            'callbackUrl': oss['data']['callback']['url'],
            'callbackBody': oss['data']['callback']['body'],
            'callbackBodyType': oss['data']['callback']['type'],
        }).encode()).decode()

        headers = {
            'X-Oss-Date': time,
            'X-Oss-Security-Token': security_token,
            'Content-Type': mimetypes.guess_type(filename)[0],
            'X-Oss-Callback': callback
        }

        signature = Signature(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            verb='PUT',
            content_md5='',
            headers=headers,
            bucket=bucket,
            object=object,
            sub_resources=[]
        ).make_signature()

        headers ['Authorization'] = f'OSS {access_key_id}:{signature}'
        url = f'https://{bucket}.{accelerate}/{object}'
        return url, headers

    async def create_task(self, source: str | bytes, enhance_face: bool) -> tuple[str, dict]:
        """
        Creates an enhancement task for the given image source.

        :param source: The image source, which can be a file path or bytes.
        :type source: str | bytes
        :param enhance_face: Indicates whether to enhance faces in the image.
        :type enhance_face: bool

        :return: A tuple containing the task ID and the scale data.
        :rtype: tuple[str, dict]
        """

        if isinstance(source, str):
            source: Path = Path(source)
            filename = source.name
            bytes_ = source.read_bytes()
        elif isinstance(source, bytes):
            ft = filetype.guess(source)
            filename = f'f.{ft.extension}'
            bytes_ = source
        else:
            raise TypeError('Source must be string or bytes.')

        oss = await self.get_oss_authorizations(filename)
        url, headers = await self._signature(filename, oss)
        response, _ = await self.request('PUT', url, data=bytes_, headers=headers)
        type = 2 if enhance_face else 1
        scale_data = await self.get_task_id(response['data']['resource_id'], type)
        task_id = scale_data['data']['task_id']
        while True:
            scale = await self.get_scale(task_id)
            if scale['data']['image']:
                return task_id, scale
            await asyncio.sleep(0.5)

    async def get_image_url(self, task_id: str, pic_quality: str = 'free') -> tuple[str, dict]:
        """
        Retrieves the image URL for the given task ID.

        :param task_id: The ID of the task.
        :type task_id: str
        :param pic_quality: The quality of the image. Can be free or high.
        :type pic_quality: str

        :return: A tuple containing the image URL and additional data.
        :rtype: tuple[str, dict]
        """
        url = f'https://gw.aoscdn.com/app/picwish/tasks/login/image-url/scale/{task_id}'
        params = self._params | {'pic_quality': pic_quality}
        response, _ = await self.request('GET', url, params=params, headers=self._headers)
        return response

    async def get_task_id(self, resource_id: str, type: int) -> dict:
        """
        Retrieves the task ID for the given resource ID.

        :param resource_id: The ID of the resource.
        :type resource_id: str
        :param type: The type of the task.
        :type type: int

        :return: A dictionary containing the task ID and additional data.
        :rtype: dict
        """
        url = 'https://gw.aoscdn.com/app/picwish/tasks/login/scale'
        data = {
            "website": "en",
            "source_resource_id": resource_id,
            "resource_id": resource_id,
            "type": type
        }
        response, _ = await self.request('POST', url, params=self._params, json=data, headers=self._headers)
        return response

    async def get_scale(self, task_id: str) -> dict:
        """
        Retrieves the scale information for the given task ID.

        :param task_id: The ID of the task.
        :type task_id: str

        :return: A dictionary containing the scale information.
        :rtype: dict
        """
        url = f'https://gw.aoscdn.com/app/picwish/tasks/login/scale/{task_id}'
        response, _ = await self.request('GET', url, params=self._params, headers=self._headers)
        return response

    async def enhance(
        self,
        source: str | bytes,
        *,
        no_watermark: bool = True,
        quality: str = 'free',
        enhance_face: bool = True
    ) -> EnhancedImage:
        """
        Enhances the image.
        And returns an EnhancedImage object.

        :param source: The image source, which can be a file path or bytes.
        :type source: str | bytes
        :param no_watermark: Whether to remove the watermark from the image.
        :type no_watermark: bool
        :param quality: The quality of the image. Defaults to 'free'.
        :type quality: str
        :param enhance_face: Whether to enhance faces in the image.
        :type enhance_face: bool

        :return: An EnhancedImage object containing the enhanced image and watermark status.
        :rtype: EnhancedImage
        """
        task_id, data = await self.create_task(source, enhance_face)
        watermark = True
        if no_watermark:
            no_watermark = await self.get_image_url(task_id, quality)
            if no_watermark['status'] == 200:
                data = no_watermark
                watermark = False
        return EnhancedImage(self.http, data['data']['image'], watermark=watermark)
