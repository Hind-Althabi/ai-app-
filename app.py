from flask import Flask, render_template, request
import openai
import os
import sqlite3
import smtplib
from email.message import EmailMessage
#import dotenv
#from dotenv import load_dotenv, find_dotenv
#_ = load_dotenv(find_dotenv()) # read local .env file


app = Flask(__name__)

#openai.api_key  = os.getenv('OPENAI_API_KEY')

# Set up OpenAI API credentials
API_KEY = "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"


# Define the default route to return the index.html file
@app.route("/")
def index():
    return render_template("index.html")

# Define the /api route to handle POST requests
@app.route("/api", methods=["POST"])
def api():
    # Get the message from the POST request
    message = request.json.get("message")
    # Send the message to OpenAI's API and receive the response
    
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": message}
    ]
    )
    #call translate function
    trans= translatearabic(message)
    # Extract response text 
    response = get_completion(trans)
    # Extract keywords from user msg
    keywords = extract_keywords(response)
    print(keywords)

    # to generate report and send it to email
    report= summary(keywords , message)
    print("Report: ")
    print(report)

    send_email(report)
    print("Database answer")
    # Connect to database
    conn = sqlite3.connect('example224.db')

    #Create a cursor object to execute SQL commands
    cur = conn.cursor()
    # Execute an SQL command to select rows from the users table that match the keywords
    cur.execute("SELECT * FROM users WHERE name LIKE ? OR email LIKE ?", ('%{}%'.format(keywords[0]), '%{}%'.format(keywords[1])))
    # Fetch all rows and print them
    row = cur.fetchone()
    print(row) 
    # Close the connection
    conn.close()

    

    if completion.choices[0].message!=None:
        
        return completion.choices[0].message

    else :
        return 'Failed to Generate response!'
    

def get_completion(prompt, model="gpt-3.5-turbo"): # Andrew mentioned that the prompt/ completion paradigm is preferable for this class
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]

#----------------------
#function to translate to English
def translatearabic(message):
    prompt = f"""
    Translate the following Arabic text to English: \
    Review: ```{message}```
    """
    EnglishText = get_completion(prompt)
    return EnglishText

#------------------
# Extract keywords from  msg by using OpenAI API
def extract_keywords(message):
    # Set prompt
    prompt = f"""
    The task is to extract the keywords from the following message:

    {message}

    Keywords:
    """

    response = get_completion(prompt)
    # Return keywords as list
    return response



#------------------
def summary(x, y):
    # Combine x and y into one sentence
    sentence = x + ' ' + y

    # Set prompt
    prompt = f"""
    Your task is to generate a short summary of a product review from an ecommerce site.

    Summarize the review below, delimited by triple backticks, in at most 30 words.

    Review: ```{sentence}```
    """
    # Send prompt 
    summary = get_completion(prompt)
    return summary


#------------------
# send email
def send_email(message):
    # Set up email message
    msg = EmailMessage()
    msg.set_content(message)
    msg['Subject'] = 'Message from Python'
    msg['From'] = 'hind.althabi@gmail.com'
    msg['To'] = 'hind.althabi@gmail.com'

    # Send email using SMTP server
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login('hind.althabi@gmail.com', 'wzriouwecqkfscvf')

        smtp.send_message(msg)

    print('Email sent successfully.')


#------------------
#----database
import sqlite3

# Connect to database
conn = sqlite3.connect('example224.db')

# Create a cursor object to execute SQL commands
cur = conn.cursor()

# Execute  SQL command to drop the users table (if it exists)
cur.execute("DROP TABLE IF EXISTS users")


# Execute an SQL command to create a table
cur.execute('''CREATE TABLE users
               (name TEXT, email TEXT, time TEXT, specialty TEXT)''')

# Insert some data into the table
cur.execute("INSERT INTO users (name, email, time, specialty) VALUES (?, ?, ?, ?)",
            ("Eng. A", "a", "Sunday – Thursday 8:00 AM – 12:00 PM", "IoT"))
cur.execute("INSERT INTO users (name, email, time, specialty) VALUES (?, ?, ?, ?)",
            ("E", "n.com.sa", "Sunday – Thursday 8:00 AM – 12:00 PM", "cloud"))
cur.execute("INSERT INTO users (name, email, time, specialty) VALUES (?, ?, ?, ?)",
            ("E", "e", "Sunday – Thursday 11:00 AM – 3:00 PM", "Data Analysis"))
cur.execute("INSERT INTO users (name, email, time, specialty) VALUES (?, ?, ?, ?)",
            ("N", "n", "Sunday – Thursday 8:00 AM – 12:00 PM", "Machine Learning"))
cur.execute("INSERT INTO users (name, email, time, specialty) VALUES (?, ?, ?, ?)",
            ("G", "g", "Sunday – Thursday 8:00 AM – 12:00 PM", "Business development"))

# Commit changes to the database
conn.commit()

# Close the connection
conn.close()


if __name__=='__main__':
    app.run()

