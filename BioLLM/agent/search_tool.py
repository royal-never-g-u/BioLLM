from ddgs import DDGS

class SearchTool:
    def run(self, prompt: str, memory=None) -> str:
        query = prompt.strip()
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=3)
            if results:
                return "\n\n".join(
                    [f"[{i + 1}] {r['body']}\nURL: {r['href']}" for i, r in enumerate(results)]
                )
            else:
                return "No relevant search results found." 