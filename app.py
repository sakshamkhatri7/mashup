from flask import Flask, request, render_template
from download import Download
from email.message import EmailMessage
import ssl
import smtplib
import os
import zipfile
import io
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['GET', 'POST'])
def getValue():
    if request.method == 'POST':
        try:
            # Get form data
            singer = request.form['singer']
            number = int(request.form['number'])
            duration = int(request.form['duration'])
            email = request.form['mail']

            # Run the download and mashup process
            logging.info(f"Starting download for {singer}, {number} songs, {duration} seconds each.")
            Download(singer, number, duration)

            mashup_path = f"static/{singer}/mashup.mp3"
            zip_path = f"static/{singer}/mashup.zip"
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, 'w') as myzip:
                myzip.write(mashup_path, arcname="mashup.mp3")
            buffer.seek(0)

            with open(zip_path, "wb") as f:
                f.write(buffer.read())
            
            email_sender = 'samplemashup12@gmail.com'
            email_password = 'vcgdcnxfxqiufmgv' 
            email_receiver = email

            em = EmailMessage()
            em['From'] = email_sender
            em['To'] = email_receiver
            em['Subject'] = 'Your Mashup'
            em.set_content("Here is your Requested Mashup")

            with open(zip_path, "rb") as fp:
                file_data = fp.read()
                em.add_attachment(file_data, maintype='application', subtype='zip', filename="mashup.zip")

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                smtp.login(email_sender, email_password)
                smtp.send_message(em)

            logging.info(f"Email sent successfully to {email_receiver}.")
            return render_template('pass.html')

        except Exception as e:
            logging.error(f"Error occurred: {e}")
            return render_template('error.html')

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

