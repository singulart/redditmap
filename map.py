# Cleanup of noise subreddits:
# sed -i -- 's/\[\[AskReddit\]\]//g' obsidian-map/*.md

from jsonpath_ng import jsonpath, parse
import requests
import os
from apiclient import handle_api_call

blacklist_usernames = ['AutoModerator', '[deleted]']
user_agent = 'web:net.ua.singulart:v0.1.0 (by /u/reddit)'
reddit_api = 'https://oauth.reddit.com'
start_subreddit = 'TheHermesGame'

author_expression = parse('$..author')

if 'CLIENT_ID' not in os.environ and 'CLIENT_SECRET' not in os.environ: 
    print('Provide both CLIENT_ID and CLIENT_SECRET')
    exit(1)
    
reddit_oauth2_client_id = os.environ['CLIENT_ID']
reddit_oauth2_client_secret = os.environ['CLIENT_SECRET']

auth_token_response = requests.post(
            'https://www.reddit.com/api/v1/access_token', 
            auth = (reddit_oauth2_client_id, reddit_oauth2_client_secret), # basic auth base64-encoded
            headers = {
                 'Content-Type': 'application/x-www-form-urlencoded',
                 'User-Agent': user_agent # NEVER lie about your User-Agent. 
            },
            data = {
                'grant_type': 'client_credentials', # https://auth0.com/docs/authenticate/login/oidc-conformant-authentication/oidc-adoption-client-credentials-flow
                'scope': 'history read'
            }
)

session_token = auth_token_response.json()['access_token']
print('Obtained Reddit JWT token')

api_pagination_cursor = None;
with open('backlog.txt', 'w') as usernames_write:
    while True:
        sub_posts_response = handle_api_call(f'{reddit_api}/r/{start_subreddit}/new',
                    headers={
                        'Authorization': 'Bearer ' + session_token,
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
                            'Authorization': 'Bearer ' + session_token,
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
    

print('Done collecting users') 

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
                                'Authorization': 'Bearer ' + session_token,
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
                                'Authorization': 'Bearer ' + session_token,
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
