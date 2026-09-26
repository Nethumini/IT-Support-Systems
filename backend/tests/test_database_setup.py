"""The database must open from a clean clone.

``backend/data/processed`` is ignored by git, so a fresh checkout has no
directory for the default SQLite file, and every test that started the app
failed with "unable to open database file". The engine now creates the
configured file's directory on first connection. These tests pin down that it
creates exactly that directory, only when connecting, and never for an
in-memory database.
"""
from pathlib import Path

from sqlalchemy import text

from app.core.database import create_app_engine, sqlite_file_path


def _connect(engine):
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    engine.dispose()


def _everything_under(root: Path):
    return sorted(p.relative_to(root).as_posix() for p in root.rglob("*"))


# --- which URLs name a file ---------------------------------------------------

def test_a_relative_sqlite_url_names_its_file():
    assert sqlite_file_path("sqlite:///./data/processed/app.db") == Path("./data/processed/app.db")


def test_an_absolute_sqlite_url_names_its_file(tmp_path):
    assert sqlite_file_path(f"sqlite:///{tmp_path}/app.db") == tmp_path / "app.db"


def test_in_memory_databases_name_no_file():
    for url in (
        "sqlite://",
        "sqlite:///:memory:",
        "sqlite:///file:shared?mode=memory&uri=true",
    ):
        assert sqlite_file_path(url) is None, url


def test_other_databases_are_left_alone():
    assert sqlite_file_path("postgresql://user@localhost/autoops") is None


# --- what connecting creates --------------------------------------------------

def test_the_directory_is_created_on_first_connection(tmp_path):
    database = tmp_path / "data" / "processed" / "app.db"
    engine = create_app_engine(f"sqlite:///{database}")

    assert not database.parent.exists()      # creating the engine touches nothing
    _connect(engine)

    assert database.exists()


def test_only_the_configured_directory_is_created(tmp_path):
    engine = create_app_engine(f"sqlite:///{tmp_path}/one/two/app.db")
    _connect(engine)

    assert _everything_under(tmp_path) == ["one", "one/two", "one/two/app.db"]


def test_a_relative_path_resolves_under_the_working_directory(tmp_path, monkeypatch):
    """The same resolution SQLite uses, so the directory made is the one the
    file will be written to - never somewhere else."""
    monkeypatch.chdir(tmp_path)
    engine = create_app_engine("sqlite:///./data/processed/app.db")
    _connect(engine)

    assert (tmp_path / "data" / "processed" / "app.db").exists()


def test_an_existing_directory_is_reused(tmp_path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "keep.txt").write_text("untouched")
    engine = create_app_engine(f"sqlite:///{tmp_path}/data/app.db")
    _connect(engine)

    assert (tmp_path / "data" / "keep.txt").read_text() == "untouched"
    assert (tmp_path / "data" / "app.db").exists()


def test_an_in_memory_database_creates_nothing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for url in ("sqlite://", "sqlite:///:memory:"):
        _connect(create_app_engine(url))

    assert _everything_under(tmp_path) == []
