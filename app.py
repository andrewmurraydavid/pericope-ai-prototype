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
    matched_pericopes = chroma_client.query(data['input'], n=10)  # or any desired n
    # process and return results as needed
    array_of_objects = [{ 'id': id_val, "pericope": meta['pericope'], 'distance': dist, 'metadata': { "pericope": meta['pericope'], "reference": meta['reference'], "start": meta['start'], "end": meta['end'] } }
        for id_list, dist_list, meta_list in zip(matched_pericopes['ids'], matched_pericopes['distances'], matched_pericopes['metadatas'])
        for id_val, dist, meta in zip(id_list, dist_list, meta_list)
    ]
    return jsonify(array_of_objects)

@app.route('/healthcheck')
def healthcheck():
    return 'OK'


if __name__ == '__main__':
    app.run(debug=True)
