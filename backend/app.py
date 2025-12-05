from flask import Flask, send_from_directory
from flask_cors import cross_origin

from scripts.recherche import recherche_book



app = Flask(__name__)
app.register_blueprint(recherche_book)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'
@app.route("/pdf/<path:filename>")
@cross_origin(origins=['http://localhost:8081'], supports_credentials=True)
def serve_pdf(filename):
    pdf_dir = "ressources"
    return send_from_directory(pdf_dir, filename)


if __name__ == '__main__':
    app.run()
