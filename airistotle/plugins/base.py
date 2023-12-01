from abc import ABC, abstractmethod


class BasePlugin(ABC):
    name: str
    description: str

    def __call__(self, *args, **kwargs):
        return self.run(*args, **kwargs)

    @abstractmethod
    def run(self, *args, **kwargs) -> str:
        raise NotImplementedError("Plugin has not properly implemented the run method.")
