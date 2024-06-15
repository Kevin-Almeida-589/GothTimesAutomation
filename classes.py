"""
    Classes that compose a script to run website automation
"""

from pathlib import Path
import re
from RPA.Browser.Selenium import Selenium
import requests
import pandas as pd
from loguru import logger


class GothAmistLocators:
    """
    Locators of the website
    """

    def __init__(self):
        self.title_locator = '(//*[@class="h2"])[{}]'
        self.description_locator = '(//*[@class="desc"])[{}]'
        self.picture_locator = '(//*[@class="image native-image prime-img-class"])[{}]'
        self.result_amount_locator = '//div[@class="search-page-results pt-2"]'
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
        self.article = Article()
        self.data_list = []
        self.df = None

    def launch(self):
        """
        Accessing the website
        """
        logger.info("Acessing the Webiste")
        self.driver.open_available_browser(
            f"https://gothamist.com/search?q={self.phrase}"
        )

    def result_amount(self):
        """
        Method to get the amount of results according to the phrase searched
        """
        self.results = re.findall(
            r"\d+", self.driver.get_text(self.locators.result_amount_locator)
        )[0]
        logger.info(f"Total search results: {str(self.results)}")

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
            logger.info("Click on Load more not necessary yet")

        except AssertionError:
            # Wait when clickable, clickelement, click_button, press_key. Nothing works, except javascript
            self.driver.execute_javascript(
                f"document.evaluate(`{self.locators.load_more_locator}`,document,null,XPathResult.FIRST_ORDERED_NODE_TYPE,null).singleNodeValue.click()"
            )
            logger.info("Successfully Clicked on Load more")

    def get_title(self, index):
        """
        Method to get the news title
        """
        self.driver.wait_until_page_contains_element(
            self.locators.title_locator.format(index), timeout=5
        )
        self.article.set_title(
            self.driver.get_text(self.locators.title_locator.format(index))
        )
        logger.info(f"{index}º news title: {self.article.title}")

    def get_description(self, index):
        """
        Method to get the news description
        """
        self.article.set_description(
            self.driver.get_text(self.locators.description_locator.format(index))
        )
        logger.info(f"{index}º news description: {self.article.description}")

    def get_picture(self, index):
        """
        Method to get the news picture
        """
        self.article.set_picture_name(
            self.driver.get_element_attribute(
                self.locators.picture_locator.format(index), "src"
            )
        )
        logger.info(f"{int(index/2)}º news picture: {self.article.picture_name}")

    def counting_phrases(self):
        """
        Method to validate how many times the phrase appears in the description
        """
        self.article.counting_phrases(self.phrase.lower())
        logger.info(
            f"Number of phrases searched from the news: {self.article.phrases_count}"
        )

    def validate_news_context(self):
        """
        Method to validate if description and title talks about cash
        """
        self.article.about_cash()
        logger.info(
            f"The news: {self.article.title} talks about cash?: {self.article.cash}"
        )

    def close_popup(self):
        """
        Method to validate if pop up exists and close it
        """
        try:
            self.driver.wait_until_element_is_visible(
                locator=self.locators.close_locator,
                error="Element does not exists",
                timeout=1,
            )
            self.driver.click_element_when_clickable(
                self.locators.close_locator, timeout=5
            )
            logger.info("Pop up Clicked!!")

        except AssertionError:
            logger.info("Pop up does not exists")

    def append_data(self):
        """
        Method used to append data into data list
        """
        self.data_list.append(
            [
                self.article.title,
                self.article.description,
                self.article.picture_name,
                self.article.phrases_count,
                self.article.cash,
                self.article.title,
            ]
        )

    def download_image(self):
        """
        Method to download the news Image
        """
        compiler = r"[^A-Za-z0-9\s]+"
        with open(
            rf'{Path.cwd()}/output/{re.sub(compiler, "", self.article.title)}.png',
            "wb",
        ) as file:
            file.write(requests.get(self.article.picture_name, timeout=10).content)
        logger.info(
            f"Image: {self.article.title}.png downloaded from news title: {self.article.title}"
        )

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
        logger.info("DataFrame created")


class Article:
    """
    Class that contains data from the news Articles
    """

    def __init__(self):
        self.title = None
        self.description = None
        self.picture_name = None
        self.phrases_count = None
        self.cash = None

    def set_title(self, title):
        """
        Method to set the news title
        """
        self.title = title

    def set_description(self, description):
        """
        Method to set the news description
        """
        self.description = description

    def set_picture_name(self, picture_name):
        """
        Method to set the news picture name
        """
        self.picture_name = picture_name

    def counting_phrases(self, phrase):
        """
        Method to validate how many times the phrase appears in the description
        """
        self.phrases_count = f"{self.title.lower()} {self.description.lower()}".count(
            phrase.lower()
        )

    def about_cash(self):
        """
        Method to validate if description and title talks about cash
        """
        self.cash = "True" if re.search(r"\$|dollar|USD", f"{self.title.lower()} {self.description.lower()}") else "False"
