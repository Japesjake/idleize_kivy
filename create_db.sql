CREATE TABLE Player (
    player_id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    start_date TEXT DEFAULT (datetime('now')),
    address INTEGER
);

CREATE TABLE Item (
    item_id INTEGER PRIMARY KEY,
    item_name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE PlayerItem (
    player_id INT NOT NULL,
    item_id INT NOT NULL,
    count INT,
    PRIMARY KEY (player_id, item_id),
    FOREIGN KEY (player_id) REFERENCES Player(player_id),
    FOREIGN KEY (item_id) REFERENCES Item(item_id)
);