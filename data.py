data = {'copper ore': 0,
        'iron ore': 0,
        'copper ingot': 0,
        'iron ingot': 0,
        'copper armor': 1, 
        'iron armor': 1, 
        'wood': 0, 
        'stick':0, 
        'copper arrow': 0,
        'copper sword': 1,
        'iron sword': 1,
        'bow': 1}
xps = {'mining': 0, 
       'smelting': 0, 
       'crafting': 0, 
       'gathering': 0}
groups = {'mining': ('copper ore', 'iron ore'),
          'smelting': ('copper ingot', 'iron ingot'),
          'crafting': ('copper armor', 'iron armor', 'copper arrow'), 
          'gathering':('wood', 'stick')}
recipies = {'copper ingot': {'copper ore': 1}, 
            'iron ingot': {'iron ore': 1}, 'copper armor': {'copper ingot': 1}, 
            'iron armor': {'iron ingot': 1}, 
            'stick': {'wood': 1}, 
            'copper arrow': {'copper ingot': 1, 'stick': 1}}
xp_values = {'copper ore': 1, 
             'iron ore': 2, 
             'copper ingot': 1, 
             'iron ingot': 2, 
             'copper armor': 1, 
             'iron armor': 2, 
             'wood':1, 
             'stick':1, 
             'copper arrow': 1}
difficulties = {'copper ore': 1, 
                'iron ore': 500, 
                'copper ingot': 1, 
                'iron ingot': 500, 
                'copper armor': 1, 
                'iron armor': 500, 
                'wood': 1,
                'stick': 1, 
                'copper arrow': 1}
enemies = {
    'rat': {'hp': 5, 'attack': 1, 'defense': 1}
}
hps = {
    'player': 10,
    'rat': 5
}
player_stats = {
    'hp': 10,
    'strength': 1,
    'dexterity': 1,
    'defense': 1,
    'max hp': 10,
    'armor type': 'strength',
}

equipment_stats = {
    'copper armor': 1,
    'copper sword': 1,
    'bow': 1
}

equipped = {
    'body': '',
    'right': ''
}

equippables = {
    'copper armor': 'strength', 
    'iron armor': 'strength',
    'copper sword': 'strength', 
    'iron sword': 'strength',
    'leather armor': 'dexterity',
    'bow': 'dexterity'
}