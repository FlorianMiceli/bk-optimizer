import json

def ratioCrownsPrice():
    with open('crowns.json', 'r') as f:
        crowns = json.load(f)
    with open('productPrices.json', 'r') as f:
        prices = json.load(f)
    ratio = {}
    for product in prices:
        if product in crowns:
            ratio[product] = prices[product]/crowns[product]

    # sort by value
    ratio = {k: v for k, v in sorted(ratio.items(), key=lambda item: item[1])}
    # make a list with names and values
    ratio = [[k,v] for k,v in ratio.items()]
    #transform values to grades /20
    for i in range(len(ratio)):
        ratio[i][1] = (ratio[i][1]/ratio[-1][1])*20
    return ratio

ratio = ratioCrownsPrice()

print(ratio)

