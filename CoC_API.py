import requests, sys

class CoC():
    def __init__(self, token):
        # Constructor
        self.requests = requests
        self.token = token
        self.base_url = "https://api.clashofclans.com/v1"

    # Base function; Not called directly
    def get_request(self, uri):
        headers = {
            'Accept': "application/json",
            'Authorization': "Bearer " + self.token
            }

        url = self.base_url + uri
        try:
            response = self.requests.get(url, headers=headers, timeout=30)
            return response
        except:
            e = sys.exc_info()[0]
            return "Error: {}".format(e)

    
    def get_member(self, members_tag):
        """Get player information not in clan api

        ARGS:
            player tag

        EXAMPLE:
            CoC.get_member("#123LGM")
        """
        return self.get_request('/players/%23' + members_tag.lstrip("#").upper())



    def get_clan(self, clan_tag):
        """Returns Clan information such as War frequency, name, tag, streaks etc.

        membersList is a limited list of player information. More information such as
        achievements are provided in the get_member() call.

        ARGS:
            Clan Tag
            """
        return self.get_request('/clans/%23{}'.format(clan_tag.lstrip("#").upper()))

    def get_clanMembers(self, clan_tag):
        """Returns the memberList portion of get_clan while ignoring the clan information

        ARGS:
            clan_tag
            """
        return self.get_request('/clans/%23{}/members'.format(clan_tag.lstrip("#").upper()))

    def get_clanWarLog(self, clan_tag):
        """Returns last war status. Win/Lost/Damage Percentage/stars won

        ARGS:
            clan_tag
        """
        return self.get_request('/clans/%23{}/warlog'.format(clan_tag.lstrip("#").upper()))

    def get_clanCurrentWar(self, clan_tag):
        """Gives you stats on the current war like who attack who and for how many stars

        ARGS:
            clan_tag
        """
        return self.get_request('/clans/%23{}/currentwar'.format(clan_tag.lstrip("#").upper()))

    def get_clanLeagueGroup(self, clan_tag):
        """Returns 2 import things. 1 all the clans invovled in the clan wars and 2 the wartag.
        The issue is that you can't tell what the wartag represents, so you have to query
        each one to see what clans are invovled. 

        ARGS:
            clan_tag
        """
        return self.get_request('/clans/%23{}/currentwar/leaguegroup'.format(clan_tag.lstrip("#").upper()))

    def get_clanLeagueWars(self, war_tag):
        """This one requires the clan_war tag that you get from get_clanLeagueGroup
        It's currently not working. Doesn't return roster numbers or peoples accurate position

        ARGS:
            war_tag
            """
        return self.get_request('/clanwarleagues/wars/%23{}'.format(war_tag.lstrip("#").upper()))
      