from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response, jsonify
from models import User, Invoice, Client, Activity
import config

from util.createPdf import invoice_to_pdf
from util.sendMail import send_email

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY


@app.route('/')
def index():
    if 'email' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        print (f"password/email { password,email }")

        user = User.find_by_email(email)
        print (f"user.password/user.email { user.password,user.email }")
        if user and user.check_password(password):
            flash('Logged in successfully')
            session['user_id'] = user.user_id
            session['email'] = user.email
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials')
            print ("Invalido")
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('email', None)
    session.pop('user_id', None)
    return redirect(url_for('index'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        lastname = request.form['lastname']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']

        user = User.create(name, lastname, email, password, phone)

        if user:
            flash('Account created successfully')
            return redirect(url_for('index'))
        else:
            flash('Error creating account')
            return redirect(url_for('signup'))

    return render_template('signup.html')

@app.route('/profile')
def profile():
    # Recuperar el usuario por su ID desde la base de datos
    user_data = User.get_current_user()
    if user_data:
        # Renderizar la plantilla de usuario y pasar los datos del usuario a la plantilla
        return render_template('profile.html', user=user_data)
    else:
        # Manejar el caso cuando el usuario no se encuentra en la base de datos
        return "User not found", 404


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    user_id = session['user_id']
    email = session['email']
    if request.method == 'GET':
        # Fetch user information based on user_id
        #id as user_id, name, lastname, email, password, phone, abn, bank, account_name, bsb, account_number
        user = User.get_current_user()

        # Render the edit profile template with user data
        return render_template('edit_profile.html', user=user)

    if request.method == 'POST':
        # Get updated user data from the POST request

        updated_name = request.form['name']
        updated_lastname = request.form['lastname']
        updated_email = request.form['email']
        updated_phone = request.form['phone']
        updated_address = request.form['address']
        

        updated_abn = request.form['abn']
        updated_bank = request.form['bank']
        updated_account_name = request.form['account_name']
        updated_bsb = request.form['bsb']
        updated_account_number = request.form['account_number']


        # Update user information in the database or data source
        User.update_user_info(user_id, updated_name, updated_lastname, updated_email, updated_phone, updated_address, updated_abn, updated_bank, updated_account_name, updated_bsb, updated_account_number)

        # Redirect to the user's profile page after successful update
        return redirect(url_for('profile'))
    
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    # user = User.get_current_user()
    user_id = session['user_id']
    email = session['email']

    if request.method == 'GET':
        invoices = Invoice.get_all_invoices(user_id)
        
        # Get all clients 
        # TODO: get all user clients (not all because the list needs to be by each user)
        
        clients = Client.get_by_user()

    return render_template('dashboard.html', invoices=invoices, clients=clients, user_id=user_id)


@app.route('/invoices/new', methods=['GET', 'POST'])
def new_invoice():
    # if request.method == 'GET':
    #     clients = Client.all()
    #     print(f"{clients}")
    #     return render_template('invoice.html', clients=clients)
    
    if request.method == 'POST':
        user_id = session['user_id']

        # Get client_id
        client_id = request.form['client_id']
        # Get the current invoice number
        last_invoice = Invoice.find_last_invoice(user_id)

        if last_invoice == None:
            invoice_number = 1
        else:
            invoice_number = int(last_invoice['invoice_number']) + 1

        # Create an invoice object and save it to the database
        invoice_id = Invoice.create( invoice_number, user_id, client_id)  


        for key, value in request.form.items():
            if key.startswith('address') and value:
                # Obtener el número del artículo del nombre del campo
                item_number = key.replace('address', '')
                
                # Obtener los valores relacionados con este artículo
                item_address = request.form[f'address{item_number}']
                item_date = request.form[f'date{item_number}']
                item_activity = request.form[f'activity{item_number}']
                item_hours = request.form[f'hours{item_number}']
                item_rate = request.form[f'rate{item_number}']
                
               
                # Save the activities of the invoice
                activity = Activity.create(invoice_id, item_activity, item_date, item_hours, item_rate, item_address)

        # Redirect to the dashboard)

        if invoice_id:
            flash('Invoice created successfully')
            return redirect(url_for('dashboard'))
        else:
            flash('Error creating invoice')

    return redirect(url_for('dashboard'))

@app.route('/clients/new', methods=['GET', 'POST'])
def new_client():
    if request.method == 'POST':
        name = request.form['name']
        lastname = request.form['lastname']
        company_name = request.form['company_name']
        email = request.form['email']
        address = request.form['address']
        phone = request.form['phone']

        client = Client.create(name, lastname, company_name, email, phone, address)

        if client:
            flash('Client created successfully')
            return redirect(url_for('/invoices/new'))
        else:
            flash('Error creating client')

    return redirect(url_for('dashboard'))



@app.route('/invoice_details/<int:invoice_id>')
def invoice_details(invoice_id):
    if request.method == 'GET':
        invoice_data = Invoice.find_by_id(invoice_id)
        item_data = Activity.find_by_invoice(invoice_id)
        return render_template('invoice_details.html', invoice_data=invoice_data, item_data=item_data)



@app.route('/print_invoices/<int:invoice_id>')
def print_invoice(invoice_id):
    invoice_data = Invoice.all_invoice_info_by_id(invoice_id)

    pdf_bytes=invoice_to_pdf(invoice_data)
    response = make_response(pdf_bytes)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=invoice.pdf'
    return response


@app.route('/send_invoices/<int:invoice_id>')
def send_invoice(invoice_id):
    invoice_data = Invoice.all_invoice_info_by_id(invoice_id)

    pdf_bytes=invoice_to_pdf(invoice_data)

    #response = make_response(pdf_bytes)

    subject = f"Invoice number: { invoice_data['invoice_number'] }"
    text = f"Invoice Attached from { invoice_data['name'] }"

    response = send_email( invoice_data['client_email'], invoice_data['client_name'], subject, text, pdf_bytes)

    return response



@app.route('/delete_invoices/<int:invoice_id>')
def delete_invoices(invoice_id):
    Invoice.delete_invoice(invoice_id)

    return redirect(url_for('dashboard'))





@app.route('/send_invoice_email/<int:invoice_id>', methods=['POST'])
def send_invoice_email(invoice_id):
    
    api_key = '4979a7ad40406f42ea3619e8daa8c06a-us22'  # Reemplaza con tu clave API de Mailchimp
    list_id = 'invoice_hero'  # Reemplaza con el ID de tu lista de Mailchimp

    endpoint = f'https://<dc>.api.mailchimp.com/3.0/lists/{list_id}/members'
    data = {
        'email_address': email,
        'status': 'subscribed'
    }
    headers = {
        'Authorization': f'apikey {api_key}'
    }

    response = requests.post(endpoint, json=data, headers=headers)
    if response.status_code == 200:
        print('Usuario suscrito correctamente a la lista de correo.')
    else:
        print('Error al suscribir al usuario:', response.text)

    return jsonify({'message': 'Email sent successfully'})


@app.route('/client/<int:client_id>')
def show_client(client_id):
    if request.method == 'GET':
    
        client = Client.get_by_client_id(client_id)
        invoices = Invoice.all_invoice_info_by_id(client_id)

        return render_template('mostrar_cliente.html', client=client, invoices=invoices)

@app.route('/client')
def clients():

    if request.method == 'GET':
        
        clients = Client.get_by_user()

        return render_template('clients.html', clients=clients)




if __name__ == '__main__':
    app.run(debug=True)

