import requests
import json
from datetime import datetime, timedelta

def get_popular_repositories(token):
    headers = {'Authorization': 'token ' + token}
    params = {'q': 'stars:>0', 'per_page': 200}
    response = requests.get('https://api.github.com/search/repositories', headers=headers, params=params)
    repositories = response.json()['items']
    return repositories

def get_pull_requests(repository, token):
    headers = {'Authorization': 'token ' + token}
    params = {'state': 'all', 'per_page': 100}
    response = requests.get(f"https://api.github.com/repos/{repository['full_name']}/pulls", headers=headers, params=params)
    pull_requests = response.json()
    return pull_requests

def filter_pull_requests(pull_requests):
    filtered_prs = []
    for pr in pull_requests:
        if pr['merged_at'] or pr['closed_at']:
            if pr['state'] == 'closed':
                if pr['merged_at']:
                    pr_status = 'merged'
                else:
                    pr_status = 'closed'
                if 'review_comments' in pr and pr['review_comments'] > 0:
                    created_at = datetime.strptime(pr['created_at'], '%Y-%m-%dT%H:%M:%SZ')
                    merged_at = datetime.strptime(pr['merged_at'] or pr['closed_at'], '%Y-%m-%dT%H:%M:%SZ')
                    if (merged_at - created_at) > timedelta(hours=1):
                        filtered_prs.append({'number': pr['number'], 'status': pr_status})
    return filtered_prs


def save_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def main(token):
    result = {}
    popular_repositories = get_popular_repositories(token)
    for repo in popular_repositories:
        print(f"Getting pull requests for {repo['full_name']}...")
        pull_requests = get_pull_requests(repo, token)
        filtered_prs = filter_pull_requests(pull_requests)
        result[repo['full_name']] = filtered_prs
    save_to_json(result, 'pull_requests.json')

if __name__ == "__main__":
    github_token = 'tokenPessoal'
    main(github_token)
