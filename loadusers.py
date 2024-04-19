from apiclient import *
from jsonpath_ng import parse

from processusers import process_redditor_activity

start_subreddit = 'HENRYFinance'
reddit_api = 'https://oauth.reddit.com'
author_expression = parse('$..author')

def process_posts_type(post_type, redditors, session_token): 
    print(f'Processing {post_type} posts')
    api_pagination_cursor = None
    while True:
        posts_response = handle_api_call(f'{reddit_api}/r/{start_subreddit}/{post_type}',
            headers={
                'Authorization': f'Bearer {session_token}',
                'User-Agent': user_agent
            },
            params={
                'limit': 100,
                'after': api_pagination_cursor
            }
        )
        if not posts_response:
            break
                
        authors = [match.value for match in author_expression.find(posts_response)]
        for user in authors:
            process_redditor_activity.delay(user.rstrip()) # push to Redis
        redditors.extend(authors) # this is more for statistics
        
        
        for record in posts_response['data']['children']:
            artcle_comments_response = handle_api_call(f"{reddit_api}/r/{start_subreddit}/comments/{record['data']['id']}",
                        headers={
                            'Authorization': f'Bearer {session_token}',
                            'User-Agent': user_agent
                        }
            )
            if not artcle_comments_response:
                break

            authors = [match.value for match in author_expression.find(artcle_comments_response)]
            for user in authors:
                process_redditor_activity.delay(user.rstrip()) # push to Redis
            redditors.extend(authors) # this is more for statistics
                    
        
        print(f'Found {len(redditors)} non-unique users so far..')
        
        if 'after' not in posts_response['data'] or posts_response['data']['after'] is None: 
            break
        else:
            api_pagination_cursor = posts_response['data']['after']
            print(api_pagination_cursor)
    


def main():

    session_token = get_api_token()

    redditors = []
    process_posts_type('new', redditors, session_token)
    process_posts_type('top', redditors, session_token)
    process_posts_type('hot', redditors, session_token)
    process_posts_type('controversial', redditors, session_token)

    redditor_set = set(redditors)
    print(f'Total unique redditors: {len(redditor_set)}')

    for redditor in redditor_set:
        process_redditor_activity.delay(redditor.rstrip()) # push to Redis

    print(f'Sent users to Redis. All OK.')

if __name__ == "__main__":
    main()