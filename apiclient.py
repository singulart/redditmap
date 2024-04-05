import requests
import time
import os

user_agent = 'web:net.ua.singulart:v0.1.0 (by /u/reddit)'

def get_api_token():
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
    return session_token

def handle_api_call(reddit_api, headers, params = {}):
    while True:
        api_response = requests.get(reddit_api, headers=headers, params=params)
        
        rate_limit_remaining = api_response.headers['X-Ratelimit-Remaining']
        if rate_limit_remaining and float(rate_limit_remaining) < 10: # preventive check for low remaining requests
            print(f'Low rate limit remaining requests... {rate_limit_remaining}')
            time.sleep(5) # hopefully this would prevent longer waits when the limit is hit
        if api_response.status_code == 429:
            rate_limit_reset_in = api_response.headers['X-Ratelimit-Reset']
            print(f'Sleeping until rate limit resets... {rate_limit_reset_in} sec.')
            time.sleep(int(rate_limit_reset_in) + 5) # sleep needed time + some extra seconds
        if api_response.status_code == 403:
            session_token = get_api_token();
            headers['Authorization'] = f'Bearer {session_token}'
            print(f'Token expired... Requested new one.')
            time.sleep(5)
        elif api_response.status_code != 200:
            print(f'Error code {api_response.status_code} with payload: {api_response.text}')
            return {"data": {"children": [{"data": {"subreddit": "dummy"}}]}}
        else:             
            return api_response.json()