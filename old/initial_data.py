thresholds = (100,500,3000,10000)
xps = {'mining':0,'smelting':0,'crafting':0}
groups = {'mining':('copper ore', 'iron ore'),'smelting':('copper ingot', 'iron ingot'),'crafting':('copper armor','iron armor')}
amounts = {'copper ingot':1,'iron ingot':1,'copper armor':5,'iron armor':5}
relationships = {'copper ore': None,'iron ore': None,'copper ingot': 'copper ore', 'iron ingot': 'iron ore', 'copper armor': 'copper ingot', 'iron armor': 'iron ingot'}
data = {'copper ore': 0,'iron ore': 0,'copper ingot': 0, 'iron ingot': 0, 'copper armor': 0, 'iron armor': 0}

initial_data = {'thresholds': thresholds, 'xps': xps, 'groups': groups, 'amounts': amounts, 'relationships': relationships, 'data': data}