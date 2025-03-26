
from jsonpath_ng.ext import parse
from itertools import islice
import json
import sys
import os
sys.path.append('../celeryconfig')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from apiclient import *
from CommentGrabberWorker import getMoreComments
from CommentPersisterWorker import persistComments

reddit_api = 'https://oauth.reddit.com'

author_expression = parse('$..author')

comment_expression = parse('$..body')
more_comments_expression = parse("$..*[?(@.kind=='more')]..children[*]")

chunk_size = 200


def chunked_iterable(iterable, size):
    """Yield successive chunks of given size from an iterable."""
    it = iter(iterable)
    while chunk := list(islice(it, size)):
        yield chunk

def process_posts_type(target_subreddit, post_type, session_token): 
    # print(f'Processing {post_type} posts')
    api_pagination_cursor = None
    while True:
        posts_response = handle_api_call(f'{reddit_api}/r/{target_subreddit}/{post_type}',
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

        # print(json.dumps(posts_response['data'], indent=4))
        
        # Data points of interest
        # 1. num_comments
        # 2. id
        # 3. selftext
        # 4. title
        
        
        print('++++++++++++++++++++++++++++++++++++++++++++')
                       
        # authors = [match.value for match in author_expression.find(posts_response)]
        # for user in authors:
        #     process_redditor_activity.delay(user.rstrip()) # push to Redis
        # redditors.extend(authors) # this is more for statistics
        
        
        for thread in posts_response['data']['children']:
            if thread['data']['num_comments'] > 0:
                artcle_comments_response = handle_api_call(f"{reddit_api}/r/{target_subreddit}/comments/{thread['data']['id']}",
                            headers={
                                'Authorization': f'Bearer {session_token}',
                                'User-Agent': user_agent
                            }, 
                            params={
                                'limit': 10000,
                                'depth': 10000
                            }
                )
                # TODO persist threads
                # print(json.dumps(artcle_comments_response, indent=4))
                # print(json.dumps(artcle_comments_response, indent=4))
                            
                for listing in artcle_comments_response:
                    for comment in listing['data']['children']:
                        if comment['kind'] == 't1': 
                            persistComments.delay(
                                {
                                    'comment_id': comment['data']['id'],
                                    'parent_id': comment['data']['parent_id'],
                                    'body': comment['data']['body'],
                                    'score': comment['data']['ups'],
                                    'created_at': comment['data']['created'],
                                    'post_id': comment['data']['link_id'],
                                    'author': comment['data']['author']
                                }
                            )

                additional_comment_ids = [match.value for match in more_comments_expression.find(artcle_comments_response)]
                if len(additional_comment_ids) > 0 and additional_comment_ids[0] == '_': 
                    continue
                if len(additional_comment_ids) == 0: 
                    continue
               
                # send to Celery / Redis
                getMoreComments.delay({
                    'threadId': thread['data']['id'],
                    'commentIds': additional_comment_ids
                })
                
        if 'after' not in posts_response['data'] or posts_response['data']['after'] is None: 
            break
        else:
            api_pagination_cursor = posts_response['data']['after']
            print(api_pagination_cursor)
    

def main():
    
    session_token = get_api_token()

    target_subreddit = 'SaaS'
    process_posts_type(target_subreddit, 'new', session_token)
    process_posts_type(target_subreddit, 'top', session_token)
    process_posts_type(target_subreddit, 'hot', session_token)
    process_posts_type(target_subreddit, 'controversial', session_token)

    # for redditor in redditor_set:
    #     process_redditor_activity.delay(redditor) # push to Redis

    # print(f'Sent users to Redis. All OK.')

if __name__ == "__main__":
    main()