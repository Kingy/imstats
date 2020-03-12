class Athlete:

    def __init__(self, name, country):
        self.name = name
        self.country = country

    def athleteInfo(self):
        return self.name + " from " + self.country