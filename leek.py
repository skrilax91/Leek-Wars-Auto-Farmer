import json
import requests
import getpass
import time

f = open('config.json')
config = json.load(f)

def connect(username, passwd):
	r = requests.post("https://leekwars.com/api/farmer/login", data={'login': username, 'password':passwd, 'keep_connected': 'true'})
	if r.status_code == 200:
		token = r.cookies.get('token')
		phpsessid = r.cookies.get('PHPSESSID')
		farmer = r.json()['farmer']
		cookies = r.cookies
		headers = r.headers
		if token is None or cookies is None:
			raise Exception("[-] Unable to connect. Aborted.")
		print("[+] Token and cookies retrieved.")
		return farmer, token, phpsessid, cookies, headers

def processLeek(id, cookies):
	garden_r = requests.get("https://leekwars.com/api/garden/get", cookies=cookies)
	garden = garden_r.json()['garden']

	if garden['fights'] == 0:
		print("You have no fight remaining for this leek !")
		return
	
	print("You have " + str(garden['max_fights']) + " fights available !")

	while garden['fights'] > 0:
		opponents_r = requests.get("https://leekwars.com/api/garden/get-leek-opponents/" + id, cookies=cookies)
		opponents = opponents_r.json()["opponents"]
		opponent = opponents[0]

		time.sleep(config["fight"]["cooldown"])

		print("Fighting against " + opponent["name"] + " leek ! (id: "+ str(opponent['id']) +")")
		r = requests.post("https://leekwars.com/api/garden/start-solo-fight", data = {'leek_id': str(id), 'target_id': str(opponent['id'])}, cookies=cookies)
		print(r.json())
		garden['fights'] -= 1



login = config["auth"]["username"]
passwd = config["auth"]["password"]

headers = {'Authorization': "Bearer $"}

try:
	if login == "":
		login = input("Username: ")

	if passwd == "":
		passwd = getpass.getpass(prompt='Password: ')

except Exception as error:
	print('ERROR', error)
	exit(1)

# connexion
print("Connection...")
farmer, token, phpsessid, cookies, headers = connect(login, passwd)

cookies = {'token':token, 'PHPSESSID':phpsessid}

print("Welcome back " + farmer["name"] + " !")

if config["fight"]["cooldown"] < 0.5:
	config["fight"]["cooldown"] = 0.5
	print("[WARN] cooldown setting set under minimum requirement (0.5). Default settings used instead")

for index, leek in enumerate(farmer["leeks"]):
	print("processing leek " + farmer["leeks"][leek]["name"])
	processLeek(leek, cookies)