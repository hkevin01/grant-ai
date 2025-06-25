from datetime import datetime

import scrapy

from grant_ai.models.grant import EligibilityType, FundingType, Grant, GrantStatus


class GrantsGovSpider(scrapy.Spider):
    name = "grantsgov"
    allowed_domains = ["grants.gov"]
    start_urls = [
        "https://www.grants.gov/web/grants/search-grants.html"
    ]

    def parse(self, response):
        # This is a placeholder: grants.gov uses JavaScript for search results, so real scraping would require Selenium or API
        # For demo, parse static HTML for grant titles (if any)
        for grant in response.css(".search-result"):  # Example selector
            title = grant.css(".search-title::text").get()
            funder = grant.css(".search-agency::text").get()
            deadline = grant.css(".search-deadline::text").get()
            url = grant.css("a::attr(href)").get()
            yield {
                "title": title,
                "funder_name": funder,
                "application_deadline": deadline,
                "application_url": url,
            }
        # In production, use Selenium or the grants.gov API for robust scraping.
