import time

from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parser
from scrapy_selenium import SeleniumRequest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# 1. This spider utilizes scrapy_selenium


class IndCountyCommissionersSpider(CityScrapersSpider):
    name = "ind_county_commissioners"
    agency = "Indianapolis County Commissioners"
    timezone = "America/Chicago"
    start_urls = ["https://www.indy.gov/activity/county-commissioners-meeting-schedule"]

    def parse(self, response):
        print("inside parse")
        yield SeleniumRequest(
            url="https://www.indy.gov/activity/county-commissioners-meeting-schedule",
            callback=self.parse_result,
            wait_time=10,
            wait_until=EC.presence_of_element_located((By.CLASS_NAME, "description")),
        )

    def parse_result(self, response):
        print("inside parse_result")
        meeting_list = []
        driver = webdriver.Chrome()
        driver.get(
            "https://www.indy.gov/activity/county-commissioners-meeting-schedule"
        )
        time.sleep(10)
        try:
            element = driver.find_element(By.CLASS_NAME, "description")
            print("found element")
            html = element.get_attribute("innerHTML")
            # print("This is the returned html of the element")
            print(element.get_attribute("innerHTML"))
            for item in html.split("<p>"):
                meeting_list.append(item)
        finally:
            driver.quit()

        if (
            "Meetings are held in the City-County Building, 200 E. Washington Street Indianapolis, IN 46204 Room 260 and will begin at 2:00 p.m. unless specified otherwise."  # noqa
            in meeting_list[2]
        ):
            location = "City-County Building, 200 E. Washington Street Indianapolis, IN 46204 Room 260"  # noqa

        for item in meeting_list[3::]:
            if "Upcoming Dates" in item:
                continue

            if "CANCELLED" in item:
                continue
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
        return "City Commissioners Meeting"

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        return parser().parse(item.split("-")[0])

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
        return [{"href": "", "title": ""}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
