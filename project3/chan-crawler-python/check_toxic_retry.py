
import psycopg2
from dotenv import load_dotenv
import os
import json
import requests

# Load environment variables
load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL')

def check_toxicity():
    conn = psycopg2.connect(
        dsn=DATABASE_URL
    )

    cur = conn.cursor()

    cur.execute("SELECT * FROM posts WHERE checked_toxic = 0 and data != ''")

    entries = cur.fetchall()

    #print(entries)
    
    for entry in entries:
        new_checked_toxic = 1
        new_is_toxic = 0
        success = False
        try:
            CONF_THRESHOLD = 0.5

            data = {
                "token": "6d7f5ae46dd96ddb4384a82a7eb5b416",
                "text": entry[8]
            }

            response = requests.post("https://api.moderatehatespeech.com/api/v1/moderate/", json=data).json()

            if response["class"] == "flag" and float(response["confidence"]) > CONF_THRESHOLD:
                new_is_toxic = 1
            
            success = True

        except Exception as e:
            print(f'exception {e}')
            new_checked_toxic = 0

        if success:
            update_query = "UPDATE posts SET checked_toxic = %s, is_toxic = %s WHERE id = %s"

            cur.execute(update_query, (new_checked_toxic, new_is_toxic, entry[0]))
            print(f'updated post at id {entry[0]}, is_toxic = {new_is_toxic}')
            conn.commit()

    
    cur.close()
    conn.close()

check_toxicity()

