import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class Crawler:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")

        self.driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))

    def open_url(self, url):
        self.driver.get(url)
        time.sleep(3)

    def find_element(self, by, value):
        return self.driver.find_element(by, value)

    def find_elements(self, by, value):
        return self.driver.find_elements(by, value)

    def close(self):
        self.driver.quit()
