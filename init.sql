-- connect to default database (postgres)
\connect postgres

-- drop the old db if it exists
DROP DATABASE IF EXISTS stock_pipeline;

-- create a fresh database
CREATE DATABASE stock_pipeline;

-- connect to your new database to create tables
\connect stock_pipeline

-- create your raw_stock_prices table
CREATE TABLE raw_stock_prices (
    date DATE NOT NULL,
    open NUMERIC,
    high NUMERIC,
    low NUMERIC,
    close NUMERIC,
    volume BIGINT,
    symbol VARCHAR(10) NOT NULL,
    PRIMARY KEY (date, symbol)
);
