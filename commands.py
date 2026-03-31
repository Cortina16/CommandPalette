import ddgs


class Commands:
    def __init__(self):
        pass
    @staticmethod
    def web_search(query: str):
        """
        performs a web search and returns the result
        :param query: the web search query
        :return: the search result
        """
        try:
            results = ddgs.DDGS().text(query=query, max_results=3)
            results_array = [{'title': r['title'], 'description': r['body'], 'url': r['href']} for r in results]
            if results_array:
                return "\n".join([f"Title: {r['title']}\nDescription: {r['description']}" for r in results_array])
        except Exception as e:
            print(f'error in web search: {query}, error: {e}')
        return f'No results found for {query}'