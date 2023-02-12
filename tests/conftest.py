import logging
import threading
from typing import Optional

import pytest

from server.dummy_server import start_server, shutdown_server, app
from server.models.server_config import ServerConfigs


def pytest_addoption(parser):
    parser.addoption("--port", action='store_true', help='DummyServer port to start', default=6000)
    parser.addoption("--host", action='store_true', help='DummyServer host to start', default="127.0.0.1")
    parser.addoption("--debug-mode", action='store_true', help='DummyServer port debug mode on/off', default=True)


@pytest.fixture(scope="session")
def server_configs(request):
    return ServerConfigs(request.config.getoption('--host'),
                         request.config.getoption('--port'),
                         request.config.getoption('--debug-mode'))


@pytest.fixture(scope="session", autouse=True)
def setup_server(server_configs):

    class DummyServerThread(threading.Thread):

        def run(self) -> None:
            logging.info(f"Inner thread is {threading.current_thread().name}")
            try:
                start_server(server_configs.host, server_configs.port, server_configs.debug)
            except Exception as e:
                logging.error(e)

        def join(self, timeout: Optional[float] = 0) -> None:
            shutdown_server()
            super().join(timeout)


    server_daemon = DummyServerThread(daemon=True)
    server_daemon.start()
    logging.debug(f"Starting server on http://{server_configs.host}:{server_configs.port}")
    yield
    server_daemon.join()
    logging.debug(f"Stop server on http://{server_configs.host}:{server_configs.port}")


@pytest.fixture(scope="session", autouse=True)
def origin(server_configs):
    return f"http://{server_configs.host}:{server_configs.port}"
