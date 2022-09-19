from lxml import html
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[@id="onetrust-accept-btn-handler"]'))).click()
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    courses = []
    driver.execute_script("window.scrollTo(0, window.scrollY + 4400)")
    pageCount = len(driver.find_elements(by=By.XPATH, value="//div[@class='pageButtons']/div[contains(@class, 'pageNumber')]"))
    courseCount = driver.find_element("xpath", "//div[@class='race-count']/p[1]").text
    print(courseCount)

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
                    db.execute("INSERT INTO course (name, location, url) VALUES (%s, %s, %s)", (name,location, url,))
                    courseID = db.cursor.lastrowid
                else:
                    courseID = checkCourseExists[0][0]

            course = Course(courseID, name, location, url)
            courses.append(course)

            # Make and insert the next race for this course here

        if currPage != pageCount:
            driver.execute_script("window.scrollTo(0, window.scrollY + 4400)")
            time.sleep(2)
            nxt = driver.find_element("xpath", "//div[@class='paginationButtons']/button[@class='nextPageButton']")
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

    WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, '//button[@id="onetrust-accept-btn-handler"]'))).click()
    WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="mktoModalClose"]'))).click()

    raceCount = len(driver.find_elements(by=By.XPATH, value="//ul[@class='contentTabs layoutContainerTabs']/li"))

    print(Course.name)
    print(raceCount)

    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    
    races = []

    for racesUl in soup.find_all('ul', {'class': 'contentTabs layoutContainerTabs'}):
        for raceLi in racesUl.find_all('li'):
            date = raceLi.span.a.text

            with Database() as db:
                checkRaceExists = db.query("SELECT race_id from race where name = %s AND course_id = %s", (date, Course.id,))
                if not checkRaceExists:
                    db.execute("INSERT INTO race (course_id, name) VALUES (%s, %s)", (Course.id,date,))
                    raceID = db.cursor.lastrowid
                else:
                    raceID = checkRaceExists[0][0]

            race = Race(raceID, Course.name, date)
            races.append(race)


    driver.quit()
    return races   


def getRaceResults(Course, Race):
    results = []
    result_url = im_url + Course.url_segment + '-results'
    
    #'/layout_container/show_layout_tab?layout_container_id=64187417&page_node_id=5333561&tab_element_id=213209'

    driver = webdriver.Chrome(chrome_driver, options=chrome_options)    
    driver.get(result_url)

    WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.XPATH, '//button[@id="onetrust-accept-btn-handler"]'))).click()
    try:
        WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="mktoModalClose"]'))).click()
    except:
        print("No Frame")
    
    raceXpath = "//ul[@class='contentTabs layoutContainerTabs']/li/span/a[text() = '" + Race.name.strip() + "']"
    raceAHref = driver.find_element(by=By.XPATH, value=raceXpath).get_attribute('href')
    athlete_list_url = raceAHref

    driver.set_window_size(1024, 768)
    driver.get(athlete_list_url)

    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, '//iframe')));

    iframe = driver.find_element(by=By.XPATH, value="//iframe")
    driver.switch_to.frame(iframe)

    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, 'resultList')));

    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')   

    athleteTable = soup.find(id="resultList")
    for athleteTr in athleteTable.tbody.find_all('tr'):
        athleteTd = athleteTr.find_all('td')
        print(athleteTd)

    # for athleteTable in soup.find_all('div', {'id': 'resultList'}):
    #     print("HELLO")
    #     for raceTr in athleteTable.find_all('tr'):
    #         raceTd = raceTr.find_all('td');
    #         print(raceTd[1].span.text)    

    #driver.quit()
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
    url = im_url + '/races'
    courses = []
    races = []
    athleteResults = []

    ######## Get all courses ########
    #courses = getCourses(url)

    ######## Get races for one course ########
    # course = None
    # with Database() as db:
    #     course_res = db.query("SELECT * from course LIMIT 1")
    #     if not course_res:
    #         print("No Course Found")
    #         return
    #     else:
    #         course = Course(course_res[0][0], course_res[0][1], course_res[0][2], course_res[0][3])

    # course_races = getRaces(course)

    ######### Get all races for the courses #########
    #for c in courses:
    #    print(c.courseInfo())
    #    races = getRaces(c)
    #print(courses[0].courseInfo())
    #races = getRaces(courses[0])

    ######## Get results for one race #########
    race = '2021'
    with Database() as db:
        race_res = db.query("SELECT course.*, race.* FROM race inner JOIN course ON course.course_id = race.course_id WHERE race.name = %s", (race,))
        if not race_res:
            print("No Race Found")
            return
        else:
            print(race_res)
            course = Course(race_res[0][0], race_res[0][1], race_res[0][2], race_res[0][3])
            race = Race(race_res[0][5],race_res[0][6],race_res[0][7])

    raceResults = getRaceResults(course, race)
        
    # Get all athlete race results
    #for r in races:
    #    print(r)
    #    raceResults = getRaceResults(r) 
        

if __name__== "__main__":
    main()
