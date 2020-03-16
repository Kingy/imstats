from lxml import html
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from classes.Course import Course
from classes.Athlete import Athlete
from mysql.connector import connect
import time, sys
import configparser

config = configparser.ConfigParser()
config.read('config.properties')

connection = connect(host=config['Database']['database.host'],
                    database=config['Database']['database.dbname'],
                    user=config['Database']['database.user'],
                    password=config['Database']['database.pass'],
                    auth_plugin='mysql_native_password')

im_url = config['Main']['ironman.base_url']
chrome_driver = config['Main']['chromedriver.location']

chrome_options = webdriver.ChromeOptions()
#chrome_options.add_argument('--headless')
chrome_options.add_argument('--blink-settings=imagesEnabled=false')
chrome_options.add_argument('--log-level=3')

def getCourses(url):
    driver = webdriver.Chrome(chrome_driver, options=chrome_options)
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    courses = []
    driver.execute_script("window.scrollTo(0, window.scrollY + 4800)")
    pageCount = len(driver.find_elements_by_xpath("//div[@class='pageButtons']/div[contains(@class, 'pageNumber')]"))
    courseCount = driver.find_element_by_xpath("//div[@class='race-count']/p[1]").text

    # Do the first page
    driver.execute_script("window.scrollTo(0, window.scrollY + 0)")

    currPage = 1

    for i in progressbar(range(pageCount), "Getting Courses: "):
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')

        for courseDiv in soup.find_all('div', {'class' : 'race-card'}):
            name = courseDiv.find('div', {'class' : 'details-left'}).h3.text
            location = courseDiv.find('p', {'class' : 'race-location'}).text
            month = courseDiv.find('p', {'class' : 'race-month'}).text
            day = courseDiv.find('p', {'class' : 'race-day'}).text
            year = courseDiv.find('p', {'class' : 'race-year'}).text
            date = month + ' ' + day + ' ' + year
            url = courseDiv.find('div', {'class' : 'race-details-right'}).a['href']
            course = Course(name, location, date, url)
            courses.append(course)

        if currPage != pageCount:
            driver.execute_script("window.scrollTo(0, window.scrollY + 4600)")
            time.sleep(2)
            nxt = driver.find_element_by_xpath("//div[@class='paginationButtons']/button[@class='nextPageButton']")
            actions = ActionChains(driver)
            actions.click(nxt).perform()
            currPage += 1
            time.sleep(2)

    driver.quit()

    return courses

def getRaceResults(Race):

    result_url = im_url + Race.url_segment + '-results'

    driver = webdriver.Chrome(chrome_driver, options=chrome_options)    
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
    courses = getCourses(url)
    for c in courses:
        print(c.courseInfo())
        raceResults = getRaceResults(c)
        print(raceResults)

if __name__== "__main__":
    main()
