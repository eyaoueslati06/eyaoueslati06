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


# GitHub topics that we want to display as technologies/tools.
TOOL_TOPIC_MAP = {

    "react": "React",
    "reactjs": "React",
    "nextjs": "Next.js",
    "next-js": "Next.js",

    "nodejs": "Node.js",
    "node-js": "Node.js",

    "express": "Express",
    "expressjs": "Express",

    "mongodb": "MongoDB",

    "mysql": "MySQL",
    "postgresql": "PostgreSQL",

    "power-bi": "Power BI",
    "powerbi": "Power BI",

    "tableau": "Tableau",

    "pandas": "Pandas",
    "numpy": "NumPy",

    "scikit-learn": "Scikit-learn",
    "sklearn": "Scikit-learn",

    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",

    "huggingface": "Hugging Face",
    "hugging-face": "Hugging Face",

    "langchain": "LangChain",

    "openai": "OpenAI",

    "flask": "Flask",
    "fastapi": "FastAPI",
    "django": "Django",

    "spark": "Apache Spark",
    "pyspark": "PySpark",

    "hadoop": "Hadoop",
    "kafka": "Kafka",

    "docker": "Docker",

    "sql": "SQL",
    "tsql": "T-SQL",
}


def api_request(url):

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": f"{USERNAME}-profile-updater",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    token = os.getenv("GITHUB_TOKEN")

    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(
        url,
        headers=headers
    )

    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode())


def get_repositories():

    url = (
        f"https://api.github.com/users/{USERNAME}/repos"
        "?per_page=100"
        "&sort=updated"
        "&type=owner"
    )

    return api_request(url)


def get_repository_languages(repo_name):

    url = (
        f"https://api.github.com/repos/"
        f"{USERNAME}/{repo_name}/languages"
    )

    try:
        languages = api_request(url)

        # GitHub returns something like:
        # {"Python": 120000, "Jupyter Notebook": 60000}
        #
        # Sort by amount of code.
        languages = sorted(
            languages.items(),
            key=lambda item: item[1],
            reverse=True
        )

        return [
            language
            for language, _ in languages
        ]

    except Exception as error:

        print(
            f"Could not read languages for "
            f"{repo_name}: {error}"
        )

        return []


def normalize(text):

    return (
        text or ""
    ).lower().replace(
        "_",
        " "
    ).replace(
        "-",
        " "
    )


def classify_repository(repo):

    name = normalize(repo.get("name"))

    description = normalize(
        repo.get("description")
    )

    language = normalize(
        repo.get("language")
    )

    topics = " ".join(
        normalize(topic)
        for topic in repo.get(
            "topics",
            []
        )
    )

    text = (
        f"{name} "
        f"{description} "
        f"{topics} "
        f"{language}"
    )

    scores = {}

    for category, keywords in CATEGORY_KEYWORDS.items():

        score = 0

        for keyword in keywords:

            keyword_normalized = normalize(
                keyword
            )

            if keyword_normalized in text:
                score += 1

        scores[category] = score

    best_category = max(
        scores,
        key=scores.get
    )

    if scores[best_category] == 0:
        return "📁 Other Projects"

    return best_category


def detect_tools(repo):

    tools = []

    # --------------------------------
    # 1. GitHub detected languages
    # --------------------------------

    languages = get_repository_languages(
        repo["name"]
    )

    for language in languages:

        if language not in tools:
            tools.append(language)

    # --------------------------------
    # 2. Useful technologies from topics
    # --------------------------------

    topics = repo.get(
        "topics",
        []
    )

    for topic in topics:

        topic_lower = topic.lower()

        if topic_lower in TOOL_TOPIC_MAP:

            tool = TOOL_TOPIC_MAP[
                topic_lower
            ]

            if tool not in tools:
                tools.append(tool)

    # Keep the line readable.
    return tools[:7]


def format_repo(repo):

    name = repo["name"]

    url = repo["html_url"]

    description = repo.get(
        "description"
    )

    tools = detect_tools(repo)

    lines = []

    # ------------------------------
    # Project name
    # ------------------------------

    lines.append(
        f"#### 🔹 [{name}]({url})"
    )

    # ------------------------------
    # Description
    # ------------------------------

    if description:

        lines.append("")
        lines.append(description)

    # ------------------------------
    # Tools
    # ------------------------------

    if tools:

        lines.append("")

        lines.append(
            "**Tools:** "
            + " • ".join(tools)
        )

    return "\n".join(lines)


def generate_projects(repositories):

    categorized = defaultdict(list)

    for repo in repositories:

        # Do not display the profile repository itself.
        if (
            repo["name"].lower()
            == USERNAME.lower()
        ):
            continue

        # Do not display forks.
        if repo.get("fork"):
            continue

        # Do not display archived repos.
        if repo.get("archived"):
            continue

        category = classify_repository(
            repo
        )

        categorized[
            category
        ].append(repo)

    output = []

    for category in CATEGORY_ORDER:

        repos = categorized.get(
            category
        )

        if not repos:
            continue

        output.append(
            f"### {category}"
        )

        output.append("")

        for repo in repos:

            output.append(
                format_repo(repo)
            )

            output.append("")

            output.append("---")

            output.append("")

    return "\n".join(
        output
    ).rstrip()


def update_readme(projects_markdown):

    with open(
        README_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        content = file.read()

    start_marker = (
        "<!-- PROJECTS_START -->"
    )

    end_marker = (
        "<!-- PROJECTS_END -->"
    )

    if (
        start_marker not in content
        or end_marker not in content
    ):

        raise ValueError(
            "README markers not found."
        )

    before = content.split(
        start_marker
    )[0]

    after = content.split(
        end_marker
    )[1]

    new_content = (
        before
        + start_marker
        + "\n\n"
        + projects_markdown
        + "\n\n"
        + end_marker
        + after
    )

    with open(
        README_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            new_content
        )


def main():

    print(
        "Reading GitHub repositories..."
    )

    repositories = get_repositories()

    print(
        f"Found {len(repositories)} repositories."
    )

    projects_markdown = (
        generate_projects(
            repositories
        )
    )

    update_readme(
        projects_markdown
    )

    print(
        "README successfully updated."
    )


if __name__ == "__main__":
    main()
