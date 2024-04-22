# Creates Celery tasks to categorize subreddits and publishes those to Redis.
# Every task is a 50 subreddits strong mini-batch

import sqlite3
from AiCategorizationWorker import categorize

def main():

    # Establish a connection to the SQLite database file
    conn = sqlite3.connect('reddit.db')
    cur = conn.cursor()
    
    page_size = 50
    for i in range(5): # TODO scan entire table 
        cur.execute(f"select row_number() over() || '. ' || sub  from (select sub from reddit_subs_best order by sub limit {page_size} offset {i*page_size})") 
        i += 1
        subreddits = '\n'.join([row for (row,) in cur])
        categorize.delay(subreddits)

    print('Done.')

if __name__ == "__main__":
    main()