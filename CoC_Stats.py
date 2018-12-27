class CoC_Stats():
    def __init__(self, jjson):
        self.coc_name = jjson['name']
        self.coc_tag = jjson['tag']
        self.th_lvl = jjson['townHallLevel']
        self.league = jjson['league']['name']
        self.league_icon = jjson['league']['iconUrls']['tiny']

        for i in jjson['achievements']:
            if i['name'] == "Friend in Need":
                self.total_Donations = i['value']


        

        