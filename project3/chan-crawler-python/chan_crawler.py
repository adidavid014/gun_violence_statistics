import faktory
import logging
from faktory import Worker
from chan_client import Client
from datetime import datetime, timedelta
import time
import psycopg2
from dotenv import load_dotenv
import os
from datetime import datetime
import requests

# these three lines allow psycopg to insert a dict into
# a jsonb coloumn
from psycopg2.extras import Json
from psycopg2.extensions import register_adapter
register_adapter(dict, Json)

# load our .env file
load_dotenv()

keywords = [
    '2a', 'self defense', ' murica', 'progun', 'constitutional right', 'patriot', 'maga', 'bubba', 'come and take them',
    'shall not be infringed', 'biden', 'harris', 'assault rifle', ' ar ', 'concealed carry', 'bear arms', 'pistol', 'ak47', 
    'ak-47', 'bump stock'
]

DATABASE_URL = os.environ.get('DATABASE_URL')
FAKTORY_URL = os.environ.get('FAKTORY_URL')

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                    level=logging.INFO,
                    datefmt='%Y-%m-%d %H:%M:%S')

''' Find thread numbers in a given catalog '''
def thread_numbers_from_catalog(catalog):
    thread_numbers = set()

    for page in catalog:
        page_number = page["page"]
        
        # thread numbers
        for thread in page["threads"]:
            thread_number = thread["no"]

            thread_numbers.add(thread_number)

    return thread_numbers

''' Find the threads that have died since the last run '''
def find_dead_threads(old_thread_numbers, new_thread_numbers):
    dead_threads = old_thread_numbers.difference(new_thread_numbers)
    return dead_threads

''' Crawl a thread and add it to the database if desired '''
def crawl_thread(board, thread_number, last_modified=None):
    client = Client()
    thread = client.get_thread(board, thread_number, last_modified)

    if not thread:  # This means data hasn't changed
        logging.info(f'/{board}/{thread_number} has not been modified since {last_modified}')
        return


    conn = psycopg2.connect(
        dsn=DATABASE_URL
    )

    cur = conn.cursor()

    # for each post that we have, we want to insert it into the db
    for post in thread["posts"]:
        is_gunpride = 0
        is_toxic = 0
        checked_toxic = 1

        post_number = post["no"]
        try:
            cur.execute("SELECT 1 FROM posts WHERE post_number = %s AND thread_number = %s AND board = %s", (post_number, thread_number, board,))
            if not cur.fetchone():

                post_text = post.get('com', '')
                
                if any(word in post_text for word in keywords):
                    is_gunpride = 1

                try:
                    CONF_THRESHOLD = 0.5

                    data = {
                        "token": "6d7f5ae46dd96ddb4384a82a7eb5b416",
                        "text": post_text
                    }

                    response = requests.post("https://api.moderatehatespeech.com/api/v1/moderate/", json=data).json()

                    if response["class"] == "flag" and float(response["confidence"]) > CONF_THRESHOLD:
                        is_toxic = 1

                except:
                    checked_toxic = 0

                post_time = post["time"]
                creation_date = datetime.utcfromtimestamp(post_time)
                sql = "INSERT INTO posts (board, thread_number, post_number, created_at, is_gunpride, is_toxic, checked_toxic, data) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id"
                
                cur.execute(sql, (board, thread_number, post_number, creation_date, is_gunpride, is_toxic, checked_toxic, post_text))

                conn.commit()

                db_id = cur.fetchone()[0]
                logging.info(f'Inserted DB id: {db_id}')
        except: 
            logging.info(f'Error inserting into database')
        
    cur.close()
    conn.close()

''' Look through the catalog to see if any threads have died, queue them as new jobs '''
def crawl_catalog(board, old_thread_numbers=[], last_modified=None):
    client = Client()

    catalog = client.get_catalog(board)
    
    new_thread_numbers = thread_numbers_from_catalog(catalog)

    dead_thread_numbers = find_dead_threads(set(old_thread_numbers), new_thread_numbers)

    conn = psycopg2.connect(
        dsn=DATABASE_URL
    )

    cur = conn.cursor()

    for dead_thread_number in dead_thread_numbers:
        # enqueue a new job to collect the dead thread number
        with faktory.connection(FAKTORY_URL) as client:
            cur.execute("SELECT 1 FROM posts WHERE thread_number = %s AND board = %s", (dead_thread_number, board,))

            if not cur.fetchone():
                client.queue("crawl-thread", args=(board, dead_thread_number, last_modified), queue="crawl-threads", reserve_for=300)

    cur.close()
    conn.close()

    # now we need to schedule to crawl the catalog again in 15 minutes
    run_at = datetime.utcnow() + timedelta(minutes=15)
    run_at = run_at.isoformat()[:-7] + "Z"
    logging.info(f'scheduling a new catalog crawl to run at: {run_at}')
    
    with faktory.connection(FAKTORY_URL) as client:
        client.queue("crawl-catalog", args=(board,list(new_thread_numbers)), queue="crawl-catalogs", reserve_for=300, at=run_at)


if __name__ == "__main__":
    w = Worker(faktory=FAKTORY_URL, queues=["crawl-catalogs", "crawl-threads"], concurrency=10, use_threads=True)
    w.register("crawl-catalog", crawl_catalog)
    w.register("crawl-thread", crawl_thread)
    logging.info("running?")
    w.run()