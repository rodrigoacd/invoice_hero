from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response, jsonify
from models import User, Invoice, Client, Activity
import config

from util.createPdf import invoice_to_pdf

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY


@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.find_by_username(username)

        if user and user.check_password(password):
            flash('Logged in successfully')
            session['user_id'] = user.user_id
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']
        abn = request.form['abn']
        bank = request.form['bank']
        account_name = request.form['account_name']
        bsb = request.form['bsb']
        account_number = request.form['account_number']

        user = User.create(username, password, email, phone, abn, bank, account_name, bsb, account_number)

        if user:
            flash('Account created successfully')
            return redirect(url_for('index'))
        else:
            flash('Error creating account')
            return redirect(url_for('signup'))

    return render_template('signup.html')



@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    # user = User.get_current_user()
    user = session['user_id']
    invoices = Invoice.get_all_invoices(user)
    print(f"Print username {invoices}")

    return render_template('dashboard.html', invoices=invoices)


@app.route('/invoices/new', methods=['GET', 'POST'])
def new_invoice():
    if request.method == 'GET':
        clients = Client.all()
        print(f"{clients}")
        return render_template('invoice.html', clients=clients)
    
    if request.method == 'POST':
        user_id = session['user_id']

        
        # Get the form data

        activity = request.form['activity']
        hours = request.form['hours']
        rate = request.form['rate']
        date = request.form['date']
        address = request.form['address']
        client_id = request.form['client_id']
        style = request.form['style']

        # find the last invoice number
        last_invoice = Invoice.find_last_invoice(user_id)
        print(f"Print invoice number: {last_invoice['invoice_number']}")
        print(f"Print user_id: {user_id}")

        
        if last_invoice == None:
            invoice_number = 1
        else:
            invoice_number = int(last_invoice['invoice_number']) + 1

        # Create an invoice object and save it to the database
        invoice = Invoice.create( invoice_number, user_id, client_id, address)

        # Save the invoice activities to the database
        # todo: create many activities
        print(f"Imprimient {invoice, activity, date, hours, rate}")
        activity = Activity.create(invoice, activity, date, hours, rate )

        # Redirect to the dashboard)

        if invoice:
            flash('Invoice created successfully')
            return redirect(url_for('dashboard'))
        else:
            flash('Error creating invoice')

    return redirect(url_for('dashboard'))

@app.route('/clients/new', methods=['GET', 'POST'])
def new_client():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        address = request.form['address']
        phone = request.form['phone']

        client = Client.create(name, email, phone, address)

        if client:
            flash('Client created successfully')
            return redirect(url_for('/invoices/new'))
        else:
            flash('Error creating client')

    return render_template('new_client.html')

@app.route('/invoice_details/<int:invoice_id>')
def invoice_details(invoice_id):
    invoice_data = Invoice.find_by_id(invoice_id)
    return render_template('invoice_details.html', invoice_data=invoice_data)


@app.route('/print_invoices/<int:invoice_id>')
def print_invoice(invoice_id):
    invoice_data = Invoice.all_invoice_info_by_id(invoice_id)

    pdf_bytes=invoice_to_pdf(invoice_data)
    response = make_response(pdf_bytes)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=invoice.pdf'
    return response



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


if __name__ == '__main__':
    app.run(debug=True)

