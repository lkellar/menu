from menu.scrapers.base import BaseScraper
from menu.scrapers.sage import SageScraper, SageConfig
import sqlite3
import requests
import pytest

def test_build_url():
    # Tests the build_url function of BaseScraper
    class TestScraper(BaseScraper):
        # Creating a mock scraper to get access to the build_url function
        def __init__(self, base_url: str):
            self.menu = 'testmenu'
            self.base_url = base_url
            super().__init__(self.base_url, self.menu)

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
    config = SageConfig('test@example.com', 'test1234')
    return SageScraper(config, 12345, 'sage_testing', cursor)


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
    
