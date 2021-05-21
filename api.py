from flask import Flask, request
from flask_restful import Resource, Api

import os
import requests

PORT = int(os.environ.get('PORT', 5000))            # Retrieve port from environment variables or default to port 5000
app = Flask(__name__)
app.config['DEBUG'] = True
api = Api(app)


# https://docs.github.com/en/rest/reference/users#get-a-user
def get_user_information(username: str):
    response = requests.get(f'https://api.github.com/users/{username}')

    # 200 status code only
    if response.ok:
        try:
            return response.json()
        except Exception:
            return None
    else:
        return None


# https://docs.github.com/en/rest/reference/repos#list-repositories-for-a-user
def get_user_repos(username: str, forked=True):
    all_user_repos = []
    page_number = 1

    # Loop to iterate through pages while there are more results
    while True:
        response = requests.get(f'https://api.github.com/users/{username}/repos', params={
            'per_page': 100,                    # Max results per page according to GitHub API
            'page': page_number
        })
        # 200 status code only
        if response.ok:
            try:
                response_json = response.json()
                # No more repos found on this page: break out of loop
                if len(response_json) == 0:
                    break
                else:
                    # Add all repos on this page since we don't care about fork status
                    if forked:
                        all_user_repos.extend(response_json)
                    # Only add repos that are not forked
                    else:
                        for repo in response_json:
                            if repo['fork'] is False:
                                all_user_repos.append(repo)
                    page_number += 1            # Increment page number to move to next page
            except Exception:
                return None
        else:
            return None
    return all_user_repos


def get_repo_stats(repos: list):
    total_count = 0                             # Total count of repositories
    total_stargazers = 0                        # Total stargazers for all repositories
    total_fork_count = 0                        # Total fork count for all repositories

    total_repo_size = 0.0                       # Total repositories size (retrieved in KB units)

    all_repo_languages = {}

    for repo in repos:
        try:
            total_count += 1
            total_stargazers += repo['stargazers_count']
            total_fork_count += repo['forks_count']
            total_repo_size += repo['size']

            languages_response = requests.get(repo['languages_url'])
            if languages_response.ok:
                languages_info = languages_response.json()
                for language in languages_info:
                    if language in all_repo_languages:
                        all_repo_languages[language] += languages_info[language]
                    else:
                        all_repo_languages[language] = languages_info[language]
            else:
                return None
        except Exception:
            return None

    average_repo_size = total_repo_size / total_count       # Average repository size (in KB units)
    all_repo_languages = {k: v for k, v in sorted(all_repo_languages.items(), key=lambda item: item[1], reverse=True)}

    return {
        'total_repo_count': total_count,
        'total_stargazers': total_stargazers,
        'total_forks_count': total_fork_count,
        'total_size_repos': total_repo_size,
        'average_repo_size': average_repo_size,
        'repo_languages': all_repo_languages
    }


class GhApi(Resource):
    def get(self):
        query_parameters = request.args
        username_param = query_parameters.get('username')

        forked_param = query_parameters.get('forked')
        if forked_param and forked_param.strip().lower() == 'false':
            forked_param = False
        else:
            forked_param = True

        if username_param:
            user_data = get_user_information(username_param)
            user_repos = get_user_repos(username_param, forked_param)
            repo_stats = get_repo_stats(user_repos)
            return {
                'username': username_param,
                'viewing_forked_repos': forked_param,
                'repo_stats': repo_stats,
                'user_data': user_data,
                'user_repos': user_repos
            }
        else:
            return {
                'error': 'No username specified in \'username\' query variable.'
            }


api.add_resource(GhApi, '/')

if __name__ == '__main__':
    app.run(debug=True, port=PORT)
