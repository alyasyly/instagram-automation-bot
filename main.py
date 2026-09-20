from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException,TimeoutException
from dotenv import load_dotenv
import os


load_dotenv()

USERNAME = os.getenv('ING_USERNAME')
PASSWORD = os.getenv('ING_PASSWORD')


class InstagramBot:
    def __init__(self,target) -> None:
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_experimental_option("detach", True)
        self.user_data_dir = os.path.join(os.getcwd(), "chrome_profile")
        self.chrome_options.add_argument(f"--user-data-dir={self.user_data_dir}")
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.driver.get('https://www.instagram.com/')
        self.wait = WebDriverWait(self.driver, 4)
        self.target = target

    def login(self):
        try:
            home_icon = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href='/']")))
            print("you've already logged")
            return
        except TimeoutException:
        
            try:
                continue_ = self.wait.until(EC.element_to_be_clickable((By.XPATH,"//div[@role='button' and starts-with(@aria-label, 'Continue')]")))
                continue_.click()
            except TimeoutException:
                email = self.wait.until(EC.element_to_be_clickable((By.NAME,'email')))
                email.send_keys(USERNAME)
                passw = self.wait.until(EC.element_to_be_clickable((By.NAME,'pass')))
                passw.send_keys(PASSWORD)


    def find_followers(self):
        pass

    def follow(self):
        pass









if __name__ == '__main__':
    target = input('Inter your target"s instagram account')
    bot = InstagramBot(target)
    bot.login()