import sys
from duckduckgo_search import DDGS

def get_live_news_context(sport_name: str) -> str:
    """
    Queries live search spaces using the highly stable fallback layout.
    """
    search_query = f"{sport_name} latest tournament results match updates 2026"
    retrieved_texts = []

    try:
        # Standard configuration format for stable pipeline extraction
        with DDGS() as ddgs:
            # We use keywords= to align perfectly across varying system library updates
            results = list(ddgs.text(keywords=search_query, max_results=2))
        
        if results:
            for index, r in enumerate(results, start=1):
                title = r.get("title", "Recent Match Update")
                snippet = r.get("body") or r.get("snippet") or "Data context empty."
                retrieved_texts.append(f"Source {index}: {title}\nSnippet: {snippet}")
    except Exception as e:
        print(f"[SEARCH LOG]: Web crawl exception caught: {e}")

    if not retrieved_texts:
        return f"Notice: Live search context offline. Grounding generation using historical patterns for {sport_name}."

    return "\n\n".join(retrieved_texts)