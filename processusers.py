# Cleanup of noise subreddits:
# sed -i -- 's/\[\[AskReddit\]\]//g' obsidian-map/*.md

from celery import Celery
from celery.utils.log import get_task_logger
from jsonpath_ng import parse
import os
import multiprocessing

from oauth import replace_token
from apiclient import *

reddit_api = 'https://oauth.reddit.com'
blacklist_usernames = ['AutoModerator', '[deleted]']

subreddit_expression = parse('$..subreddit')

logger = get_task_logger(__name__)

app = Celery(config_source='celeryconfig')

@app.task(name='Process Redditor activity')
def process_redditor_activity(redditor):
    
    file_path = './obsidian-map/{}.md'.format(redditor)
    if os.path.exists(file_path): 
        logger.info('Redditor {} already processed'.format(redditor))
        return
    if redditor in blacklist_usernames: 
        return

    with open('noise_subreddits.txt', 'r') as noise_file:
        noise_subs = noise_file.read().splitlines()

    # Celery threads are named ForkPoolThread-1, ForkPoolThread-2, ... (last character is a digit)    
    unique_thread_number = int(multiprocessing.current_process().name[-1])
    with open('tokens.txt', 'r') as token_file:
        tokens = token_file.read().splitlines()
        token_to_use = tokens[unique_thread_number - 1].rstrip()
    
    
    with open('./obsidian-map/{}.md'.format(redditor), 'w') as obsidian_note_file:
        print('---', file=obsidian_note_file)
        print('Type: Redditor', file=obsidian_note_file)
        print('---', file=obsidian_note_file)
        
        logger.info('Fetching Redditor {} posts...'.format(redditor))
        api_pagination_cursor = None;
        subreddits = []
        while True:
            posts_response = handle_api_call(f'{reddit_api}/user/{redditor}/submitted',
                headers= {
                    'Authorization': f'Bearer {token_to_use}',
                    'User-Agent': user_agent
                },
                params={
                    'limit': 100,
                    'after': api_pagination_cursor
                }
            )
            if not posts_response or 'data' not in posts_response:
                logger.info('Refreshing token')
                replace_token(unique_thread_number - 1)
                break
            
            subreddits.extend(['[[{}]]'.format(match.value) for match in subreddit_expression.find(posts_response) if match.value not in noise_subs]) 
                
            if 'after' not in posts_response['data'] or posts_response['data']['after'] is None: # we're at last page
                break
            else:
                api_pagination_cursor = posts_response['data']['after']
                logger.info(api_pagination_cursor)
                
        logger.info('Fetching Redditor {} comments...'.format(redditor))
        api_pagination_cursor = None;

        while True:
            comments_response = handle_api_call(f'{reddit_api}/user/{redditor}/comments',
                headers= {
                    'Authorization': f'Bearer {token_to_use}',
                    'User-Agent': user_agent
                },
                params={
                    'limit': 100,
                    'after': api_pagination_cursor
                }
            )
            if not comments_response:
                logger.info('Refreshing token')
                replace_token(unique_thread_number - 1)
                break

            subreddits.extend(['[[{}]]'.format(match.value) for match in subreddit_expression.find(comments_response) if match.value not in noise_subs]) 
                
            if 'after' not in comments_response['data'] or comments_response['data']['after'] is None: 
                break
            else:
                api_pagination_cursor = comments_response['data']['after']
                logger.info(api_pagination_cursor)
                
        print(', '.join(set(subreddits)), file=obsidian_note_file)

