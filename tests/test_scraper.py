import sqlite3
from datetime import date
import pytest
from menu.scrapers.base import BaseScraper
from menu.scrapers.sage import SageScraper, SageConfig, SageDateHandler, SageDateRangeError
from menu.models import SageMenuItem

# The example menu_item response from the docs
EXAMPLE_MENU_ITEM_RESPONSE = {"error":False, "items":[
    {"id":"294260406", "menuId":"90945", "recipeId":"127972", "day":"1", "week":"0", "meal":"1",
     "station":"0", "card":"0", "name":"Corn Chowder", "desc":"", "price":"0.00", "dot":2,
     "featured":False, "rating":-1, "popular":True,
     "allergens":[{"id":"41"}, {"id":"161"}, {"id":"611"}, {"id":"999999"}],
     "compositeItem":False}]}

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
    cursor = sqlite3.connect(':memory:').cursor()
    config = SageConfig('test@example.com', 'test1234', 1234, 12345)
    return SageScraper(config, 'sage_testing', cursor)


def test_sage_login(sage_scraper, monkeypatch):
    # Tests the login functionality of the Sage Scraper
    class SageLoginMockResponse:
        # Mock Class to mock the login request
        @staticmethod
        def json():
            return {'credentials':{'accessToken': '61v262de30acv41091894fjf938f388baceb9eff'}}

    def mock_login(url: str, json: dict, auth: tuple):
        assert url.endswith('/login')

        assert 'grant' in json
        assert json['grant'] == 'password'

        assert auth[0] == sage_scraper.config.email
        assert auth[1] == sage_scraper.config.password

        return SageLoginMockResponse()

    # Patches the requests post function to return the mock login class
    monkeypatch.setattr(sage_scraper.session, 'post', mock_login)

    access_token = sage_scraper.login(sage_scraper.config.email, sage_scraper.config.password)
    # Making sure the token equals the mock one from the mock class
    assert access_token == '61v262de30acv41091894fjf938f388baceb9eff'

def test_sage_get_menu(sage_scraper, monkeypatch):
    # tests the get_menu function of the Sage Scraper
    class SageGetMenuMockResponse:
        # Mock class to mock the /getmenus endpoint
        @staticmethod
        def json():
            return {"error": False, "accessGranted": True, "menus":
                    [{"id":"12345", "name":"Test School", "schoolId":"1234"}]}


    def mock_get_menu(url: str, params: dict):
        assert url.endswith('/getmenus')
        assert params['unitId'] == 1234

        return SageGetMenuMockResponse()

    # Patches the requests get function to return the mock menu data
    monkeypatch.setattr(sage_scraper.session, 'get', mock_get_menu)

    menu = sage_scraper.get_menu(1234, 12345)

    assert menu['id'] == '12345'
    assert menu['schoolId'] == '1234'

def test_sage_get_menu_items(sage_scraper, sage_date_handler, monkeypatch):
    # tests the get_menu_items function of SageScraper
    class SageGetMenuItemsMockResponse:
        # Mock class to mock the /getMenuItems endpoint
        @staticmethod
        def json():
            # The response below is literally just the example response fron the docs
            return EXAMPLE_MENU_ITEM_RESPONSE


    def mock_get_menu_items(url: str, json: dict):
        assert url.endswith('/getmenuitems')
        assert json['id'] == 90945
        assert json['week'] == 0

        return SageGetMenuItemsMockResponse()

    # patch up the scraper to use testing data
    monkeypatch.setattr(sage_scraper.session, 'post', mock_get_menu_items)

    response = sage_scraper.get_menu_items(90945, 0)

    # verifying the data matches the example data
    assert response[0]['id'] == '294260406'

def test_sage_format_data_for_storage(sage_date_handler):
    formatted_item = SageScraper.format_data_for_storage(EXAMPLE_MENU_ITEM_RESPONSE['items'],
                                                         sage_date_handler)[0]
    assert isinstance(formatted_item, SageMenuItem)
    assert isinstance(formatted_item.date, date)
    assert isinstance(formatted_item.id, int)

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
