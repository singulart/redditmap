import multiprocessing
from celery import Celery
from celery_batches import Batches
from celery.utils.log import get_task_logger
from apiclient import *
import sys 

sys.path.append('../celeryconfig')

reddit_api = 'https://oauth.reddit.com'

app = Celery(config_source='celeryconfig')
logger = get_task_logger(__name__)

@app.task(name='Fetches comments from /api/morechildren Reddit API', base=Batches, flush_every=200, flush_interval=10)
def getMoreComments(comments): # has `threadId` and `commentIds`
    
    # Celery threads are named ForkPoolThread-1, ForkPoolThread-2, ... (last character is a digit)    
    unique_thread_number = int(multiprocessing.current_process().name[-1])
    with open('tokens.txt', 'r') as token_file:
        tokens = token_file.read().splitlines()
        token_to_use = tokens[unique_thread_number - 1].rstrip()

        additional_comment_response = handle_api_call(f"{reddit_api}/api/morechildren",
                headers={
                    'Authorization': f'Bearer {token_to_use}',
                    'User-Agent': user_agent
                }, 
                params={
                    'children': ','.join(comments['commentIds']),
                    'link_id': comments['threadId'], 
                    'api_type': 'json',
                    'depth': 10000
                }
        )
        final_flat_list = []
        walk_comments_tree(additional_comment_response['json']['data']['things'], final_flat_list)

def walk_comments_tree(things, comments_flat = []): 
    for comment in things:
        if comment['kind'] == 'more': 
            getMoreComments.delay(','.join(comment['data']['children'])) # add un-fetched IDs to the same Celery queue
        else:
            comments_flat.extend(
                {
                    'id': comment['data']['id'],
                    'parent': comment['data']['parent_id'],
                    'body': comment['data']['body'],
                    'ups': comment['data']['ups'],
                    'thread': comment['data']['link_id'],
                    'author': comment['data']['author']
                }
            )
            
        walk_comments_tree(comment['data']['replies'], comments_flat)