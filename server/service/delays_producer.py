import time


def produce_delay(start_time_ms=10, increase_by_ms=0):
    def delayed_func(func):
        def delayed_call(*args, **kwargs):
            time.sleep((start_time_ms + increase_by_ms*delayed_call.calls)/1000)
            delayed_call.calls += 1
            return func(*args, **kwargs)
        delayed_call.calls = 0
        return delayed_call
    return delayed_func