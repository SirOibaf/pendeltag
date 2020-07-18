import configparser
import time
import threading

from datetime import datetime, timedelta
from typing import List
from requests.exceptions import ConnectionError

from trafiklab.client import TrafiklabClient
from trafiklab.departure import Departure
from display import Display


def get_departures(
    station_id: str, config: configparser.ConfigParser
) -> List[Departure]:
    departures = client.get_line_updates(
        station_id, config["LINE"]["type"], int(config["LINE"]["time_window"])
    )

    # Split line_numbers by comma
    line_numbers = config["LINE"]["line_numbers"].split(",")

    return [
        d
        for d in departures
        if (
            d.line_number in line_numbers
            and d.journey_direction == int(config["LINE"]["direction"])
        )
    ]


def apply_cutoff(
    departures: List[Departure], config: configparser.ConfigParser
) -> List[Departure]:
    if "cutoff_min" not in config["LINE"]:
        return departures

    # Compute cutoff date
    cutoff = datetime.now() + timedelta(minutes=int(config["LINE"]["cutoff_min"]))
    return [
        d
        for d in departures
        if d.expected_date_time != ""
        and datetime.strptime(d.expected_date_time, "%Y-%m-%dT%H:%M:%S") > cutoff
    ]


def poll_updates(
    client: TrafiklabClient, site_id: str, config: configparser.ConfigParser, display
) -> None:
    while True:
        try:
            departures = get_departures(station_id, config)
            departures = apply_cutoff(departures, config)

            display.update_departures(departures)
            display.render()

            for d in departures:
                print(
                    "{} - {} - {} - {}".format(
                        d.line_number,
                        d.destination,
                        d.display_time,
                        [dev.text for dev in d.deviations],
                    )
                )

            time.sleep(int(config["APP"]["refresh_min"]) * 60)
        except ConnectionError:
            # Keep retry if there is a connection error
            pass


def setup_display() -> Display:
    display = Display()

    th = threading.Thread(target=display.run)
    th.start()

    return display


if __name__ == "__main__":

    # Parse and read configuration file
    config = configparser.ConfigParser()
    config.read("config.ini")

    client = TrafiklabClient(
        config["API_KEY"]["stations"], config["API_KEY"]["traffic"]
    )

    station_id = client.get_station_site(config["LINE"]["station"]).site_id
    display = setup_display()
    poll_updates(client, station_id, config, display)
