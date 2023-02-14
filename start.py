import requests

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
    nearest_bk_id = getNearestBkId(lon,lat,radius)
    URL = f'https://ecoceabkstorageprdnorth.blob.core.windows.net/catalog/catalog.{nearest_bk_id}.json'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    r = requests.get(URL, headers=headers)
    data = r.json()
    list_products = data['products']
    list_menus = data['menus']
    # max_price = max([int(p['price']) for p in list_products if p['available'] and p['active']])
    # print([(p['name'], p['price']) for p in list_products if p['price'] == max_price and p['available'] and p['active']])
    return list_products, list_menus

'''Get the proucts in a menu'''
def getAvailableInMenu(routeID):
    menu = [m for m in list_menus if m['routeId'] == routeID][0]
    products = [p['productIds'] for p in menu['steps']]
    productsRouteIDs = []
    for i in range(len(menu['steps'])):
        productsRouteIDs.append([r['routeId'] for r in list_products if r['id'] in products[i]])
    return productsRouteIDs

'''Get the calories/crowns ratio of the nearest Burger King'''
# crowns 
def getCrownProducts():
    URL = 'https://webapi.burgerking.fr/blossom/api/v12/kingdom/points'
    AUTH_TOKEN = ''
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36','authorization' : AUTH_TOKEN}
    r = requests.get(URL, headers=headers)
    data = r.json()
    # save json
    # with open('data.json', 'w') as f:
    #     f.write(r.text)
    crownProducts = {}
    for level in data['levels']:
        for offer in level['offers']:
            crownProducts[offer['routeId']] = level['minPoints']
    return crownProducts

# calories
def getMaxCal(routeID):
    # product
    try : 
        URL = f'https://webapi.burgerking.fr/blossom/api/v12/public/produit/{routeID}'
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        r = requests.get(URL, headers=headers)
        data = r.json()
        cal = data['product']['nutrition'][0]['portion']
    # menu
    except:
        productsRouteIDs = getAvailableInMenu(routeID)
        # get max cal for each list in productsRouteIDs and sum them : 
        # cal = 
    return cal

# ratio
def getRatios():
    crownProducts = getCrownProducts()
    ratios = {}
    exceptions = []
    for routeID in crownProducts:
        routeIDwords = routeID.split('-')
        words_nbr = len(routeIDwords)
        sepator = '-'
        error = True
        while error == True:
            try:
                routeIDtemp = sepator.join(routeIDwords[:words_nbr])
                cal = getMaxCal(routeIDtemp)
                ratios[routeID] = int(cal) / int(crownProducts[routeID])
                error = False
            except:
                words_nbr = words_nbr - 1
                if words_nbr == 0:
                    exceptions.append(routeID)
                    error = False
    return ratios,exceptions

'''Needs to be global'''
lon, lat = getCoordinates('Le Havre')
radius = 50000
list_products, list_menus = getProductsAndMenus(getNearestBkId(lon,lat,radius))




# print(getProductsAndMenus(getNearestBkId(lon,lat,radius)))
# print(getMaxCal('cheeseburger-')) #305

print(getAvailableInMenu('kingdom-menu-whopper'))

# ratios,exceptions = getRatios()
# print('Meilleur rapport calories/couronnes :')
# print(max(ratios, key=ratios.get),'qui contient',getMaxCal(max(ratios, key=ratios.get)),'calories et coûte',getCrownProducts()[max(ratios, key=ratios.get)],'couronnes')
# print('Pire rapport calories/couronnes :')
# print(min(ratios, key=ratios.get),'qui contient',getMaxCal(min(ratios, key=ratios.get)),'calories et coûte',getCrownProducts()[min(ratios, key=ratios.get)],'couronnes')
# print("Les éléments dont les calories n'ont pas pu être récupérées sont :")
# print(exceptions)