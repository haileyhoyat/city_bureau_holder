import time

from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parser
from selenium import webdriver
from selenium.webdriver.common.by import By


class IndCitizensPoliceComplaintSpider(CityScrapersSpider):
    name = "ind_citizens_police_complaint"
    agency = "Indianapolis Citizens Police Complaint Board"
    timezone = "America/Chicago"
    start_urls = ["https://www.indy.gov/activity/citizens-police-complaint-board"]
    """
    def parse(self, response):
        print("inside parse")
        yield SeleniumRequest(
            url="https://www.indy.gov/activity/citizens-police-complaint-board",
            callback=self.parse_result,
            wait_time=10,
            wait_until=EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".collapsible div:nth-child(2) dd")
            ),
        )
        # wait_until=EC.presence_of_element_located((By.CLASS_NAME, "collapsible")))
    """

    def parse(self, response):
        print("inside parse_result")
        meeting_list = []
        driver = webdriver.Chrome()
        driver.get("https://www.indy.gov/activity/citizens-police-complaint-board")
        time.sleep(10)
        try:
            element = driver.find_element(
                By.CSS_SELECTOR, ".collapsible div:nth-child(2) dd"
            )
            print("found element")
            html = element.get_attribute("innerHTML")
            # print("This is the returned html of the element")
            # print(element.get_attribute('innerHTML'))
            for item in html.split("<p>"):
                meeting_list.append(item)

            # print(meeting_list)
        finally:
            driver.quit()

        for item in meeting_list:
            if item is "":  # noqa
                continue

            if "Meeting Canceled" in item:
                continue

            meeting = Meeting(
                title=self._parse_title(item),
                description=self._parse_description(item),
                classification=self._parse_classification(item),
                start=self._parse_start(item),
                end=self._parse_end(item),
                all_day=self._parse_all_day(item),
                time_notes=self._parse_time_notes(item),
                location="location",
                links=self._parse_links(item),
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return "Citizens' Police Complaint Board"

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        str = item.split("</p>")[0].strip()
        str_en = str.encode("ascii", "ignore")
        str_de = str_en.decode()
        return parser().parse(str_de)

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return (
            "Please double check the meeting notice for the meeting time and location."
        )

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self, item):
        """Parse or generate location."""
        return {
            "address": "200 East Washington Street Suite 1841 Indianapolis, IN 46204",
            "name": "City-County Building - Room 260",
        }

    def _parse_links(self, item):
        """Parse or generate links."""

        links_raw_html = []
        meeting_notice = ""
        meeting_agenda = ""
        meeting_minutes = ""
        voting_results = ""
        links_raw_html.append(item.split("<li><a href=")[1::])

        try:
            for link in links_raw_html[0]:
                if "Meeting Notice" in link:
                    meeting_notice_raw = link.split("title")[0].strip()
                    meeting_notice = meeting_notice_raw.replace('"', "")
                if "Meeting Agenda" in link:
                    meeting_agenda_raw = link.split("title")[0].strip()
                    meeting_agenda = meeting_agenda_raw.replace('"', "")
                if "Meeting Minutes" in link:
                    meeting_minutes_raw = link.split("title")[0].strip()
                    meeting_minutes = meeting_minutes_raw.replace('"', "")
                if "Voting Results" in link:
                    voting_results_raw = link.split("title")[0].strip()
                    voting_results = voting_results_raw.replace('"', "")

        except:  # noqa
            print("no links")

        return [
            {"href": meeting_notice, "title": "Meeting Notice"},
            {"href": meeting_agenda, "title": "Meeting Agenda"},
            {"href": meeting_minutes, "title": "Meeting Minutes"},
            {"href": voting_results, "title": "Voting Results"},
        ]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
