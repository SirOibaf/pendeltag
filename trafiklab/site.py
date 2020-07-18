import humps


class Site:
    def __init__(
        self, name: str, site_id: str, type: str, X: str, Y: str, products: str
    ) -> None:
        self._name = name
        self._site_id = site_id
        self._type = type
        self._x = X
        self._y = Y
        self._products = products

    @classmethod
    def from_response_json(cls, json_dict):
        json_decamelized = humps.decamelize(json_dict)
        return cls(**json_decamelized)

    @property
    def site_id(self) -> str:
        return self._site_id
