import logging

import jsonschema
import pytest
import requests

endpoint = "/planets/"


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
class TestGetPlanetEndpointPositive:

    @pytest.fixture(scope="class")
    def response_body(self, response):
        if response.status_code != 200:
            pytest.skip("Response wasn't successful")
        return response.json()

    def test_get_people_endpoint_status_code(self, response, id):
        assert response.status_code == 200

    def test_get_planets_endpoint_json_schema(self, response_body, id):
        planets_schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "rotation_period": {"type": "string"},
                "orbital_period": {"type": "string"},
                "diameter": {"type": "string"},
                "climate": {"type": "string"},
                "gravity": {"type": "string"},
                "terrain": {"type": "string"},
                "surface_water": {"type": "string"},
                "population": {"type": "string"},
                "residents": {"type": "array", "items": {"type": "string"}},
                "films": {"type": "array", "items": {"type": "string"}},
                "created": {"type": "string"},
                "edited": {"type": "string"},
                "url": {"type": "string"}
            }
        }
        jsonschema.validate(response_body, planets_schema)

    def test_get_planets_endpoint_data(self, response_body, id):
        actual_data = response_body
        expected_data = requests.get("https://swapi.dev/api/planets/3").json()
        discrepancies = []
        for key, expected_value in expected_data.items():
            if not actual_data.get(key) == expected_value:
                discrepancies.append(f"{key} doesn't match: expected '{expected_value}', actual '{actual_data.get(key)}'")
        assert not discrepancies, "\n".join(discrepancies)


@pytest.mark.functional
@pytest.mark.negative
class TestGetPlanetsEndpointErrors:

    @pytest.mark.parametrize('id', [-1, "not_a_number"], ids=id_for_value, indirect=True)
    def test_wrong_format_response(self, response, id):
        assert response.status_code == 400
        assert response.json() == {"Error": f"Id should match pattern '\\d+'"}

    @pytest.mark.parametrize('id', [100], ids=id_for_value, indirect=True)
    def test_object_not_found_error(self, response, id):
        assert response.status_code == 404
        assert response.json() == {"Error": f"Object with id {id} not found"}