from storage.supabase_storage import _normalize_url

PROJECT_URL = "https://abcdefgh.supabase.co"


def test_project_url_is_unchanged():
    assert _normalize_url(PROJECT_URL) == PROJECT_URL


def test_rest_suffix_is_stripped():
    # This is the mistake that actually happened: copying the REST API URL from the
    # dashboard instead of the project URL. Every auth call 404s and the app reports
    # a generic 401, so it looks like bad credentials rather than a bad URL.
    assert _normalize_url(f"{PROJECT_URL}/rest/v1/") == PROJECT_URL
    assert _normalize_url(f"{PROJECT_URL}/rest/v1") == PROJECT_URL


def test_other_api_suffixes_are_stripped():
    assert _normalize_url(f"{PROJECT_URL}/auth/v1") == PROJECT_URL
    assert _normalize_url(f"{PROJECT_URL}/storage/v1") == PROJECT_URL


def test_trailing_slash_and_whitespace_are_stripped():
    assert _normalize_url(f"  {PROJECT_URL}/  ") == PROJECT_URL
