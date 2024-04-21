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

def calculate_size(pull_request):
    total_files = len(pull_request['files'])
    total_additions = sum(file['additions'] for file in pull_request['files'])
    total_deletions = sum(file['deletions'] for file in pull_request['files'])
    return {'total_files': total_files, 'total_additions': total_additions, 'total_deletions': total_deletions}

def calculate_analysis_time(pull_request):
    created_at = datetime.strptime(pull_request['created_at'], '%Y-%m-%dT%H:%M:%SZ')
    closed_at = datetime.strptime(pull_request['closed_at'] or pull_request['merged_at'], '%Y-%m-%dT%H:%M:%SZ')
    analysis_time = closed_at - created_at
    return analysis_time.total_seconds() / 3600  # Convertendo para horas

def calculate_description_length(pull_request):
    description = pull_request['body']
    return len(description)

def calculate_interactions(pull_request):
    participants = len(pull_request['participants'])
    comments = pull_request['comments']
    return {'participants': participants, 'comments': comments}

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
                    size_metrics = calculate_size(pr)
                    analysis_time = calculate_analysis_time(pr)
                    description_length = calculate_description_length(pr)
                    interaction_metrics = calculate_interactions(pr)
                    filtered_prs.append({
                        'number': pr['number'],
                        'status': pr_status,
                        'size_metrics': size_metrics,
                        'analysis_time': analysis_time,
                        'description_length': description_length,
                        'interaction_metrics': interaction_metrics
                    })
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
