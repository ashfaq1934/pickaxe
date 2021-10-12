from elasticsearch import Elasticsearch
from elasticsearch.serializer import JSONSerializer
from elasticsearch_dsl import Search, Q
from flask import Flask, render_template, request
import json

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
        return render_template('results.html', response=response, q=query)


@app.route('/graph/<id>', methods=['GET'])
def graph(id):
    query = {
        'from': 0, 'size': 1,
        'query': {
            'bool': {
              'must': [
                {
                  'match': {
                    'nodes.id': id
                  }
                }
              ]
            }
        }
    }

    response = es.search(index='arguments', body=query)
    nodeset_id = response['hits']['hits'][0]['_id']
    nodes = response['hits']['hits'][0]['_source']['nodes']
    edges = response['hits']['hits'][0]['_source']['edges']

    return render_template('graph.html', nodes=nodes, edges=edges, nodeset_id=nodeset_id)


if __name__ == "__main__":
    app.run(debug=True)
