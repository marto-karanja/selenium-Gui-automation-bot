import os
import wx
import time
import logging

from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotVisibleException

class AcademiaBot(object):
    def __init__(self, email, password, window, logger = None):
        self.email = email
        self.password = password
        self.CHROME_DRIVER = os.path.join(os.path.join(os.getcwd(), 'driver'), 'chromedriver.exe')
        self.logger = logger or logging.getLogger(__name__)

        self.chrome_options = Options()
        self.chrome_options.add_argument("--incognito")
        self.chrome_options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(options=self.chrome_options, executable_path=self.CHROME_DRIVER)
        self.delay = 3
        self.links = []

        self.login_url = "https://writers.academia-research.com/index.php?r=account%2Flogin"
        self.dashboard_url = "https://writers.academia-research.com/index.php?r=order%2Findex"

        self.login(window)

    def set_email(self, email):
        self.email = email

    def set_password(self, password):
        self.password = password

    def login(self, window):
        self.logger.info("Attempting to login")

        self.driver.get(self.login_url)
        email_field = self.driver.find_element_by_id("loginform-login")
        email_field.send_keys(self.email)
        password_field = self.driver.find_element_by_id("loginform-password")
        password_field.send_keys(self.password)

        submit_button = self.driver.find_element_by_class_name("b-btn_red")
        submit_button.submit()

        self.update_gui(window,"Login was Successful")

    def start_bidding(self, event, window):
        self.logger.info("Beginning to apply for orders")

        while not event.isSet():
            try:

                link_elements = self.driver.find_elements_by_class_name("b-table__order-link")
                if link_elements:
                    for link_element in link_elements:
                        href = link_element.get_attribute("href")
                        if href not in self.links:
                            self.links.append(href)
                            self.apply_for_order(href, window)
                        else:
                            self.update_txt_field(window)
                else:
                    self.update_txt_field(window)
                    time.sleep(self.delay)
            except Exception as e:
                self.logger.error(e)
                self.update_gui(window, "Refreshing dashboard link")
                self.driver.get(self.dashboard_url)



    def apply_for_order(self, link, window):
        self.update_gui(window, f"New link found {link[:40]}...")

        try:
            self.driver.get(link)
            button = self.driver.find_element_by_id("btn-request")
            button.click()
        except NoSuchElementException:
            self.update_gui(window, "Link does not exist")
        else:
            self.update_gui(window, "Clicked button")

        self.update_gui(window, "Returning to dashboard")
        self.driver.get(self.dashboard_url)

        return

    def update_gui(self, window, msg):
        wx.CallAfter(window.log_message_to_txt_field,msg )

    def update_txt_field(self, window):
        wx.CallAfter(window.show_no_links)


