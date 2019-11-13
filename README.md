# Gitlab Registry Pruner
[![Build Status](https://drone.quving.com/api/badges/Quving/gitlab-registry-pruner/status.svg)](https://drone.quving.com/Quving/gitlab-registry-pruner)

## Description
Contains scripts to keep your Gitlab-Registry clean.


## Configuration
| Env                  | Description                                  | Example | Required             |
|----------------------|----------------------------------------------|---------|-----------------------|
| GITLAB_GROUP_ID      | The ID of the group of your gitlab-instance. | 12      | :heavy_check_mark:
| GITLAB_SERVER        | Your Gitlab host including protocol.         | 'https://gitlab.com'       | :heavy_check_mark: |
| GITLAB_PRIVATE_TOKEN | Your Gitlab private access token.            | 'jbArsqXnXqhd28DMfCh3'    | :heavy_check_mark: |
|TAGS_TO_KEEP|A comma seperated string of tags what want to be kept.|'latest,stable,develop'|:heavy_check_mark:|
|DELETE_TAGS_WITH_PREFIX|A comma seperated string of string prefixes that should be removed. For example setting 'v' would have the effect that tags such as v0.1.4, v0.2.4 and version will be deleted. In general v*.|'v,test_'|:heavy_check_mark:|
|KEEP_N_LATEST_TAGS|A number of latest tags (specified  by 'DELETE_TAGS_WITH_PREFIX') that should be kept.| 5 |:heavy_check_mark:
|DRY_RUN| Execute script with dry-run option. Set '1' for dry-run. Else '0'. For safety it's set on '1' as default.| 1 |:heavy_check_mark:


## Usage
### Using Docker
```sh
docker run --rm -it \
    -e GITLAB_GROUP_ID='...' \
    -e GITLAB_SERVER={} \
    -e GITLAB_PRIVATE_TOKEN='...' \
    -e TAGS_TO_KEEP='...' \
    -e DELETE_TAGS_WITH_PREFIX='...' \
    -e KEEP_N_LATEST_TAGS='...' \
    pingu/gitlab-registry-pruner
```
### Using python
1. (Export the environment variables.)
2. ```pip install -r requirements.txt```
3. ```python main.py```
