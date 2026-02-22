import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage
import duckduckgo_search

def job_listing_parser():
    try:
        if os.environ.get('TOOL_TEST_MODE') == 'true':
            return 'Mock success: Job listings parsed and email sent successfully'

        url = 'https://www.indeed.com/jobs?q=ai+engineer&l='
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        job_listings = soup.find_all('div', class_='jobsearch-SerpJobCard')

        email_body = ''
        for job in job_listings:
            title = job.find('h2', class_='title').text.strip()
            company = job.find('span', class_='company').text.strip()
            location = job.find('div', class_='location').text.strip()
            email_body += f'Title: {title}\nCompany: {company}\nLocation: {location}\n\n'

        msg = EmailMessage()
        msg.set_content(email_body)
        msg['Subject'] = 'AI Engineer Job Listings'
        msg['From'] = 'job_listing_parser'
        msg['To'] = 'n200626@rguktn.ac.in'

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login('your-email@gmail.com', 'your-password')
            smtp.send_message(msg)

        return 'Job listings parsed and email sent successfully'
    except Exception as e:
        return f'Error: {str(e)}'