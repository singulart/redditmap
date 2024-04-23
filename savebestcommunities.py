# Saves names of 'best' Reddit subreddits to a database table
# TODO Parallel execution of this task doesn't produce good result. Luckily, even single thread works fast enough

import sqlite3
import requests
import re
import datetime
from celery import Celery
from celery.utils.log import get_task_logger

app = Celery(config_source='celeryconfig')
logger = get_task_logger(__name__)

@app.task(name='Save Best Reddits')
def save_best_communities(pagenum):
    
    regex_pattern = r'(\/r\/\w+)'

    # Establish a connection to the SQLite database file
    conn = sqlite3.connect('reddit.db')
    # Create a cursor object using the connection
    cur = conn.cursor()

    # Create a table (if it does not already exist)
    cur.execute('CREATE TABLE IF NOT EXISTS reddit_subs_best (sub VARCHAR(64))')
    
    now = datetime.datetime.now()
    subs_response = requests.get(f'https://www.reddit.com/best/communities/{pagenum}/', timeout=30.0)
    if not subs_response or subs_response.status_code != 200:
        logger.warn(subs_response.status_code)
        return 
            
    sub_names_matches = [match for match in re.findall(regex_pattern, subs_response.text)]
    sub_names = [(s, ) for s in set(sub_names_matches)]
    # logger.info('HTTP call + regexp took {} ms.'.format((datetime.datetime.now() - now).total_seconds()))
    
    # This produces 1300+ duplicated records, see README.md on how to dedup using SQL
    cur.executemany('INSERT INTO reddit_subs_best (sub) VALUES (?)', sub_names)
    conn.commit()
