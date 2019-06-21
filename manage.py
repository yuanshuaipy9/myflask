from flask import Flask
from flask_sqlalchemy import SQLAlchemy


class Config(object):
    DEBUG=True

    SQLALCHEMY_DATABASE_URI="mysql://root:mysql@127.0.0.1:3306/classflask"
    SQLALCHEMY_TRACK_MODIFICATIONS=False

app = Flask(__name__)
app.config.from_object(Config)
db=SQLAlchemy(app)

@app.route("/")
def index():
    return "index"


if __name__ == '__main__':
    app.run()


