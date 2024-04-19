import redis
import os
import re 
import logging

logging.basicConfig(level = logging.INFO)

redis_client = redis.Redis(host='localhost', port=6379, db=0)
pipeline = redis_client.pipeline()
directory = './obsidian-map'

regex_pattern = r'([\[]{2}\w*[\]]{2})'

iterations_counter = 0
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    if not os.path.isfile(f): 
        continue
    with open(f) as redditor:
        content = redditor.read()
        matches = re.findall(regex_pattern, content)
        for match in matches:
            pipeline.zincrby("subreddits", 1, match.replace('[', '').replace(']', ''))
    iterations_counter = iterations_counter + 1
    if iterations_counter % 1000 == 0: 
        logging.info("Executing pipeline")
        pipeline.execute()

logging.info("Done")

top_50_words_with_scores = redis_client.zrevrange('subreddits', 0, 49, withscores=True)

# Convert bytes to string (if necessary) and print
for word, score in top_50_words_with_scores:
    logging.info(f"{word.decode('utf-8')}: {int(score)}")