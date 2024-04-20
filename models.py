from db import connect_to_mysql
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session


class User:

    def __init__(self,user_id, username, password, email = None, phone = None, abn = None, bank = None, account_name = None, bsb = None, account_number = None):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.email = email
        self.phone = phone
        self.abn = abn
        self.bank = bank
        self.account_name = account_name
        self.bsb = bsb
        self.account_number = account_number



    @classmethod
    def create(cls, username, password, email, phone, abn, bank, account_name, bsb, account_number):
        """
        Creates a new user in the database.

        Args:
            username: The username of the new user.
            password: The password of the new user.

        Returns:
            The newly created user object, or None if creation failed.
        """
        try:
            connection = connect_to_mysql()
            if not connection:
                return None

            cursor = connection.cursor()

            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

            cursor.execute(
                "INSERT INTO users (username, password, email, phone, abn, bank, account_name, bsb, account_number ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (username, hashed_password, email, phone, abn, bank, account_name, bsb, account_number)
            )
            connection.commit()
            
            user_id = cursor.lastrowid
            

            user = cls(user_id, username, hashed_password)
            return user
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
        finally:
            if connection:
                connection.close()

    @classmethod
    def find_by_username(cls, username):
        """
        Finds a user by their username.

        Args:
            username: The username of the user to find.

        Returns:
            The user object if found, otherwise None.
        """
        try:
            connection = connect_to_mysql()
            if not connection:
                return None

            cursor = connection.cursor()

            cursor.execute(
                "SELECT * FROM users WHERE username = %s",
                (username,)
            )
            result = cursor.fetchone()
            print(result)
            if result:
                user = cls(*result)
                return user
            else:
                return None
        except Exception as e:
            print(f"Error finding user by username: {e}")
            return None
        finally:
            if connection:
                connection.close()

    def check_password(self, password):
        """
        Checks if the given password is correct for this user.

        Args:
            password: The password to check.

        Returns:
            True if the password is correct, False otherwise.
        """
        return check_password_hash(self.password, password)
    
    @classmethod
    def get_current_user(cls):
        user_id = session.get('user_id')
        if user_id:
            return cls.find_by_id(user_id)
        else:
            return None


class Invoice:

    def __init__(self, invoice_id, user_id, invoice_number, invoice_date, date_due, client_id, address, status ):
        self.invoice_id = invoice_id
        self.user_id = user_id
        self.invoice_number = invoice_number
        self.invoice_date = invoice_date
        self.date_due = date_due
        self.client_id = client_id
        self.address = address
        self.status = status

    @classmethod
    def create(cls, invoice_number, user_id, client_id, address):
        
        """
        Creates a new invoice in the database.

        Args:
            user_id: The ID of the user who created the invoice.
            date_sent: The date the invoice was sent.
            status: The status of the invoice.

        Returns:
            The newly created invoice object, or None if creation failed.
        """
        try:
            connection = connect_to_mysql()
            if not connection:
                return None

            cursor = connection.cursor()

            cursor.execute(
                "INSERT INTO invoices (user_id, invoice_number, invoice_date, date_due, status, address,client_id ) VALUES (%s, %s, now(), DATE(DATE_ADD(now(), INTERVAL 30 DAY)), 'created', %s, %s)",
                (user_id, invoice_number, address, client_id)
            )

            connection.commit()

            invoice_id = cursor.lastrowid
            
            invoice = invoice_id

            return invoice
        except Exception as e:
            print(f"Error creating invoice: {e}")
            return None
        finally:
            if connection:
                connection.close()



    @classmethod
    def find_by_id(cls, invoice_id):
        """
        Finds an invoice by its ID.

        Args:
            invoice_id: The ID of the invoice to find.

        Returns:
            The invoice object if found, otherwise None.
        """
        try:
            connection = connect_to_mysql()
            if not connection:
                return None

            cursor = connection.cursor()

            cursor.execute(
                """ select 
                        i.id as invoice_id, i.user_id, i.invoice_number, 
                        i.invoice_date, i.date_due, i.date_sent, i.date_paid, 
                        i.status, i.address as invoice_address, i.client_id, 
                        c.client_name, c.client_email, c.client_phone
                    from invoices i 
                    inner join client c 
                    on i.client_id = c.id 
                    WHERE i.id = %s
                """,
                (invoice_id,)
            )
            result = cursor.fetchone()
            if result:
                return {
                    'invoice_id': result[0],
                    'user_id': result[1],
                    'invoice_number': result[2],
                    'invoice_date': result[3],
                    'date_due': result[4],
                    'date_sent': result[5],
                    'date_paid': result[6],
                    'status': result[7],
                    'invoice_address': result[8],
                    'client_id': result[9],
                    'client_name': result[10],
                    'client_email': result[11],
                    'client_phone': result[12]                                        
                }
            else:
                print ('Invalid')
                return None
        except Exception as e:
            print(f"Error finding invoice by ID: {e}")
            return None
        finally:
            if connection:
                connection.close()

    @classmethod
    def all_invoice_info_by_id(cls, invoice_id):
        """
        Finds all invoice information by its ID.

        Args:
            invoice_id: The ID of the invoice to find.

        Returns:
            The invoice object if found, otherwise None.
        """
        try:
            connection = connect_to_mysql()
            if not connection:
                return None

            cursor = connection.cursor()

            cursor.execute(
                """ select 
                        i.id as invoice_id, i.user_id, i.invoice_number, 
                        i.invoice_date, i.date_due, i.date_sent, i.date_paid, 
                        i.status, i.address as invoice_address, i.client_id, 
                        c.client_name, c.client_email, c.client_phone,
                        u.username, u.email, u.phone as user_phone, u.abn, u.bank, u.account_name,bsb,account_number,
                        ii.item_name, ii.quantity, ii.date, ii.rate
                    from invoices i 
                    inner join client c 
                    on i.client_id = c.id
                    inner join users u
                    on u.id = i.user_id
                    inner join invoice_items ii
                    on ii.invoice_id = i.id
                    WHERE i.id = %s
                """,
                (invoice_id,)
            )
            results = cursor.fetchall()
            if results:
                columns = [desc[0] for desc in cursor.description]
                result = results[0]
                invoice_info = {column: value for column, value in zip(columns, result)}
                return invoice_info
            else:
                print('Invalid')
                return None
            # result = cursor.fetchone()
            # if result:
            #     return {
            #         'invoice_id': result[0],
            #         'user_id': result[1],
            #         'invoice_number': result[2],
            #         'invoice_date': result[3],
            #         'date_due': result[4],
            #         'date_sent': result[5],
            #         'date_paid': result[6],
            #         'status': result[7],
            #         'invoice_address': result[8],
            #         'client_id': result[9],
            #         'client_name': result[10],
            #         'client_email': result[11],
            #         'client_phone': result[12],
            #         'username': result[13],
            #         'email': result[14],
            #         'user_phone': result[15],
            #         'abn': result[16],
            #         'bank': result[17],
            #         'account_name': result[18],
            #         'bsb': result[19],
            #         'account_number': result[20],

            #     }
            # else:
            #     print ('Invalid')
            #     return None
        except Exception as e:
            print(f"Error finding invoice by ID: {e}")
            return None
        finally:
            if connection:
                connection.close()


    @classmethod
    def find_last_invoice(cls, user_id):
        try:
            connection = connect_to_mysql()
            if not connection:
                return None

            cursor = connection.cursor()

            cursor.execute(
                "SELECT id, user_id, invoice_number, invoice_date, date_due, client_id, address, status  FROM invoices WHERE user_id = %s ORDER BY id DESC LIMIT 1",
                (user_id,)
            )
            result = cursor.fetchone()

            if result:
                return {
                    'invoice_id': result[0],
                    'user_id': result[1],
                    'invoice_number': result[2],
                    'invoice_date': result[3],
                    'date_due': result[4],
                    'client_id': result[5],
                    'address': result[6],
                    'status': result[7]
                }
            else:
                print ('Invalid')
                return None
        except Exception as e:
            print(f"Error finding last invoice: {e}")
            return None
        finally:
            if connection:
                connection.close()

    # find all invoices of one user
    @classmethod
    def get_all_invoices(cls, user_id):
        """
        """
        try:
            connection = connect_to_mysql()
            if not connection:
                return None

            cursor = connection.cursor()

            cursor.execute(
                "SELECT id, user_id, invoice_number, invoice_date, date_due, client_id, address, status  FROM invoices WHERE user_id = %s ORDER BY id DESC ",
                (user_id,)
            )
            results = cursor.fetchall()

            invoices = []
            for result in results:
                invoice = cls(*result)
                invoices.append(invoice)

            return invoices
        except Exception as e:
            print(f"Error finding all clients: {e}")
            return None
        finally:
            if connection:
                connection.close()



    def update(self, date_sent, status):
        """
        Updates the invoice with the given data.

        Args:
            date_sent: The new date sent for the invoice.
            status: The new status for the invoice.
        """
        try:
            connection = connect_to_mysql()
            if not connection:
                return

            cursor = connection.cursor()

            cursor.execute(
                "UPDATE invoices SET date_sent = %s, status = %s WHERE id = %s",
                (date_sent, status, self.id)
            )
            connection.commit()
        except Exception as e:
            print(f"Error updating invoice: {e}")
        finally:
            if connection:
                connection.close()


class Activity:

    def __init__(self, activity_id, activity, date, hours, rate):
        self.activity_id = activity_id
        self.activity = activity
        self.date = date
        self.hours = hours
        self.rate = rate

    @classmethod
    def create(cls, invoice_id, activity, date, hours, rate):
        """
        Creates a new activity in the database.

        Args:
            invoice_id: The ID of the invoice that the activity belongs to.
            activity: The description of the activity.
            date: The date the activity was performed.
            hours: The number of hours spent on the activity.
            rate: The hourly rate for the activity.

        Returns:
            The newly created activity object, or None if creation failed.
        """
        try:
            connection = connect_to_mysql()
            if not connection:
                return None

            cursor = connection.cursor()

            cursor.execute(
                "INSERT INTO invoice_items (invoice_id, item_name, quantity, date, rate) VALUES (%s, %s, %s, %s, %s)",
                (invoice_id, activity,  hours, date, rate)
            )
            connection.commit()

            activity = cls(invoice_id, activity, date, hours, rate)
            return activity
        except Exception as e:
            print(f"Error creating activity: {e}")
            return None
        finally:
            if connection:
                connection.close()



class Client:

    def __init__(self, client_id, name, email, phone, address):
        self.id = client_id
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address

    @classmethod
    def create(cls, name, email, phone, address):
        """
        Creates a new client in the database.

        Args:
            name: The name of the client.
            email: The email address of the client.
            phone: The phone number of the client.
            address: The address of the client.

        Returns:
            The newly created client object, or None if creation failed.
        """
        try:
            connection = connect_to_mysql()
            if not connection:
                return None

            cursor = connection.cursor()

            cursor.execute(
                "INSERT INTO client (client_name, client_email, client_phone, client_address) VALUES (%s, %s, %s, %s)",
                (name, email, phone, address)
            )
            connection.commit()

            client_id = cursor.lastrowid
            print(f" Client_id : {client_id}")
            client = cls(client_id, name, email, phone, address)
            return client
        except Exception as e:
            print(f"Error creating client: {e}")
            return None
        finally:
            if connection:
                connection.close()


    @classmethod
    def all(cls):
        """
        Finds all clients in the database.

        Returns:
            A list of all client objects.
        """
        try:
            connection = connect_to_mysql()
            if not connection:
                return None

            cursor = connection.cursor()

            cursor.execute(
                "SELECT * FROM client"
            )
            results = cursor.fetchall()

            clients = []
            for result in results:
                client = cls(result[0],result[1], result[2], result[3], result[4])
                clients.append(client)

            return clients
        except Exception as e:
            print(f"Error finding all clients: {e}")
            return None
        finally:
            if connection:
                connection.close()
