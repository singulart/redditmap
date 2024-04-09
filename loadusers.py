from apiclient import *
from jsonpath_ng import parse

from processusers import process_redditor_activity

def main():
    start_subreddit = 'HENRYFinance'
    reddit_api = 'https://oauth.reddit.com'
    author_expression = parse('$..author')

    session_token = get_api_token()
    api_pagination_cursor = None

    redditors = []
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
        )
        if not sub_posts_response:
            print('Refreshing token')
            session_token = get_api_token()
            continue
        else: 
            sub_posts_response = sub_posts_response['data']
        
        redditors.extend([record['data']['author'] for record in sub_posts_response['children']])
        
        
        for record in sub_posts_response['children']:
            artcle_comments_response = handle_api_call(f"{reddit_api}/r/{start_subreddit}/comments/{record['data']['id']}",
                        headers={
                            'Authorization': f'Bearer {session_token}',
                            'User-Agent': user_agent
                        }
            )
            if not artcle_comments_response:
                print('Refreshing token')
                session_token = get_api_token()
                continue

            redditors.extend([match.value for match in author_expression.find(artcle_comments_response)])
                    
        
        print(f'Found {len(redditors)} non-unique users so far..')
        
        if 'after' not in sub_posts_response or sub_posts_response['after'] is None: 
            break
        else:
            api_pagination_cursor = sub_posts_response['after']
            print(api_pagination_cursor)
        

    redditor_set = set(redditors)
    print(f'Total unique redditors: {len(redditor_set)}')

    for redditor in redditor_set:
        process_redditor_activity.delay(redditor)

    print(f'Sent users to Redis. All OK.')

if __name__ == "__main__":
    main()