import datetime
from celery import Celery
from celery_batches import Batches
from celery.utils.log import get_task_logger
import sys 

sys.path.append('../celeryconfig')

from sqlalchemy import create_engine
from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert

from celeryconfig import *
from subs_extraction.models import CommentsStaging

# engine = create_engine(DATABASE_URL, echo=True)
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

reddit_api = 'https://oauth.reddit.com'

app = Celery(config_source='celeryconfig')
logger = get_task_logger(__name__)


def print_comment_state(comment: CommentsStaging):
    attrs = [
        'comment_id', 'post_id', 'parent_id', 'path',
        'body', 'author', 'created_at', 'score', 'depth'
    ]

    logger.info("📌 Comment State:")
    for attr in attrs:
        value = getattr(comment, attr, None)
        print(f"  {attr:12}: {value}")
        
@app.task(name='Staging Comment Persister', base=Batches, flush_every=256, flush_interval=10)
def persistComments(comments): 
    records = []
    for simple_request in comments:
        for com in simple_request.args:
            ormComment = CommentsStaging(
                **{
                    **com, 
                    'created_at': datetime.date.fromtimestamp(com['created_at']),
                    'path': '',
                }
            )
            inspector = inspect(ormComment)
            # Why? God? Why I have to convert a nice ORM entity into dict??? 
            comment_dict = {attr.key: getattr(ormComment, attr.key) for attr in inspector.mapper.column_attrs}
            records.append(comment_dict)
        
    stmt = insert(CommentsStaging).values(records).on_conflict_do_nothing(index_elements=['comment_id']) 
    try:
        session.execute(stmt)
        session.commit()
        logger.info(f"Persisted {len(records)} comments")
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to persist comments: {e}")