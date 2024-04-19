from savebestcommunities import save_best_communities

def main():

    for i in range(1, 1238): # 1238 is the last page as of April 2024
        save_best_communities.delay(i) # push to Redis

    print(f'Published messages to Redis. All OK.')

if __name__ == "__main__":
    main()