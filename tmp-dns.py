import requests as re

#/catalog/17a89aab16404e77/videokarty/'

from playwright.sync_api import Page


class DNS:
    url = 'https://www.dns-shop.ru'

    def __init__(self, page: Page) -> None:
        self.page = page
        self.search_button = page.locator('#search_button_homepage')
        self.search_input = page.locator('#search_form_input_homepage')

    def load(self) -> None:
        self.page.goto(self.url)

    def search(self, phrase: str) -> None:
        self.search_input.fill(phrase)
        self.search_button.click()


d = DNS()
