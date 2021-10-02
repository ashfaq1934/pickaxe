from elasticsearch import Elasticsearch
from elasticsearch.serializer import JSONSerializer
from elasticsearch_dsl import Search
from flask import Flask, render_template, request

app = Flask(__name__, static_folder="static")
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])


@app.route('/')
def index():

    return render_template('index.html')


@app.route('/results', methods=['GET'])
def results():
    query = request.args.get('q')
    if query is not None:
        s = Search(using=es, index="arguments").query("multi_match", query=query, fields=['nodes.text'])
        response = s.execute()
        return render_template('results.html', response=response)


if __name__ == "__main__":
    app.run(debug=True)


