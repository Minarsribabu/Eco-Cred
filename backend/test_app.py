from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello World! Home page working!"

@app.route('/test')
def test():
    return "Test route working!"

if __name__ == '__main__':
    app.run(debug=True, port=5001)
