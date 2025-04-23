import pytest
import pytest_asyncio
import os
from flask import Flask
from flask.testing import FlaskClient, FlaskCliRunner
from pymongo import MongoClient
from app import create_app


def pytest_configure():
    # Set app to use test database
    os.environ["MONGO_DB_NAME"] = "test"
    # Overwrite API key. Tests should not contact setlist.fm API
    os.environ["SETLISTFM_API_KEY"] = "mango"


@pytest_asyncio.fixture()
async def app() -> Flask:
    app = create_app()

    # Reset database
    mongo_client = MongoClient("mongodb://localhost:27017/")
    db = mongo_client[os.getenv("MONGO_DB_NAME")]
    db.drop_collection("artists")
    mongo_client.close()

    yield app

    # Remove handlers from all loggers
    # This also silences logs after the first test...
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
