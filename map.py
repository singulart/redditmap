# Cleanup of noise subreddits:
# sed -i -- 's/\[\[AskReddit\]\]//g' obsidian-map/*.md

from jsonpath_ng import parse
import os
from apiclient import *

reddit_api = 'https://oauth.reddit.com'
blacklist_usernames = ['AutoModerator', '[deleted]']

subreddit_expression = parse('$..subreddit')

session_token = get_api_token()

api_pagination_cursor = None

with open('backlog.txt', 'r') as redditors_backlog:
    while redditor := redditors_backlog.readline():
        file_path = './obsidian-map/{}.md'.format(redditor.rstrip())
        if os.path.exists(file_path): 
            print('Redditor {} already processed'.format(redditor.rstrip()))
            continue
        if redditor.rstrip() in blacklist_usernames: 
            continue
        with open('./obsidian-map/{}.md'.format(redditor.rstrip()), 'w') as obsidian_note_file:
            print('---', file=obsidian_note_file)
            print('Type: Redditor', file=obsidian_note_file)
            print('---', file=obsidian_note_file)
            
            print('Fetching Redditor {} posts...'.format(redditor.rstrip()))
            api_pagination_cursor = None;
            subreddits = []
            while True:
                posts_response = handle_api_call(f'{reddit_api}/user/{redditor}/submitted',
                    headers= {
                        'Authorization': f'Bearer {session_token}',
                        'User-Agent': user_agent
                    },
                    params={
                        'limit': 100,
                        'after': api_pagination_cursor
                    }
                )
                if not posts_response or 'data' not in posts_response:
                    print('Refreshing token')
                    session_token = get_api_token()
                    continue
                
                subreddits.extend(['[[{}]]'.format(match.value) for match in subreddit_expression.find(posts_response)]) 
                    
                if 'after' not in posts_response['data'] or posts_response['data']['after'] is None: # we're at last page
                    break
                else:
                    api_pagination_cursor = posts_response['data']['after']
                    print(api_pagination_cursor)
                    
            print('Fetching Redditor {} comments...'.format(redditor.rstrip()))
            api_pagination_cursor = None;

            while True:
                comments_response = handle_api_call(f'{reddit_api}/user/{redditor}/comments',
                    headers= {
                        'Authorization': f'Bearer {session_token}',
                        'User-Agent': user_agent
                    },
                    params={
                        'limit': 100,
                        'after': api_pagination_cursor
                    }
                )
                if not comments_response:
                    print('Refreshing token')
                    session_token = get_api_token()
                    continue

                subreddits.extend(['[[{}]]'.format(match.value) for match in subreddit_expression.find(comments_response)]) 
                    
                if 'after' not in comments_response['data'] or comments_response['data']['after'] is None: 
                    break
                else:
                    api_pagination_cursor = comments_response['data']['after']
                    print(api_pagination_cursor)
                    
            print(', '.join(set(subreddits)), file=obsidian_note_file)

