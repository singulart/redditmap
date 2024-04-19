# Reddit user activity visualizer

Walks over posts and comments of Reddit users and forms an insightful map


## Redis dependency

This tool uses Celery library with Redis broker as a backend. Tested on 64 bit Redis v7.2.4

Run Redis locally with 1-minute data persistence interval: `docker run --name reddit -d -p 6379:6379 redis redis-server --save 60 1`
Data persistence makes data written to Redis available after restart.

Connecting to the running Redis instance using `redis-cli`: 

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

## Order of execution

### Get and save necessary Reddit tokens

Regardless of how many Reddit apps you will use in parallel for data processing, you'd need to create corresponding Reddit tokens in advance. Assuming your `appconfig.json` is ready, run `python3 oauth.py` which will produce `tokens.txt` output file. 


### Load users from a subreddit of interest

`CLIENT_ID=<client id> CLIENT_SECRET=<secret> python3 loadusers.py`

This script pushes data for downstream processing into Redis. 

### Process the users data

Spin up several Celery worker tasks: 

`celery --app=processusers worker --concurrency=<number of apps in appconfig.json> -l info`

NOTE: Celery worker tasks can be ran in parallel with users collecting. If there is no user to process, workers will quietly wait.
