import json
import os
import urllib.request
from collections import defaultdict


USERNAME = "eyaoueslati06"
README_FILE = "README.md"


CATEGORY_KEYWORDS = {
    "📊 Data Analysis & Business Intelligence": [
        "data analysis",
        "data analytics",
        "analytics",
        "exploratory data analysis",
        "eda",
        "sql",
        "tsql",
        "t-sql",
        "dashboard",
        "power bi",
        "powerbi",
        "tableau",
        "reporting",
        "financial reporting",
        "business intelligence",
        "visualization",
        "excel",
        "kpi",
    ],

    "🤖 Data Science & Machine Learning": [
        "data science",
        "machine learning",
        "prediction",
        "predict",
        "classification",
        "regression",
        "clustering",
        "random forest",
        "decision tree",
        "xgboost",
        "scikit-learn",
        "sklearn",
        "model",
        "fraud detection",
        "anomaly detection",
        "forecasting",
    ],

    "🧠 AI, NLP & LLM": [
        "artificial intelligence",
        "ai",
        "llm",
        "large language model",
        "rag",
        "retrieval augmented generation",
        "nlp",
        "natural language processing",
        "information retrieval",
        "transformer",
        "huggingface",
        "embedding",
        "embeddings",
        "semantic search",
        "vector database",
        "chatbot",
        "openai",
        "langchain",
        "agent",
        "agents",
    ],

    "🧬 Deep Learning": [
        "deep learning",
        "neural network",
        "neural networks",
        "tensorflow",
        "pytorch",
        "cnn",
        "rnn",
        "lstm",
        "computer vision",
    ],

    "💻 Software & Web Development": [
        "web",
        "website",
        "react",
        "frontend",
        "backend",
        "full stack",
        "full-stack",
        "mern",
        "html",
        "css",
        "javascript",
        "java",
        "spring",
        "api",
        "application",
        "software",
    ],
}


CATEGORY_ORDER = [
    "📊 Data Analysis & Business Intelligence",
    "🤖 Data Science & Machine Learning",
    "🧠 AI, NLP & LLM",
    "🧬 Deep Learning",
    "💻 Software & Web Development",
    "📁 Other Projects",
]


def get_repositories():
    url = (
        f"https://api.github.com/users/{USERNAME}/repos"
        "?per_page=100&sort=updated&type=owner"
    )

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": f"{USERNAME}-profile-updater",
    }

    token = os.getenv("GITHUB_TOKEN")

    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode())


def normalize(text):
    return (text or "").lower().replace("_", " ").replace("-", " ")


def classify_repository(repo):
    name = normalize(repo.get("name"))
    description = normalize(repo.get("description"))
    language = normalize(repo.get("language"))

    topics = " ".join(
        normalize(topic)
        for topic in repo.get("topics", [])
    )

    text = f"{name} {description} {topics} {language}"

    scores = {}

    for category, keywords in CATEGORY_KEYWORDS.items():
        score = 0

        for keyword in keywords:
            keyword_normalized = normalize(keyword)

            if keyword_normalized in text:
                score += 1

        scores[category] = score

    best_category = max(scores, key=scores.get)

    if scores[best_category] == 0:
        return "📁 Other Projects"

    return best_category


def format_repo(repo):
    name = repo["name"]
    url = repo["html_url"]

    description = repo.get("description")

    language = repo.get("language")

    topics = repo.get("topics", [])

    lines = []

    lines.append(f"### 🔹 [{name}]({url})")

    if description:
        lines.append("")
        lines.append(description)

    metadata = []

    if language:
        metadata.append(language)

    if topics:
        nice_topics = [
            topic.replace("-", " ").title()
            for topic in topics[:4]
        ]

        metadata.extend(nice_topics)

    if metadata:
        lines.append("")
        lines.append(
            "**Tech / Topics:** " + " • ".join(metadata)
        )

    return "\n".join(lines)


def generate_projects(repositories):
    categorized = defaultdict(list)

    for repo in repositories:

        if repo["name"].lower() == USERNAME.lower():
            continue

        if repo.get("fork"):
            continue

        if repo.get("archived"):
            continue

        category = classify_repository(repo)

        categorized[category].append(repo)

    output = []

    for category in CATEGORY_ORDER:

        repos = categorized.get(category)

        if not repos:
            continue

        output.append(f"### {category}")
        output.append("")

        for repo in repos:
            output.append(format_repo(repo))
            output.append("")
            output.append("---")
            output.append("")

    return "\n".join(output).rstrip()


def update_readme(projects_markdown):

    with open(README_FILE, "r", encoding="utf-8") as file:
        content = file.read()

    start_marker = "<!-- PROJECTS_START -->"
    end_marker = "<!-- PROJECTS_END -->"

    if start_marker not in content or end_marker not in content:
        raise ValueError(
            "README markers not found. "
            "Add PROJECTS_START and PROJECTS_END."
        )

    before = content.split(start_marker)[0]

    after = content.split(end_marker)[1]

    new_content = (
        before
        + start_marker
        + "\n\n"
        + projects_markdown
        + "\n\n"
        + end_marker
        + after
    )

    with open(README_FILE, "w", encoding="utf-8") as file:
        file.write(new_content)


def main():

    print("Reading GitHub repositories...")

    repositories = get_repositories()

    print(f"Found {len(repositories)} repositories.")

    projects_markdown = generate_projects(repositories)

    update_readme(projects_markdown)

    print("README successfully updated.")


if __name__ == "__main__":
    main()
