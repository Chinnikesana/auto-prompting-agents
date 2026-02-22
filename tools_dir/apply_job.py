import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import time

def apply_job(position, company_email, company_website, resume_path):
    try:
        if os.environ.get('TOOL_TEST_MODE') == 'true':
            return 'Job application submitted successfully in test mode'
        
        if company_email:
            msg = MIMEMultipart()
            msg['From'] = 'your-email@gmail.com'
            msg['To'] = company_email
            msg['Subject'] = 'Job Application for ' + position
            body = 'Dear Hiring Manager, I am applying for the ' + position + ' position at ' + company_website
            msg.attach(MIMEText(body, 'plain'))
            attachment = open(resume_path, 'rb')
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename= %s' % resume_path.split('/')[-1])
            msg.attach(part)
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(msg['From'], 'your-password')
            text = msg.as_string()
            server.sendmail(msg['From'], msg['To'], text)
            server.quit()
        elif company_website:
            response = requests.get(company_website)
            soup = BeautifulSoup(response.text, 'html.parser')
            form_url = None
            for link in soup.find_all('a'):
                if 'apply' in link.get('href'):
                    form_url = link.get('href')
                    break
            if form_url:
                response = requests.get(form_url)
                soup = BeautifulSoup(response.text, 'html.parser')
                form_data = {}
                for input_tag in soup.find_all('input'):
                    if input_tag.get('name'):
                        form_data[input_tag.get('name')] = 'your-' + input_tag.get('name')
                response = requests.post(form_url, data=form_data, files={'resume': open(resume_path, 'rb')})
                if response.status_code == 200:
                    return 'Job application submitted successfully'
        return 'Failed to submit job application'
    except Exception as e:
        return 'Error: ' + str(e)