from dataclasses import dataclass


@dataclass(eq=True)
class ServerConfigs:
    host: str
    port: int
    debug: bool

    def check_missing_configs(self):
        missing_configs = [field for field in self.__dict__.keys() if self.__getattribute__(field) is None]
        return missing_configs

    def set_missing_configs_from(self, *args):
        assert all(isinstance(arg, ServerConfigs) for arg in args)
        for field in self.__dict__.keys():
            if field is None:
                self.__setattr__(field, next(filter(args, lambda arg: arg.host is not None)))