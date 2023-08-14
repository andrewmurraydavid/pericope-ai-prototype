from flask import Flask, request, jsonify
from chroma_client import ChromaClient
chroma_client = ChromaClient()
chroma_client.init_chroma()

app = Flask(__name__)

@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    matched_pericopes = chroma_client.query(data['input'], 20)  # or any desired n

    return jsonify(matched_pericopes)

@app.route('/feedback', methods=['POST'])
def feedback():
    data = request.json
    query = data['query']
    uid = data['uid']
    _feedback = data['feedback']

    if _feedback == 'positive':
        chroma_client.reinforce_document_with_query(query, uid)
    elif _feedback == 'negative':
        # TODO: implement negative feedback
        pass

    return jsonify({'status': 'OK'})


@app.route('/healthcheck')
def healthcheck():
    return 'OK'


if __name__ == '__main__':
    app.run(debug=True)
