import os

from flask import Flask
from flask import request
from flask import render_template



app = Flask(__name__)



@app.route("/")
def index():
    return render_template('hello.html')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        return render_template('submit.html')





if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)