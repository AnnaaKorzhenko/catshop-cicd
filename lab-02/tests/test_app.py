import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import app as shop

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(shop, "DATABASE_URL", None)
    monkeypatch.setattr(shop, "COUNTER_FILE", tmp_path / "data" / "visits.txt")
    return shop.app.test_client()


@pytest.fixture
def broken_store(tmp_path, monkeypatch):
    blocker = tmp_path / "not-a-folder"
    blocker.write_text("")
    monkeypatch.setattr(shop, "COUNTER_FILE", blocker / "visits.txt")


def test_health_says_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.text == "ok\n"


def test_ready_names_the_file_store(client):
    r = client.get("/ready")
    assert r.status_code == 200
    assert r.json == {"ready": True, "store": f"file:{shop.COUNTER_FILE}"}


def test_visits_counts_up(client):
    assert client.get("/visits").json == {"visits": 1, "store": "file"}
    assert client.get("/visits").json == {"visits": 2, "store": "file"}


def test_visits_continues_from_the_saved_count(client):
    shop.COUNTER_FILE.parent.mkdir(parents=True)
    shop.COUNTER_FILE.write_text("41")
    assert client.get("/visits").json["visits"] == 42
    assert shop.COUNTER_FILE.read_text() == "42"


def test_visits_is_503_when_the_store_is_broken(client, broken_store):
    r = client.get("/visits")
    assert r.status_code == 503
    assert "error" in r.json


def test_health_stays_ok_when_the_store_is_broken(client, broken_store):
    assert client.get("/health").status_code == 200
    assert client.get("/ready").status_code == 503