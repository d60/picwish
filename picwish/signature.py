import base64
import hashlib
import hmac
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Signature:
    """
    Represents the signature for OSS.

    :param access_key_id: The access key ID for OSS.
    :type access_key_id: str
    :param access_key_secret: The access key secret for OSS.
    :type access_key_secret: str
    :param verb: The HTTP method.
    :type verb: str
    :param content_md5: The MD5 hash of the content.
    :type content_md5: str
    :param headers: The headers to include in the request.
    :type headers: dict[str, Any]
    :param bucket: The OSS bucket name.
    :type bucket: str
    :param object: The OSS object key.
    :type object: str
    :param sub_resources: A dict of sub resources for the request.
    :type sub_resources: dict
    """
    access_key_id: str
    access_key_secret: str
    verb: str
    content_md5: str
    headers: dict[str, Any]
    bucket: str
    object: str
    sub_resources: dict

    def CanonicalizedOSSHeaders(self):
        """
        Generates the canonicalized OSS headers for signing.

        x-oss-name1:value1\nx-oss-name2:value2\nx-oss-name3:value3

        :return: The canonicalized OSS headers as a string.
        :rtype: str
        """
        headers = {k.lower(): v for k, v in self.headers.items()}
        keys = [i.lower() for i in headers.keys()]
        keys.sort()

        l = []
        for k in keys:
            if k.startswith('x-oss-'):
                l.append(f'{k}:{headers[k]}')
        return '\n'.join(l)

    def CanonicalizedResource(self):
        """
        Generates the canonicalized resource string for signing.

        /BucketName/ObjectName?q1=value1&q2=value2&...

        :return: The canonicalized resource path and query parameters as a string.
        :rtype: str
        """
        resource_path = f'/{self.bucket}' if self.bucket else ''
        resource_path += f'/{self.object}' if self.object else ''
        if self.sub_resources:
            query_params = '&'.join([f'{k}={v}' for k, v in self.sub_resources.items()])
            resource_path += f'?{query_params}'
        return resource_path

    def make_signature(self):
        """
        Creates the HMAC-SHA1 signature for the OSS request.

        Base64(SHA1(
            VERB\n
            MD5\n
            Content-Type\n
            Date\n
            CanonicalizedOSSHeaders\n
            CanonicalizedResource
        ))

        :return: The base64-encoded signature.
        :rtype: str
        """
        l = [
            self.verb,
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
