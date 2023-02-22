import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()
AUTH_TOKEN = os.environ['AUTH_TOKEN']

'''Update the json file containing the products avaible with each crown price'''
def updateCrownProducts(AUTH_TOKEN):
    URL = 'https://webapi.burgerking.fr/blossom/api/v12/kingdom/points'
    headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36','authorization':AUTH_TOKEN}
    r = requests.get(URL, headers=headers)
    data = r.json()
    # save json
    with open('data/crowns.json', 'w') as f:
        crownProducts = {}
        for level in data['levels']:
            for offer in level['offers']:
                crownProducts[offer['routeId']] = level['minPoints']
        json.dump(crownProducts,f)

updateCrownProducts(AUTH_TOKEN)