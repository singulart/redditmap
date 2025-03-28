# Reddit user activity visualizer

Walks over posts and comments of Reddit users and forms an insightful map


## Redis dependency

This tool uses Celery library with Redis broker as a backend. Tested on 64 bit Redis v7.2.4

Run Redis locally with 1-minute data persistence interval: `docker run --name reddit -d -p 6379:6379 redis redis-server --save 60 1`
Data persistence makes data written to Redis available after restart.

To connect to Redis using nice UI, use Redis Insight app. 

Alternatively, connecting to the running Redis instance using `redis-cli` is also possible: 

- Create a network `docker network create reddit-network`
- Connect a network to the container `docker network connect reddit-network reddit`
- Run CLI `docker run -it --network reddit-network --rm redis redis-cli -h reddit`


## Reddit API clients config file structure

Reddit allows 3 (three) [developer applications](https://old.reddit.com/prefs/apps/) (API clients) per account. Create all three and fill out the file `appconfig.json` as follows:

```json
{
    "apps": [
        {
            "client_id": "client id",
            "client_secret": "client secret",
            "user_agent": "unique user agent"
        },
        ...
    ]
}
```

## Subreddit names downloading: order of execution

### Run Redis docker container and execute the script:

[text](best.subs.grab.publisher.py)

Note: Update the counter inside if needed (currently set to 1285)

### Run Celery task that fetches subreddits and saves to SQLite3 db

From terminal: `celery --app=subs_extraction.PersistBestSubsWorker worker -l info`

Note: this may produce a lot of 429 errors. 

### Check data in SQLite

From terminal: `sqlite3 reddit.db`

`select count(*) from reddit_subs_best;`

### Deduplicate records

Assuming "reddit_with_duplicates" is the name of the table containing duplicated records...

```sql
insert into reddit_deduped select sub from (select sub, count(sub) as cnt from reddit_with_duplicates group by sub having cnt = 1);

insert into reddit_deduped select distinct(sub) from (select sub, count(sub) as cnt from reddit_with_duplicates group by sub having cnt > 1);
```

### Fetch 'new' subreddits, if needed

From terminal: `CLIENT_ID=<client id> CLIENT_SECRET=<secret> python3 subs_extraction/PersistNewSubs.py`

I found this useful, as it added 16k unique subreddits (5%) to ~310k of subreddits grabbed in previous step


## User Activity processing: order of execution

### Get and save necessary Reddit tokens

Regardless of how many Reddit apps you will use in parallel for data processing, you'd need to create corresponding Reddit tokens in advance. Assuming your `appconfig.json` is ready, run `python3 oauth.py` which will produce `tokens.txt` output file. 


### Fetch redditors from a subreddit of interest

`CLIENT_ID=<client id> CLIENT_SECRET=<secret> python3 redditors.publisher.py`

This script pushes data for downstream processing into Redis. 

### Process the users data

Spin up several Celery worker tasks: 

`celery --app=processusers worker --concurrency=<number of apps in appconfig.json> -l info`

NOTE: Celery worker tasks can be ran in parallel with users collecting. If there is no user to process, workers will quietly wait.


### Cleanup if needed

run `python3 analytics/cleanup.py`
