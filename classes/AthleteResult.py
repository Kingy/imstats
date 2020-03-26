class AthleteResult:

    def __init__(self, id, race_id, name, country, division, gender, div_rank, gen_rank, ovr_rank, tot_time):
        self.id = id
        self.race_id = race_id
        self.name = name
        self.country = country
        self.division = division
        self.gender = gender
        self.div_rank = div_rank
        self.gen_rank = gen_rank
        self.ovr_rank = ovr_rank
        self.tot_time = tot_time

    def athleteInfo(self):
        return self.name + " from " + self.country

    