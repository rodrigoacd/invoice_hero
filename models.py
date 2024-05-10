from db import connect_to_mysql
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session


class User:

    def __init__(self,user_id, name, lastname, email, password,  address = None, phone = None, abn = None, bank = None, account_name = None, bsb = None, account_number = None):
        self.user_id = user_id
        self.name = name
        self.lastname = lastname
        self.password = password
        self.email = email
        self.phone = phone
        self.address = address
        self.abn = abn
        self.bank = bank
        self.account_name = account_name
        self.bsb = bsb
        self.account_number = account_number

#         print()

    @classmethod
    def create(cls, name, lastname,  email, password, phone):
        """
        Creates a new user in the database.
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
                "INSERT INTO users (name, lastname, password, email, phone) VALUES (%s, %s, %s, %s, %s)",
                (name, lastname, hashed_password, email, phone)
            )
            connection.commit()
            
            user_id = cursor.lastrowid

            user = cls(user_id, name, lastname, email, hashed_password)
            return user
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
        finally:
            if connection:
                connection.close()

    @classmethod
    def find_by_email(cls, email):
        """
        Finds a user by their email.

        Args:
            email: string

        Returns:
            The user object if found, otherwise None.
        """
        try:
            connection = connect_to_mysql()
            if not connection:
                return None

            cursor = connection.cursor()

            cursor.execute(
                "SELECT id as user_id, name, lastname, email, password, address, phone, abn, bank, account_name, bsb, account_number  FROM users WHERE email = %s",
                (email,)
            )
            result = cursor.fetchone()

            if result:
                user = cls(*result)
                return user
            else:
                return None
        except Exception as e:
            print(f"Error finding user by email: {e}")
            return None
        finally:
            if connection:
                connection.close()


    def update_user_info(user_id, updated_name, updated_lastname, updated_email, updated_phone, updated_address, updated_abn, updated_bank, updated_account_name, updated_bsb, update_account_number):
        try:
            connection = connect_to_mysql()
            if not connection:
                return False  # Or raise an exception

            cursor = connection.cursor()
            cursor.execute(
                "UPDATE users SET name = %s, lastname = %s, email= %s, phone = %s, address = %s, abn = %s, bank = %s, account_name = %s, bsb = %s,  account_number= %s WHERE id = %s",
                (updated_name, updated_lastname, updated_email, updated_phone, updated_address, updated_abn, updated_bank, updated_account_name, updated_bsb, update_account_number, user_id)
            )
            connection.commit()  # Commit the changes to the database
            return True  # Indicate successful update

        except Exception as e:
            print(f"Error Updating user by id: {e}")
            # Log the error details for debugging (optional)
            return False  # Or raise an exception

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
        email = session.get('email')
        if email:
            return cls.find_by_email(email)
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
    def create(cls, invoice_number, user_id, client_id):
        
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
                "INSERT INTO invoices (user_id, invoice_number, invoice_date, date_due, status, address, client_id ) VALUES (%s, %s, now(), DATE(DATE_ADD(now(), INTERVAL 30 DAY)), 'created',%s, %s)",
                (user_id, invoice_number, "none", client_id)
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
                        u.name, u.email, u.phone as user_phone, u.abn, u.bank, u.account_name,bsb,account_number,
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
                """
                With totalPrice as(
                    SELECT invoice_id, CAST(sum(quantity * rate) AS INT) total FROM invoice_items GROUP BY invoice_id
                )
                SELECT 
                    i.id, i.user_id, i.invoice_number, i.invoice_date, i.date_due, i.client_id, i.address, i.status,
                    c.client_email, c.client_name, c.client_phone, c.client_address, t.total
                FROM 
                    invoices i
                INNER JOIN 
                    client c
                ON 
                    c.id = i.client_id
                INNER JOIN 
                    totalPrice t
                ON 
                    t.invoice_id = i.id
                WHERE 
                    i.user_id = %s 
                ORDER BY id DESC                 
                """,
                (user_id,)
            )
            results = cursor.fetchall()

            if results:
                columns = [desc[0] for desc in cursor.description]
                items_by_group = []
                for row in results:
                    group_data = {column: value for column, value in zip(columns, row)}
                    items_by_group.append(group_data)
                return items_by_group
            else:
                print('No activities by group')
                return []
        except Exception as e:
            print(f"Error finding all invoices with details: {e}")
            return None
        finally:
            if connection:
                connection.close()


    def Update_status(invoice_id, status):
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
                "UPDATE invoices SET status = %s WHERE id = %s",
                (status, invoice_id,)
            )
            connection.commit()
        except Exception as e:
            print(f"Error updating invoice: {e}")
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


    @classmethod
    def delete_invoice(self, invoice_id):
        """
        Delete the invoice with the given data.

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
                "DELETE FROM invoices WHERE id = %s",
                (invoice_id)
            )
            connection.commit()
        except Exception as e:
            print(f"Error deleting invoice: {e}")
        finally:
            if connection:
                connection.close()


class Activity:

    def __init__(self, activity_id, invoice_id, name, hours, date, rate, address=None):
        self.activity_id = activity_id
        self.invoice_id = invoice_id
        self.name = name
        self.date = date
        self.hours = hours
        self.rate = rate
        self.address = address

    @classmethod
    def create(cls, invoice_id, activity, date, hours, rate, address):
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
                "INSERT INTO invoice_items (invoice_id, item_name, quantity, date, rate, address) VALUES (%s, %s, %s, %s, %s, %s)",
                (invoice_id, activity,  hours, date, rate, address)
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


    @classmethod
    def find_by_invoice(cls, invoice_id):
        """
        Finds all activities by id

        """
        try:
            connection = connect_to_mysql()
            if not connection:
                return None

            cursor = connection.cursor()

            cursor.execute(
                """ SELECT 
                        id as activity_id, invoice_id, item_name as name,
                        quantity as hours, CAST(date AS DATE), rate, address  
                        FROM invoice_items 
                        WHERE invoice_id = %s""",
                (invoice_id,)
            )
            results = cursor.fetchall()

            activities = []
            for result in results:
                activity = cls(*result)
                activities.append(activity)
                print(activity.name)
            return activities
        
        except Exception as e:
            print(f"Error finding activities by invoice_id: {e}")
            return None
        finally:
            if connection:
                connection.close()

class Client:

    def __init__(self, client_id, name, lastname, company_name, email, phone, address, user_id):
        self.id = client_id
        self.name = name
        self.lastname = lastname
        self.company_name = company_name
        self.email = email
        self.phone = phone
        self.address = address
        self.user_id = user_id

    @classmethod
    def create(cls, name, lastname, company_name, email, phone, address):
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

            user_id = session.get('user_id')
            cursor.execute(
                "INSERT INTO client (client_name, client_lastname, client_company, client_email, client_phone, client_address, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (name, lastname, company_name, email, phone, address, user_id)
            )
            connection.commit()

            client_id = cursor.lastrowid
            print(f" Client_id : {client_id}")
            client = cls(client_id, name, lastname, company_name, email, phone, address)
            return client
        except Exception as e:
            print(f"Error creating client: {e}")
            return None
        finally:
            if connection:
                connection.close()


    @classmethod
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
                "SELECT id, client_name, client_lastname, client_company, client_email, client_phone, client_address, user_id FROM client WHERE user_id = %s",
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

 

    @classmethod
    def get_by_client_id(cls, client_id):
        try:
            connection = connect_to_mysql()
            if not connection:
                raise ConnectionError("Could not connect to the database.")

            cursor = connection.cursor()
            cursor.execute(
                "SELECT id as client_id, client_name name, client_lastname as lastname, client_company as company_name, client_email as email,client_phone as phone, client_address as address, user_id FROM client WHERE id = %s ", 
                (client_id,)
            )

            result = cursor.fetchone()

            if result:
                user = cls(*result)
                return user
            else:
                return None
        
        except Exception as e:
            # Consider logging the error for better traceability
            print(f"Error fetching clients : {e}")
            return None
        finally:
            if connection:
                connection.close()

    def update(client_id, client_name , client_email ,client_phone ,client_address  ,client_lastname ,client_company):
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
                "UPDATE client SET client_name = %s, client_email = %s ,client_phone = %s ,client_address = %s ,client_lastname = %s ,client_company = %s WHERE id = %s",
                (client_name , client_email ,client_phone ,client_address  ,client_lastname ,client_company,client_id, )
            )
            connection.commit()
        except Exception as e:
            print(f"Error updating invoice: {e}")
        finally:
            if connection:
                connection.close()