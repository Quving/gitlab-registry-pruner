import requests
from pip._vendor.pyparsing import Dict
from tqdm import tqdm

from config import GITLAB_GROUP_ID, GITLAB_PRIVATE_TOKEN, GITLAB_API_BASE_URL


def get_gitlab_projects(group_id):
    """
    Returns a list of projects within a given group.
    :return:
    """
    url = '{}/groups/{}'.format(GITLAB_API_BASE_URL, GITLAB_GROUP_ID)
    headers = {
        'PRIVATE-TOKEN': GITLAB_PRIVATE_TOKEN,
    }

    params = (
        ('with_projects', 'true'),
    )

    response = requests.get(url=url, headers=headers, params=params)
    projects = response.json()['projects']
    return projects


def get_group_repositories(group_id):
    """
    Returns a list of repositories within a given group.
    :return:
    """
    url = '{}/groups/{}/registry/repositories'.format(GITLAB_API_BASE_URL, group_id)
    headers = {
        'PRIVATE-TOKEN': GITLAB_PRIVATE_TOKEN,
    }

    params = (
        ('tags', 'true'),
    )
    response = requests.get(url=url, headers=headers, params=params)
    return response.json()


def get_repository_details(project_id, repository_id, tag_name):
    """
    Returns detailes of a repository given the project_id and tag_name
    :return:
    """
    url = '{}/projects/{}/registry/repositories/{}/tags/{}'.format(
        GITLAB_API_BASE_URL,
        project_id,
        repository_id,
        tag_name
    )
    headers = {
        'PRIVATE-TOKEN': GITLAB_PRIVATE_TOKEN,
    }

    params = (
        ('tags', 'true'),
    )
    response = requests.get(url=url, headers=headers, params=params)
    return response.json()


def get_projects_to_be_pruned():
    """
    Returns a list of projects that is to be pruned.

    Example:
    [
    {'number_of_tags': 1,
     'project_id': 55,
     'project_name': 'apollo-web',
     'repository_id': 47,
     'repository_tags': [{'created_at': '2018-05-16T16:39:14.123+00:00',
                      'location': 'git.hoou.tech:4567/hoou/apollo-web:master',
                      'name': 'master',
                      'path': 'hoou/apollo-web:master'}]}
    ]

    :return:
    """
    all_projects = get_gitlab_projects(group_id=GITLAB_GROUP_ID)
    all_repositories = get_group_repositories(group_id=GITLAB_GROUP_ID)
    all_projects_with_repository = []
    for p in tqdm(all_projects):

        # Meta informations
        project_name = p['name']
        project_id = p['id']
        repository_id = None
        repository_tags = None

        for r in all_repositories:
            if project_id == r['project_id']:
                repository_id = r['id']
                repository_tags = r['tags']

        # Take only those who has a repository.
        if repository_id and repository_tags:
            project_with_repository = {
                'project_name': project_name,
                'project_id': project_id,
                'repository_id': repository_id,
                'repository_tags': repository_tags,
                'number_of_tags': len(repository_tags),
            }

            # Retrieve repository details.
            for repository_tag in repository_tags:
                repository_details = get_repository_details(
                    project_id=project_id,
                    repository_id=repository_id,
                    tag_name=repository_tag['name']
                )
                repository_tag['created_at'] = repository_details['created_at']
            all_projects_with_repository.append(project_with_repository)

    return all_projects_with_repository


def delete_repository(project_id, repository_id, tag_name):
    """
    Deletes a repository tag.
    :return:
    """
    url = '{}/projects/{}/registry/repositories/{}/tags/{}'.format(
        GITLAB_API_BASE_URL,
        project_id,
        repository_id,
        tag_name
    )
    headers = {
        'PRIVATE-TOKEN': GITLAB_PRIVATE_TOKEN,
    }

    params = (
        ('tags', 'true'),
    )
    response = requests.delete(url=url, headers=headers, params=params)
    return response.json()


def generate_report(tags_to_keep: Dict, tags_to_delete: Dict, all_tags: Dict):
    """
    Prints the log to console.
    :param tags_to_keep:
    :param tags_to_delete:
    :param all_tags:
    :return:
    """
    for k, v in all_tags.items():
        print("\n", k.upper())
        for t in v:
            if t in tags_to_keep[k]:
                print("  - [+]\t{}\t{}".format(t['path'].ljust(25), t['created_at']))
            else:
                print("  - [-]\t{}\t{}".format(t['path'].ljust(25), t['created_at']))

    print("\n-------------------------------------------------------------------------\n")
    print(" SUMMARY\n")
    print(' {} repository tags kept.'.format((sum([len(tags_to_keep[k]) for k in tags_to_keep]))))
    print(' {} repository tags deleted.\n'.format((sum([len(tags_to_delete[k]) for k in tags_to_delete]))))
