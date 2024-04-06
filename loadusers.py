from apiclient import *
from jsonpath_ng import parse

start_subreddit = 'HENRYFinance'
reddit_api = 'https://oauth.reddit.com'
author_expression = parse('$..author')

session_token = get_api_token()
api_pagination_cursor = None

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
        )
        if not sub_posts_response:
            print('Refreshing token')
            session_token = get_api_token()
            continue
        else: 
            sub_posts_response = sub_posts_response['data']
        
        authors = [record['data']['author'] for record in sub_posts_response['children']]
        
        
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

            authors.extend([match.value for match in author_expression.find(artcle_comments_response)])
            
        authors_set = set(authors)
        print('\n'.join(authors_set), file=usernames_write)
        print(f'Logged {len(authors_set)} users')
        
        if 'after' not in sub_posts_response['data'] or sub_posts_response['data']['after'] is None: 
            break
        else:
            api_pagination_cursor = sub_posts_response['data']['after']
            print(api_pagination_cursor)
    

print('Done collecting users') 
