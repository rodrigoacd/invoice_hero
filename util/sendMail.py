from flask import Flask, request, render_template
from mailjet_rest import Client
import base64

import config

app = Flask(__name__)




def send_email( to_email, client_name, subject, text, attachment_data):
    try:
        # MailJet configuration settings
        mailjet_api_key = config.MAIL_API_KEY
        mailjet_api_secret = config.MAIL_SECRET_KEY
        # Crea un cliente de Mailjet
        mailjet = Client(auth=(mailjet_api_key, mailjet_api_secret), version='v3.1')


        attachment_data_base64 = base64.b64encode(attachment_data).decode('utf-8')

        attachment_filename = 'invoice.pdf'

        # Define los parámetros del correo electrónico

        data = {
            'Messages': [
                {
                    'From': {
                        'Email': 'rodrigo.delgado@student.torrens.edu.au',
                        'Name': 'Invoice Hero'
                    },
                    'To': [
                        {
                            'Email': to_email,
                            'Name': client_name
                        }
                    ],
                    'Subject': subject,
                    'TextPart': text,
                    'Attachments': [
                        {
                            'ContentType': 'application/pdf',
                            'Filename': attachment_filename,
                            'Base64Content': attachment_data_base64
                        }
                    ]
                }
            ]
        }
        # Envía el correo electrónico
        result = mailjet.send.create(data=data)

        # Verifica si el correo electrónico se envió correctamente
        if result.status_code == 200:
            return 'True'
        else:
            return f"Error al enviar el correo electrónico: {result.status_code} - {result.json()}"
    except Exception as e:
        return False, f"Error al enviar el correo electrónico: {e}"

