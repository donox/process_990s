CREATE TABLE IF NOT EXISTS investments (
    id SERIAL PRIMARY KEY,
    return_id INT REFERENCES return(returnid) ON DELETE CASCADE, -- Foreign key to `returns`
    stock_name VARCHAR(255), -- Name of the stock
    eoy_book_value BIGINT, -- End of Year Book Value
    eoy_fmv BIGINT -- End of Year Fair Market Value
);
