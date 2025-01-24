import os
import sys
import random
import traceback

import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.base import AssistantService, get_config
from utils import log
from utils.terminal_formatter import Style

logger = log.get_logger("LLM service")

OLLAMA_SCHEME = "http"
OLLAMA_PORT = 11434
# OLLAMA_HOST = "127.0.0.1"
OLLAMA_HOST = "192.168.1.83"
OLLAMA_MODEL = "llama3.2"

MAX_LINES_FOR_QUIZ = 30
MAX_HISTORY = 2


class LLM(AssistantService):
    """Interaction with local LLM
    """

    def __init__(self):
        super().__init__()
        self.url = f"{OLLAMA_SCHEME}://{OLLAMA_HOST}:{OLLAMA_PORT}/api/chat"
        self.nb_path = os.path.expanduser(get_config("nb_path") or "~/.nb")
        self.history = []  # Chat history

    def save_history(self, message):
        if len(self.history) == MAX_HISTORY:
            self.history = self.history[1:]
        self.history.append(message)

    def get_random_nb_note_section(self, dir="home"):
        path = f"{self.nb_path}/{dir}"
        files = [x.name for x in os.scandir(path) if x.is_file()]

        filepath = path + "/" + random.choice(files)
        lines = open(filepath).readlines()[5:]  # Skip the initial metadata, might need to read that as well
        lines = [x for x in lines if x != '\n']

        if len(lines) <= MAX_LINES_FOR_QUIZ:
            content = '\n'.join(lines)
        else: # find a section
            start = random.randint(0, len(lines) - MAX_LINES_FOR_QUIZ)
            content = '\n'.join(lines[start : start + MAX_LINES_FOR_QUIZ])

        return content

    def query_data(self, message):
        
        return {
          "model": OLLAMA_MODEL,
          "system": "You are knowledgeable in various topics and you can ask insightful review questions based on some document",
          "messages": [
              *self.history,
              message,
              # TODO: history
          ],
          "stream": False
        }

    def handle_quiz(self, args):
        if args and args[0] == "answer":
            answer = " ".join(args[1:])
            query_message = {
                "role": "user",
                "conent": answer,
            }
        else:
            section = self.get_random_nb_note_section()
            query_message = {
                "role": "user",
                "content": f"Ask me insigntful question based on the following and evaluate my answer\n\n {section}"
            }
        query_data = self.query_data(query_message)
        query_message = query_data["messages"][-1]

        resp = requests.post(self.url, json=query_data)
        logger.info(resp.request.headers)
        logger.info(f"POST {self.url} {resp.status_code}")

        resp = resp.json()
        message = resp["message"]
        msg = message["content"]

        self.save_history(query_message)
        self.save_history(message)
        logger.info(self.history)

        return Style.green(f"{msg}")


if __name__ == '__main__':
    m = LLM()
    port = sys.argv[1]
    try:
        m.initialize_and_run(port)
    except SystemExit:
        pass
    except Exception:
        logger.error(traceback.format_exc())
