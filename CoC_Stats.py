class CoC_Stats():
    def __init__(self, jjson):

        self.coc_name = jjson['name']
        self.coc_tag = jjson['tag']
        self.th_lvl = jjson['townHallLevel']
        self.expLevel = jjson['expLevel']
        self.trophies = jjson['trophies']
        self.bestTrophies = jjson['bestTrophies']
        self.warStars = jjson['warStars']
        self.attackWins = jjson['attackWins']
        self.defenseWins = jjson['defenseWins']
        self.builderHallLevel = jjson['builderHallLevel']
        self.versusTrophies = jjson['versusTrophies']
        self.bestVersusTrophies = jjson['bestVersusTrophies']
        self.versusBattleWins = jjson['versusBattleWins']
        self.role = jjson['role']
        self.donation = jjson['donations']
        self.donationsReceived = jjson['donationsReceived']
        
        #League dict
        self.league = jjson['league']['name']
        self.league_icon = jjson['league']['iconUrls']['tiny']

        # Donations 
        for i in jjson['achievements']:
            if i['name'] == "Friend in Need":
                self.total_Donations = i['value']
        
        
        # Clan Dict
        self.currentClan_name = jjson['clan']['name']
        self.currentClan_tag = jjson['clan']['tag']
        self.currentClan_lvl = jjson['clan']['clanLevel']

        # Heroes
        hero_dict = {'Barbarian King':0, 'Archer Queen':0, 'Grand Warden':0, 'Battle Machine':0}
        for hero in jjson['heroes']:
             hero_dict[hero['name']] = hero['level']

        self.bk_lvl = hero_dict['Barbarian King']
        self.aq_lvl = hero_dict['Archer Queen']
        self.gw_lvl = hero_dict['Grand Warden']
        self.bm_lvl = hero_dict['Battle Machine']




        
        
        
        
        
       

        

        

        