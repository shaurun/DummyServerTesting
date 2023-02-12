import logging
import statistics
import time
from collections import defaultdict
from threading import Thread, Lock, Event

import pytest
import requests

endpoint = "/people/"

@pytest.fixture(scope="class", params=[10], ids=lambda x: f"{x} clients spamming")
def number_of_clients(request):
    return request.param


@pytest.fixture(scope="class", params=[60], ids=lambda x: f"{x} clients spamming")
def test_duration_sec(request):
    return request.param


@pytest.mark.performance
@pytest.mark.parametrize("number_of_clients", [10], indirect=True, ids=lambda x: f"{x} clients spamming")
@pytest.mark.parametrize("test_duration_sec", [60], indirect=True, ids=lambda x: f"{x} clients spamming")
class TestGetPeopleEndpointPerformance:

    def start_spamming(self, clients):
        for client in clients:
            client.start()

    def stop_spamming(self, clients, event):
        event.set()
        for client in clients:
            client.join()

    @pytest.fixture(scope="class")
    def spam_results(self, number_of_clients, test_duration_sec, origin):
        responses_results = []

        def request_job(origin, id, event):
            logger = logging.getLogger(name=f"Client_{id}")
            logger.info(f"Client_{id} starts spamming {origin}{endpoint}{id}")
            while not event.is_set():
                logger.debug(f"curl -i -X GET '{origin}{endpoint}{id}'")
                event.wait(1)
                try:
                    response = requests.request("GET", f"{origin}{endpoint}{id}", timeout=5)
                    with Lock():
                        responses_results.append(response)
                except Exception as e:
                    logger.error(e)

        event = Event()
        clients = [Thread(target=request_job, args=(origin, i, event), daemon=True)
                   for i in range(number_of_clients)]
        print(clients)
        self.start_spamming(clients)
        time.sleep(test_duration_sec)
        self.stop_spamming(clients, event)
        return responses_results

    def test_mean_response_time(self, spam_results):
        mean = statistics.mean([response.elapsed.total_seconds() for response in spam_results])
        logging.info(f"Mean response time, sec: {mean}")
        assert mean < 2, "Mean response time is greater than 2 seconds"

    def test_standard_deviation_response_time(self, spam_results):
        standard_deviation = statistics.stdev([response.elapsed.total_seconds() for response in spam_results])
        logging.info(f"Standard deviation for response time, sec: {standard_deviation}")
        assert standard_deviation < 10/1000, "Standard deviation of response time is greater than 0.01 seconds"

    def test_failures_after_spamming(self, spam_results):
        errors = [response for response in spam_results if response.status_code >= 500]
        logging.info(f"Server failure rate (500 errors only): {round(len(errors)/len(spam_results) * 100, 2)}")
        grouped_errors = defaultdict(lambda: 0)
        for error in errors:
            grouped_errors[(error.status_code, error.text)] += 1
        assert not errors, f"{len(errors)} responses failed out from {len(spam_results)}:\n" \
                           f"{grouped_errors.values()}"