import requests
from flask import Flask, render_template, request

app = Flask(__name__, template_folder='templates')

# Function to fetch GitHub stats for a given username
def fetch_github_stats(username):
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url)

    if response.status_code == 200:
        user_data = response.json()
        stats = {
            'public_repos': user_data.get('public_repos'),
            'followers': user_data.get('followers'),
            'following': user_data.get('following'),
            'created_at': user_data.get('created_at')
        }

        repos_url = f"https://api.github.com/users/{username}/repos"
        repos_response = requests.get(repos_url)

        if repos_response.status_code == 200:
            repos_data = repos_response.json()
            stats['num_repos'] = len(repos_data)

            languages_used = {}
            for repo in repos_data:
                repo_languages_url = repo['languages_url']
                repo_languages_response = requests.get(repo_languages_url)

                if repo_languages_response.status_code == 200:
                    repo_languages_data = repo_languages_response.json()
                    for lang, bytes_used in repo_languages_data.items():
                        if lang in languages_used:
                            languages_used[lang] += bytes_used
                        else:
                            languages_used[lang] = bytes_used

            stats['languages_used'] = languages_used

        return stats

    else:
        return {'error': f"User {username} not found or API rate limit exceeded."}

# Route for the landing page
@app.route('/')
def index():
    return render_template('landing.html')

# Route for the GitHub stats app
@app.route('/app', methods=['GET', 'POST'])
def app_page():
    if request.method == 'POST':
        username = request.form['username']
        stats = fetch_github_stats(username)

        if 'error' in stats:
            return render_template('app.html', error=stats['error'])
        else:
            return render_template('app.html', stats=stats, username=username)
    else:
        return render_template('app.html')

if __name__ == "__main__":
    app.run(debug=True)