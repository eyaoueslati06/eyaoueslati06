import json
import os
import urllib.request
import base64
import re
from collections import defaultdict


USERNAME = "eyaoueslati06"
README_FILE = "README.md"


README_CACHE = {}
LANGUAGE_CACHE = {}


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
        "fraud detection",
        "anomaly detection",
        "forecasting",
    ],

    "🧠 AI, NLP & LLM": [
        "artificial intelligence",
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
        "gemini",
        "faiss",
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
        "node.js",
        "nodejs",
        "express",
        "mongodb",
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

    "gemini": "Gemini",
    "google-gemini": "Gemini",

    "faiss": "FAISS",

    "streamlit": "Streamlit",

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

    "jupyter": "Jupyter Notebook",
}


README_TOOL_KEYWORDS = {

    "streamlit": "Streamlit",

    "langchain": "LangChain",

    "faiss": "FAISS",

    "gemini": "Gemini",

    "google generative ai": "Gemini",

    "hugging face": "Hugging Face",
    "huggingface": "Hugging Face",

    "openai": "OpenAI",

    "pandas": "Pandas",

    "numpy": "NumPy",

    "scikit-learn": "Scikit-learn",
    "sklearn": "Scikit-learn",

    "tensorflow": "TensorFlow",

    "pytorch": "PyTorch",

    "matplotlib": "Matplotlib",

    "seaborn": "Seaborn",

    "plotly": "Plotly",

    "power bi": "Power BI",

    "tableau": "Tableau",

    "react": "React",

    "node.js": "Node.js",
    "nodejs": "Node.js",

    "express": "Express",

    "mongodb": "MongoDB",

    "mysql": "MySQL",

    "postgresql": "PostgreSQL",

    "spark": "Apache Spark",

    "pyspark": "PySpark",

    "hadoop": "Hadoop",

    "kafka": "Kafka",

    "elasticsearch": "Elasticsearch",

    "flask": "Flask",

    "fastapi": "FastAPI",

    "django": "Django",

    "docker": "Docker",

    "jupyter": "Jupyter Notebook",

    "nltk": "NLTK",

    "spacy": "spaCy",

    "gensim": "Gensim",
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
        return json.loads(
            response.read().decode()
        )


def get_repositories():

    url = (
        f"https://api.github.com/users/{USERNAME}/repos"
        "?per_page=100"
        "&sort=updated"
        "&type=owner"
    )

    return api_request(url)


def get_repository_languages(repo_name):

    if repo_name in LANGUAGE_CACHE:
        return LANGUAGE_CACHE[repo_name]

    url = (
        f"https://api.github.com/repos/"
        f"{USERNAME}/{repo_name}/languages"
    )

    try:

        languages = api_request(url)

        languages = sorted(
            languages.items(),
            key=lambda item: item[1],
            reverse=True
        )

        result = [
            language
            for language, _ in languages
        ]

        LANGUAGE_CACHE[repo_name] = result

        return result

    except Exception as error:

        print(
            f"Could not read languages for "
            f"{repo_name}: {error}"
        )

        LANGUAGE_CACHE[repo_name] = []

        return []


def get_readme_content(repo_name):

    if repo_name in README_CACHE:
        return README_CACHE[repo_name]

    url = (
        f"https://api.github.com/repos/"
        f"{USERNAME}/{repo_name}/readme"
    )

    try:

        readme_data = api_request(url)

        encoded_content = readme_data.get(
            "content",
            ""
        )

        if not encoded_content:
            README_CACHE[repo_name] = ""
            return ""

        content = base64.b64decode(
            encoded_content
        ).decode(
            "utf-8",
            errors="ignore"
        )

        README_CACHE[repo_name] = content

        return content

    except Exception as error:

        print(
            f"Could not read README for "
            f"{repo_name}: {error}"
        )

        README_CACHE[repo_name] = ""

        return ""


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


def clean_markdown_text(text):

    text = re.sub(
        r"!\[.*?\]\(.*?\)",
        "",
        text
    )

    text = re.sub(
        r"\[(.*?)\]\(.*?\)",
        r"\1",
        text
    )

    text = re.sub(
        r"<.*?>",
        "",
        text
    )

    text = re.sub(
        r"\*\*(.*?)\*\*",
        r"\1",
        text
    )

    text = re.sub(
        r"\*(.*?)\*",
        r"\1",
        text
    )

    text = re.sub(
        r"`(.*?)`",
        r"\1",
        text
    )

    return text.strip()


def get_readme_description(repo_name):

    readme_content = get_readme_content(
        repo_name
    )

    if not readme_content:
        return ""

    readme_content = re.sub(
        r"<!--.*?-->",
        "",
        readme_content,
        flags=re.DOTALL
    )

    lines = readme_content.splitlines()

    paragraphs = []
    current_paragraph = []

    for line in lines:

        line = line.strip()

        if not line:

            if current_paragraph:

                paragraph = " ".join(
                    current_paragraph
                )

                paragraphs.append(
                    paragraph
                )

                current_paragraph = []

            continue

        if line.startswith("#"):
            continue

        if line.startswith("!["):
            continue

        if "img.shields.io" in line:
            continue

        if line in [
            "---",
            "***",
            "___"
        ]:
            continue

        if line.startswith("<"):
            continue

        if (
            line.startswith("- ")
            or line.startswith("* ")
            or line.startswith("+ ")
        ):
            continue

        if re.match(
            r"^\d+\.",
            line
        ):
            continue

        cleaned_line = clean_markdown_text(
            line
        )

        if cleaned_line:
            current_paragraph.append(
                cleaned_line
            )

    if current_paragraph:

        paragraphs.append(
            " ".join(
                current_paragraph
            )
        )

    for paragraph in paragraphs:

        paragraph = clean_markdown_text(
            paragraph
        )

        if len(paragraph) >= 40:

            if len(paragraph) > 300:

                paragraph = (
                    paragraph[:297].rstrip()
                    + "..."
                )

            return paragraph

    return ""


def classify_repository(repo):

    name = normalize(
        repo.get("name")
    )

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

    readme_text = normalize(
        get_readme_content(
            repo["name"]
        )
    )

    text = (
        f"{name} "
        f"{description} "
        f"{topics} "
        f"{language} "
        f"{readme_text}"
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
    # GitHub detected languages
    # --------------------------------

    languages = get_repository_languages(
        repo["name"]
    )

    for language in languages:

        if language not in tools:
            tools.append(language)

    # --------------------------------
    # GitHub topics
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

    # --------------------------------
    # README tool detection
    # --------------------------------

    readme_content = get_readme_content(
        repo["name"]
    ).lower()

    for keyword, tool in README_TOOL_KEYWORDS.items():

        if keyword in readme_content:

            if tool not in tools:
                tools.append(tool)

    return tools[:8]


def format_repo(repo):

    name = repo["name"]

    url = repo["html_url"]

    description = repo.get(
        "description"
    )

    if not description:

        description = get_readme_description(
            repo["name"]
        )

    tools = detect_tools(repo)

    lines = []

    lines.append(
        f"#### 🔹 [{name}]({url})"
    )

    if description:

        lines.append("")
        lines.append(description)

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

        # Skip profile repository
        if (
            repo["name"].lower()
            == USERNAME.lower()
        ):
            continue

        # Skip forks
        if repo.get("fork"):
            continue

        # Skip archived repos
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

    projects_markdown = generate_projects(
        repositories
    )

    update_readme(
        projects_markdown
    )

    print(
        "README successfully updated."
    )


if __name__ == "__main__":
    main()
