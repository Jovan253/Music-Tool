from db import _normalize_url


def test_bare_postgresql_gets_explicit_psycopg_driver():
    assert (
        _normalize_url("postgresql://u:p@host:5432/db")
        == "postgresql+psycopg://u:p@host:5432/db"
    )


def test_heroku_style_postgres_scheme_is_upgraded():
    # SQLAlchemy rejects postgres:// outright; several hosts still emit it.
    assert (
        _normalize_url("postgres://u:p@host:5432/db")
        == "postgresql+psycopg://u:p@host:5432/db"
    )


def test_explicit_driver_is_left_alone():
    url = "postgresql+psycopg2://u:p@host:5432/db"
    assert _normalize_url(url) == url


def test_query_params_survive():
    assert _normalize_url("postgres://u:p@host/db?sslmode=require").endswith(
        "?sslmode=require"
    )
