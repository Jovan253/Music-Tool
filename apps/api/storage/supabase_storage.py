import os
from supabase import create_client, Client

_url = os.environ.get("SUPABASE_URL")
_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not _url:
    raise RuntimeError("SUPABASE_URL environment variable is not set")
if not _key:
    raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY environment variable is not set")

_client: Client = create_client(_url, _key)


def upload_file(bucket: str, path: str, data: bytes, content_type: str) -> None:
    _client.storage.from_(bucket).upload(
        path=path,
        file=data,
        file_options={"content-type": content_type},
    )


def download_file(bucket: str, path: str) -> bytes:
    return _client.storage.from_(bucket).download(path)


def get_client() -> Client:
    return _client


def create_signed_url(bucket: str, path: str, ttl_seconds: int) -> str:
    result = _client.storage.from_(bucket).create_signed_url(path, ttl_seconds)
    if isinstance(result, dict):
        return result.get("signedURL") or result.get("signedUrl", "")
    return result.signed_url
