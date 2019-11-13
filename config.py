import os

DRY_RUN = os.getenv("DRY_RUN", '1')
LOG_DIR = 'logs'

GITLAB_GROUP_ID = os.getenv("GITLAB_GROUP_ID")
GITLAB_PRIVATE_TOKEN = os.getenv("GITLAB_PRIVATE_TOKEN")
GITLAB_API_BASE_URL = "{}/api/v4".format(os.getenv("GITLAB_SERVER"))

TAGS_TO_KEEP = os.getenv('TAGS_TO_KEEP', "latest").split(',')
DELETE_TAGS_WITH_PREFIX = os.getenv("DELETE_TAGS_WITH_PREFIX", "").split(',')
KEEP_N_LATEST_TAGS = int(os.getenv("KEEP_N_LATEST_TAGS", 10))
