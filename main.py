import requests
from selenium import webdriver
import time
import json
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options
import os


def enter_location_loadMore(driver, location):
    inp = driver.find_element_by_class_name("ant-input")
    time.sleep(5)
    inp.send_keys(location)
    time.sleep(5)
    driver.find_element_by_class_name("ant-btn").click()
    time.sleep(5)
    i = 0
    # clicking loadmore only 3 times to avoid blockage
    while i < 3:
        try:
            time.sleep(5)
            button = driver.find_element_by_class_name("ant-btn")
            time.sleep(2)
            button.click()
            i = i + 1

        except:
            print("Number of pages scraped: ", i)
            i = 50


def get_resturants_location(url):
    try:
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        pageData = soup.find('script', {'id': '__NEXT_DATA__'})
        json_obj = json.loads(pageData.contents[0])
        rest_data = json_obj['props']['initialReduxState']['pageRestaurantDetail']['entities']
        rest_id = list(rest_data.keys())[0]
        return rest_data[rest_id]['latlng']
    except Exception as e:
        return {"latitude": '', "longitude": ''}


def main():
    url = 'https://food.grab.com/ph/en'
    options = Options()
    # An attempt to fool the server with diffrent user agents
    ua = UserAgent()
    userAgent = ua.random
    options.add_argument(f'user-agent={userAgent}')

    resturant_names = []
    resturant_urls = []
    final_data = {}
    directory = 'data'
    driver = webdriver.Chrome(
        options=options, executable_path='./chromedriver.exe')
    driver.get(url)
    driver.maximize_window()
    time.sleep(5)
    # location = 'Marriott Hotel Manila - 2 Resorts Dr., Pasay City, Metro Manila, NCR, 1309, Philippines'
    # enter_location_loadMore(driver, location)

    print('Enter the location manually, scroll-down and click load-more...')
    input('Press Enter When done....')
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    rest_elems = soup.select(
        'div.ant-col-24.RestaurantListCol___1FZ8V.ant-col-md-12.ant-col-lg-6')
    for sub_elems in rest_elems:
        h_elems = sub_elems.find('h6', {"class": "name___2epcT"})
        resturant_names.append(h_elems.text)
        a_elems = sub_elems.find('a')
        resturant_urls.append(a_elems['href'])

    url = 'https://food.grab.com'
    # Going for only first 5 urls to avoid the blocking from food-grab
    for index in range(len(resturant_urls[:5])):
        locationObj = get_resturants_location(url + resturant_urls[index])
        final_data[resturant_names[index]] = {}
        final_data[resturant_names[index]]['latlng'] = locationObj
        final_data[resturant_names[index]]['href'] = resturant_urls[index]

    if not os.path.exists(directory):
        os.makedirs(directory)
    final_data_json = json.dumps(final_data)
    fp = open('data/final_data.json', 'a')
    fp.write(final_data_json)
    fp.close
    print('Find the Final Data in data directory')


if __name__ == '__main__':
    main()
