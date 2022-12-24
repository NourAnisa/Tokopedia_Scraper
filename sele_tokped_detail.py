from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime
import pymongo
import re
import json

url = 'https://shopee.co.id/search?keyword=bahan%20kain&page=0'

# options = Options()
# options.add_argument("--headless")
browser = webdriver.Chrome("chromedriver.exe")
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
db = myclient["admin"]
collection = db["marketplace"]

batch_number = "Batch-" + datetime.today().strftime('%Y%m%d') + "-" + \
    str(random.randint(1, 999999999999))


def search(base_url):
    browser.get(base_url)
    time.sleep(5)
    browser.execute_script('window.scrollTo(0, 1500);')
    time.sleep(5)
    browser.execute_script('window.scrollTo(0, 2500);')
    time.sleep(5)
    html = browser.page_source
    # browser.close()
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find_all('div', {"class": "css-7fmtuv"})
    data = []
    for x, div in enumerate(table):
        tag_link = div.find("a",  class_="pcv3__info-content")
        if tag_link is not None:
            link = tag_link.get('href')
            location = soup.find("span", class_="css-4pwgpi").text

            a_dict = dict()
            a_dict["link"] = tag_link.get('href')
            a_dict["location"] = soup.find("span", class_="css-4pwgpi").text

            data.append(a_dict)

    return data


def getProductName(soup):
    div_product_name = soup.find("h1", class_="css-x7lc0h")
    if div_product_name is not None:
        return div_product_name.text

    # label_product_name = soup.find("span", class_ = "OSgLcw")
    # if label_product_name is not None:
    # 	product_name = label_product_name.text
    # 	return product_name

    # div_title = soup.find("span", class_ = "$0")
    # if div_title is not None:
    # 	product_name = div_title.text
    # 	return product_name

    return ''


def getMerek(soup):
    label_merek = soup.find("th", string="Brand")
    if label_merek is not None:
        merek = label_merek.find_next_sibling("td")
        merek2 = merek.find_next_sibling("td")
        return merek2.text

    return ''


def getBahan(soup):
    label_bahan = soup.find("p", class_="css-1s46cvt")
    if label_bahan is not None:
        return label_bahan.text

    return ''


def getStyle(soup):
    label_bahan = soup.find("th", string="Type")
    if label_bahan is not None:
        bahan = label_bahan.find_next_sibling("td")
        bahan2 = bahan.find_next_sibling("td")
        return bahan2.text

    return ''


def getProductOrigin(soup):
    label_bahan = soup.find("th", string="Asal")
    if label_bahan is not None:
        bahan = label_bahan.find_next_sibling("td")
        bahan2 = bahan.find_next_sibling("td")
        return bahan2.text

    return ''


def removeHiddenSpace(teks):
    name = teks.replace('\n', ' ').replace('\r', '')
    return name.strip()


def product_detail(data_array):
    url_suffix = data_array['link']
    browser.get(url_suffix)
    time.sleep(5)
    browser.execute_script('window.scrollTo(0, 1500);')
    time.sleep(5)
    browser.execute_script('window.scrollTo(0, 2500);')
    time.sleep(5)
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')

    data = []

    # PRODUCT NAME
    product_name = getProductName(soup)
    shop_name = soup.find("a", class_="css-xmjuvc").text

    string_price = soup.find("h3", class_="css-c820vl").text
    remove_dot = string_price.replace(".", "")
    price = remove_dot.replace("Rp", "")

    span_rating = soup.find("h5", class_="css-wano70")
    rating = ''
    if span_rating is not None:
        rating = span_rating.text

    merek = ''
    bahan = getBahan(soup)
    style = ''
    dimensi = ''

    location = data_array['location']

    product_origin = getProductOrigin(soup)

    stock = ''

    is_insert = False
    include_category = ["Fashion Wanita", "Fashion Muslim"]
    product_category = []
    for temp_category in soup.find_all("a", class_="css-yoyor-unf-heading"):
        if temp_category.text in include_category:
            is_insert = True
        product_category.append(temp_category.text)

    if not is_insert:
        return False

    description = soup.find("p", class_="css-olztn6-unf-heading").text
    div_sold = soup.find("span", string="Terjual")
    sold = ''
    if div_sold is not None:
        sold = int(re.search(r'\d+', div_sold.text).group())

    string_review = soup.find("div", string="Ulasan")
    total_review = ''
    if string_review is not None:
        total_review = int(re.search(r'\d+', string_review.text).group())

    customer_review = []
    for temp_review in soup.find_all("div", class_="css-1np3d84-unf-heading"):
        string_customer_review = label_merek.find_next_sibling("span").text
        customer_review.append(string_customer_review)

    product_color = ''

    obj = {
        'marketplace_name': 'tokopedia',
        'link': url_suffix,
        'shop_name': shop_name,
        'shop_category': '',
        'location': location,
        'product_name': product_name,
        'product_category': product_category,
        'price': price,
        'rating': rating,
        'total_review':  total_review,
        'sold': sold,
        'merek': merek,
        'bahan': bahan,
        'dimensi': dimensi,
        'style': style,
        'product_origin': product_origin,
        'stock': stock,
        'product_color': product_color,
        'customer_review': customer_review,
        'description': description,
        'total_views': '',
        'insert_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'date': datetime.now().strftime('%Y-%m-%d'),
        'batch_number': batch_number
    }
    with open("data_marketplace_tokped.json", "a") as data:
        data.write(json.dumps(obj) + ', ')
        data.close()
    return obj


all_data = []
limit = 1
for i in range(4):
    page = i + 1
    base_url = 'https://www.tokopedia.com/search?navsource=home&page=' + \
        str(page) + '&q=bahan%20kain&st=product'
    product_urls = search(base_url)
    for index, product_url in enumerate(product_urls):
        temp = product_detail(product_url)
        if temp:
            all_data.append(temp)

        if index == limit:
            break

print(all_data)
# if all_data:
# 	x = collection.insert_many(all_data)
