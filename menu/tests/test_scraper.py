from menu.scrapers.base import BaseScraper
from menu.scrapers.sage import SageScraper, SageConfig, SageDateHandler, SageDateRangeError
import sqlite3
import requests
import pytest
from datetime import date

def test_build_url():
    # Tests the build_url function of BaseScraper
    class TestScraper(BaseScraper):
        # Creating a mock scraper to get access to the build_url function
        def __init__(self, base_url: str):
            self.base_url = base_url
            super().__init__(self.base_url)

        def scrape(self):
            pass

    test_scraper = TestScraper('https://menusite.com/rest')
    assert test_scraper.build_url('login') == 'https://menusite.com/rest/login'
    assert test_scraper.build_url('/login') == 'https://menusite.com/rest/login'

    test_scraper = TestScraper('https://menusite.com/rest/')
    assert test_scraper.build_url('login') == 'https://menusite.com/rest/login'
    assert test_scraper.build_url('/login') == 'https://menusite.com/rest/login'

@pytest.fixture
def sage_scraper() -> SageScraper:
    # Generates a dummy SageScraper used for testing
    cursor = sqlite3.connect(":memory:").cursor()
    config = SageConfig('test@example.com', 'test1234', 1234, 1234)
    return SageScraper(config, 'sage_testing', cursor)


def test_sage_login(sage_scraper, monkeypatch):
    # Tests the login functionality of the Sage Scraper
    class SageLoginMockResponse:
        # Mock Class to mock the login request
        @staticmethod
        def json():
            return {'credentials':{'accessToken': '61v262de30acv41091894fjf938f388baceb9eff'}}

    def mock_login(*args, **kwargs):
        return SageLoginMockResponse()

    # Patches the requests get function to return the mock login class
    monkeypatch.setattr(sage_scraper.session, 'post', mock_login)

    access_token = sage_scraper.login(sage_scraper.config.email, sage_scraper.config.password)
    # Making sure the token equals the mock one from the mock class
    assert access_token == '61v262de30acv41091894fjf938f388baceb9eff'
    

def test_sage_first_date_parser():
    # Tests the SageDateHandler.parse_first_date function
    
    # Testing to make sure the date is converted to the correct day
    assert SageDateHandler.parse_first_date('08/13/2019') == date(2019, 8, 11)

    # Testing to make sure the returned date is a sunday
    assert SageDateHandler.parse_first_date('09/23/2020').weekday() == 6

@pytest.fixture
def sage_date_handler() -> SageDateHandler:
    # Returns a standard Sage Date Handler with cycle_length 16 and menu_first_date 08/13/2019
    return SageDateHandler(16, '08/13/2019')

def test_sage_date_conversion(sage_date_handler):
    # Tests the sage_to_date and date_to_sage functions of SageDateHandler

    assert sage_date_handler.date_to_sage(date(2019, 9, 14)) == {'week': 4, 'day': 6} 
    assert sage_date_handler.sage_to_date(4, 6) == date(2019, 9, 14)

def test_sage_date_conversion_failure(sage_date_handler):
    # Tests the error detection logic of date_to_sage by passing an invalid date in the past
    with pytest.raises(SageDateRangeError):
        sage_date_handler.date_to_sage(date(2019, 6, 13))