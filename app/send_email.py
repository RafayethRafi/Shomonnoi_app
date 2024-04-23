from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from jinja2 import Template
from .config import settings



def read_email_template(template_name):
    with open(template_name, 'r') as template_file:
        template_content = template_file.read()
    return template_content



def render_email_template(template_content, replacements):
    template = Template(template_content)
    rendered_content = template.render(replacements)
    return rendered_content


smtp_server = settings.smtp_server
smtp_port = settings.smtp_port
smtp_username = settings.smtp_username
smtp_password = settings.smtp_password



def send_invitation_email(email,role):

    api_endpoint_link = f'{settings.protocol}://{settings.host}:{settings.port}/users/register_user/{email}_{role}'

    email_template = read_email_template("app\email templates\email_template.html")

    replacements = {
            "link": api_endpoint_link
    }


    email_body = render_email_template(email_template, replacements)

    subject = "Click the link to register your account"

    msg = MIMEMultipart()
    msg["From"] = settings.smtp_msg_from
    msg["To"] = email
    msg["Subject"] = subject
    msg.attach(MIMEText(email_body, "html"))

    # Connect to the SMTP server and send the email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Use TLS encryption
            server.login(smtp_username, smtp_password)
            server.sendmail(msg["From"], msg["TO"], msg.as_string())
            return {"message": "Email sent successfully"}
    except Exception as e:
        return {"error": f"Failed to send email: {str(e)}"}




def send_pass_recovery_email(id,email):

    # split the email into 2 variables by @
    email_part1 = email.split('@')[0]
    email_part2 = email.split('@')[1]

    email_special_string = f"#%#%{email_part2}#%#%{id}#%#%{email_part1}"

    api_endpoint_link =  f'{settings.protocol}://{settings.host}:{settings.port}/password_reset/{email_special_string}'
    email_template = read_email_template("app\email templates\password-recovery.html")

    replacements = {
            "link": api_endpoint_link
    }

    email_body = render_email_template(email_template, replacements)

    subject = "Click the link to reset your password."

    msg = MIMEMultipart()
    msg["From"] = settings.smtp_msg_from
    msg["To"] = email
    msg["Subject"] = subject
    msg.attach(MIMEText(email_body, "html"))

    # Connect to the SMTP server and send the email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Use TLS encryption
            server.login(smtp_username, smtp_password)
            server.sendmail(msg["From"], msg["TO"], msg.as_string())
            return {"message": "Email sent successfully"}
    except Exception as e:
        return {"error": f"Failed to send email: {str(e)}"}


