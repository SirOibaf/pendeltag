import os
import time

from typing import Dict, List, Any
from datetime import datetime

from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.oled.device import ssd1322
from luma.core.virtual import viewport, snapshot
from luma.core.sprite_system import framerate_regulator

from PIL import ImageFont, ImageDraw
from PIL.ImageFont import FreeTypeFont

from trafiklab import departure


class Display:
    def __init__(self) -> None:
        self._fonts = self._load_fonts()

        # Initialize the display
        serial = spi()
        self._device = ssd1322(serial, mode="1")

        self._d_width = self._device.size[0]
        self._d_height = self._device.size[1]

        self._departures: List[departure.Departure] = []

        self._current_alert = ""
        self._display_alert = self._current_alert

    def run(self) -> None:
        while True:
            self.render()
            self._rotate_alert()
            time.sleep(0.5)

    def update_departures(self, departures: List[departure.Departure]) -> None:
        self._departures = departures

    def render(self) -> None:
        with canvas(self._device) as draw:
            self._render_departures(draw)
            self._render_time(draw)
            self._render_alert(draw)

    def _render_departures(self, draw: ImageDraw) -> None:
        if not self._departures or len(self._departures) == 0:
            return

        # Only show alert for the first departure
        deviations_text = [dev.text for dev in self._departures[0].deviations]
        self._current_alert = " - ".join(deviations_text)

        # Show the first departure bigger
        first_height = self._render_departure_font(
            draw, 0, self._departures[0], self._fonts["regular_first"]
        )

        if len(self._departures) > 1:
            # show also the second departure
            self._render_departure_font(
                draw, first_height, self._departures[1], self._fonts["regular"]
            )

    def _render_departure_font(
        self,
        draw: ImageDraw,
        y: int,
        departure: departure.Departure,
        font: FreeTypeFont,
    ) -> int:
        _, dst_height = draw.textsize(
            "{} {}".format(departure.line_number, departure.destination), font=font
        )
        time_width, time_height = draw.textsize(departure.display_time, font=font)

        dst_y = y + 5
        dst_x = 0  # set border

        time_x = self._d_width - time_width - 2
        time_y = y + 5

        draw.text(
            (dst_x, dst_y),
            "{} {}".format(departure.line_number, departure.destination),
            fill="white",
            font=font,
        )

        draw.text((time_x, time_y), departure.display_time, fill="white", font=font)

        return dst_height

    def _render_time(self, draw: ImageDraw) -> None:
        font = self._fonts["alert"]
        hour, minute, second = str(datetime.now().time()).split(".")[0].split(":")

        time_width, time_height = draw.textsize("{}:{}".format(hour, minute), font=font)
        time_x = self._d_width - time_width
        time_y = self._d_height - time_height

        draw.text(
            (time_x, time_y), "{}:{}".format(hour, minute), fill="white", font=font
        )

    def _render_alert(self, draw: ImageDraw) -> None:
        font = self._fonts["alert"]

        alert_width, alert_height = draw.textsize(self._display_alert[:30], font=font)
        alert_x = 0
        alert_y = self._d_height - alert_height

        draw.text((alert_x, alert_y), self._display_alert[:30], fill="white", font=font)

    def _load_fonts(self) -> Dict[str, FreeTypeFont]:
        return {
            "alert": ImageFont.truetype(
                self._font_path("open_24_display_st.ttf"), 14, encoding="unic"
            ),
            "regular": ImageFont.truetype(
                self._font_path("open_24_display_st.ttf"), 17, encoding="unic"
            ),
            "regular_first": ImageFont.truetype(
                self._font_path("open_24_display_st.ttf"), 20, encoding="unic"
            ),
        }

    def _rotate_alert(self) -> None:
        if len(self._current_alert) < 30:
            # No need to rotate
            return

        self._display_alert = self._display_alert[1:]

        if len(self._display_alert) < 30:
            self._display_alert = "{} - {}".format(
                self._display_alert, self._current_alert
            )

    def _font_path(self, font_name: str) -> str:
        return os.path.join(os.path.abspath("fonts"), font_name)
