from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import json

options = Options()
options.add_argument("--disable-notifications")
options.add_argument("--start-maximized")

service = Service("C:/Users/achom/Downloads/fb scraper/chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)

driver.get("https://www.facebook.com")
print("Facebook opened. Log in manually now.")
print("Waiting 90 seconds...")

time.sleep(90)

cookies = driver.get_cookies()
driver.quit()

with open("facebook_cookies.json", "w") as f:
    json.dump(cookies, f, indent=2)

print("Cookies saved to facebook_cookies.json")
