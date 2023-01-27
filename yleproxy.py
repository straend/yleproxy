from flask import Flask, Response, send_file
from bs4 import BeautifulSoup
import requests
from pathlib import Path
import os

MY_URL = os.getenv("URL", "http://127.0.0.1:5000")
MY_DATA_DIR = os.getenv("DATA_DIR", "./data")
MY_DEBUG = os.getenv("DEBUG", False)

dataDir = Path(MY_DATA_DIR)
dataDir.mkdir(exist_ok=True, parents=True)

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/rss/<string:id>')
def show_rss(id):
    data = requests.get("https://feeds.yle.fi/areena/v1/series/{}.rss?lang=sv".format(id))
    soup = BeautifulSoup(data.content, "lxml-xml")

    # Find links to audiofiles that doesn't end with .mp3, and route them via ourself
    for l in soup.find_all('enclosure'):
        url = l.get('url')
        if url.endswith(".mp3"):
            continue
        # split url to only include last id
        x = url.split('/')[-1]
        l['url'] = "{}/get/{}.mp3".format(MY_URL, x)
    dat = soup.prettify()
    return Response(dat, mimetype="text/xml")

@app.route('/get/<path:fname>.mp3')
def get_file(fname):
    f = dataDir / fname
    if not f.exists():
        data = requests.get("https://yleawsaudioipv4.akamaized.net/mediaredirect/{}".format(fname))
        f.write_bytes(data.content)

    return send_file(f)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=MY_DEBUG)
