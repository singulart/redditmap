### WARNING: Running this code will spend funds from your OpenAI platform credit. 
### Refer to https://platform.openai.com/settings/organization/billing/overview for more details.
import multiprocessing
import sqlite3
import re
from openai import OpenAI
from celery import Celery
from celery.utils.log import get_task_logger

app = Celery(config_source='celeryconfig')
logger = get_task_logger(__name__)

@app.task(name='Categorize subreddits using ChatGPT')
def categorize(subreddits_list):


    conn = sqlite3.connect('reddit.db')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS reddit_subs_categorized (sub VARCHAR(64), cat VARCHAR(32), subcat VARCHAR(64), niche VARCHAR(64))')


    # Celery threads are named ForkPoolThread-1, ForkPoolThread-2, ... (last character is a digit)
    unique_thread_number = int(multiprocessing.current_process().name[-1])
    with open('chatgpt_tokens.txt', 'r') as token_file:
        tokens = token_file.read().splitlines()
        token_to_use = tokens[unique_thread_number - 1].rstrip()
    
        chatGPT_client = OpenAI(api_key=token_to_use)
        
        response_turbo = chatGPT_client.chat.completions.create(
            model="gpt-4-turbo-2024-04-09",
            messages=[
                {"role": "system", "content":
                f""" For every Reddit subreddit below
{subreddits_list}
find three levels of categories, from the most specific one to the most generic one. Output all three like so:
x. <Most generic Category>, <More specific category>, <Most specific category>
"x" is the position of a subreddit in the list. 
Use alphanumeric characters only. Limit every category to maximum of three words. Do NOT output anything else. Do this for every input subreddit, don't skip anything.
"""             }]
            )
        chatGpt_response = response_turbo.choices[0].message.content
        logger.info("Got AI response. Parsing...")
        
        subreddits_list_no_numbers = [re.sub(r'(\d+\. )', '', s) for s in subreddits_list.split('\n') if s != '']
        data_to_store = []
        split = [cg for cg in chatGpt_response.split('\n') if cg != '']
        for iii in range(len(split)):
            categorized_sub = re.sub(r'(\d+\. )', '', split[iii])
            categories = [c.strip() for c in categorized_sub.split(', ')]
            if len(categories) != 3: 
                logger.warn(categories)
            data_to_store.append((subreddits_list_no_numbers[iii], *categories, ))
        
        logger.info("Storing categorized subreddits...")
        try: 
            cur.executemany('INSERT INTO reddit_subs_categorized (sub, cat, subcat, niche) VALUES (?, ?, ?, ?)', data_to_store)
            conn.commit()
        except sqlite3.ProgrammingError as er:
            logger.error(er.sqlite_errorname)
            logger.warn(data_to_store)
        finally:
            conn.close()
