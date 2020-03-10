from lxml import html
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from classes.Race import Race
import time

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--blink-settings=imagesEnabled=false')

def getRaces(url):
    driver = webdriver.Chrome('driver/chromedriver.exe', options=chrome_options)
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    races = []
    driver.execute_script("window.scrollTo(0, window.scrollY + 4800)")
    pageCount = len(driver.find_elements_by_xpath("//div[@class='pageButtons']/div[contains(@class, 'pageNumber')]"))

    # Do the first page
    driver.execute_script("window.scrollTo(0, window.scrollY + 0)")

    currPage = 1

    while True: 
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')

        for raceDiv in soup.find_all('div', {'class' : 'race-card'}):
            name = raceDiv.find('div', {'class' : 'details-left'}).h3.text
            location = raceDiv.find('p', {'class' : 'race-location'}).text
            month = raceDiv.find('p', {'class' : 'race-month'}).text
            day = raceDiv.find('p', {'class' : 'race-day'}).text
            year = raceDiv.find('p', {'class' : 'race-year'}).text
            date = month + ' ' + day + ' ' + year
            url = raceDiv.find('div', {'class' : 'race-details-right'}).a['href']
            race = Race(name, location, date, url)
            races.append(race)

        if currPage != pageCount:
            driver.execute_script("window.scrollTo(0, window.scrollY + 4600)")
            time.sleep(2)
            nxt = driver.find_element_by_xpath("//div[@class='paginationButtons']/button[@class='nextPageButton']")
            actions = ActionChains(driver)
            actions.click(nxt).perform()
            currPage += 1
            time.sleep(2)
        else:
            break

    driver.quit()

    return races

def getRaceResults(race):
    driver = webdriver.Chrome('driver/chromedriver.exe', options=chrome_options)    
    driver.get('https://www.ironman.com/im703-bahrain-results')
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    races = []
    raceResults = []
    # Do the first page
    for link in soup.find_all('a', {'class' : 'tab-remote'}):
        races.append(link['href'])

    for raceYear in races:
        driver.get('https://www.ironman.com' + raceYear)
        time.sleep(3)
        #driver.get('https://www.ironman.com' + '/layout_container/show_layout_tab?layout_container_id=64131430&page_node_id=5321701&tab_element_id=212986')
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        labURL = soup.iframe['src']

        driver.set_window_size(1110, 950)
        driver.get(labURL)
        time.sleep(10)
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')    

        # Let's just keep it at one page for now
        #pageCount = int(driver.find_element_by_xpath("//div[@class='jss369']/button[contains(@class, 'page-number')][last()]").text)
        pageCount = 1

        # First page of racers
        for tr in soup.find_all('tr', {'class' : 'MuiTableRow-root'}):
            td = tr.find('td', {'class' : 'column-Contact.FullName'})
            if td:
                raceResults.append(td.span.text)

        x = 0

        while x < pageCount:
            nxt = driver.find_element_by_xpath("//div[@class='jss369']/button[contains(@class, 'next-page')]")
            actions = ActionChains(driver)
            actions.click(nxt).perform()
            time.sleep(2)

            html = driver.page_source
            soup = BeautifulSoup(html, 'lxml')

            for tr in soup.find_all('tr', {'class' : 'MuiTableRow-root'}):
                td = tr.find('td', {'class' : 'column-Contact.FullName'})
                if td:
                    raceResults.append(td.span.text)

            x += 1

    driver.quit()
    return raceResults

def main():
    url = 'https://www.ironman.com/races'
    races = getRaces(url)
    for r in races:
        print(r.raceInfo())  

    #raceResults = getRaceResults('im703-bahrain')
    #print(raceResults)

if __name__== "__main__":
    main()
