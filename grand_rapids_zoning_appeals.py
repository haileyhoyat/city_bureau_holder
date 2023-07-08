from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parser


class GrandRapidsZoningAppealsSpider(CityScrapersSpider):
    name = "grand_rapids_zoning_appeals"
    agency = "Grand Rapids Board of Zoning Appeals"
    timezone = "America/Chicago"
    start_urls = ["http://grandrapidscitymi.iqm2.com/Citizens/calendar.aspx?View=List"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for item in response.css('.MeetingRow'):
            if (response.css('.RowTop .RowRight span::text').get() is not None):
                if ('Zoning' in item.css('.RowBottom div:nth-child(2)::text').get()):
                    meeting = Meeting(
                        title=self._parse_title(item),
                        description=self._parse_description(item),
                        classification=self._parse_classification(item),
                        start=self._parse_start(item),
                        end=self._parse_end(item),
                        all_day=self._parse_all_day(item),
                        time_notes=self._parse_time_notes(item),
                        location=self._parse_location(item),
                        links=self._parse_links(item),
                        source=self._parse_source(response),
                    )

                    meeting["status"] = self._get_status(meeting)
                    meeting["id"] = self._get_id(meeting)

                    yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        title = item.css('.RowBottom div:nth-child(2)::text').get().split('-')[0]
        return title

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return BOARD

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        try:
            start_time = item.css('.RowTop .RowLink a::text').get()
        except:
            start_time = item.css('.RowTop .RowLink a::text').get() + " 12:00PM"
        return parser().parse(start_time)

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
        address_raw = item.css('.RowTop .RowLink a::attr(title)').get()
        try:
            address = address_raw.split('Scheduled')[1].replace('\r', "").replace('\t', " ").strip()
        except:
            address = address_raw
        return {
            "address": address,
            "name": "",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        
        if item.css('.RowTop .RowLink a::attr(href)').get():
            Meeting_Page = 'http://grandrapidscitymi.iqm2.com/' + item.css('.RowTop .RowLink a::attr(href)').get()
        else:
            Meeting_Page = None

        if item.css('.RowTop .RowRight div:nth-child(1) a::attr(href)').get():
            Agenda = 'http://grandrapidscitymi.iqm2.com/' + item.css('.RowTop .RowLink a::attr(href)').get()
        else:
            Agenda = None

        if item.css('.RowTop .RowRight div:nth-child(2) a::attr(href)').get():
            Agenda_Packet = 'http://grandrapidscitymi.iqm2.com/Citizens/' + item.css('.RowTop .RowRight div:nth-child(2) a::attr(href)').get()
        else:
            Agenda_Packet = None

        if item.css('.RowTop .RowRight div:nth-child(3) a::attr(href)').get():
            Summary = 'http://grandrapidscitymi.iqm2.com/Citizens/' + item.css('.RowTop .RowRight div:nth-child(3) a::attr(href)').get()
        else:
            Summary = None

        if item.css('.RowTop .RowRight div:nth-child(4) a::attr(href)').get():
            Minutes = 'http://grandrapidscitymi.iqm2.com/Citizens/' + item.css('.RowTop .RowRight div:nth-child(4) a::attr(href)').get()
        else:
            Minutes = None
        
        return [
            {"href": Meeting_Page, "title": "Meeting Page"},
            {"href": Agenda, "title": "Agenda"},
            {"href": Agenda_Packet, "title": "Agenda Packet"},
            {"href": Summary, "title": "Summary"},
            {"href": Minutes, "title": "Minutes"}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
