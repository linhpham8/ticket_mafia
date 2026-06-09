from re import match, search, DOTALL
from typing import List

from robot.api.deco import keyword
from robot.api.logger import warn

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.event_firing_webdriver import (
    EventFiringWebElement
)

from SeleniumLibrary import ElementFinder, LibraryComponent


class SeleniumLibraryEx(LibraryComponent):
    def __init__(self, ctx, warnings=True):
        LibraryComponent.__init__(self, ctx)
        self.element_finder = ElementFinder(ctx)

        self._warnings = [] if warnings else None

    @keyword()
    def get_all_texts(self, locator) -> List[str]:
        """Returns a list of texts of WebElements matching the locator
        """
        elements = self.find_elements(locator)
        return [element.text for element in elements]
