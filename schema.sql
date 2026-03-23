CREATE TABLE categories(
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL
);

CREATE TABLE transactions(
    t_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    t_date DATETIME,
    type TEXT CHECK(type IN('cr', 'db')),
    category_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    FOREIGN KEY (category_id) REFERENCES categories(categories_id)
);