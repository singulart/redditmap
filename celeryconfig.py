import os 

broker_url = 'redis://localhost:6379/0'
DATABASE_URL = os.getenv("DATABASE_URL")

# imports = ('processusers', 'subs_extraction.savebestcommunities', 'AiCategorizationWorker')

imports = ('subs_extraction.CommentGrabberWorker', 'subs_extraction.CommentPersisterWorker')

result_backend = 'redis://localhost:6379/0'
