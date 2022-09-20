class AthleteResult:

    def __init__(self, id, race_id, name, country, div_rank, gen_rank, rank, swim_time, bike_time, run_time, time, points):
        self.id = id
        self.race_id = race_id
        self.name = name
        self.country = country
        self.div_rank = div_rank
        self.gen_rank = gen_rank
        self.rank = rank
        self.swim_time = swim_time
        self.bike_time = bike_time
        self.run_time = run_time
        self.time = time
        self.points = points

    def athleteInfo(self):
        return self.name + " from " + self.country

    
