
from flask_cors import CORS
from flask import Flask
from flask import render_template
from flask import send_from_directory

app = Flask(__name__)
CORS(app)


@app.route('/f5app/')
def index_f5():
    return render_template('indexf5.html')

@app.route('/fortiapp/')
def index_forti():
    return render_template('indexforti.html')

@app.route("/static/<path:path>")
def static_dir(path):
    return send_from_directory("static", path)



if __name__ == '__main__':
    app.run(port=5001)