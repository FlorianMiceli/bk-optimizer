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
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36','authorization' :AUTH_TOKEN}
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
    cal_choices = {}
    try : 
        URL = f'https://webapi.burgerking.fr/blossom/api/v12/public/produit/{routeID}'
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        r = requests.get(URL, headers=headers)
        data = r.json()
        if data['product']['nutrition'] != []:
            cal_choices[routeID] = data['product']['nutrition'][0]['portion']
        else:
            # print(routeID,'has no calories')
            cal_choices[routeID] = 0
    # menu
    except:
        productsRouteIDs = getAvailableInMenu(routeID)
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

'''Needs to be global'''
lon, lat = getCoordinates('Orsay')
radius = 50000
list_products, list_menus = getProductsAndMenus(getNearestBkId(lon,lat,radius))

# print(getProductsAndMenus(getNearestBkId(lon,lat,radius)))
# print(getMaxCal('cheeseburger-')) #305


# print(getMaxCal('big-king')) 
#verif si getratios marche

# print(getAvailableInMenu('kingdom-menu-whopper'))
# print('meilleur combinaison pr un max de calories :',getMaxCal('kingdom-menu-whopper'))

# print(getCrownProducts())


# ratios,exceptions = getRatios()
# print('Meilleur rapport calories/couronnes :')
# print(max(ratios, key=ratios.get),'qui contient',list(getMaxCal(max(ratios, key=ratios.get)))[0],'calories et coûte',getCrownProducts()[max(ratios, key=ratios.get)],'couronnes')
# print('Pire rapport calories/couronnes :')
# print(min(ratios, key=ratios.get),'qui contient',list(getMaxCal(min(ratios, key=ratios.get)))[0],'calories et coûte',getCrownProducts()[min(ratios, key=ratios.get)],'couronnes')
# print("Les éléments dont les calories n'ont pas pu être récupérées sont :")
# print(exceptions)