import requests
from typing import List, Dict, Any

from trafiklab import site, departure


class TrafiklabClient:
    def __init__(self, stations_api_key: str, traffic_api_key: str) -> None:
        self._stations_api_key = stations_api_key
        self._traffic_api_key = traffic_api_key

    def get_station_site(self, station_name: str) -> site.Site:
        url = "https://api.sl.se/api2/typeahead.json"

        query_params = {
            "key": self._stations_api_key,
            "searchstring": station_name,
        }

        return site.Site.from_response_json(
            self._send_request("GET", url=url, query_params=query_params)[
                "ResponseData"
            ][0]
        )

    def get_line_updates(
        self, station_id: str, line_type: str, time_window: int
    ) -> List[departure.Departure]:
        url = "https://api.sl.se/api2/realtimedeparturesV4.json"

        query_params = {
            "key": self._traffic_api_key,
            "siteid": station_id,
            "TimeWindow": str(time_window),
            "bus": str(line_type == "bus"),
            "metro": str(line_type == "metro"),
            "train": str(line_type == "train"),
            "tram": str(line_type == "tram"),
        }

        return [
            departure.Departure.from_response_json(d)
            for d in self._send_request("GET", url=url, query_params=query_params)[
                "ResponseData"
            ][(line_type + "s").title()]
        ]

    def _send_request(
        self,
        method: str,
        url: str,
        path_params: List[str] = None,
        query_params: Dict[str, str] = None,
        headers: Dict[str, str] = None,
        data: Dict = None,
    ) -> Any:
        request = requests.Request(
            method, url=url, headers=headers, data=data, params=query_params
        )

        session = requests.session()
        prepared_request = session.prepare_request(request)
        response = session.send(prepared_request)

        if response.status_code // 100 != 2:
            raise Exception

        session.close()

        # handle different success response codes
        if response.status_code == 204:
            return None
        return response.json()
