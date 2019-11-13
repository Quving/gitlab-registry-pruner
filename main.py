import json
import logging
import time

import services
from config import DELETE_TAGS_WITH_PREFIX, TAGS_TO_KEEP, KEEP_N_LATEST_TAGS, DRY_RUN

# Configure Logger
from services import generate_report

logger = logging.getLogger('Gitlab-Registry-Pruner')
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(ch)


def prune(dry_run=False):
    logger.info("Fetch projects. Please wait...")
    projects = services.get_projects_to_be_pruned()

    # # Cache results in local file for development.
    # with open("projects.json", "w") as file:
    #     json.dump(projects, file, indent=True)
    #
    # # Use file from cache for development.
    # with open("projects.json", "r") as file:
    #     projects = json.load(file)

    # All available tags
    all_tags = {}
    tags_to_keep = {}

    for p in projects:
        all_tags[p['project_name']] = p['repository_tags']
        tags_to_keep_in_project = []
        # Prune for each tag prefix seperately.
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
        tags_to_keep[p['project_name']] = tags_to_keep_in_project

    # Get tags to delete. Get the Diff between two dicts.
    tags_to_delete = {}
    for keep, delete in zip(tags_to_keep, all_tags):
        assert keep == delete
        tags_keep = tags_to_keep[keep]
        tags_all = all_tags[delete]
        tags_to_delete[keep] = [t for t in tags_all if t not in tags_keep]

    # Delete tags
    logger.info("Start deleting repository tags selectively...")
    for k, v in tags_to_delete.items():
        print(k.upper())
        for tag in v:
            if dry_run:
                time.sleep(0.1)
            else:
                services.delete_repository(project_id=v['project_id'], repository_id=v['repository_id'], tag_name=tag['name'])
            print("\t{} ... deleted".format(tag['path']))

    logger.info("Generate summary.")
    generate_report(tags_to_keep=tags_to_keep, tags_to_delete=tags_to_delete, all_tags=all_tags)


if __name__ == '__main__':
    prune(dry_run=DRY_RUN)
