from lxml import html
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from classes.Course import Course
from classes.AthleteResult import AthleteResult
from classes.Database import Database
from classes.Race import Race
import time, sys
import configparser

config = configparser.ConfigParser()
config.read('config.properties')

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
    driver.execute_script("window.scrollTo(0, window.scrollY + 4400)")
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
            courseID = None

            with Database() as db:
                checkCourseExists = db.query("SELECT course_id from course where name = %s", (name,))
                if not checkCourseExists:
                    db.execute("INSERT INTO course (name) VALUES (%s)", (name,))
                    courseID = db.cursor.lastrowid
                else:
                    courseID = checkCourseExists[0][0]

            course = Course(courseID, name, location, url)
            courses.append(course)

            # Make and insert the next race for this course here

        if currPage != pageCount:
            driver.execute_script("window.scrollTo(0, window.scrollY + 4400)")
            time.sleep(2)
            nxt = driver.find_element_by_xpath("//div[@class='paginationButtons']/button[@class='nextPageButton']")
            actions = ActionChains(driver)
            actions.click(nxt).perform()
            currPage += 1
            time.sleep(2)

    driver.quit()

    return courses

def getRaces(Course):

    result_url = im_url + Course.url_segment + '-results'

    driver = webdriver.Chrome(chrome_driver, options=chrome_options)    
    driver.get(result_url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    races = []
    raceResults = []
    
    try:
        raceURL = link['href']
        raceDate = link.text[:4]
        raceID = None
        raceName = "N/A"
        raceCourse = Course.id

        with Database() as db:
            checkCourseRaceExists = db.query("SELECT race_id from race where race_date = %s", (raceDate,))
            if not checkCourseRaceExists:
                db.execute("INSERT INTO race (course_id, name, race_date) VALUES (%s, %s, %s)", (raceCourse,'N/A',raceDate,))
                raceID = db.cursor.lastrowid

        race = Race(raceID, raceCourse, raceName, raceDate, raceURL)
        races.append(race)
    except Exception:
        print("Error: " + Exception)
        pass

    driver.quit()
    return races

def getRaceResults(Race):

    results = []

    driver.get(im_url + Race.url)
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

            resultID = None

            with Database() as db:
                checkAthleteResultExists = db.query("SELECT result_id from race_results where race_id = %s AND name = %s AND cty_Code = %s", (Race.id,name,country,))
                if not checkCourseRaceExists:
                    db.execute("INSERT INTO race_results (race_id, name, cty_code, part_div_tp, part_gen, part_div_rank, part_gen_rank, part_ovrl_rank, part_tot_time) VALUES (%s, %s, %s, 'N/A', 'N', 0, 0, 0, '00:00:00')", (Race.id,name,country,))
                    resultID = db.cursor.lastrowid

            athlete = AthleteResult(resultID, Race.id, name, country, 'N/A', 'N', 0, 0, 0, '00:00:00')
            results.append(athlete)
        if currPage != pageCount:
            nxt = driver.find_element_by_xpath("//button[contains(@class, 'next-page')]")
            actions = ActionChains(driver)
            actions.click(nxt).perform()
            currPage += 1
            time.sleep(2)  

    return results      

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
        races = getRaces(c)
        for r in races:
            print(r)
            raceResults = getRaceResults(r) 
            print(raceResults)

if __name__== "__main__":
    main()
