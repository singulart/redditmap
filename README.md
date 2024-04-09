# Reddit user activity visualizer

Walks over posts and comments of Reddit users and forms an insightful map


## Infra dependencies

1. Redis

Tested on 64 bit Redis v7.2.4

Run locally with 1-minute data persistence interval: `docker run --name reddit -d redis redis-server --save 60 1`
Data persistence makes data written to Redis available after restart.

Connecting to the running Redis instance using `redis-cli`: 

- Create a network `docker network create reddit-network`
- Connect a network to the container `docker network connect reddit-network reddit`
- Run CLI `docker run -it --network reddit-network --rm redis redis-cli -h reddit`


## Reddit API clients config file structure

File name: `appconfig.json`

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


