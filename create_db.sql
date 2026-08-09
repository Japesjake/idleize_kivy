CREATE TABLE IF NOT EXISTS Player (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(255) NOT NULL UNIQUE,
    password BLOB NOT NULL,
    start_date TEXT DEFAULT (datetime('now'))
);

DROP TABLE Item;

CREATE TABLE IF NOT EXISTS Item (
    item_id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    category_id INTEGER,
    difficulty INTEGER,
    xp_reward INTEGER,
    FOREIGN KEY (category_id) REFERENCES Category(category_id)
);

DROP TABLE Category;

CREATE TABLE IF NOT EXISTS Category (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) UNIQUE
);

CREATE TABLE IF NOT EXISTS Inventory (
    player_id INTEGER NOT NULL,
    item_id TEXT NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (player_id, item_id),
    FOREIGN KEY (player_id) REFERENCES Player(player_id),
    FOREIGN KEY (item_id) REFERENCES Item(item_id)
);