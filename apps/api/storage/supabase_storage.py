import os
from supabase import create_client, Client

_url = os.environ.get("SUPABASE_URL")
_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not _url:
    raise RuntimeError("SUPABASE_URL environment variable is not set")
if not _key:
    raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY environment variable is not set")


def _normalize_url(url: str) -> str:
    # The dashboard shows both a project URL and a REST URL. Pasting the REST one
    # makes the client build paths like /rest/v1/auth/v1/user, which 404s and then
    # surfaces as a generic 401 with nothing pointing at the real cause.
    url = url.strip().rstrip("/")
    for suffix in ("/rest/v1", "/auth/v1", "/storage/v1"):
        if url.endswith(suffix):
            url = url[: -len(suffix)]
    return url


SUPABASE_URL = _normalize_url(_url)

_client: Client = create_client(SUPABASE_URL, _key)


def upload_file(bucket: str, path: str, data: bytes, content_type: str) -> None:
    _client.storage.from_(bucket).upload(
        path=path,
        file=data,
        file_options={"content-type": content_type},
    )


def download_file(bucket: str, path: str) -> bytes:
    return _client.storage.from_(bucket).download(path)


def delete_files(bucket: str, paths: list[str]) -> None:
    # Deleting an absent path is not an error here: the retention sweep must be
    # safe to re-run after a partial failure.
    if not paths:
        return
    _client.storage.from_(bucket).remove(paths)


def list_files(bucket: str, prefix: str) -> list[str]:
    entries = _client.storage.from_(bucket).list(prefix)
    return [f"{prefix.rstrip('/')}/{e['name']}" for e in entries if e.get("name")]


def get_client() -> Client:
    return _client


def create_signed_url(bucket: str, path: str, ttl_seconds: int) -> str:
    result = _client.storage.from_(bucket).create_signed_url(path, ttl_seconds)
    if isinstance(result, dict):
        return result.get("signedURL") or result.get("signedUrl", "")
    return result.signed_url
