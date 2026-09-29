from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException,TimeoutException
from dotenv import load_dotenv
import os
import time


load_dotenv()

USERNAME = os.getenv('ING_USERNAME')
PASSWORD = os.getenv('ING_PASSWORD')


class InstagramBot:
    SCROLL_JS = r"""
            const mode = arguments[0];
    
            let dialog = null;
            for (const d of document.querySelectorAll("div[role='dialog']")) {
                if (d.querySelector("a[href^='/']")) dialog = d;
            }
            if (!dialog) return {found: false, count: 0};
    
            let scroller = null;
            for (const el of dialog.querySelectorAll('div')) {
                const oy = getComputedStyle(el).overflowY;
                if ((oy === 'auto' || oy === 'scroll') && el.scrollHeight > el.clientHeight + 5) {
                    scroller = el;
                    break;
                }
            }
    
            
            window.__followers = window.__followers || new Set();
            const root = scroller || dialog;
            root.querySelectorAll("a[href^='/']").forEach(a => {
                const m = a.getAttribute('href').match(/^\/([^\/]+)\/$/);
                if (m) window.__followers.add(m[1]);
            });
    
            if (!scroller) return {found: false, count: window.__followers.size};
    
            if (mode === 'up') {
                scroller.scrollTop = Math.max(0, scroller.scrollHeight - scroller.clientHeight * 1.5);
            } else if (mode === 'down') {
                scroller.scrollTop = scroller.scrollHeight;   
            }
    
            return {
                found: true,
                count: window.__followers.size,
                top: Math.round(scroller.scrollTop),
                height: scroller.scrollHeight,
                client: scroller.clientHeight
            };
        """
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
            self.find_followers()
        except TimeoutException:
        
            try:
                continue_ = self.wait.until(EC.element_to_be_clickable((By.XPATH,"//div[@role='button' and starts-with(@aria-label, 'Continue')]")))
                continue_.click()
                self.find_followers()
            except TimeoutException:
                email = self.wait.until(EC.element_to_be_clickable((By.NAME,'email')))
                email.send_keys(USERNAME)
                passw = self.wait.until(EC.element_to_be_clickable((By.NAME,'pass')))
                passw.send_keys(PASSWORD)
                login_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[role="button"][aria-label="Log In"]')))
                login_btn.click()
                self.find_followers()

    def scroll_to_bottom_and_wait(self):
            self.driver.execute_script(self.SCROLL_JS, "up")
            time.sleep(0.4)
            info = self.driver.execute_script(self.SCROLL_JS, "down")
            if not info["found"]:
                return info
    
            start_height = info["height"]

            for _ in range(12):
                time.sleep(0.4)
                info = self.driver.execute_script(self.SCROLL_JS, "down")
                if info["found"] and info["height"] > start_height:
                    break
            return info
    

    def find_followers(self):
            self.driver.get(f'https://www.instagram.com/{self.target}/')
    
            followers_link = self.wait.until(EC.element_to_be_clickable((
                By.XPATH,
                "//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'follower') "
                "or contains(@href, '/followers')]"
            )))
            followers_link.click()
    
            WebDriverWait(self.driver, 15).until(
                lambda d: d.execute_script(
                    "return document.querySelectorAll(\"div[role='dialog'] a[href^='/']\").length"
                ) > 0
            )
            time.sleep(1)
    
            last_count = 0
            same_rounds = 0
            while same_rounds < 4:
                info = self.scroll_to_bottom_and_wait()
    
                if not info["found"]:
                    print("Scrollable element not found:", info)
                    same_rounds += 1
                    continue
    
                print(f"collected: {info['count']} | scrollTop={info['top']} + {info['client']} / {info['height']}")
    
                if info["count"] == last_count:
                    same_rounds += 1
                else:
                    same_rounds = 0
                    last_count = info["count"]
    
            self.followers = self.driver.execute_script(
                "return Array.from(window.__followers || [])")
            print(f"Finished. Total followers collected: {len(self.followers)}")
            return self.followers
    
    def follow(self):
        pass
    
    
if __name__ == '__main__':
    target = input("Enter your target's instagram account: ")
    bot = InstagramBot(target)
    bot.login()
    bot.find_followers()