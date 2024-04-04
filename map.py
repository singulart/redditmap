# Cleanup of noise subreddits:
# sed -i -- 's/\[\[AskReddit\]\]//g' obsidian-map/*.md


import requests
import os

blacklist_usernames = ['AutoModerator', '[deleted]']
user_agent = 'web:net.ua.singulart:v0.0.1 (by /u/reddit)'
reddit_api = 'https://oauth.reddit.com'
start_subreddit = 'TheHermesGame'


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
        sub_posts_response = requests.get(reddit_api + '/r/' + start_subreddit + '/new',
                    headers={
                        'Authorization': 'Bearer ' + session_token,
                        'User-Agent': user_agent
                    },
                    params={
                        'limit': 100,
                        'after': api_pagination_cursor
                    }
        ).json()

        authors = set([record['data']['author'] for record in sub_posts_response['data']['children']]) 
        print('\n'.join(authors), file=usernames_write)
        if 'after' not in sub_posts_response['data'] or sub_posts_response['data']['after'] is None: 
            break
        else:
            api_pagination_cursor = sub_posts_response['data']['after']
            print(api_pagination_cursor)
    


with open('backlog.txt', 'r') as usernames:
    while redditor := usernames.readline():
        file_path = './obsidian-map/{}.md'.format(redditor.rstrip())
        if os.path.exists(file_path): 
            print('User {} already processed'.format(redditor.rstrip()))
            continue
        if redditor.rstrip() in blacklist_usernames: 
            continue
        with open('./obsidian-map/{}.md'.format(redditor.rstrip()), 'w') as obsidian_note_file:
            print('---', file=obsidian_note_file)
            print('Type: Redditor', file=obsidian_note_file)
            print('---', file=obsidian_note_file)
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

                subreddits = set(['[[{}]]'.format(record['data']['subreddit']) for record in posts_response['data']['children']]) 
                print(', '.join(subreddits), file=obsidian_note_file)
                    
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
                
                subreddits = set(['[[{}]]'.format(record['data']['subreddit']) for record in comments_response['data']['children']]) 
                print(', '.join(subreddits), file=obsidian_note_file)
                    
                if 'after' not in comments_response['data'] or comments_response['data']['after'] is None: 
                    break
                else:
                    api_pagination_cursor = comments_response['data']['after']
                    print(api_pagination_cursor)
