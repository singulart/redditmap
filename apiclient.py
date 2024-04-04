import requests
import time

def handle_api_call(reddit_api, headers, params = {}):
    while True:
        api_response = requests.get(reddit_api, headers=headers, params=params)
        
        if api_response.status_code != 200:
            print(f'API returned non-OK payload: {api_response.text}')

            # rate_limit_remaining = api_response.headers['X-Ratelimit-Remaining']
            # print(f"X-Ratelimit-Remaining={rate_limit_remaining}")
            
            rate_limit_reset_in = api_response.headers['X-Ratelimit-Reset']
            print(f'Sleeping until rate limit resets... {rate_limit_reset_in} sec.')
            time.sleep(int(rate_limit_reset_in) + 5) # sleep needed time + some extra seconds
        else:             
            return api_response.json()