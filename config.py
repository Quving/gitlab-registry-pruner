import os

GITLAB_GROUP_ID = 2
GITLAB_PRIVATE_TOKEN = os.getenv("GITLAB_PRIVATE_TOKEN")
GITLAB_API_BASE_URL = os.getenv("GITLAB_API_BASE_URL")
TAGS_TO_KEEP = ['master', 'develop', 'latest-tag', 'latest']
TAGS_TO_PRUNE_WITH_PREFIX = ['v']
KEEP_LAST_N_TAGS = 7
