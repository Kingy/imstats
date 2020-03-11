from lxml import html
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from classes.Race import Race
from classes.Athlete import Athlete
import time, sys

im_url = 'https://www.ironman.com/'

chrome_options = webdriver.ChromeOptions()
#chrome_options.add_argument('--headless')
chrome_options.add_argument('--blink-settings=imagesEnabled=false')
chrome_options.add_argument('--log-level=3')

def getRaces(url):
    driver = webdriver.Chrome('driver/chromedriver.exe', options=chrome_options)
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    races = []
    driver.execute_script("window.scrollTo(0, window.scrollY + 4800)")
    pageCount = len(driver.find_elements_by_xpath("//div[@class='pageButtons']/div[contains(@class, 'pageNumber')]"))
    raceCount = driver.find_element_by_xpath("//div[@class='race-count']/p[1]").text

    print(raceCount)

    # Do the first page
    driver.execute_script("window.scrollTo(0, window.scrollY + 0)")

    currPage = 1

    for i in progressbar(range(pageCount), "Getting Races: "):
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

    driver.quit()

    return races

def getRaceResults(Race):

    result_url = im_url + Race.url_segment + '-results'

    driver = webdriver.Chrome('driver/chromedriver.exe', options=chrome_options)    
    driver.get(result_url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    races = []
    raceResults = []
    athletes = []
    for link in soup.find_all('a', {'class' : 'tab-remote'}):
        races.append(link['href'])

    for raceYearURL in races:
        driver.get(im_url + raceYearURL)
        time.sleep(3)
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        labURL = soup.iframe['src']

        driver.set_window_size(1110, 950)
        driver.get(labURL)
        time.sleep(10)
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')    

        athleteCount = int(driver.find_element_by_xpath("//p[@class='MuiTypography-root MuiTablePagination-caption MuiTypography-body2 MuiTypography-colorInherit'][2]").text.split()[2])

        print("Athletes Found {0}".format(str(athleteCount)))

        # Let's just keep it at one page for now
        #pageCount = int(driver.find_element_by_xpath("//div[@class='jss369']/button[contains(@class, 'page-number')][last()]").text)
        pageCount = 2

        currPage = 1

        for i in progressbar(range(pageCount), "Getting Athlete Results: "):
            html = driver.page_source
            soup = BeautifulSoup(html, 'lxml')

            for tr in soup.find_all('tr', {'class' : 'MuiTableRow-root'}):
                name = ""
                country = ""

                nameTd = tr.find('td', {'class' : 'column-Contact.FullName'})
                if nameTd:
                    name = nameTd.span.text
                countryTd = tr.find('td', {'class' : 'column-CountryISO2'})
                if countryTd:
                    country = countryTd.span.text

                athlete = Athlete(name, country)
                athletes.append(athlete)

            if currPage != pageCount:
                nxt = driver.find_element_by_xpath("//button[contains(@class, 'next-page')]")
                actions = ActionChains(driver)
                actions.click(nxt).perform()
                currPage += 1
                time.sleep(2)        

    driver.quit()
    return athletes

def progressbar(it, prefix="", size=60, file=sys.stdout):
    count = len(it)
    def show(j):
        x = int(size*j/count)
        perc = int(j/count*100)
        file.write("%s[%s%s] (%i%s)\r" % (prefix, "#"*x, "."*(size-x), perc,"%"))
        file.flush()        
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    file.write("\n")
    file.flush()

def main():
    url = im_url + 'races'
    races = getRaces(url)
    for r in races:
        print(r.raceInfo())
        raceResults = getRaceResults(r)
        print(raceResults)

if __name__== "__main__":
    main()
