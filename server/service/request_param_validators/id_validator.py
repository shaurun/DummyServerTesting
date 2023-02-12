import inspect
import re


def validate_id_param(func):
    field_name = "id"

    def validate(*args, **kwargs):
        listed_args = inspect.getfullargspec(func)[0]
        id = None
        if field_name in listed_args:
            id = args[listed_args.index(field_name)]
        elif field_name in kwargs.keys():
            id = kwargs[field_name]
        if id is not None:
            # check that id is an integer number
            int_pattern = re.compile("\\d+")
            if not int_pattern.match(str(id)):
                return {"Error": f"Id should match pattern '{int_pattern.pattern}'"}, 400
            if int(id) >= 100:
                return {"Error": f"Object with id {id} not found"}, 404
        return func(*args, **kwargs)
    return validate
