from urllib.parse import urlparse

class Course:
    def __init__(self, id, name, location, url):
        self.id = id
        self.name = name
        self.location = location
        self.url = url
        self.url_segment = self.createUrlSegment()

    def createUrlSegment(self):
        parsed = urlparse(self.url)
        return parsed.path

    def courseInfo(self):
        return self.name + ' will be held in ' + self.location + ' (' + self.url_segment + ')'