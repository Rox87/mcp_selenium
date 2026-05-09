import pytest
from unittest.mock import patch, MagicMock
from scraper import Scraper

@pytest.fixture
def mock_driver():
    with patch('scraper.webdriver.Chrome') as mock_chrome:
        mock_instance = MagicMock()
        mock_chrome.return_value = mock_instance
        yield mock_instance

def test_scraper_init_default(mock_driver):
    with patch('scraper.get_profile_config', return_value={"headless": True}) as mock_config:
        scraper = Scraper("default")
        mock_config.assert_called_once_with("default")
        assert scraper.driver == mock_driver

def test_navigate(mock_driver):
    with patch('scraper.get_profile_config', return_value={}):
        scraper = Scraper("test_profile")
        result = scraper.navigate("http://example.com")
        mock_driver.get.assert_called_once_with("http://example.com")
        assert result == "Navigated to http://example.com"

def test_get_text(mock_driver):
    with patch('scraper.get_profile_config', return_value={}):
        scraper = Scraper("test_profile")
        mock_element = MagicMock()
        mock_element.text = "Hello World"
        mock_driver.find_element.return_value = mock_element

        result = scraper.get_text(".my-class", "css")
        assert result == "Hello World"

def test_export_html(mock_driver):
    with patch('scraper.get_profile_config', return_value={}):
        scraper = Scraper("test_profile")
        mock_driver.page_source = "<html><body>Test</body></html>"

        result = scraper.export_html()
        assert result == "<html><body>Test</body></html>"

def test_execute_js(mock_driver):
    with patch('scraper.get_profile_config', return_value={}):
        scraper = Scraper("test_profile")
        mock_driver.execute_script.return_value = 42

        result = scraper.execute_js("return 42;")
        mock_driver.execute_script.assert_called_once_with("return 42;")
        assert result == 42
