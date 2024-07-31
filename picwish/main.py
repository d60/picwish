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
    Exception raised for errors related to the PicWish API.

    :ivar token: The token associated with the request that caused the error.
    :type token: str
    :ivar status_code: The HTTP status code associated with the error.
    :type status_code: int | None
    :ivar api_status: API-specific error code.
    :type api_status: int | None
    """
    def __init__(self, message: str, token: str, status_code: int | None = None, api_status: int | None = None) -> None:
        super().__init__(message)
        self.token = token
        self.status_code = status_code
        self.api_status = api_status


class API:
    """
    A class for interacting with the PicWish API.

    :param http: The asynchronous HTTP client.
    :type http: AsyncClient
    :param retry_after: Delay before retrying requests if a 429 error occurs.
    :type retry_after: float | None
    """
    _base_url = 'https://gw.aoscdn.com/app/picwish'
    _api_version = 'v2'
    _product_id = 482
    _language = 'en'
    _params = {
        'product_id': _product_id,
        'language': _language
    }

    def __init__(self, http: AsyncClient, retry_after: float | None) -> None:
        self.http = http
        self.retry_after = retry_after
        self.token = ','.join([
            self._api_version,
            str(random.randint(10000000, 99999999)),
            str(self._product_id),
            uuid.uuid4().hex
        ])

    @property
    def _headers(self) -> dict:
        return {
            'Authorization': f'Bearer {self.token}'
        }

    async def request(self, method: str, url: str, *args, **kwargs) -> tuple[Any, Response]:
        response = await self.http.request(method, url, *args, **kwargs)
        try:
            response_data: dict = response.json()
            api_status = response_data.get('status')
            error_message = response_data.get('message')
        except json.JSONDecodeError:
            response_data = response.text
            api_status = None
            error_message = response.reason_phrase

        status = response.status_code
        if (api_status is not None and api_status != 200) or 400 <= status < 600:
            if status == 429 and self.retry_after is not None:
                # Sleep and retry if the status is 429
                await asyncio.sleep(self.retry_after)
                return await self.request(method, url, *args, **kwargs)

            messages = [f'status: {status}']
            if api_status is not None:
                messages.append(f'APIStatus: {response_data["status"]}')
            messages.append(f'message: {error_message}')
            raise PicwishError(', '.join(messages), self.token, status, api_status)

        return response_data, response

    async def oss_authorizations(self, filename: str) -> dict:
        """
        Retrieves OSS authorization data for the specified filename.

        :param filename: The name of the file to retrieve authorizations for.
        :type filename: str

        :return: A dictionary containing OSS authorization data.
        :rtype: dict
        """
        url = self._base_url + '/authorizations/oss'
        data = {'filenames': [filename]}
        response, _ = await self.request('POST', url, json=data, params=self._params, headers=self._headers)
        return response

    async def get_task(self, resource_id: str, type: int) -> dict:
        """
        Retrieves task data for the given resource ID.

        :param resource_id: The ID of the resource.
        :type resource_id: str
        :param type: The type of the task.
        :type type: int

        :return: A dictionary containing task data.
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

    async def image_url(self, task_id: str) -> dict:
        """
        Retrieves the image URL for the given task ID.

        :param task_id: The ID of the task.
        :type task_id: str

        :return: A dict containing the image URL and additional data.
        :rtype: dict
        """
        url = self._base_url + f'/tasks/login/image-url/scale/{task_id}'
        params = self._params | {'pic_quality': 'free'}
        response, _ = await self.request('GET', url, params=params, headers=self._headers)
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


@dataclass(frozen=True)
class EnhancedImage:
    """
    Represents an enhanced image.

    :ivar url: The URL of the enhanced image.
    :type url: str
    :ivar watermark: Indicates whether the image has a watermark.
    :type watermark: bool
    """
    _http: AsyncClient
    url: str
    watermark: bool

    async def get_bytes(self) -> bytes:
        """
        Fetches the image bytes from the URL.

        :return: The content of the image in bytes.
        :rtype: bytes
        """
        response = await self._http.get(self.url)
        return response.content

    async def download(self, output: str) -> None:
        """
        Downloads the image and saves it to the specified file path.

        :param output: The file path where the image will be saved.
        :type output: str
        """
        Path(output).write_bytes(await self.get_bytes())


class Enhancer:
    """
    Provides methods to enhance images using the PicWish API.

    :param sleep_duration: The duration to sleep between progress checks, in seconds.
    :type sleep_duration: float
    :param retry_after: Delay before retrying requests if 429 error occurs.
    :type retry_after: float | None
    :param kwargs: Optional HTTP client settings.
    """
    def __init__(self, sleep_duration: float = 0.5, retry_after: float | None = 0.5, **kwargs) -> None:
        self.http = AsyncClient(**kwargs)
        self.sleep_duration = sleep_duration
        self.retry_after = retry_after

    def _signature(self, mimetype: str, oss: str) -> tuple[str, dict]:
        """
        Creates the necessary signature for OSS requests.
        Returns the URL and headers.

        :param mimetype: The mimetype of the source.
        :type mimetype: str
        :param oss: The OSS authorization data obtained from the PicWish API.
        :type oss: dict

        :return: The signed URL and headers.
        :rtype: tuple[str, dict]
        """
        access_key_id = oss['data']['credential']['access_key_id']
        access_key_secret = oss['data']['credential']['access_key_secret']
        security_token = oss['data']['credential']['security_token']
        accelerate = oss['data']['accelerate']
        bucket = oss['data']['bucket']
        object = next(iter(oss['data']['objects'].values()))
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
            'Content-Type': mimetype,
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

        headers['Authorization'] = f'OSS {access_key_id}:{signature}'
        url = f'https://{bucket}.{accelerate}/{object}'
        return url, headers

    @staticmethod
    def _process_source(source: str | bytes) -> tuple[str, bytes]:
        """
        Processes the image source and returns the filename and bytes.

        :param source: The image source. path or bytes.
        :type source: str | bytes

        :return: Tuple of filename, mimetype, the bytes of the image.
        :rtype: tuple[str, str, bytes]
        """
        if isinstance(source, str):
            path: Path = Path(source)
            filename = path.name
            bytes_ = path.read_bytes()
            mimetype = mimetypes.guess_type(filename)[0]
        elif isinstance(source, bytes):
            ft = filetype.guess(source)
            filename = f'image.{ft.extension}'
            bytes_ = source
            mimetype = ft.mime
        else:
            raise TypeError('Source must be string or bytes.')
        return filename, mimetype, bytes_

    async def enhance(
        self,
        source: str | bytes,
        *,
        no_watermark: bool = True,
        enhance_face: bool = True
    ) -> EnhancedImage:
        """
        Enhances the image and returns an EnhancedImage object.

        :param source: The image source, which can be a file path or a byte stream.
        :type source: str | bytes
        :param no_watermark: Whether to remove the watermark from the image.
        :type no_watermark: bool
        :param enhance_face: Whether to enhance faces in the image.
        :type enhance_face: bool

        :return: An EnhancedImage object containing the enhanced image and watermark status.
        :rtype: EnhancedImage
        """
        api = API(self.http, self.retry_after)
        filename, mimetype, bytes_ = self._process_source(source)
        oss = await api.oss_authorizations(filename)
        url, headers = self._signature(mimetype, oss)
        # Upload the image with signature
        response, _ = await api.request('PUT', url, data=bytes_, headers=headers)
        type = 2 if enhance_face else 1
        scale_data = await api.get_task(response['data']['resource_id'], type)
        task_id = scale_data['data']['task_id']

        # Wait for the image processing to complete
        while True:
            data = await api.get_scale(task_id)
            if data['data']['image']:
                break
            await asyncio.sleep(self.sleep_duration)

        watermark = True
        if no_watermark:
            watermark = False
            data = await api.image_url(task_id)
        return EnhancedImage(self.http, data['data']['image'], watermark=watermark)
