import pytest
from unittest.mock import patch, MagicMock
from cml_exporter.cml_exporter import CMLClient


@pytest.fixture
def client():
    return CMLClient("https://test-host", "testuser", "testpass")


def test_login_success(client):
    with patch.object(client.session, "post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = "fake-token"
        mock_post.return_value = mock_resp

        client.login()
        assert client.token == "fake-token"
        assert client.session.headers["Authorization"] == "Bearer fake-token"


def test_login_failure(client):
    with patch.object(client.session, "post") as mock_post:
        mock_post.side_effect = Exception("Auth failed")
        with pytest.raises(Exception):
            client.login()


def test_check_authentication_token_valid(client):
    client.token = "some-token"
    with patch.object(client.session, "get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp
        client.check_authentication()
        assert client.token == "some-token"


def test_check_authentication_token_invalid(client):
    client.token = "some-token"
    with patch.object(client.session, "get") as mock_get, patch.object(client, "login") as mock_login:
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = Exception()
        mock_get.return_value = mock_resp
        client.token = None
        client.check_authentication()
        mock_login.assert_called_once()


def test_check_authentication_no_token(client):
    client.token = None
    with patch.object(client, "login") as mock_login:
        client.check_authentication()
        mock_login.assert_called_once()


def test_get_system_stats(client):
    with patch.object(client.session, "get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {"stats": "value"}
        mock_get.return_value = mock_resp
        result = client.get_system_stats()
        assert result == {"stats": "value"}


def test_get_labs(client):
    with patch.object(client.session, "get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = ["lab1", "lab2"]
        mock_get.return_value = mock_resp
        result = client.get_labs()
        assert result == ["lab1", "lab2"]


def test_get_lab_details(client):
    with patch.object(client.session, "get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {"id": "lab1", "state": "STARTED"}
        mock_get.return_value = mock_resp
        result = client.get_lab_details("lab1")
        assert result == {"id": "lab1", "state": "STARTED"}


def test_get_lab_element_states(client):
    with patch.object(client.session, "get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {"nodes": {"n1": "BOOTED"}}
        mock_get.return_value = mock_resp
        result = client.get_lab_element_states("lab1")
        assert result == {"nodes": {"n1": "BOOTED"}}


def test_error_count_increment_on_exception(client):
    with patch.object(client.session, "get") as mock_get:
        mock_get.side_effect = Exception("API error")
        with pytest.raises(Exception):
            client.get_system_stats()
    # error_count is not incremented here, but in collect_metrics
    assert client.error_count == 0
