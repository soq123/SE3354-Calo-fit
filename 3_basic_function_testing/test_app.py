from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>Flask is working</h1>"

if __name__ == "__main__":
    print("STARTING SERVER...")
    app.run(debug=True, use_reloader=False)