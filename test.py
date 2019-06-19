from flask import Flask

app = Flask(__name__)


@app.route("/")
def index():
    print("nihao")
    print("66")
    return "index"


if __name__ == '__main__':
    app.run(debug=True)


