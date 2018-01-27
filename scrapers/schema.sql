DROP TABLE IF EXISTS urls;
CREATE TABLE urls (
       id INTEGER PRIMARY KEY autoincrement,
       url TEXT UNIQUE NOT NULL,
       scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       Created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
