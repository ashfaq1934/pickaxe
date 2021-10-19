from elasticsearch import Elasticsearch
from elasticsearch.serializer import JSONSerializer
from elasticsearch_dsl import Search, Q
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

        ra_nodes = []
        ca_nodes = []
        support_edges = []
        conflict_edges = []

        supporting_arguments = []
        conflicting_arguments = []

        for item in response.hits:
            for node in item.nodes:
                if node.type == 'scheme':
                    if node.metadata.aif_json.type == 'RA':
                        ra_nodes.append(node)
                    if node.metadata.aif_json.type == 'CA':
                        ca_nodes.append(node)
            for edge in item.edges:
                for node in ra_nodes:
                    if node.id in edge.source_id:
                        support_edges.append(edge)
                for node in ca_nodes:
                    if node.id in edge.source_id:
                        conflict_edges.append(edge)
            for node in item.nodes:
                if node.type == 'atom':
                    for edge in support_edges:
                        if node.id in edge.target_id:
                            supporting_arguments.append(node)
                    for edge in conflict_edges:
                        if node.id in edge.target_id:
                            conflicting_arguments.append(node)

        return render_template('results.html', response=response, q=query, supporting_arguments=supporting_arguments,
                               conflicting_arguments=conflicting_arguments)


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
