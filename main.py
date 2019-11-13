import json
import logging
import os
import time
from copy import copy, deepcopy

import services
from config import DELETE_TAGS_WITH_PREFIX, TAGS_TO_KEEP, KEEP_N_LATEST_TAGS, LOG_DIR, DRY_RUN
# Configure Logger
from services import generate_report

logger = logging.getLogger('Gitlab-Registry-Pruner')
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(ch)


def prune(dry_run=True):
    logger.info("Fetch projects. Please wait...")

    if dry_run:
        logger.warning("DRY_RUN is enabled. Nothing will be deleted.")
    else:
        logger.warning("DRY_RUN is disabled. Please be careful !!!")

    projects = services.get_projects_to_be_pruned()
    #
    # # Cache results in local file for development.
    # with open("projects.json", "w") as file:
    #     json.dump(projects, file, indent=True)

    # # Use file from cache for development.
    # with open("projects.json", "r") as file:
    #     projects = json.load(file)

    # All available tags
    all_projects_with_all_tags = {}
    all_projects_with_tags_to_keep = {}
    all_projects_with_tags_to_delete = {}

    for p in projects:
        all_projects_with_all_tags[p['project_name']] = deepcopy(p)

        all_projects_with_tags_to_keep[p['project_name']] = deepcopy(p)
        tags_to_keep_in_project = []

        for tag_prefix in DELETE_TAGS_WITH_PREFIX:
            # Get all tags with the prefix.
            tags_with_prefix = [t for t in p['repository_tags'] if t['name'].startswith(tag_prefix)]

            # Sort them descending according the 'created_at' and keep the latest N tags.
            tags_with_prefix_to_keep = sorted(
                tags_with_prefix,
                key=lambda i: i['created_at'],
                reverse=True
            )[:KEEP_N_LATEST_TAGS]

            tags_to_keep_in_project += tags_with_prefix_to_keep

        # Add the whitelisted tags to the tags that is to be kept.
        tags_to_keep_in_project += [t for t in p['repository_tags'] if t['name'] in TAGS_TO_KEEP]

        # Overrite repository_tags with filtered tags from above (for-loop).
        all_projects_with_tags_to_keep[p['project_name']]['repository_tags'] = copy(tags_to_keep_in_project)

    # Get tags to delete. Get the Diff between two dicts.
    for k, v in deepcopy(all_projects_with_all_tags).items():
        tags_to_delete = []
        all_tags = v['repository_tags']
        if k in all_projects_with_tags_to_keep:
            tags_to_keep = all_projects_with_tags_to_keep[k]['repository_tags']
            tags_to_delete = [tag for tag in all_tags if tag not in tags_to_keep]

        all_projects_with_tags_to_delete[k] = v
        all_projects_with_tags_to_delete[k]['repository_tags'] = tags_to_delete

    logger.info("Start deleting repository tags selectively...")

    # Delete tags
    for k, v in all_projects_with_tags_to_delete.items():
        print('\t', k.upper())
        for tag in v['repository_tags']:
            if dry_run:
                time.sleep(0.01)
            else:
                services.delete_repository(
                    project_id=v['project_id'],
                    repository_id=v['repository_id'],
                    tag_name=tag['name'])
            print("\t\t{} ... deleted".format(tag['path']))

    logger.info("Generate summary.")

    generate_report(
        keep=all_projects_with_tags_to_keep,
        delete=all_projects_with_tags_to_delete,
        all=all_projects_with_all_tags
    )


def prepare():
    """
    Make preparations before running pruning script.
    :return:
    """

    # Create log dir if necessary
    if not os.path.exists(LOG_DIR):
        logger.info("Log directory ({}) not found and will be created automatically.".format(LOG_DIR))
        os.makedirs(LOG_DIR)


if __name__ == '__main__':
    # Interpret DRY_RUN variable
    DRY_RUN = DRY_RUN == '1'
    prepare()
    prune(dry_run=DRY_RUN)
