import urllib.request
import json
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from threading import Thread
from time import sleep, perf_counter

DELAY = 2
BASE_URL = 'https://www.ankhang.vn'
TOTAL = []


def startThread():
    f = open('./data/links.json')
    data = json.load(f)
    link1 = data[0:4];
    link2 = data[4:8];
    link3 = data[8:12];
    start_time = perf_counter()
    # Create Thread
    thread1 = Thread(target=getProductInCategory, args=(link1,))
    thread2 = Thread(target=getProductInCategory, args=(link2,))
    thread3 = Thread(target=getProductInCategory, args=(link3,))
    # Start Thread
    thread1.start()
    thread2.start()
    thread3.start()
    # Wait to done
    thread1.join()
    thread2.join()
    thread3.join()
    end_time = perf_counter()
    print(f'It took {end_time - start_time: 0.2f} second(s) to complete.')
    print(TOTAL)


def getProductInCategory(linkCategories):
    DRIVER_CHROME = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    for i in linkCategories:
        dataCategory = []
        page = urllib.request.urlopen(i.get('url'))
        soup = BeautifulSoup(page, 'html.parser')
        container = soup.find('ul', class_='ul product-list product-lists pro-container-2020')
        listItems = container.find_all('li', class_="p-item-2021")
        for item in listItems:
            id_product = item.get('data-id')
            path = item.find('a', class_='p-name').get('href')
            link = BASE_URL + path
            try:
                dataCategory.append(getContentInPage(id_product, link, DRIVER_CHROME))
            except:
                print("Error when getContentInPage {} {}".format(id_product, path))
            finally:
                continue
        TOTAL.append({i.get('name'): len(dataCategory)})
        exportDataToJson(i.get('name'), dataCategory)


def getContentInPage(id_product, url, DRIVER_CHROME):
    DRIVER_CHROME.get(url)
    WebDriverWait(DRIVER_CHROME, DELAY)
    html = DRIVER_CHROME.page_source
    soup = BeautifulSoup(html, features="lxml")
    containerContent = soup.find('div', class_='pro-summary').find('ul', class_='ul')
    listSpecifications = containerContent.find_all('span')
    listImages = soup.find('div', class_='list_img_product_smaill').find_all('a', class_='img-box')
    # Get context
    images = []
    specifications = ""
    try:
        name = soup.find('h1', class_='text-700').getText()
        try:
            cost = soup.find('span', class_='pro-oldprice').getText()
        except:
            cost = soup.find('span', class_='pro-price').getText().replace("\u0110", "D")
        for item in listImages:
            images.append(item.get('href'))
        for item in listSpecifications:
            specifications = specifications + str(item.getText().rstrip('\n')) + ", "
        try:
            details = []
            listDetails = soup.find('div', class_='content-item crib').find('div', class_='nd').find_all('p')
            for item in listDetails:
                try:
                    detail = item.getText()
                    details.append(detail)
                except:
                    detail = ''
        except Exception as e:
            details = []
    except Exception as e:
        print("Error when get text {}".format(e))
    content = {'id_prodcut': id_product, 'name': name, 'cost': cost, 'specifications': specifications,
               'images': images, 'details': details}
    print("Done product: {}".format(id_product))
    return content


def exportDataToJson(name, data):
    with open('./data/' + name + '.json', 'w') as f:
        json.dump(data, f)
    print("Export {} Done".format(name))


def testSinglePage():
    DRIVER_CHROME = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    id_product = 1
    url = 'https://www.ankhang.vn/laptop-asus-rog-strix-g15-g513im-hn008w.html'
    content = getContentInPage(id_product, url, DRIVER_CHROME)
    with open('./data/test.json', 'w') as f:
        json.dump(content, f)
    print("Export {} Done".format('Test'))


def printFileTest():
    f = open('./data/test.json', 'r')
    data = json.load(f)
    print(data)


if __name__ == '__main__':
    # testSinglePage()
    # printFileTest()
    startThread()
