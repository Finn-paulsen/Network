import webbrowser
import threading
import os
from app import app
from routes import *

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000')

if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Timer(1.25, open_browser).start()
    app.run(host="0.0.0.0", port=5000, debug=True)
