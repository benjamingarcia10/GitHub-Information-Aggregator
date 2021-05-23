from flask import Flask, request, send_from_directory, render_template
from flask_restful import Resource, Api
import concurrent.futures
import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

GITHUB_ACCESS_TOKEN = os.getenv('GITHUB_ACCESS_TOKEN')
PORT = os.getenv('PORT', 5000)  # Retrieve port from environment variables or default to port 5000
app = Flask(__name__)
app.config['DEBUG'] = True
api = Api(app)

headers = {}
if GITHUB_ACCESS_TOKEN:
    headers = {
        'Authorization': f'Token {GITHUB_ACCESS_TOKEN}'
    }


def format_from_kb(size):
    # 2**10 = 1024
    power = 2 ** 10
    n = 0
    power_labels = {0: 'KB', 1: 'MB', 2: 'GB', 3: 'TB'}
    while size > power:
        size /= power
        n += 1
    return size, power_labels[n]


# Function to retrieve JSON response from url argument
# Returns JSON response unless non 200 status code retrieved or exception (in which case returns None)
def get_json_response(url: str, params=None):
    try:
        response = requests.get(url, params=params, headers=headers)

        # 200 status code only
        if response.ok:
            return response.json()
        else:
            return None
    except Exception:
        return None


# https://docs.github.com/en/rest/reference/users#get-a-user
def get_user_information(username: str):
    return get_json_response(f'https://api.github.com/users/{username}')


# https://docs.github.com/en/rest/reference/repos#list-repositories-for-a-user
def get_user_repos(username: str, forked=True):
    all_user_repos = []
    page_number = 1

    # Loop to iterate through pages while there are more results
    while True:
        page_result = get_json_response(f'https://api.github.com/users/{username}/repos', params={
            'per_page': 100,  # Max results per page according to GitHub API
            'page': page_number
        })
        if page_result is None:
            return None
        else:
            # No more repos found on this page: break out of loop
            if len(page_result) == 0:
                break
            else:
                # Add all repos on this page since we don't care about fork status
                if forked:
                    all_user_repos.extend(page_result)
                # Only add repos that are not forked
                else:
                    for repo in page_result:
                        if repo['fork'] is False:
                            all_user_repos.append(repo)
                page_number += 1  # Increment page number to move to next page
    return all_user_repos


# Retrieve all repository stats from repos list
def get_repo_stats(repos: list):
    total_repo_count = 0  # Total count of repositories
    total_stargazers = 0  # Total stargazers for all repositories
    total_fork_count = 0  # Total fork count for all repositories
    total_repo_size = 0  # Total repositories size (retrieved in KB units)
    all_repo_languages = {}

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Create a thread for each repository to retrieve languages information
        futures = [executor.submit(get_json_response, repo['languages_url']) for repo in repos]
        for future in concurrent.futures.as_completed(futures):
            try:
                languages_info = future.result()
                if languages_info is None:
                    return None
                else:
                    # Store lines written in each language to calculate most -> least used
                    for language in languages_info:
                        if language in all_repo_languages:
                            all_repo_languages[language] += languages_info[language]
                        else:
                            all_repo_languages[language] = languages_info[language]
            except Exception:
                return None

    for repo in repos:
        total_repo_count += 1
        total_stargazers += repo['stargazers_count']
        total_fork_count += repo['forks_count']
        total_repo_size += repo['size']
        formatted_size, size_unit = format_from_kb(repo['size'])
        repo['formatted_size'] = f'{round(formatted_size, 2)} {size_unit}'

    if total_repo_size > 0:
        average_repo_size, size_unit = format_from_kb(total_repo_size / total_repo_count)    # Average repository size (with proper units)
    else:
        average_repo_size = 0
        size_unit = 'KB'

    all_repo_languages = {k: v for k, v in sorted(all_repo_languages.items(), key=lambda item: item[1], reverse=True)}

    return {
        'total_repo_count': total_repo_count,
        'total_stargazers': total_stargazers,
        'total_forks_count': total_fork_count,
        'total_size_repos': total_repo_size,
        'average_repo_size': round(average_repo_size, 2),
        'size_unit': size_unit,
        'repo_languages': all_repo_languages
    }


def retrieve_gh_data(username: str, forked: bool):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        user_data_future = executor.submit(get_user_information, username)
        user_repos_future = executor.submit(get_user_repos, username, forked)
        user_data = user_data_future.result()
        user_repos = user_repos_future.result()

    if user_data is None or user_repos is None:
        return {
            'success': False,
            'error': 'GitHub API error.'
        }
    else:
        repo_stats = get_repo_stats(user_repos)
        if repo_stats is None:
            return {
                'success': False,
                'error': 'GitHub API error.'
            }
        else:
            return {
                'success': True,
                'username': username,
                'viewing_forked_repos': forked,
                'repo_stats': repo_stats,
                'user_data': user_data,
                'user_repos': user_repos
            }


class GhApi(Resource):
    def get(self):
        query_parameters = request.args
        username = query_parameters.get('username')
        forked = query_parameters.get('forked')

        if username:
            username = username.strip()
            if forked and forked.strip().lower() == 'false':
                forked = False
            else:
                forked = True
            return retrieve_gh_data(username, forked)
        else:
            return {
                'success': False,
                'error': 'No username specified in \'username\' query variable.'
            }


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')


@app.route('/')
def ui():
    query_parameters = request.args
    username = query_parameters.get('username')
    forked = query_parameters.get('forked')

    if username:
        username = username.strip()
        if forked and forked.strip().lower() == 'true':
            forked = True
        else:
            forked = False
        gh_info = retrieve_gh_data(username, forked)
        if gh_info['success']:
            return render_template('ui-data.html',
                                   username=username,
                                   repo_stats=gh_info['repo_stats'],
                                   user_data=gh_info['user_data'],
                                   user_repos=gh_info['user_repos'])
        else:
            return gh_info
    else:
        return render_template('ui-index.html')


api.add_resource(GhApi, '/api')

if __name__ == '__main__':
    app.run(debug=True, port=PORT)
