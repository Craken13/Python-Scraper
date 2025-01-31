import requests
from bs4 import BeautifulSoup
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Scraper function
def scrape_hackathons(location_filter):
    location_filter = location_filter.replace(' ', '+')
    urls = [
        f"https://devpost.com/hackathons?search={location_filter}",
        f"https://www.eventbrite.com/d/south-africa/hackathon/?q={location_filter}"
    ]
    
    hackathons = []
    
    for url in urls:
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from {url}: {e}")
            continue
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for event in soup.select(".event"):
            title = event.select_one("h3").text.strip()
            date = event.select_one(".event-date").text.strip()
            location = event.select_one(".event-location").text.strip()
            link = event.select_one("a")['href']
            
            if location_filter.lower() in location.lower():
                hackathons.append(f"{title} - {date} - {location} - {link}")
    
    return hackathons

# Email sending function
def send_email(hackathons):
    sender_email = os.getenv("EMAIL_SENDER")
    receiver_email = os.getenv("EMAIL_RECEIVER")
    password = os.getenv("EMAIL_PASSWORD")
    
    if not sender_email or not receiver_email or not password:
        print("Email credentials are not set properly.")
        return
    
    subject = "Upcoming Hackathons!"
    body = "\n".join(hackathons)
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("Email sent successfully!")
    except smtplib.SMTPException as e:
        print(f"Error sending email: {e}")

# ...existing code...

if __name__ == "__main__":
    location_filter = "Cape Town"  # Specify the location here
    hackathons = scrape_hackathons(location_filter)
    if hackathons:
        send_email(hackathons)
    else:
        print(f"No hackathons found for {location_filter}.")
