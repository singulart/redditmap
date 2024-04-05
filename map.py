# Cleanup of noise subreddits:
# sed -i -- 's/\[\[AskReddit\]\]//g' obsidian-map/*.md

from jsonpath_ng import parse
import os
from apiclient import *

reddit_api = 'https://oauth.reddit.com'
blacklist_usernames = ['AutoModerator', '[deleted]']
start_subreddit = 'HENRYFinance'

author_expression = parse('$..author')

session_token = get_api_token()

api_pagination_cursor = None;
with open('backlog.txt', 'w') as usernames_write:
    while True:
        sub_posts_response = handle_api_call(f'{reddit_api}/r/{start_subreddit}/new',
                    headers={
                        'Authorization': f'Bearer {session_token}',
                        'User-Agent': user_agent
                    },
                    params={
                        'limit': 100,
                        'after': api_pagination_cursor
                    }
        )['data']
        authors = [record['data']['author'] for record in sub_posts_response['children']]
        
        
        for record in sub_posts_response['children']:
            artcle_comments_response = handle_api_call(f"{reddit_api}/r/{start_subreddit}/comments/{record['data']['id']}",
                        headers={
                            'Authorization': f'Bearer {session_token}',
                            'User-Agent': user_agent
                        }
            )
            authors.extend([match.value for match in author_expression.find(artcle_comments_response)])
        
        
        authors_set = set(authors)
        print('\n'.join(authors_set), file=usernames_write)
        print(f'Logged {len(authors_set)} users')
        
        if 'after' not in sub_posts_response or sub_posts_response['after'] is None: 
            break
        else:
            api_pagination_cursor = sub_posts_response['after']
            print(api_pagination_cursor)
    

# print('Done collecting users') 

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
            while True:
                posts_response = handle_api_call(f'{reddit_api}/user/{redditor}/submitted',
                            headers={
                                'Authorization': f'Bearer {session_token}',
                                'User-Agent': user_agent
                            },
                            params={
                                'limit': 100,
                                'after': api_pagination_cursor
                            }
                )['data']
                subreddits = set(['[[{}]]'.format(record['data']['subreddit']) for record in posts_response['children']]) 
                print(', '.join(subreddits), file=obsidian_note_file)
                    
                if 'after' not in posts_response or posts_response['after'] is None: # we're at last page
                    break
                else:
                    api_pagination_cursor = posts_response['after']
                    print(api_pagination_cursor)
                    
            print('Fetching Redditor {} comments...'.format(redditor.rstrip()))
            api_pagination_cursor = None;

            while True:
                comments_response = handle_api_call(f'{reddit_api}/user/{redditor}/comments',
                            headers={
                                'Authorization': f'Bearer {session_token}',
                                'User-Agent': user_agent
                            },
                            params={
                                'limit': 100,
                                'after': api_pagination_cursor
                            }
                )['data']

                subreddits = set(['[[{}]]'.format(record['data']['subreddit']) for record in comments_response['children']]) 
                print(', '.join(subreddits), file=obsidian_note_file)
                    
                if 'after' not in comments_response or comments_response['after'] is None: 
                    break
                else:
                    api_pagination_cursor = comments_response['after']
                    print(api_pagination_cursor)
