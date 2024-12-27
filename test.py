from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello World!'

if __name__ == '__main__':
    print("=== DÉMARRAGE DU TEST ===")
    app.run(host='0.0.0.0', port=9090, debug=True)
