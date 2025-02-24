from abc import ABC, abstractmethod

class BaseTTS(ABC):
    @abstractmethod
    def __init__(
        self,
        text: str,
        output_filename: str,
        pick_random_voice: bool = False,
        voice: str = "",
        speed: float = 1.0,
    ):
        pass

    @abstractmethod
    def text_to_mp3(self):
        pass
