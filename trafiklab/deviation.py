import humps


class Deviation:
    def __init__(self, consequence: str, importance_level: int, text: str) -> None:
        self._consequence = consequence
        self._importance_level = importance_level
        self._text = text

    @property
    def consequence(self) -> str:
        return self._consequence

    @property
    def importance_level(self) -> int:
        return self._importance_level

    @property
    def text(self) -> str:
        return self._text

    @classmethod
    def from_response_json(cls, json_dict):
        json_decamelized = humps.decamelize(json_dict)
        return cls(**json_decamelized)
