"""
    Classes that compose a script to run website automation
"""

from pathlib import Path
import re
from RPA.Browser.Selenium import Selenium
import requests
import pandas as pd


class GothAmistLocators:
    """
    Locators of the website
    """

    def __init__(self):
        self.title_locator = '(//*[@class="h2"])[{}]'
        self.description_locator = '(//*[@class="desc"])[{}]'
        self.picture_locator = '(//*[@style="aspect-ratio: 3 / 2;"]/img[1])[{}]'
        self.result_amount_locator = (
            '//div[@class="col"]/div[contains(@class,"search-page")]/span/strong'
        )
        self.load_more_locator = '(//*[@aria-label="Load More"])[last()]'
        self.close_locator = (
            '(//*[contains(@class,"CloseButton__ButtonElement")])[last()]'
        )


class GothAmistController:
    """
    Controller of the website automation
    """

    def __init__(self, phrase: str, data_amount: int):
        self.phrase = phrase
        self.data_amount = data_amount
        self.results = None
        self.driver = Selenium()
        self.locators = GothAmistLocators()
        self.data_list = []
        self.title = None
        self.description = None
        self.picture_name = None
        self.phrases_count = None
        self.cash = None
        self.df = None

    def launch(self):
        """
        Accessing the website
        """
        self.driver.open_available_browser(
            f"https://gothamist.com/search?q={self.phrase}"
        )

    def result_amount(self):
        """
        Method to get the amount of results according to the phrase searched
        """
        self.results = self.driver.get_text(self.locators.result_amount_locator)

    def load_more(self, index):
        """
        Method to click on load more, if button exists
        """
        try:
            self.driver.wait_until_page_contains_element(
                locator=self.locators.title_locator.format(index),
                error="Element does not exists",
                timeout=1,
            )

        except AssertionError:
            #Wait when clickable, clickelement, click_button, press_key. Nothing works, except javascript
            self.driver.execute_javascript(
                f"document.evaluate(`{self.locators.load_more_locator}`,document,null,XPathResult.FIRST_ORDERED_NODE_TYPE,null).singleNodeValue.click()"
            )

    def get_title(self, index):
        """
        Method to get the news title
        """
        self.driver.wait_until_page_contains_element(
            self.locators.title_locator.format(index), timeout=5
        )
        self.title = self.driver.get_text(self.locators.title_locator.format(index))

    def get_description(self, index):
        """
        Method to get the news description
        """
        self.description = self.driver.get_text(
            self.locators.description_locator.format(index)
        )

    def get_picture(self, index):
        """
        Method to get the news picture
        """
        self.picture_name = self.driver.get_element_attribute(
            self.locators.picture_locator.format(index), "src"
        )

    def counting_phrases(self):
        """
        Method to validate how many times the phrase appears in the description
        """
        self.phrases_count = f"{self.title.lower()} {self.description.lower()}".count(
            self.phrase.lower()
        )
        print(self.phrases_count)

    def about_cash(self):
        """
        Method to validate if description and title talks about cash
        """
        self.cash = (
            "true"
            if any(
                valor in f"{self.title.lower()} {self.description.lower()}"
                for valor in ["$", "dollar", "usd"]
            )
            else "false"
        )

    def close_popup(self):
        """
        Method to validate if pop up exists and close it
        """
        try:
            self.driver.wait_until_element_is_visible(
                locator=self.locators.close_locator,
                error="Element does not exists",
                timeout=0.2,
            )
            self.driver.click_element_when_clickable(
                self.locators.close_locator, timeout=5
            )

        except AssertionError:
            print("PopUp not exists")

    def append_data(self):
        """
        Method used to append data into data list
        """
        self.data_list.append(
            [
                self.title,
                self.description,
                self.picture_name,
                self.phrases_count,
                self.cash,
                self.title,
            ]
        )

    def download_image(self):
        """
        Method to download the news Image
        """
        with open(
            f'{Path.cwd()}/output/{re.sub("[^A-Za-z0-9]+", "", self.title)}.png',
            "wb",
        ) as file:
            file.write(requests.get(self.picture_name, timeout=10).content)

    def create_dataframe(self):
        """
        Method to transform the news data into a dataframe
        """
        self.df = pd.DataFrame(
            self.data_list,
            columns=[
                "Title",
                "Description",
                "Picture_Name",
                "Phrases Count",
                "About Cash",
                "Downloaded Image",
            ],
        )
        self.df.to_excel(f"{Path.cwd()}/output/Data.xlsx", index=False)
