import pytest
from server.main import server


def test_server_init():
    assert server is not None
