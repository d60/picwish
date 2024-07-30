import asyncio
import base64
import json
import mimetypes
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from httpx import AsyncClient, Response

from .errors import PicwishError
from .signature import Signature


@dataclass(frozen=True)
class EnhancedImage:
    _http: AsyncClient
    url: str
    watermark: bool

    async def download(self, output: str) -> None:
        response = await self._http.get(self.url)
        with open(output, 'wb') as f:
            f.write(response.content)


class Enhancer:
    _product_id = 482
    _language = 'en'
    _params = {
        'product_id': _product_id,
        'language': _language
    }

    def __init__(self, token: str, **kwargs) -> None:
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
        url = 'https://gw.aoscdn.com/app/picwish/authorizations/oss'
        data = {'filenames': [filename]}
        response, _ = await self.request('POST', url, json=data, params=self._params, headers=self._headers)
        return response

    async def _signature(self, filename: str, oss: str) -> tuple[str, dict]:
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

    async def create_task(self, path: Path) -> tuple[str, dict]:
        oss = await self.get_oss_authorizations(path.name)
        url, headers = await self._signature(path.name, oss)
        response, _ = await self.request('PUT', url, data=path.read_bytes(), headers=headers)
        scale_data = await self.get_task_id(response['data']['resource_id'])
        task_id = scale_data['data']['task_id']
        while True:
            scale = await self.get_scale(task_id)
            if scale['data']['image']:
                return task_id, scale
            await asyncio.sleep(0.5)

    async def get_image_url(self, task_id: str, pic_quality: str = 'free') -> tuple[str, dict]:
        url = f'https://gw.aoscdn.com/app/picwish/tasks/login/image-url/scale/{task_id}'
        params = self._params | {'pic_quality': pic_quality}
        response, _ = await self.request('GET', url, params=params, headers=self._headers)
        return response

    async def get_task_id(self, resource_id: str) -> dict:
        url = 'https://gw.aoscdn.com/app/picwish/tasks/login/scale'
        data = {
            "website": "en",
            "source_resource_id": resource_id,
            "resource_id": resource_id,
            # "type": 2
        }
        response, _ = await self.request('POST', url, params=self._params, json=data, headers=self._headers)
        return response

    async def get_scale(self, task_id: str) -> dict:
        url = f'https://gw.aoscdn.com/app/picwish/tasks/login/scale/{task_id}'
        response, _ = await self.request('GET', url, params=self._params, headers=self._headers)
        return response

    async def enhance(self, path: str, *, no_watermark: bool = True, quality: str = 'free') -> EnhancedImage:
        task_id, data = await self.create_task(Path(path))
        watermark = True
        if no_watermark:
            no_watermark = await self.get_image_url(task_id, quality)
            if no_watermark['status'] == 200:
                data = no_watermark
                watermark = False
        return EnhancedImage(self.http, data['data']['image'], watermark=watermark)
