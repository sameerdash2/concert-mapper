import pytest
from flask import Flask
from flask.testing import FlaskClient, FlaskCliRunner
from app import create_app


@pytest.fixture()
def app() -> Flask:
    app = create_app()
    app.config.update({
        "TESTING": True,
    })

    yield app


@pytest.fixture()
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture()
def runner(app: Flask) -> FlaskCliRunner:
    return app.test_cli_runner()
