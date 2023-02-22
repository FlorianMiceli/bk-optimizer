import requests
import json

from bk import getProductsAndMenusFromLocation

list_products,list_menus = getProductsAndMenusFromLocation('Orsay',50000)

'''Update the json file with product prices'''
def updateProductPrices():
    with open('data/productPrices.json', 'w') as f:
        prices = {}
        for product in list_products:
            prices[product['routeId']] = product['price']
        json.dump(prices,f)

'''Update the json file with menu prices'''
def updateMenuPrices():
    with open('data/menuPrices.json', 'w') as f:
        prices = {}
        for menu in list_menus:
            prices[menu['routeId']] = menu['price']
        json.dump(prices,f)

updateProductPrices()
updateMenuPrices()