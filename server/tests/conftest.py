import pytest
import pytest_asyncio
from flask import Flask
from flask.testing import FlaskClient, FlaskCliRunner
from app import create_app


@pytest_asyncio.fixture()
async def app() -> Flask:
    app = create_app()
    app.config.update({
        "TESTING": True,
    })

    yield app

    # Remove handlers from all loggers
    # https://github.com/pytest-dev/pytest/issues/5502#issuecomment-1190557648
    import logging
    loggers = [logging.getLogger()] + list(logging.Logger.manager.loggerDict.values())
    for logger in loggers:
        logger.handlers = []

    app.wss.stop_server()


@pytest.fixture()
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture()
def runner(app: Flask) -> FlaskCliRunner:
    return app.test_cli_runner()
