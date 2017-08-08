from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time

LOGIN_URL = 'https://www.netflix.com/login'
VIEWING_ACTIVITY = 'https://www.netflix.com/viewingactivity'


class Driver(webdriver.Chrome):
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
        options.add_argument('headless')
        super(Driver, self).__init__(chrome_options=options)
        self.get(url=LOGIN_URL)
        self.log_in()

    def log_in(self):
        usr_email = input("Email: ")
        usr_password = input("Password: ")
        form_email = self.find_element_by_xpath("//input[@name='email']")
        form_password = self.find_element_by_xpath("//input[@name='password']")

        form_email.clear()
        form_email.send_keys(usr_email)
        form_password.clear()
        form_password.send_keys(usr_password)
        if form_email.get_attribute("value") != usr_email:
            raise Exception("Did not receive email input!")
        if form_password.get_attribute("value") != usr_password:
            raise Exception("Did not receive password input!")

        self.find_element_by_css_selector("button[type='submit']").click()
        if self.current_url != "https://www.netflix.com/browse":
            raise Exception("Login Failed")

        # list of user profile names
        self.user_profiles = [name.text for name in self.find_elements_by_class_name("profile-name")][:-1]

        # auth URL
        # html = self.page_source
        # auth_url__start_index = html.find("authURL")
        # self.auth_url = html[auth_url__start_index + 10:auth_url__start_index + 58]

        # cookies for the session
        cookies_list = self.get_cookies()
        result_cookies = []
        for cookie in cookies_list:
            c = '{0}={1}; '.format(cookie['name'], cookie['value'])
            result_cookies.append(c)
        self.cookies = ''.join(result_cookies)

    def switch_profile(self, name):
        start = self.find_element_by_class_name("avatar")
        final = self.find_element_by_xpath("//img[@alt='{0}']".format(name))

        actions = ActionChains(self)
        actions.move_to_element(start)
        actions.move_to_element(final)
        actions.click(final)
        actions.perform()

    def scroll_to_end(self, url):
        if self.current_url != url:
            self.get(url)

        pause_time = 0.5
        prev_page_height = self.execute_script("return document.body.scrollHeight")
        while True:
            self.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(pause_time)
            new_page_height = self.execute_script("return document.body.scrollHeight")
            if new_page_height == prev_page_height:
                break
            prev_page_height = new_page_height

if __name__ == '__main__':
    d = Driver()
    d.quit()