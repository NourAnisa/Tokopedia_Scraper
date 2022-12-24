from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

url = 'https://www.tokopedia.com/search?q=jilbab&source=universe&st=product'
driver_browser = "chromedriver.exe"
option = Options()
option.add_argument("--disable-infobars")
# option.add_argument("start-maximized")
option.add_argument("--disable-extensions")
# Pass the argument 1 to allow and 2 to block
option.add_experimental_option("prefs", {
    "profile.default_content_setting_values.notifications": 1
})

browser = webdriver.Chrome(chrome_options=option,
                           executable_path=driver_browser)
browser.get(url)

time.sleep(5)
browser.execute_script('window.scrollTo(0, 1500);')
time.sleep(5)
browser.execute_script('window.scrollTo(0, 2500);')
time.sleep(5)
html = browser.page_source
# browser.close()
soup = BeautifulSoup(html, 'html.parser')


data = []
table = soup.find_all('div', {"class": "css-1g20a2m"})
for x, div in enumerate(table):
    title = div.find("div", class_="css-18c4yhp")
    price = div.find("div", class_="css-rhd610")
    location = div.find("span", class_="css-4pwgpi")
    sold = div.find("span", class_="css-u49rxo")

    fix_title = ''
    if title is not None:
        fix_title = title.text

    fix_price = ''
    if price is not None:
        fix_price = price.text

    fix_location = ''
    if location is not None:
        fix_location = location.text

    fix_sold = ''
    if sold is not None:
        fix_sold = sold.text

    obj = {
        "name": fix_title,
        "price": fix_price,
        "location": fix_location,
        "sold": fix_sold,
    }
    data.append(obj)

print(data)
