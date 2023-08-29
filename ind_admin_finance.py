import time

from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parser
from selenium import webdriver
from selenium.webdriver.common.by import By


class IndAdminFinanceSpider(CityScrapersSpider):
    name = "ind_admin_finance"
    agency = "Indianapolis Administration Finance Committee"
    timezone = "America/Chicago"
    start_urls = [
        "https://calendar.indy.gov/event/administration-and-finance-committee-meeting/"
    ]

    def parse(self, response):
        print("inside parse_result")
        meeting_list = []
        driver = webdriver.Chrome()
        driver.get(
            "https://calendar.indy.gov/event/administration-and-finance-committee-meeting/"  # noqa
        )
        time.sleep(10)
        try:
            schedule_element = driver.find_element(
                By.CLASS_NAME, "full-schedule-container"
            )
            location_element = driver.find_element(By.CLASS_NAME, "list-event-locale")
            # print("found element")
            schedule_html = schedule_element.get_attribute("innerHTML")
            location_html = location_element.get_attribute("innerHTML")
            # print("This is the returned html of the element")
            # print(schedule_element.get_attribute("innerHTML"))
            # print(location_element.get_attribute("innerHTML"))

            if "City-County Building, Meeting Room 260" in location_html:
                location = {
                    "address": "200 East Washington Street, Indianapolis IN, 46204",
                    "name": "City-County Building, Meeting Room 260",
                }
            else:
                location = {
                    "address": "",
                    "name": "",
                }

            for meeting in schedule_html.split("<a"):
                meeting_list.append(meeting)

            print("number of meetings in list: " + str(len(meeting_list)))

        finally:
            driver.quit()

        for item in meeting_list[2::]:
            # for item in element.selector.xpath("//div[@class='descripton']//p"):
            meeting = Meeting(
                title=self._parse_title(item),
                description=self._parse_description(item),
                classification=self._parse_classification(item),
                start=self._parse_start(item),
                end=self._parse_end(item),
                all_day=self._parse_all_day(item),
                time_notes=self._parse_time_notes(item),
                location=location,
                links=self._parse_links(item),
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return "Administration and Finance Committee"

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        date = item.split(">")[1]
        date2 = date.split("<")[0]

        time = item.split("<br>")[1]
        time2 = time.split(" - ")[0]
        return parser().parse(date2 + " " + time2)

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self, item):
        """Parse or generate location."""
        return {
            "address": "",
            "name": "",
        }

    def _parse_links(self, item):
        """Parse or generate links."""

        meeting_page = item.split('href="')[1]
        meeting_page2 = meeting_page.split('" class')[0]

        return [
            {
                "href": "https://calendar.indy.gov" + meeting_page2,
                "title": "Meeting Page",
            }
        ]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
