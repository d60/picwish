import asyncio
import base64
import json
import mimetypes
import random
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import filetype
from httpx import AsyncClient, Response

from .signature import Signature


class PicwishError(Exception):
    """
    Exception raised for errors related to the Picwish API.

    :param status_code: The HTTP status code associated with the error.
    :type status_code: int | None
    :param api_status: API specific error code.
    :type api_status: int | None
    """
    def __init__(self, *args, status_code: int | None = None, api_status: int | None = None) -> None:
        super().__init__(*args)
        self.status_code = status_code
        self.api_status = api_status


@dataclass(frozen=True)
class EnhancedImage:
    """
    Represents an enhanced image.

    :param _http: The HTTP client to use for requests.
    :param url: The URL of the enhanced image.
    :param watermark: Indicates whether the image has a watermark.

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
        Path(output).write_bytes(await self.get_bytes())


class Enhancer:
    """
    Provides methods to enhance images using the Picwish API.

    :param sleep_duration: The duration to sleep between progress checks.
    :type sleep_duration: float
    :param kwargs: Optional HTTP client settings.
    """
    _api_version = 'v2'
    _base_url = 'https://gw.aoscdn.com/app/picwish'
    _product_id = 482
    _downloads_limit = 10
    _language = 'en'
    _params = {
        'product_id': _product_id,
        'language': _language
    }

    def __init__(self, sleep_duration: float = 0.5, **kwargs) -> None:
        """
        Initializes the Enhancer with the provided token and optional HTTP client settings.

        :param sleep_duration: The duration to sleep between progress checks.
        :type sleep_duration: float
        :param kwargs: Optional HTTP client settings.
        """
        self.http = AsyncClient(**kwargs)
        self.sleep_duration = sleep_duration
        self.update_token()

    def update_token(self) -> None:
        self.token = ','.join([
            self._api_version,
            str(random.randint(10000000, 99999999)),
            str(self._product_id),
            uuid.uuid4().hex
        ])
        self._remaining_downloads = self._downloads_limit

    @property
    def _headers(self) -> dict:
        return {
            'Authorization': f'Bearer {self.token}'
        }

    async def request(self, method: str, url: str, *args, **kwargs) -> tuple[Any, Response]:
        response = await self.http.request(method, url, *args, **kwargs)
        api_status = None
        error_message = None
        try:
            response_data = response.json()
            api_status = response_data.get('status')
            error_message = response_data.get('message')
        except json.JSONDecodeError:
            response_data = response.text

        status = response.status_code
        if (api_status is not None and api_status != 200) or 400 <= status < 600:
            messages = [f'status: {status}']

            if api_status is not None:
                messages.append(f'APIStatus: {response_data["status"]}')
            if error_message is not None:
                messages.append(f'message: {response_data["message"]}')
            else:
                messages.append(f'message: {response.reason_phrase}')
            raise PicwishError(', '.join(messages), status_code=status, api_status=api_status)

        return response_data, response

    async def get_oss_authorizations(self, filename: str) -> dict:
        """
        Retrieves OSS authorizations for the specified filename.

        :param filename: The name of the file to retrieve authorizations for.
        :type filename: str

        :return: A dictionary containing the OSS authorization data.
        :rtype: dict
        """
        url = self._base_url + '/authorizations/oss'
        data = {'filenames': [filename]}
        response, _ = await self.request('POST', url, json=data, params=self._params, headers=self._headers)
        return response

    def _signature(self, filename: str, oss: str) -> tuple[str, dict]:
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
            sub_resources={}
        ).make_signature()

        headers ['Authorization'] = f'OSS {access_key_id}:{signature}'
        url = f'https://{bucket}.{accelerate}/{object}'
        return url, headers

    async def create_task(self, bytes_: bytes, filename: str, enhance_face: bool) -> tuple[str, dict]:
        """
        Creates an enhancement task for the given image source.

        :param bytes_: The image data in bytes format.
        :type bytes_: bytes
        :param filename: The name of the file to be enhanced.
        :type filename: str
        :param enhance_face: Whether to enhance faces in the image.
        :type enhance_face: bool

        :return: A tuple containing the task ID and the scale data.
        :rtype: tuple[str, dict]
        """
        oss = await self.get_oss_authorizations(filename)
        url, headers = self._signature(filename, oss)
        response, _ = await self.request('PUT', url, data=bytes_, headers=headers)
        type = 2 if enhance_face else 1
        scale_data = await self.get_task_id(response['data']['resource_id'], type)
        task_id = scale_data['data']['task_id']
        while True:
            scale = await self.get_scale(task_id)
            if scale['data']['image']:
                return task_id, scale
            await asyncio.sleep(self.sleep_duration)

    async def get_image_url(self, task_id: str) -> tuple[str, dict]:
        """
        Retrieves the image URL for the given task ID.

        :param task_id: The ID of the task.
        :type task_id: str

        :return: A tuple containing the image URL and additional data.
        :rtype: tuple[str, dict]
        """
        url = self._base_url + f'/tasks/login/image-url/scale/{task_id}'
        params = self._params | {'pic_quality': 'free'}
        response, _ = await self.request('GET', url, params=params, headers=self._headers)
        self._remaining_downloads -= 1
        if self._remaining_downloads <= 0:
            self.update_token()
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
        url = self._base_url + '/tasks/login/scale'
        data = {
            'website': 'en',
            'source_resource_id': resource_id,
            'resource_id': resource_id,
            'type': type
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
        url = self._base_url + f'/tasks/login/scale/{task_id}'
        response, _ = await self.request('GET', url, params=self._params, headers=self._headers)
        return response

    async def enhance(
        self,
        source: str | bytes,
        *,
        no_watermark: bool = True,
        enhance_face: bool = True
    ) -> EnhancedImage:
        """
        Enhances the image.
        And returns an EnhancedImage object.

        :param source: The image source, which can be a file path or bytes.
        :type source: str | bytes
        :param no_watermark: Whether to remove the watermark from the image.
        :type no_watermark: bool
        :param enhance_face: Whether to enhance faces in the image.
        :type enhance_face: bool

        :return: An EnhancedImage object containing the enhanced image and watermark status.
        :rtype: EnhancedImage
        """
        if isinstance(source, str):
            path: Path = Path(source)
            filename = path.name
            bytes_ = path.read_bytes()
        elif isinstance(source, bytes):
            ft = filetype.guess(source)
            filename = f'f.{ft.extension}'
            bytes_ = source
        else:
            raise TypeError('Source must be string or bytes.')

        task_id, data = await self.create_task(bytes_, filename, enhance_face)
        watermark = True
        if no_watermark:
            watermark = False
            data = await self.get_image_url(task_id)
        return EnhancedImage(self.http, data['data']['image'], watermark=watermark)
