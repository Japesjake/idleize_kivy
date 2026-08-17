### id, name, category, difficulty, xp_reward, sort order
import random
server_version = random.randint(5,1000)
# server_version = 589

items = [
    ('copper ore','Copper Ore','mining', 1, 1,1),
    ('iron ore','Iron Ore','mining', 5, 2,2),
    ('adamant ore', 'Adamant Ore','mining', 20, 5, 3),

    ('copper ingot','Copper Ingot','smelting', 1, 1,1),
    ('iron ingot', 'Iron Ingot','smelting',5,1,2),

    ('carrot','Carrot','gathering', 1, 1,1),
    ('wood','Wood', 'gathering', 1, 1, 2),
    ('stick','Stick','gathering', 1, 1, 3),
    
    ('copper sword','Copper Sword','crafting',1,1,1),
    ('iron sword', 'Iron Sword', 'crafting',5,1,2)
]
categories = [
    ('mining',1),
    ('smelting',2),
    ('gathering',3),
    ('crafting',4)
]

### item, required_item, required_quantity
recipes = [
    ('copper ingot', 'copper ore', 2),
    ('iron ingot', 'iron ore', 2),
    ('copper sword', 'copper ingot', 3),
    ('iron sword', 'iron ingot', 3),
]