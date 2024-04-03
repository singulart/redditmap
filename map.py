import requests
import os

user_agent = 'web:net.ua.singulart:v0.0.1 (by /u/reddit)'

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

print(session_token)
