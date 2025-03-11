from celery import Celery
from celery_batches import Batches
from celery.utils.log import get_task_logger
from apiclient import *
import sys 

sys.path.append('../celeryconfig')

reddit_api = 'https://oauth.reddit.com'

app = Celery(config_source='celeryconfig')
logger = get_task_logger(__name__)

@app.task(name='Comment Persister', base=Batches, flush_every=2000, flush_interval=10)
def persistComments(comments): 
    print()
    logger.info(f"Task got {len(comments)}")
