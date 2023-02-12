import argparse
import logging
import os

import yaml
from flask import Flask, jsonify, request

from server.dummy_data_provider import DummyDataProvider
from server.models.server_config import ServerConfigs

app = Flask(__name__)
data_provider = DummyDataProvider()
logger = logging.getLogger('DummyServer')


@app.route("/people/<id>", methods=["GET"], strict_slashes=False)
def get_person_info(id):
    """
    GET /people/{id}
    """
    response_body, response_status_code = data_provider.get_person_info(id)
    return jsonify(response_body), response_status_code


@app.route("/planets/<id>", methods=["GET"], strict_slashes=False)
def get_planet_info(id):
    """
    GET /planets/{id}
    """
    response_body, response_status_code = data_provider.get_planet_info(id)
    return jsonify(response_body), response_status_code


@app.route("/starships/<id>", methods=["GET"], strict_slashes=False)
def get_starship_info(id):
    """
    GET /starships/{id}
    """
    response_body, response_status_code = data_provider.get_starship_info(id)
    return jsonify(response_body), response_status_code


def read_server_configs_from_config_file() -> ServerConfigs:
    with open(os.path.join(os.path.dirname(__file__), "configs/server_configs.yaml"), 'r') as stream:
        configs = yaml.safe_load(stream)
        return ServerConfigs(host=configs.get("host"),
                             port=configs.get("port"),
                             debug=configs.get("debug"))


def read_server_configs_from_args() -> ServerConfigs:
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, required=False, default=None)
    parser.add_argument('--port', type=int, required=False, default=None)
    parser.add_argument('--debug', type=bool, required=False, default=None)
    args_from_parser = parser.parse_args()
    return ServerConfigs(host=args_from_parser.host,
                         port=args_from_parser.port,
                         debug=args_from_parser.debug)


def init_logger(level):
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message).300s'
    # basic logger confing, also responsible for console logs
    logging.basicConfig(format=log_format, level=level)
    # file logger
    file_logger = logging.FileHandler(os.path.join(os.path.dirname(__file__), "dummy_server.log"))
    file_logger.setLevel(level)
    file_logger.setFormatter(logging.Formatter(log_format))
    logger.addHandler(file_logger)


def start_server(host, port, debug):
    init_logger(logging.DEBUG if debug else logging.INFO)
    logger.info("Server start")
    return app.run(host=host, port=port)


def shutdown_server():
    logger.info("Server shutdown")
    app.do_teardown_appcontext()


@app.after_request
def log_response(response):
    log_msg = f'{request.method} {request.url} {request.get_data()} --> '\
              f'{response.status} {response.get_data()}'
    logger.info(log_msg)
    return response


if __name__ == '__main__':
    configs = read_server_configs_from_args()
    if configs.check_missing_configs():
        default_configs = read_server_configs_from_config_file()
        configs.set_missing_configs_from(default_configs)
    start_server(configs.host, configs.port, configs.debug)
