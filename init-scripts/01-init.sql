CREATE TABLE IF NOT EXISTS user_reviews (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    rating INT NOT NULL,
    recommendations TEXT
);