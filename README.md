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





Necesito un archivo html, para una aplicación web hecha con flask, que muestre la información de los clientes (desde la tabla cliente).
La información tiene que estar en una tabla que muestre la información relevante como nombre, apellido, telefono, dirección. 
Puedes generar paginación para esta tabla un buscador interactivo, poner las letras del nombre ya debería empezar a buscar.
Tengo una ruta flask: 


@app.route('/client/')
def mostrar_cliente(user_id):
    if request.method == 'GET':
    
        clients = Client.get_by_user(user_id)

        return render_template('clients.html', clients=clients)

Y el metodo que traae la información de la tabla es el siguiente: 

   def get_by_user(cls):
        """
        Finds all clients in the database for the current user.

        Returns:
            A list of all client objects for the current user.
        """
        try:
            user_id = session.get('user_id')
            if user_id is None:
                raise ValueError("User ID not found in session.")

            connection = connect_to_mysql()
            if not connection:
                raise ConnectionError("Could not connect to the database.")

            cursor = connection.cursor()

            cursor.execute(
                "SELECT * FROM client WHERE user_id = %s",
                (user_id,)
            )

            results = cursor.fetchall()

            clients = []
            for result in results:
                client = cls(*result)
                clients.append(client)
            return clients

        except Exception as e:
            # Consider logging the error for better traceability
            print(f"Error fetching clients for user {user_id}: {e}")
            return None
        finally:
            if connection:
                connection.close()
            
La tabla client: 

desc client;
+-----------------+--------------+------+-----+---------+----------------+
| Field           | Type         | Null | Key | Default | Extra          |
+-----------------+--------------+------+-----+---------+----------------+
| id              | int(11)      | NO   | PRI | NULL    | auto_increment |
| client_name     | varchar(255) | NO   |     | NULL    |                |
| client_email    | varchar(255) | NO   |     | NULL    |                |
| client_phone    | varchar(20)  | NO   |     | NULL    |                |
| client_address  | varchar(255) | NO   |     | NULL    |                |
| client_lastname | varchar(200) | YES  |     | NULL    |                |
| client_company  | varchar(200) | YES  |     | NULL    |                |
| user_id         | int(11)      | YES  | MUL | NULL    |                |
+-----------------+--------------+------+-----+---------+----------------+

Y utiliza jinja para el html para que este contenido coinsida con el template a continuación:






<div class="col-12 col-md-6">
                        <div class="card border-light-subtle shadow-sm">
                            <div class="card-body p-3 p-md-4 p-xl-5">
                                <div class="row">
                                    <div class="col-12">
                                        <div class="mb-5">
                                            <h2 class="h4 text-center">User Bank Information</h2>
                                        </div>
                                    </div>
                                </div>
                                <div class="row gy-3 overflow-hidden">
                                    <div class="col-12">
                                        <div class="form-floating mb-3">
                                            <input type="number" class="form-control" name="abn" id="abn" placeholder="ABN" required>
                                            <label for="abn" class="form-label">ABN</label>
                                        </div>
                                        <div class="form-floating mb-3">
                                            <input type="text" class="form-control" name="bank" id="bank" placeholder="Bank" required>
                                            <label for="bank" class="form-label">Bank</label>
                                        </div>
                                        <div class="form-floating mb-3">
                                            <input type="text" class="form-control" name="account_name" id="account_name" placeholder="Account Name" required>
                                            <label for="account_name" class="form-label">Account Name</label>
                                        </div>
                                        <div class="form-floating mb-3">
                                            <input type="number" class="form-control" name="bsb" id="bsb" placeholder="BSB" required>
                                            <label for="bsb" class="form-label">BSB</label>
                                        </div>
                                        <div class="form-floating mb-3">
                                            <input type="number" class="form-control" name="account_number" id="account_number" placeholder="Account Number" required>
                                            <label for="account_number" class="form-label">Account Number</label>
                                        </div>

                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>