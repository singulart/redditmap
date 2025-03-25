from subs_extraction.PersistBestSubsWorker import save_best_communities

def main():

    # 682 is the page where under 100 users groups begin. 

    for i in range(1, 682): 
        save_best_communities.delay(i) # push to Redis

    print(f'Published messages to Redis. All OK.')

if __name__ == "__main__":
    main()