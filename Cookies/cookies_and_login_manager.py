import unittest
from selenium.webdriver.common.by import By

from selenium import webdriver

class CookieManagerTest(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.PhantomJS("E:\\working\\selenium.python\\selenium\\resources\\phantomjs.exe")
        self.driver.get("https://accounts.google.com/ServiceLogin?service=mail&continue=https://mail.google.com/mail/")
        self.driver.find_element(By.ID, "Email").send_keys("userid")
        self.driver.find_element(By.ID, "next").click()
        self.driver.find_element(By.ID, "Passwd").send_keys("supersimplepassword")
        self.driver.find_element(By.CSS_SELECTOR, "[type='submit'][value='Sign in']").click()
        self.driver.maximize_window()

    def test(self):
        driver = self.driver
        listcookies = driver.get_cookies()

        for s_cookie in listcookies:
            # this is what you are doing
            c = {s_cookie['name']: s_cookie['value']}
            print("*****The partial cookie info you are doing*****\n")
            print(c)
            # Should be done
            print("The Full Cookie including domain and expiry info\n")
            print(s_cookie)
            # driver.add_cookie(s_cookie)


    def tearDown(self):
        self.driver.quit()

