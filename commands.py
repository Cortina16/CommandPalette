import ddgs
import webbrowser
import ai
from spotify_handler import main_controller_spotify

class Commands:
    def __init__(self):
        self.BROWSER_PATHS = {
            # if you want jarvis to be able to use other browsers,\
            # add a line with what you want the browser to be titled on the left
            # then add it's directory to the right
            # then find the prompt for brwosers and add the instruction that {browser title} is how jarvis hsould refer to whatever browser you added.
            "firefox incognito": "C:\\Program Files\\Mozilla Firefox\\private_browsing.exe",
            "firefox regular": "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
            "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        }
        for name, path in self.BROWSER_PATHS.items():
            webbrowser.register(name, None, webbrowser.BackgroundBrowser(path))
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
    @staticmethod
    def toggle_playback():
        print('ball cancer')


    def open_tabs(self, url: str, browser: str = 'chrome'):
        try:
            for name, v in self.BROWSER_PATHS.items():
                if name == browser:
                    webbrowser.get(name).open_new_tab(url)
                    return 'tab opened successfully'
            webbrowser.get('chrome').open_new_tab(url)
            return 'defaulted to google because whatever you put in did not work'
        except webbrowser.Error as e:
            return f"error could not find or open the requested browser: {browser}, with error message: {e}"
        except Exception as e:
            return f"error {e}"

