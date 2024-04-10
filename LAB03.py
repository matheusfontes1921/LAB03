import requests 
import datetime
import json

def get_popular_repositories():
    url = "https://api.github.com/search/repositories?q=stars:>0&sort=stars&per_page=200"
    response = requests.get(url)
    data = response.json()
    repositories = [repo['full_name'] for repo in data['items']]
    return repositories

def get_pull_requests(repository):
    url = f"https://api.github.com/repos/{repository}/pulls?state=all"
    headers = {
        "Authorization": "token colocarToken"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching pull requests for repository {repository}: {response.status_code}")
        return []
    pull_requests = response.json()
    return pull_requests


def calculate_pr_metrics(repository, pr):
    metrics = {
        'repository': repository,
        'title': pr['title'],
        'number': pr['number'],
        'size': len(pr.get('files', [])),  # Número de arquivos
        'additions': pr.get('additions', 0),  # Total de linhas adicionadas
        'deletions': pr.get('deletions', 0),  # Total de linhas removidas
        'description_length': len(pr.get('body', '')),  # Número de caracteres na descrição
        'interactions': {
            'participants': len(pr.get('participants', [])),  # Número de participantes
            'comments': pr.get('comments', 0)  # Número de comentários
        }
    }
    return metrics


popular_repositories = get_popular_repositories()
all_metrics = []

for repository in popular_repositories:
    pull_requests = get_pull_requests(repository)
    for pr in pull_requests:
        if 'state' in pr and pr['state'] in ['closed', 'merged'] and pr['created_at'] != pr['updated_at']:
            if 'reviews' in pr:
                if pr['reviews'] > 0:
                    metrics = calculate_pr_metrics(repository, pr)
                    all_metrics.append(metrics)

with open('c:/Users/matheus.fontes/OneDrive - WBR Consultoria S.A/Área de Trabalho/LAB03/new.json', 'w') as f:
    json.dump(all_metrics, f, indent=4)
