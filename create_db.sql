CREATE TABLE IF NOT EXISTS Player (
    player_id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    start_date TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS Item (
    item_id INTEGER PRIMARY KEY,
    item_name VARCHAR(255) NOT NULL UNIQUE,
    crafts_from_item_id INT,
    crafts_from_amount INT,
    FOREIGN KEY (crafts_from_item_id) REFERENCES Item(item_id)
);

CREATE TABLE IF NOT EXISTS PlayerItem (
    player_id INT NOT NULL,
    item_id INT NOT NULL,
    count INTEGER DEFAULT 0,
    PRIMARY KEY (player_id, item_id),
    FOREIGN KEY (player_id) REFERENCES Player(player_id),
    FOREIGN KEY (item_id) REFERENCES Item(item_id)
);