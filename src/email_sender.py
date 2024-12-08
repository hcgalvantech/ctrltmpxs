# src/email_sender.py
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from .config import Config

def send_exam_submission_email(to_email, submission_time, github_link):
    """Send exam submission confirmation email"""
    try:
        message = Mail(
            from_email='examenes@institutoalfa.com',
            to_emails=to_email,
            subject='Confirmación de Envío de Examen Final',
            html_content=f'''
            <strong>Detalles de Envío de Examen:</strong>
            <p>Hora de Envío: {submission_time}</p>
            <p>Link de Proyecto: <a href="{github_link}">{github_link}</a></p>
            '''
        )
        
        sg = SendGridAPIClient(Config.SENDGRID_API_KEY)
        response = sg.send(message)
        return response
    except Exception as e:
        print(f"Error sending email: {e}")
        return None