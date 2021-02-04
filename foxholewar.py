import datetime
import enum
import json
import requests

BaseURL = "https://war-service-live.foxholeservices.com/api/"

class Team(enum.Enum):
	NONE = 0
	COLONIAL = 1
	WARDENS = 2


class War:
	"""A class representing war details"""
	warId = None
	warNumber = None
	winner = None
	conquestStartTime = None
	conquestEndTime = None
	resistanceStartTime = None
	requiredVictoryTowns = None


def getCurrentWar():
	requestUrl = BaseURL + "worldconquest/war"
	response = requests.get(requestUrl)
	json_data = json.loads(response.text)

	war = War()
	war.warId = json_data["warId"],
	war.warNumber = json_data["warNumber"]
	war.winner = json_data["winner"]
	war.conquestStartTime = json_data["conquestStartTime"]
	war.conquestEndTime = json_data["conquestEndTime"]
	war.resistanceStartTime = json_data["resistanceStartTime"]
	war.requiredVictoryTowns = json_data["requiredVictoryTowns"]
	return war
