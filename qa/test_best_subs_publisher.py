# Saves names of 'best' Reddit subreddits to a database table
# TODO Parallel execution of this task doesn't produce good result. Luckily, even single thread works fast enough

import sqlite3
import requests
import re
import datetime
from celery.utils.log import get_task_logger
import logging

logger = get_task_logger(__name__)
logging.basicConfig(level = logging.INFO)

def save_best_communities(pagenum):
    

    # Create a table (if it does not already exist)
    cur.execute('CREATE TABLE IF NOT EXISTS reddit_subs_best (sub VARCHAR(64))')
    
    now = datetime.datetime.now()
    subs_response = requests.get(f'https://www.reddit.com/best/communities/{pagenum}/', timeout=30.0)
    if not subs_response or subs_response.status_code != 200:
        logger.warn(subs_response.status_code)
        return 
            
    sub_names_matches = [match for match in re.findall(regex_pattern, subs_response.text)]
    sub_names = [f"'{s}'" for s in set(sub_names_matches)]
    
    sql_st = f"select sub from reddit_subs_best where sub in ({','.join(sub_names)})"
    # logger.info(sql_st)
    cur.execute(sql_st)
    db_results = cur.fetchall()
    logger.info(f'On page {pagenum} got {len(sub_names)} unique subs, from which {len(sub_names) - len(db_results)} NOT found in DB')

if __name__ == "__main__":
    regex_pattern = r'(\/r\/\w+)'

    # Establish a connection to the SQLite database file
    conn = sqlite3.connect('reddit.db')
    # Create a cursor object using the connection
    cur = conn.cursor()

    for i in range(1, 682): 
        save_best_communities(i)
        
        
    cur.close()