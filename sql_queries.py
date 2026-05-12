import sqlite3

try:
    with sqlite3.connect('data.db') as connection:
        cursor = connection.cursor()
except sqlite3.Error: print('error connecting to database')

cursor.execute("""
               SELECT ingredient_item_id, amount)
               FROM Recipe
               WHERE product_item_id = (SELECT item_id FROM Item WHERE item_name = 'copper arrow')
               """)

ingredients = cursor.fetchall()
print(ingredients)

cursor.execute("""
                    SELECT r.ingredient_item_id, r.amount, i.item_name 
                    FROM Recipe r 
                    JOIN Item i ON r.ingredient_item_id = i.item_id
                    WHERE r.product_item_id = (SELECT item_id FROM Item WHERE item_name = ?)
                """, ('copper arrow',))
ingredients = cursor.fetchall()
print(ingredients)

# sql = "SELECT Category.category_name, PlayerXP.xp FROM PlayerXP JOIN Category ON PlayerXP.category_id = Category.category_id JOIN Player ON PlayerXP.player_id = player.player_id WHERE Player.name = 'JpJab';"
# cursor.execute(sql)
# print(cursor.fetchall())


# sql = "SELECT count FROM PlayerItem, Item, Player WHERE PlayerItem.item_id = (SELECT crafts_from_item_id FROM Item WHERE item_name = ?) AND PlayerItem.player_id = (SELECT player_id FROM Player WHERE Player.name = ?)"
# cursor.execute(sql, ('copper ingot', 'JpJab'))
# print(cursor.fetchall())

# sql = "SELECT crafts_from_item_id FROM Item WHERE Item.item_name = ?"
# cursor.execute(sql,('copper ingot',))
# print(cursor.fetchall())

# sql = "SELECT Item.item_name, PlayerItem.count FROM PlayerItem JOIN Player ON PlayerItem.player_id = Player.player_id JOIN Item ON PlayerItem.item_id = Item.item_id WHERE Player.name = ?;"
# cursor.execute(sql,('JpJab',))
# msg = cursor.fetchall()
# print(msg)

# sql = "UPDATE PlayerItem SET count = 1 WHERE player_id = 1 AND item_id = 1"
# cursor.execute(sql)
# connection.commit()

# def create_db():
#     with open("create_db.sql", "r") as sql_file:
#         sql_script = sql_file.read()
#     cursor.executescript(sql_script)
#     connection.commit()
#     connection.close()
# create_db()

# cursor.execute("INSERT INTO Item (item_name) VALUES ('copper ore');")
# connection.commit()
# connection.close()

# cursor.execute("INSERT INTO Player (name) VALUES ('DC');")
# connection.commit()
# connection.close()

# cursor.execute("INSERT INTO PlayerItem (player_id, item_id, count) VALUES (1,2,0);")
# connection.commit()
# connection.close()

# cursor.execute("SELECT P.name, I.item_name FROM PlayerItem PI JOIN Player P ON P.player_id = PI.player_id JOIN Item I ON I.item_id = PI.item_id WHERE p.name = 'JpJab';")
# cursor.execute("SELECT * FROM item")
# print(cursor.fetchall())
# connection.close()

# cursor.execute('ALTER TABLE PlayerItem ADD COLUMN count INTEGER')
# connection.commit()
# connection.close()

# with sqlite3.connect('data.db') as db_connection:
#     cursor = db_connection.cursor()
#     cursor.execute('SELECT player_id FROM Player WHERE name = ?;',('JpJab',))
#     print(cursor.fetchall()[0][0])