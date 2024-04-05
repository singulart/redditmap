import requests
import time

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
        elif api_response.status_code != 200:
            print(f'Error code {api_response.status_code} with payload: {api_response.text}')
            return {"data": {"children": [{"data": {"subreddit": "dummy"}}]}}
        else:             
            return api_response.json()