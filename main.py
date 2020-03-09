from lxml import html
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
import pandas as pandas

url = 'https://www.ironman.com/races'
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--blink-settings=imagesEnabled=false')

driver = webdriver.Chrome('driver/chromedriver.exe', options=chrome_options)
driver.get(url)
html = driver.page_source
soup = BeautifulSoup(html, 'lxml')

raceLinks = []

driver.execute_script("window.scrollTo(0, window.scrollY + 4800)")
pageCount = len(driver.find_elements_by_xpath("//div[@class='pageButtons']/div[contains(@class, 'pageNumber')]"))
print(pageCount)

# Do the first page
for div in soup.find_all('div', {'class' : 'race-details-right'}):
    for link in div.find_all('a', href=True):
        raceLinks.append(link['href'])

driver.execute_script("window.scrollTo(0, window.scrollY + 0)")

x = 1
while x < pageCount: 
    driver.execute_script("window.scrollTo(0, window.scrollY + 4600)")
    time.sleep(2)
    nxt = driver.find_element_by_xpath("//div[@class='paginationButtons']/button[@class='nextPageButton']")
    actions = ActionChains(driver)
    actions.click(nxt).perform()
    time.sleep(2)

    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    for div in soup.find_all('div', {'class' : 'race-details-right'}):
        for link in div.find_all('a', href=True):
            raceLinks.append(link['href'])

    x += 1

print(raceLinks)

driver.quit()