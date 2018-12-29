from flask import Flask
from flask import request
import json
import requests
import sys
import gathering.googleReviews as g
app = Flask(__name__)


@app.route("/")
def home():
    return "Hello, World!"

@app.route("/google/", methods = ['POST'])
def google():
    print("START google", file=sys.stderr)

    response = request.get_json()
    print(response)
    print(response.get('accessToken'))
    try:
        result = g.googleReviews(response.get('accessToken'))
    except KeyError:
        print("encountered key error")
        return json.dumps('KeyError in fetching google reviews')

    except TypeError:
        print("encountered type error")
        return json.dumps('TypeError in fetching google reviews')

    return json.dumps(result)


if __name__ == "__main__":
    app.run(debug=True)
