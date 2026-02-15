import pytest
from server.db import FalkorDBClient


def test_db_init():
    client = FalkorDBClient()
    assert client.uri == "redis://localhost:6379"


def test_db_connect():
    client = FalkorDBClient()
    assert client.connect() is True
