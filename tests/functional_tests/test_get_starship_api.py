import logging

import jsonschema
import pytest
import requests

endpoint = "/starships/"


def id_for_value(val):
    return endpoint + str(val)


@pytest.fixture(scope="class", params=[], ids=id_for_value)
def id(request):
    return request.param


@pytest.fixture(scope="class")
def response(origin, id):
    logging.info(f"curl -X -i GET '{origin}{endpoint}{id}'")
    response = requests.get(f"{origin}{endpoint}{id}")
    return response


@pytest.mark.functional
@pytest.mark.positive
@pytest.mark.parametrize('id', [0, 1, 99], ids=id_for_value, indirect=True)
class TestGetStarshipsEndpointPositive:

    @pytest.fixture(scope="class")
    def response_body(self, response):
        if response.status_code != 200:
            pytest.skip("Response wasn't successful")
        return response.json()

    def test_get_people_endpoint_status_code(self, response, id):
        assert response.status_code == 200

    def test_get_starships_endpoint_json_schema(self, response_body, id):
        starships_schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "model": {"type": "string"},
                "manufacturer": {"type": "string"},
                "cost_in_credits": {"type": "string"},
                "length": {"type": "string"},
                "max_atmosphering_speed": {"type": "string"},
                "crew": {"type": "string"},
                "passengers": {"type": "string"},
                "cargo_capacity": {"type": "string"},
                "consumables": {"type": "string"},
                "hyperdrive_rating": {"type": "string"},
                "MGLT": {"type": "string"},
                "starship_class": {"type": "string"},
                "pilots": {"type": "array", "items": {"type": "string"}},
                "films": {"type": "array", "items": {"type": "string"}},
                "created": {"type": "string"},
                "edited": {"type": "string"},
                "url": {"type": "string"}
            }
        }
        jsonschema.validate(response_body, starships_schema)

    def test_get_starships_endpoint_data(self, response_body, id):
        actual_data = response_body
        expected_data = requests.get("https://swapi.dev/api/starships/9").json()
        discrepancies = []
        for key, expected_value in expected_data.items():
            if not actual_data.get(key) == expected_value:
                discrepancies.append(f"{key} doesn't match: expected '{expected_value}', actual '{actual_data.get(key)}'")
        assert not discrepancies, "\n".join(discrepancies)


@pytest.mark.functional
@pytest.mark.negative
class TestGetStarshipsEndpointErrors:

    @pytest.mark.parametrize('id', [-1, "not_a_number"], ids=id_for_value, indirect=True)
    def test_wrong_format_response(self, response, id):
        assert response.status_code == 400
        assert response.json() == {"Error": f"Id should match pattern '\\d+'"}

    @pytest.mark.parametrize('id', [100], ids=id_for_value, indirect=True)
    def test_object_not_found_error(self, response, id):
        assert response.status_code == 404
        assert response.json() == {"Error": f"Object with id {id} not found"}