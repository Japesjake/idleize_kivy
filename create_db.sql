CREATE TABLE IF NOT EXISTS Player (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE,
    password BLOB NOT NULL,
    start_date TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS Item (
    item_id INTEGER PRIMARY KEY,
    item_name VARCHAR(255) NOT NULL UNIQUE,
    category_id INTEGER NOT NULL,
    difficulty INTEGER NOT NULL,
    xp_reward INTEGER NOT NULL,
    FOREIGN KEY (category_id) REFERENCES Category(category_id)
);

CREATE TABLE IF NOT EXISTS PlayerItem (
    player_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    count INTEGER DEFAULT 0,
    PRIMARY KEY (player_id, item_id),
    FOREIGN KEY (player_id) REFERENCES Player(player_id),
    FOREIGN KEY (item_id) REFERENCES Item(item_id)
);

CREATE TABLE IF NOT EXISTS Category (
    category_id INTEGER PRIMARY KEY,
    category_name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS PlayerXP (
    player_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    xp INTEGER DEFAULT 0,
    PRIMARY KEY (player_id, category_id)
    FOREIGN KEY (player_id) REFERENCES Player(player_id),
    FOREIGN KEY (category_id) REFERENCES Category(category_id)
);

CREATE TABLE IF NOT EXISTS Recipe (
    product_item_id INTEGER,
    ingredient_item_id INTEGER,
    amount INTEGER,
    FOREIGN KEY (product_item_id) REFERENCES Item(item_id),
    FOREIGN KEY (ingredient_item_id) REFERENCES Item(item_id)
    PRIMARY KEY (ingredient_item_id, product_item_id)
)