from flask import Flask

app = Flask(__name__)


@app.route("/")
def index():
    print("测试")
    return "index"


if __name__ == '__main__':
    app.run(debug=True)


