
import multiprocessing
from jsonpath_ng.ext import parse
from itertools import islice
import json
import sys
import os
from celery import Celery
from celery.utils.log import get_task_logger

sys.path.append('../celeryconfig')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from apiclient import *
from subs_extraction.CommentGrabberWorker import getMoreComments
from subs_extraction.CommentPersisterWorker import persistComments

reddit_api = 'https://oauth.reddit.com'

app = Celery(config_source='celeryconfig')
logger = get_task_logger(__name__)

more_comments_expression = parse("$..*[?(@.kind=='more')]..children[*]")

def chunked_iterable(iterable, size):
    """Yield successive chunks of given size from an iterable."""
    it = iter(iterable)
    while chunk := list(islice(it, size)):
        yield chunk

@app.task(name='Save posts and comments for a given subreddit')
def process_posts_type(target_subreddit, post_type): 
    logger.info(f'Processing {post_type} posts')
    comments_counter = 0;
    api_pagination_cursor = None
    
    # Celery threads are named ForkPoolThread-1, ForkPoolThread-2, ... (last character is a digit)    
    unique_thread_number = int(multiprocessing.current_process().name[-1])
    with open('tokens.txt', 'r') as token_file:
        tokens = token_file.read().splitlines()
        token_to_use = tokens[unique_thread_number - 1].rstrip()

    while True:
        posts_response = handle_api_call(f'{reddit_api}/r/{target_subreddit}/{post_type}',
            headers={
                'Authorization': f'Bearer {token_to_use}',
                'User-Agent': user_agent
            },
            params={
                'limit': 100,
                'after': api_pagination_cursor
            }
        )
        if not posts_response:
            break

        # print(json.dumps(posts_response['data'], indent=4))
        
        # Data points of interest
        # 1. num_comments
        # 2. id
        # 3. selftext
        # 4. title
                
        for thread in posts_response['data']['children']:
            if thread['data']['num_comments'] > 0:
                artcle_comments_response = handle_api_call(f"{reddit_api}/r/{target_subreddit}/comments/{thread['data']['id']}",
                            headers={
                                'Authorization': f'Bearer {token_to_use}',
                                'User-Agent': user_agent
                            }, 
                            params={
                                'limit': 10000,
                                'depth': 10000
                            }
                )
                # TODO persist threads
                # print(json.dumps(artcle_comments_response, indent=4))
                            
                for listing in artcle_comments_response:
                    for comment in listing['data']['children']:
                        if comment['kind'] == 't1': 
                            persistComments.delay(
                                {
                                    'comment_id': comment['data']['id'],
                                    'parent_id': comment['data']['parent_id'],
                                    'body': comment['data']['body'],
                                    'score': comment['data']['ups'],
                                    'created_at': comment['data']['created'],
                                    'post_id': comment['data']['link_id'],
                                    'author': comment['data']['author']
                                }
                            )
                            comments_counter += 1

                additional_comment_ids = [match.value for match in more_comments_expression.find(artcle_comments_response)]
                if len(additional_comment_ids) > 0 and additional_comment_ids[0] == '_': 
                    continue
                if len(additional_comment_ids) == 0: 
                    continue
               
                # send to Celery / Redis
                getMoreComments.delay({
                    'threadId': thread['data']['id'],
                    'commentIds': additional_comment_ids
                })
                comments_counter += len(additional_comment_ids)
                
        if 'after' not in posts_response['data'] or posts_response['data']['after'] is None: 
            break
        else:
            api_pagination_cursor = posts_response['data']['after']
            logger.info(api_pagination_cursor)

    logger.info(f"Processed {comments_counter} comments")
