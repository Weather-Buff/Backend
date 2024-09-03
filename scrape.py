from datetime import datetime
from bs4 import BeautifulSoup
from model import Facility

import requests

__all__ = [
    'scrape'
]

live_data_url = "https://connect2concepts.com/connect2/"

def scrape() -> list[Facility]:
    facilities: list[Facility] = []

    response = requests.get(
        live_data_url,
        params = {
            "type": "circle",
            "key": "11EEE07F-7BED-418E-B7F7-547D2BB046F5"
        },
        headers = {
            "Accept": "*/*",
            "User-Agent": "weatherbuff/1.0"
        }
    )

    soup = BeautifulSoup(response.text, "html.parser")
    blocks = soup.find_all("div", class_ = "col-md-3 col-sm-6")

    for data in blocks:
        info_div = data.find("div", style="text-align:center;")

        if info_div:
            text = info_div.get_text(separator="\n", strip=True).split("\n")

            name = text[0]
            is_open = True if text[1] == "(Open)" else False
            last_count = text[2].split("Last Count: ")[1]
            updated_time = datetime.strptime(text[3].split("Updated: ")[1], "%m/%d/%Y %I:%M %p")

            circle_chart = data.find("div", class_="circleChart")
            if circle_chart:
                chart_percent = circle_chart.get("data-percent")

                facility = Facility(name, is_open, last_count, chart_percent, updated_time)

                facilities.append(facility)

    return facilities
