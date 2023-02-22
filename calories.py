import requests
import json

from bk import getProductsAndMenusFromLocation

'''Update the calories.json file with the latest data from BK API'''
def updateProductCalories(list_products):
    with open('data/calories.json', 'w') as f:
        cal_dict = {}
        for products in list_products:
            try:
                routeId = products['routeId']
                URL = f'https://webapi.burgerking.fr/blossom/api/v12/public/produit/{routeId}'
                headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                r = requests.get(URL, headers=headers)
                data = r.json()
                # print(routeId)
                if data['product']['nutrition'] != []:
                    cal_dict[routeId] = int(data['product']['nutrition'][0]['portion'])
                else:
                    print(routeId,'has no calories')
                    cal_dict[routeId] = 0
            except:
                print('pb with',routeId)
        json.dump(cal_dict,f)

'''Get the calories of a product from the calories.json file'''
def getCalProduct(routeID, calories): 
    return calories[routeID]

'''Get the max calories of a menu from the calories.json file and the getMenu function'''
#WIP

def OLDgetMaxCal(routeID):
    # product
    cal_choices = {}
    try : 
        URL = f'https://webapi.burgerking.fr/blossom/api/v12/public/produit/{routeID}'
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        r = requests.get(URL, headers=headers)
        data = r.json()
        if data['product']['nutrition'] != []:
            cal_choices[routeID] = data['product']['nutrition'][0]['portion']
        else:
            print(routeID,'has no calories')
            cal_choices[routeID] = 0
    # menu
    except:
        productsRouteIDs = getMenu(routeID)
        cal_choices = {}
        # get max cal for each list in productsRouteIDs and sum them : 
        cal = 0
        cal_choices = []
        for step in productsRouteIDs:
            choice = {}
            productRouteID = ''
            max_cal = 0
            for product in step:
                # print('.')
                cal = int(getMaxCal(product)[product])
                if cal > max_cal:
                    max_cal = cal
                    productRouteID = product
            choice[productRouteID] = max_cal
            cal_choices.append(choice)
    return cal_choices

list_products,list_menus = getProductsAndMenusFromLocation('Orsay',50000)

updateProductCalories(list_products)