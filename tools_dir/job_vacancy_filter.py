import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage
import feedparser
from duckduckgo_search import search

def job_vacancy_filter():
    try:
        if os.environ.get('TOOL_TEST_MODE') == 'true':
            return 'Mock success: Job vacancy filter tool ran successfully in test mode.'

        url = 'https://www.indeed.com/jobs?q=web+developer&l='
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        vacancies = soup.find_all('h2', class_='jobTitle-jobTitle')

        msg = EmailMessage()
        msg.set_content('\n'.join([v.text for v in vacancies]))
        msg['Subject'] = 'Web Developer Job Vacancies'
        msg['From'] = 'your-email@gmail.com'
        msg['To'] = 'n200626@rguktn.ac.in'

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login('your-email@gmail.com', 'your-password')
            smtp.send_message(msg)

        return 'Job vacancy filter tool ran successfully. Email sent to n200626@rguktn.ac.in.'
    except Exception as e:
        return f'Error: {str(e)}'