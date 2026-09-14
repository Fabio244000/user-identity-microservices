from abc import ABC, abstractmethod


class CloseSessionPort(ABC):
    @abstractmethod
    def execute(self, token: str) -> None: ...
