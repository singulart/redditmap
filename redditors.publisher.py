from apiclient import *
from jsonpath_ng import parse
import sys

from processusers import process_redditor_activity

reddit_api = 'https://oauth.reddit.com'
author_expression = parse('$..author')

def process_posts_type(start_subreddit, post_type, redditors, session_token): 
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
    

def publish_users_from_search_results(search_term, redditors, session_token): 
    print(f'Processing {search_term} search results')
    api_pagination_cursor = None
    while True:
        posts_response = handle_api_call(f'{reddit_api}/r/all/search.json',
            headers={
                'Authorization': f'Bearer {session_token}',
                'User-Agent': user_agent
            },
            params={
                'limit': 100,
                't': 'all',
                'q': search_term,
                'after': api_pagination_cursor
            }
        )
        if not posts_response:
            break
                
        authors = [match.value.strip() for match in author_expression.find(posts_response)]
        redditors.extend(authors) # this is more for statistics
        
        for record in posts_response['data']['children']:
            subreddit_id = record['data']['subreddit_id']
            # print(f"{reddit_api}/r/{subreddit_id}/comments/{record['data']['id']}")
            artcle_comments_response = handle_api_call(f"{reddit_api}/r/all/comments/{record['data']['id']}",
                        headers={
                            'Authorization': f'Bearer {session_token}',
                            'User-Agent': user_agent
                        }
            )
            if not artcle_comments_response:
                break
            
            authors = [match.value.strip() for match in author_expression.find(artcle_comments_response)]
            redditors.extend(authors) 
                    
        
        print(f'Found {len(redditors)} non-unique users so far..')
        
        if 'after' not in posts_response['data'] or posts_response['data']['after'] is None: 
            break
        else:
            api_pagination_cursor = posts_response['data']['after']
            print(api_pagination_cursor)

def main():
    
    session_token = get_api_token()

    redditors = []
    
    ## Extract from search results
    q = 'Tom Ford'
    publish_users_from_search_results(q, redditors, session_token)
    
    ## Or extract from one source reddit
    # start_subreddit = 'HENRYFinance'
    # process_posts_type(start_subreddit, 'new', redditors, session_token)
    # process_posts_type(start_subreddit, 'top', redditors, session_token)
    # process_posts_type(start_subreddit, 'hot', redditors, session_token)
    # process_posts_type(start_subreddit, 'controversial', redditors, session_token)

    redditor_set = set(redditors)
    print(f'Total unique redditors: {len(redditor_set)}')

    for redditor in redditor_set:
        process_redditor_activity.delay(redditor) # push to Redis

    print(f'Sent users to Redis. All OK.')

if __name__ == "__main__":
    main()