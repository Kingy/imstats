from urllib.parse import urlparse

class Course:
    def __init__(self, name, location, date, url):
        self.name = name
        self.location = location
        self.date = date
        self.url = url
        self.url_segment = self.createUrlSegment()

    def createUrlSegment(self):
        parsed = urlparse(self.url)
        return parsed.path

    def courseInfo(self):
        return self.name + ' will be held in ' + self.location + ' on ' + self.date + ' (' + self.url_segment + ')'