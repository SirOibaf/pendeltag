import humps

from typing import List

from trafiklab import deviation


class Departure:
    def __init__(
        self,
        secondary_destination_name: str,
        group_of_line: str,
        transport_mode: str,
        line_number: str,
        destination: str,
        journey_direction: int,
        stop_area_name: str,
        stop_area_number: int,
        stop_point_number: int,
        stop_point_designation: str,
        time_tabled_date_time: str,
        expected_date_time: str,
        display_time: str,
        journey_number: int,
        deviations: str,
    ) -> None:
        self._secondary_destination_name = secondary_destination_name
        self._group_of_line = group_of_line
        self._transport_mode = transport_mode
        self._line_number = line_number
        self._destination = destination
        self._journey_direction = journey_direction
        self._stop_area_name = stop_area_name
        self._stop_area_number = stop_area_number
        self._stop_point_number = stop_point_number
        self._stop_point_designation = stop_point_designation
        self._time_tabled_date_time = time_tabled_date_time
        self._expected_date_time = expected_date_time
        self._display_time = display_time
        self._journey_number = journey_direction

        if deviations:
            self._deviations = [
                deviation.Deviation.from_response_json(d) for d in deviations
            ]
        else:
            self._deviations = []

    @classmethod
    def from_response_json(cls, json_dict):
        json_decamelized = humps.decamelize(json_dict)
        return cls(**json_decamelized)

    @property
    def destination(self) -> str:
        return self._destination

    @property
    def line_number(self) -> str:
        return self._line_number

    @property
    def journey_direction(self) -> int:
        return self._journey_direction

    @property
    def display_time(self) -> str:
        return self._display_time

    @property
    def deviations(self) -> List[deviation.Deviation]:
        return self._deviations

    @property
    def expected_date_time(self) -> str:
        return self._expected_date_time
