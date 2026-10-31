import json
import os
import urllib.request
import html

USERNAME = "AbsalaoDev"
API = "https://api.github.com"

def github_request(endpoint):
    url = API + endpoint
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "AbsalaoDev-Stats"
        }
    )

    with urllib.request.urlopen(request) as response:
        return json.loads(response.read())

def get_stats():
    user = github_request(f"/users/{USERNAME}")
    repos = github_request(
        f"/users/{USERNAME}/repos?per_page=100&type=owner"
    )

    stars = sum(repo["stargazers_count"] for repo in repos)
    forks = sum(repo["forks_count"] for repo in repos)

    languages = {}

    for repo in repos:
        if repo["fork"]:
            continue

        data = github_request(f"/repos/{USERNAME}/{repo['name']}/languages")

        for language, size in data.items():
            languages[language] = languages.get(language, 0) + size

    top_languages = sorted(
        languages.items(),
        key=lambda item: item[1],
        reverse=True
    )[:5]

    return user, len(repos), stars, forks, top_languages

def create_card(title, lines, filename):
    width = 480
    height = 190

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg"
    width="{width}" height="{height}" viewBox="0 0 {width} {height}">
    <rect width="100%" height="100%" rx="12"
    fill="#0d1117" stroke="#8A2BE2" stroke-width="1.5"/>

    <text x="25" y="38" fill="#c084fc"
    font-size="20" font-weight="bold"
    font-family="Arial">{html.escape(title)}</text>

    <line x1="25" y1="53" x2="455" y2="53"
    stroke="#30363d"/>
    '''

    y = 88

    for line in lines:
        svg += f'''
        <text x="30" y="{y}" fill="#e6edf3"
        font-size="15" font-family="Arial">
        {html.escape(str(line))}
        </text>
        '''
        y += 25

    svg += "</svg>"

    with open(f"public/{filename}", "w", encoding="utf-8") as file:
        file.write(svg)

def main():
    os.makedirs("public", exist_ok=True)

    user, repos, stars, forks, languages = get_stats()

    stats = [
        f"Repositórios públicos: {repos}",
        f"Estrelas recebidas: {stars}",
        f"Forks recebidos: {forks}",
        f"Seguidores: {user['followers']}"
    ]

    language_lines = [
        f"{name}: {size:,} bytes"
        for name, size in languages
    ]

    create_card("Estatísticas do GitHub", stats, "stats.svg")
    create_card("Linguagens mais utilizadas", language_lines, "languages.svg")

    print("Cartões gerados com sucesso!")

if __name__ == "__main__":
    main()
