
broker_url = 'redis://localhost:6379/0'

# imports = ('processusers', 'subs_extraction.savebestcommunities', 'AiCategorizationWorker')

imports = ('subs_extraction.CommentGrabberWorker', 'subs_extraction.CommentPersisterWorker')

result_backend = 'redis://localhost:6379/0'
