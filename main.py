import datetime
import json
import logging

from config import TAGS_TO_PRUNE_WITH_PREFIX, TAGS_TO_KEEP, KEEP_LAST_N_TAGS

# Configure Logger

logger = logging.getLogger('Gitlab-Registry-Pruner')
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(ch)


def prune(verbose=False):
    logger.info("Retrieve project details...")
    # projects = services.get_projects_to_be_pruned()
    # with open("projects.json", "w") as file:
    #     json.dump(projects, file, indent=True)

    with open("projects.json", "r") as file:
        projects = json.load(file)

    all_tags = []
    tags_to_keep = []

    # Log String
    log = "\n Date: {}".format(datetime.datetime.now())

    for p in projects:
        all_tags += p['repository_tags']
        tags_to_keep_in_project = []
        # Prune for each tag prefix seperately.
        for tag_prefix in TAGS_TO_PRUNE_WITH_PREFIX:
            # Get all tags with the prefix.
            tags_with_prefix = [t for t in p['repository_tags'] if t['name'].startswith(tag_prefix)]
            # Sort them descending according the 'created_at' and keep the latest N tags.
            tags_with_prefix_to_keep = sorted(
                tags_with_prefix,
                key=lambda i: i['created_at'],
                reverse=True)[:KEEP_LAST_N_TAGS]

            tags_to_keep_in_project += tags_with_prefix_to_keep

        # Add the whitelisted tags to the tags that is to be kept.
        tags_to_keep_in_project += [t for t in p['repository_tags'] if t['name'] in TAGS_TO_KEEP]
        tags_to_keep += tags_to_keep_in_project

        log += "\nProject Name: {}:\n".format(p['project_name'])
        for t in tags_to_keep_in_project:
            log += "\n\t{}\t\t{}\t{}".format(t['created_at'], t['name'].ljust(8), t['path'])
        log += "\n\n-------------------------------------------------------------------------------------------------"

        if verbose:
            print(log)

    # Delete all other tags
    tags_to_delete = [t for t in all_tags if t not in tags_to_keep]
    print(len(tags_to_delete))

if __name__ == '__main__':
    prune(verbose=True)
