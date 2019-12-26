from abc import ABC, abstractmethod


class Navigator(ABC):
    @abstractmethod
    def go_to_view(self, view: type, parameters: any):
        pass
