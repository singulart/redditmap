import requests
import os

user_agent = 'web:net.ua.singulart:v0.0.1 (by /u/reddit)'
reddit_api = 'https://oauth.reddit.com'

if 'CLIENT_ID' not in os.environ and 'CLIENT_SECRET' not in os.environ: 
    print('Provide both CLIENT_ID and CLIENT_SECRET')
    exit(1)
    
reddit_oauth2_client_id = os.environ['CLIENT_ID']
reddit_oauth2_client_secret = os.environ['CLIENT_SECRET']

auth_token_response = requests.post(
            'https://www.reddit.com/api/v1/access_token', 
            auth = (reddit_oauth2_client_id, reddit_oauth2_client_secret),
            headers = {
                 'Content-Type': 'application/x-www-form-urlencoded',
                 'User-Agent': user_agent
            },
            data = {
                'grant_type': 'client_credentials', 
                'scope': 'history'
            }
)

session_token = auth_token_response.json()['access_token']


with open('backlog.txt') as usernames:
    while redditor := usernames.readline():
        with open('./obsidian-map/{}.md'.format(redditor.rstrip()), 'w') as obsidian_note_file:
            print('Fetching user {} posts...'.format(redditor.rstrip()))
            api_pagination_cursor = None;
            while True:
                posts_response = requests.get(reddit_api + '/user/' + redditor + '/submitted',
                            headers={
                                'Authorization': 'Bearer ' + session_token,
                                'User-Agent': user_agent
                            },
                            params={
                                'limit': 100,
                                'after': api_pagination_cursor
                            }
                ).json()
                                
                for record in posts_response['data']['children']: 
                    print('[[{}]]'.format(record['data']['subreddit']), file=obsidian_note_file)
                    
                if 'after' not in posts_response['data'] or posts_response['data']['after'] is None: 
                    break
                else:
                    api_pagination_cursor = posts_response['data']['after']
                    print(api_pagination_cursor)
                    
            print('Fetching user {} comments...'.format(redditor.rstrip()))
            api_pagination_cursor = None;

            while True:
                comments_response = requests.get(reddit_api + '/user/' + redditor + '/comments',
                            headers={
                                'Authorization': 'Bearer ' + session_token,
                                'User-Agent': user_agent
                            },
                            params={
                                'limit': 100,
                                'after': api_pagination_cursor
                            }
                ).json()
                
                for record in comments_response['data']['children']: 
                    print('[[{}]]'.format(record['data']['subreddit']), file=obsidian_note_file)
                    
                if 'after' not in posts_response['data'] or posts_response['data']['after'] is None: 
                    break
                else:
                    api_pagination_cursor = comments_response['data']['after']
                    print(api_pagination_cursor)
