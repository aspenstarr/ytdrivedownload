from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time

chrome_binary = "/opt/google/chrome/google-chrome"
chromedriver_path = "/home/aspen/Videos/chromedriver-linux64/chromedriver"

chrome_options = Options()
chrome_options.binary_location = chrome_binary
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")

service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    driver.get("https://www.google.com")
    time.sleep(2)
    print("Title:", driver.title)
finally:
    driver.quit()
