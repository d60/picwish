import base64
import hashlib
import hmac
from dataclasses import dataclass


@dataclass(frozen=True)
class Signature:
    access_key_id: str
    access_key_secret: str
    verb: str
    content_md5: str
    headers: dict
    bucket: str
    object: str
    sub_resources: list

    def CanonicalizedOSSHeaders(self):
        headers = {k.lower(): v for k, v in self.headers.items()}
        keys = [i.lower() for i in headers.keys()]
        keys.sort()

        l = []
        for k in keys:
            if k.startswith("x-oss-"):
                l.append(f"{k}:{headers[k]}")
        return '\n'.join(l)

    def CanonicalizedResource(self):
        resource_path = f'/{self.bucket}' if self.bucket else ''
        resource_path += f'/{self.object}' if self.object else ''
        if self.sub_resources:
            query_params = "&".join([f"{index}={char}" for index, char in enumerate(self.sub_resources)])
            resource_path += f"?{query_params}"
        return resource_path

    def make_signature(self):
        l = [
            'PUT',
            self.content_md5,
            self.headers['Content-Type'],
            self.headers['X-Oss-Date'],
            self.CanonicalizedOSSHeaders(),
            self.CanonicalizedResource()
        ]
        string_to_sign = '\n'.join(l)
        signature = hmac.new(self.access_key_secret.encode('utf-8'), string_to_sign.encode('utf-8'), hashlib.sha1)
        signature_base64 = base64.b64encode(signature.digest()).decode()
        return signature_base64
