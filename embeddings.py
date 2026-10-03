import json
from pathlib import Path

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


BASE_DIR = Path(__file__).resolve().parent
TOOLS_FILE = BASE_DIR / "data" / "tools.json"

model = SentenceTransformer("all-MiniLM-L6-v2")


def load_tools():
    with open(TOOLS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def create_tool_text(tool):
    return f"""
    Name: {tool["name"]}
    Description: {tool["description"]}
    Categories: {", ".join(tool["categories"])}
    Best for: {", ".join(tool["best_for"])}
    """.strip()


def search_tools(query, top_k=3):
    tools = load_tools()

    tool_texts = [create_tool_text(tool) for tool in tools]

    tool_embeddings = model.encode(tool_texts)
    query_embedding = model.encode([query])

    similarities = cosine_similarity(query_embedding, tool_embeddings)[0]

    results = []

    for index in similarities.argsort()[::-1][:top_k]:
        results.append({
            "tool": tools[index],
            "score": float(similarities[index])
        })

    return results


if __name__ == "__main__":
    query = "I want to learn Python programming"

    results = search_tools(query)

    print("Query:")
    print(query)

    print("\nSemantic search results:")

    for result in results:
        print("\nTool:", result["tool"]["name"])
        print("Score:", round(result["score"], 4))
        print("Description:", result["tool"]["description"])