from typing import Any, Final


class LoxReturn(Exception):
    def __init__(self, value: Any):
        self.value: Final = value
