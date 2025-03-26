from FetchEntireSubWorker import process_posts_type

def main():

    sub = 'Saas'
    post_types = ['new', 'top', 'hot', 'controversial']
    
    for post_type in post_types: 
        process_posts_type.delay(sub, post_type) # push to Redis

    print(f'Published messages to Redis. All OK.')

if __name__ == "__main__":
    main()