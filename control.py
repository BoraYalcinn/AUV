from abc import ABC, abstractmethod


class BaseController(ABC):

    @abstractmethod
    def execute(self, action):
        pass


class PrintController(BaseController):

    def execute(self, action):

        print(f"STATE      : {action['mode']}")
        print(f"STEERING   : {round(action['steering'], 2)}")
        print(f"SPEED      : {action['speed']}")
        print("-" * 35)