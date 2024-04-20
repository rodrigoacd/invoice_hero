# invoice_hero

## create a new enviroment
python3 -m venv venv

## access to the environment
python3 -m venv venv

## Ativate the environment
source venv/bin/activate

## install requirements 
pip install flask




## database

create database invoice;
use  invoice;

CREATE USER 'hero'@'localhost' IDENTIFIED BY 'hero123';
GRANT ALL PRIVILEGES ON invoice.* TO 'hero'@'localhost';
FLUSH PRIVILEGES;

DROP TABLE IF EXISTS invoice_items;
DROP TABLE IF EXISTS invoices;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS client;

CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            phone VARCHAR(20) NOT NULL,
            abn VARCHAR(20) NOT NULL,
            bank VARCHAR(255) NOT NULL,
            account_name VARCHAR(255) NOT NULL,
            bsb VARCHAR(20) NOT NULL,
            account_number VARCHAR(255) NOT NULL
        );


CREATE TABLE IF NOT EXISTS invoices (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            invoice_number INT NOT NULL,
            invoice_date DATE NOT NULL,
            date_due DATE NOT NULL,
            date_sent DATE,
            date_paid DATE,
            status VARCHAR(255) NOT NULL,
            address VARCHAR(255) NOT NULL,
            client_id INT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (client_id) REFERENCES client (id)
        );

CREATE TABLE IF NOT EXISTS invoice_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            invoice_id INT NOT NULL,
            item_name VARCHAR(255) NOT NULL,
            quantity INT NOT NULL,
            date datetime NOT NULL,
            rate DECIMAL(10,2) NOT NULL,
            FOREIGN KEY (invoice_id) REFERENCES invoices (id)
        );

CREATE TABLE IF NOT EXISTS client (
            id INT AUTO_INCREMENT PRIMARY KEY,
            client_name VARCHAR(255) NOT NULL,
            client_email VARCHAR(255) NOT NULL,
            client_phone VARCHAR(20) NOT NULL,
            client_address VARCHAR(255) NOT NULL
    );



insert into client (client_name, client_email, client_phone, client_address)values ("mrdata", "mrdata@gmail.com", 987654321, "222 Harry st, Ultimo");