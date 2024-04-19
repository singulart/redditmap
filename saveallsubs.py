# Saves names of all new Reddit subreddits to a database table

# Filters used:
# 1. Subscribers number
# 2. Public subreddits only

import sqlite3
from tqdm import tqdm
from jsonpath_ng.ext import parse
from apiclient import *

reddit_api = 'https://oauth.reddit.com'

subreddit_type = 'public'
minimum_subscribers = 50
subreddit_name_expression = parse(f"$..children[?(@.data.subreddit_type == {subreddit_type} & @.data.subscribers >= {minimum_subscribers})]..display_name")
# subreddit_name_expression = parse("$..display_name")


def main():

    session_token = get_api_token()

    api_pagination_cursor = None

    # Establish a connection to the SQLite database file
    conn = sqlite3.connect('reddit.db')

    # Create a cursor object using the connection
    cur = conn.cursor()

    # Create a table (if it does not already exist)
    cur.execute('CREATE TABLE IF NOT EXISTS reddit_subs (sub VARCHAR(64))')
    
    pbar = tqdm(desc="Processed", unit=" pages")

    i = 0
    try:     
        while True:
            subs_response = handle_api_call(f'{reddit_api}/subreddits/new',
                headers={
                    'Authorization': f'Bearer {session_token}',
                    'User-Agent': user_agent
                },
                params={
                    'limit': 100,
                    'after': api_pagination_cursor
                }
            )
            if not subs_response:
                break
                    
            sub_names = [(match.value, ) for match in subreddit_name_expression.find(subs_response)]
            
            # Inserting data into the table in a batch fashion
            cur.executemany('INSERT INTO reddit_subs (sub) VALUES (?)', sub_names)

            # Commit the transaction
            conn.commit()

            i += 1
            pbar.update(1)  # Increment the progress by 1 each iteration            
                        
            if 'after' not in subs_response['data'] or subs_response['data']['after'] is None: 
                break
            else:
                api_pagination_cursor = subs_response['data']['after']
                print(api_pagination_cursor)
                
    except KeyboardInterrupt:
        # Catch a keyboard interrupt (CTRL+C) to provide a way to stop the loop gracefully
        print("\nStopping...")
    finally:
        pbar.close()  # Ensure the progress bar is properly closed
        print("Task completed or stopped.")            

if __name__ == "__main__":
    main()