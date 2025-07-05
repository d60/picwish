from __future__ import annotations

import asyncio
import base64
import json
import mimetypes
import random
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, NamedTuple

import filetype
from httpx import AsyncClient, Response

from .enums import OCRFormat, OCRLanguage, T2IQuality, T2ISize, T2ITheme
from .image_models import BackgroundRemovedImage, ColorizeResult, EnhancedImage, ExpandedImageResult, OCRResult, T2IResult
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


class CustomAPIRoute(NamedTuple):
    task: str | None = None
    image_url: str | None = None


@dataclass(frozen=True)
class Task:
    api: API
    id: str  # Task ID

    async def get_result(self) -> dict:
        return await self.api.get_task_result(self.id)

    async def wait(self, interval: float) -> dict:
        """
        Waits for the task to complete and returns the final result.
        """
        while True:
            data = await self.get_result()
            if data.get('data', {}).get('image') or data.get('data', {}).get('progress') == 100:
                return data
            await asyncio.sleep(interval)

    async def get_image_url(self, quality: str = 'free') -> dict:
        """
        Retrieves the URL of the processed image for the task.
        """
        return await self.api.get_image_url(self.id, quality)


class API:
    """
    A class for interacting with the PicWish API.

    :param http: The asynchronous HTTP client.
    :type http: AsyncClient
    :param retry_after: Delay before retrying requests if a 429 error occurs.
    :type retry_after: float | None
    :param route: Route object containing API routes.
    :type CustomAPIRoute
    """
    _base_url = 'https://gw.aoscdn.com/app/picwish'
    _api_version = 'v2'
    _product_id = 482
    _language = 'en'
    _params = {
        'product_id': _product_id,
        'language': _language
    }
    _user_agent = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/126.0.0.0 Safari/537.36')

    def __init__(self, http: AsyncClient, retry_after: float | None, route: CustomAPIRoute) -> None:
        self.http = http
        self.retry_after = retry_after
        self.route = route
        self.token = ','.join([
            self._api_version,
            str(random.randint(10000000, 99999999)),
            str(self._product_id),
            uuid.uuid4().hex
        ])

    @property
    def _headers(self) -> dict:
        return {
            'Authorization': f'Bearer {self.token}',
            'User-Agent': self._user_agent
        }

    async def request(self, method: str, url: str, *args, **kwargs) -> tuple[Any, Response]:
        response = await self.http.request(method, url, *args, **kwargs)
        api_status = None
        error_message = response.reason_phrase
        try:
            response_data: dict = response.json()
            api_status = response_data.get('status')
            error_message = response_data.get('message')
        except json.JSONDecodeError:
            response_data = response.text
        except UnicodeDecodeError:
            response_data = response.content

        status = response.status_code
        if (api_status is not None and api_status not in (0, 200)) or 400 <= status < 600:
            if (api_status == 429 or status == 429) and self.retry_after is not None:
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

    async def create_task(self, resource_id: str | None = None, additional_params: dict | None = None) -> dict:
        """
        Creates a task for the given resource ID.

        :param additional_params: Optional additional parameters to include in the task creation request.
        :type additional_params: dict | None

        :return: API response.
        :rtype: dict
        """
        url = self._base_url + self.route.task
        data = {
            'website': 'en'
        }
        if resource_id is not None:
            data['source_resource_id'] = resource_id
        if additional_params is not None:
            data |= additional_params
        response, _ = await self.request('POST', url, params=self._params, json=data, headers=self._headers)
        return response

    async def get_image_url(self, task_id: str, quality: str) -> dict:
        """
        Retrieves the image URL for the given task ID.

        :param task_id: The ID of the task.
        :type task_id: str

        :return: A dict containing the image URL and additional data.
        :rtype: dict
        """
        url = self._base_url + self.route.image_url + f'/{task_id}'
        params = self._params | {'pic_quality': quality}
        response, _ = await self.request('GET', url, params=params, headers=self._headers)
        return response

    async def get_task_result(self, task_id: str) -> dict:
        """
        Retrieves the task information for the given task ID.

        :param task_id: The ID of the task.
        :type task_id: str

        :return: A dictionary containing the task information.
        :rtype: dict
        """
        url = self._base_url + self.route.task + f'/{task_id}'
        response, _ = await self.request('GET', url, params=self._params, headers=self._headers)
        return response


class PicWish:
    """
    Provides methods to process images using the PicWish API.

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

    def _init_api(self, route: CustomAPIRoute) -> API:
        return API(self.http, self.retry_after, route)

    @staticmethod
    def _signature(mimetype: str, oss: str) -> tuple[str, dict]:
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
    def _process_source(source: str | bytes) -> tuple[str, str, bytes]:
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

    async def _get_resource_id(self, api: API, source: str | bytes) -> str:
        filename, mimetype, bytes_ = self._process_source(source)
        oss = await api.oss_authorizations(filename)
        url, headers = self._signature(mimetype, oss)
        # Upload the image with signature
        response, _ = await api.request('PUT', url, data=bytes_, headers=headers)
        return response['data']['resource_id']

    async def _create_task(self, api: API, source: str | bytes | None = None, additional_params: dict | None = None) -> Task:
        if source is None:
            task_data = await api.create_task(additional_params=additional_params)
        else:
            resource_id = await self._get_resource_id(api, source)
            task_data = await api.create_task(resource_id, additional_params)
        task_id = task_data['data']['task_id']
        return Task(api, task_id)

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

        :return: An EnhancedImage object.
        :rtype: EnhancedImage
        """
        route = CustomAPIRoute(
            task='/tasks/login/scale',
            image_url='/tasks/login/image-url/scale'
        )
        api = self._init_api(route=route)
        task = await self._create_task(api, source, {'type': 2 if enhance_face else 1})
        data = await task.wait(self.sleep_duration)

        watermark = True
        if no_watermark:
            watermark = False
            data = await task.get_image_url()
        return EnhancedImage(self.http, data['data']['image'], watermark, enhance_face)

    async def remove_background(self, source: str | bytes, *, no_watermark: bool = True) -> BackgroundRemovedImage:
        """
        Removes the background from an image and returns an BackgroundRemovedImage object.

        :param source: The image source, which can be a file path or a byte stream.
        :type source: str | bytes
        :param no_watermark: Whether to remove the watermark from the image.
        :type no_watermark: bool

        :return: An BackgroundRemovedImage object.
        :rtype: BackgroundRemovedImage
        """
        route = CustomAPIRoute(
            task='/tasks/login/segmentation',
            image_url='/tasks/login/image-url/segmentation'
        )
        api = self._init_api(route=route)
        task = await self._create_task(api, source, {'output_type': 1})
        data = await task.wait(self.sleep_duration)

        watermark = True
        if no_watermark:
            watermark = False
            data = await task.get_image_url()
        return BackgroundRemovedImage(self.http, data['data']['image'], watermark, data['data']['mask'])

    async def ocr(
        self,
        source: str | bytes,
        languages: list[OCRLanguage] | None = None,
        format: OCRFormat = OCRFormat.TXT
    ) -> OCRResult:
        """
        Performs OCR on an image and returns the result.
        It supports specifying multiple languages for OCR and allows
        selecting the desired output format.

        :param source: The image source, which can be a file path or a byte stream.
        :type source: str | bytes
        :param languages: A list of OCRLanguage values representing the languages to be used for OCR.
        :type languages: list[OCRLanguage] | None
        :param format: The desired output format of the OCR result.
        :type format: OCRFormat

        :return: An OCRResult object containing the OCR result.
        :rtype: OCRResult
        """
        if languages is None:
            languages = [OCRLanguage.DEFAULT]
        route = CustomAPIRoute(
            task='/tasks/ocr',
        )
        api = self._init_api(route=route)
        task = await self._create_task(api, source, {'format': format, 'task_language': ','.join(languages)})
        data = await task.wait(self.sleep_duration)
        return OCRResult(self.http, data['data']['image'], format)

    async def text_to_image(
        self,
        prompt: str,
        *,
        theme: T2ITheme = T2ITheme.GENERAL,
        size: T2ISize = T2ISize.HD_1_1,
        negative_prompt: str | None = None,
        batch_size: int = 4,
        quality: T2IQuality = T2IQuality.LOW,
        max_attempts: int = 1
    ) -> list[T2IResult]:
        """
        Generates images based on a text prompt and settings using AI.
        The generated images can be customized using various parameters
        such as the theme, dimensions, and quality.

        :param prompt: The text prompt used to generate the image.
        :type prompt: str
        :param theme: The theme or style for the generated image.
        :type theme: T2ITheme
        :param size: Size of image to be generated. Use T2ISize
        :type size: T2ISize
        :param negative_prompt: Specifies content or elements you want to avoid in the generated image.
        :type negative_prompt: str | None
        :param batch_size: The number of images to generate (1-4).
        :type batch_size: int
        :param quality: The quality setting for the image generation. low: 10-15s, high 25-30s
        :type quality: T2IQuality
        :param max_attempts: The maximum number of attempts to retry the request in case of failure.
        :type max_attempts: int

        :return: A list of `T2IResult` objects representing the generated images.
        :rtype: list[T2IResult]
        """
        route = CustomAPIRoute(
            task='/tasks/login/external/text-to-image'
        )
        api = self._init_api(route=route)
        configs = {
            'theme': theme.value,
            'width': size[0],
            'height': size[1],
            'prompt': prompt,
            'batch_size': batch_size,
            'speed': quality.value,
        }
        if negative_prompt is not None:
            configs['negative_prompt'] = negative_prompt
        for i in range(max_attempts):
            task = await self._create_task(api, additional_params=configs)
            try:
                data = await task.wait(self.sleep_duration)
            except PicwishError as e:
                if e.api_status in (-1, -10) and i + 1 < max_attempts:
                    # Retry if the API returns a block status
                    # and the maximum retry attempts have not been reached
                    continue
                raise e from e

        return [T2IResult(self.http, i['url'], i['id']) for i in data['data']['images']]

    async def colorize(self, source: str | bytes) -> ColorizeResult:
        """
        Colorizes the provided image.

        :param source: The image source, which can be a file path or a byte stream.
        :type source: str | bytes

        :return: An ColorizeResult object.
        :rtype: ColorizeResult
        """
        route = CustomAPIRoute(
            task='/tasks/colorization',
        )
        api = self._init_api(route=route)
        task = await self._create_task(api, source)
        data = await task.wait(self.sleep_duration)
        return ColorizeResult(self.http, data['data']['image'])

    async def expand(
        self,
        source: str | bytes,
        horizontal_expansion_ratio: float,
        vertical_expansion_ratio: float,
        image_count: int = 1,
        prompt: str | None = None,
        negative_prompt: str | None = None
    ) -> list[ExpandedImageResult]:
        """
        Expand an image with AI.

        :param source: The image source, which can be a file path or a byte stream.
        :type source: str | bytes
        :param horizontal_expansion_ratio: Ratio by which to expand the image horizontally.
        :type horizontal_expansion_ratio: float
        :param vertical_expansion_ratio: Ratio by which to expand the image vertically.
        :type vertical_expansion_ratio: float
        :param image_count: Number of expanded image variants to generate. Default is 1.
        :type image_count: int
        :param prompt: Optional prompt to guide the expansion.
        :type prompt: str | None
        :param negative_prompt: Optional negative prompt to avoid unwanted elements in the expansion.
        :type negative_prompt: str | None

        :return: A list of ExpandedImageResult objects.
        :rtype: list[ExpandedImageResult]
        """
        route = CustomAPIRoute(
            task='/tasks/login/image-expand'
        )
        configs = {
            'horizontal_expansion_ratio': horizontal_expansion_ratio,
            'vertical_expansion_ratio': vertical_expansion_ratio,
            'image_count': image_count
        }
        if prompt is not None:
            configs['prompt'] = prompt
        if negative_prompt is not None:
            configs['negative_prompt'] = negative_prompt
        api = self._init_api(route=route)
        task = await self._create_task(api, source, additional_params=configs)
        data = await task.wait(self.sleep_duration)
        return [ExpandedImageResult(self.http, data['data'][f'image{i}']) for i in range(1, image_count+1)]
