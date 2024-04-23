# Creates Celery tasks to categorize subreddits and publishes those to Redis.
# Every task is a 50 subreddits strong mini-batch

import sqlite3
from tqdm import tqdm
from AiCategorizationWorker import categorize

def main():

    conn = sqlite3.connect('reddit.db')
    cur = conn.cursor()
    
    page_size = 50
    cur.execute("select count(*) from reddit_subs_best")
    total_subreddits = cur.fetchone()[0]
    total_pages_to_load = total_subreddits // page_size
    if total_subreddits % page_size != 0:
        total_pages_to_load += 1
    for i in tqdm(range(total_pages_to_load)): 
        cur.execute(f"select row_number() over() || '. ' || sub  from (select sub from reddit_subs_best order by sub limit {page_size} offset {i*page_size})") 
        i += 1
        categorize.delay('\n'.join([row for (row,) in cur]))

if __name__ == "__main__":
    main()