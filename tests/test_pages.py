from flask.testing import FlaskClient


def test_stylesheet_is_served(client: FlaskClient) -> None:
    response = client.get("/css/style.css")
    assert response.status_code == 200
    assert response.mimetype == "text/css"
    assert b":root" in response.data
    assert b"--color-primary" in response.data


def test_login_page_uses_stylesheet(client: FlaskClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert b'href="/css/style.css"' in response.data
    assert b'class="login"' in response.data
    assert b'class="login-subtitle"' in response.data


def test_pos_page_uses_stylesheet(auth_client: FlaskClient) -> None:
    response = auth_client.get("/pos")
    assert response.status_code == 200
    assert b'href="/css/style.css"' in response.data
    assert b'class="brand"' in response.data
    assert b'role="alert"' in response.data


def test_missing_stylesheet_returns_404(client: FlaskClient) -> None:
    response = client.get("/css/missing.css")
    assert response.status_code == 404
