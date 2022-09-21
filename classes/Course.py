from urllib.parse import urlparse

class Course:
    def __init__(self, id, name, location, date, image, swim, bike, run, airTemp, waterTemp, url):
        self.id = id
        self.name = name
        self.location = location
        self.date = date
        self.image = image
        self.swim = swim
        self.bike = bike
        self.run = run
        self.air_temp = airTemp
        self.water_temp = waterTemp
        self.url = url
        self.url_segment = self.createUrlSegment()

    def createUrlSegment(self):
        parsed = urlparse(self.url)
        return parsed.path

    def courseInfo(self):
        return self.name + ' will be held in ' + self.location + ' (' + self.url_segment + ')'
