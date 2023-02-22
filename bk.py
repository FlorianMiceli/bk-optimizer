import requests
import json


'''Get the coordinates of an entered adress'''
def getCoordinates(address):
    URL = f"https://api-adresse.data.gouv.fr/search/?q={address}"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    r = requests.get(URL, headers=headers)
    data = r.json()
    if not 'features' in data.keys() or not len(data['features']):
        raise Exception("Adresse incroyablement inconnue.")
    lon, lat = data['features'][0]['geometry']['coordinates']
    return lon, lat

'''Get the ID of the nearest Burger King'''
def getNearestBkId(lon, lat, radius):
    URL = 'https://webapi.burgerking.fr/blossom/api/v12/public/store-locator/search'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    r = requests.get(URL, params={'lat': lat, 'lng': lon, 'radius': radius, 'limit': 1}, headers=headers)
    data = r.json()
    if not len(data['results']):
        raise Exception(f'Aucun Burger King dans un rayon de {radius/1000}km.')
    nearest_bk_id = data['results'][0]['id']
    return nearest_bk_id

'''Get the menu of the nearest Burger King'''
def getProductsAndMenus(nearest_bk_id):
    URL = f'https://ecoceabkstorageprdnorth.blob.core.windows.net/catalog/catalog.{nearest_bk_id}.json'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    r = requests.get(URL, headers=headers)
    data = r.json()
    list_products = data['products']
    list_menus = data['menus']
    return list_products, list_menus

'''Get list of products and menus of the nearest Burger King from location'''
def getProductsAndMenusFromLocation(location,radius):
    lon, lat = getCoordinates(location)
    list_products, list_menus = getProductsAndMenus(getNearestBkId(lon,lat,radius))
    return list_products, list_menus

'''Get the products' routeIds in a menu'''
def getMenu(routeID, list_menus, list_products):
    menu = [m for m in list_menus if m['routeId'] == routeID][0]
    products = [p['productIds'] for p in menu['steps']]
    productsRouteIDs = []
    for i in range(len(menu['steps'])):
        productsRouteIDs.append([r['routeId'] for r in list_products if r['id'] in products[i]])
    return productsRouteIDs


# ratio
def OLDgetRatios():
    crownProducts = updateCrownProducts()
    ratios = {}
    exceptions = []
    for routeID in crownProducts:
        routeIDwords = routeID.split('-')
        words_nbr = len(routeIDwords)
        sepator = '-'
        error = True
        # while we can't get the ratio, remove a word from the routeID
        while error == True:
            try:
                routeIDtemp = sepator.join(routeIDwords[:words_nbr])
                try :
                    cal = getMaxCal(routeIDtemp)[routeIDtemp]
                except:
                    print(routeIDtemp)
                    print('EST PASSE ICI --------------------------')
                    print(getMaxCal(routeIDtemp).values())
                    print(sum(getMaxCal(routeIDtemp).values()))
                    cal = sum(getMaxCal(routeIDtemp).values())
                ratios[routeID] = int(cal) / int(crownProducts[routeID])
                error = False
            except:
                words_nbr = words_nbr - 1
                if words_nbr == 0:
                    exceptions.append(routeID)
                    error = False
    return ratios,exceptions


