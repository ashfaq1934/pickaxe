from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from flask import Flask, render_template, request
from collections import OrderedDict
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

        ra_nodes = []
        ca_nodes = []
        edges = []
        atoms = []

        supporting_arguments = []
        conflicting_arguments = []

        for item in response.hits:
            for node in item.nodes:
                """
                Separate RA and CA type schemes
                """
                if node.type == 'scheme':
                    if node.metadata.aif_json.type == 'RA':
                        scheme = {
                            "node": node
                        }
                        ra_nodes.append(scheme)
                    if node.metadata.aif_json.type == 'CA':
                        scheme = {
                            "node": node
                        }
                        ca_nodes.append(scheme)
            for edge in item.edges:
                edges.append(edge)

            for node in item.nodes:
                if node.type == 'atom':
                    atoms.append(node)

        for node in ra_nodes:
            for edge in edges:
                if node['node']['id'] in edge.target_id or node['node']['id'] in edge.source_id:
                    node.setdefault('connections', []).append(edge)

        for node in ca_nodes:
            for edge in edges:
                if node['node']['id'] in edge.target_id or node['node']['id'] in edge.source_id:
                    node.setdefault('connections', []).append(edge)

        for atom in atoms:
            for node in ra_nodes:
                for connection in node['connections']:
                    if atom.id in connection['source_id'] or atom.id in connection['target_id']:
                        node.setdefault("atoms", []).append(atom)
            for node in ca_nodes:
                for connection in node['connections']:
                    if atom.id in connection['source_id'] or atom.id in connection['target_id']:
                        node.setdefault("atoms", []).append(atom)

        for node in ra_nodes:
            for connection in node['connections']:
                if connection['target_id'] in node['node']['id']:
                    node.setdefault("premise_edges", []).append(connection)
                elif connection['source_id'] in node['node']['id']:
                    node.setdefault("conclusion_edges", []).append(connection)
            for atom in node['atoms']:
                for premise_edge in node['premise_edges']:
                    if atom['id'] in premise_edge['source_id']:
                        node.setdefault("premises", []).append(atom)
                for conclusion_edge in node['conclusion_edges']:
                    if atom['id'] in conclusion_edge['target_id']:
                        node["conclusion"] = atom
            for premise in node['premises']:
                support = {
                    "premise": premise,
                    "conclusion": node['conclusion']
                }
                supporting_arguments.append(support)

        for node in ca_nodes:
            for connection in node['connections']:
                if connection['target_id'] in node['node']['id']:
                    node.setdefault("premise_edges", []).append(connection)
                elif connection['source_id'] in node['node']['id']:
                    node.setdefault("conclusion_edges", []).append(connection)
            for atom in node['atoms']:
                for premise_edge in node['premise_edges']:
                    if atom['id'] in premise_edge['source_id']:
                        node.setdefault("premises", []).append(atom)
                for conclusion_edge in node['conclusion_edges']:
                    if atom['id'] in conclusion_edge['target_id']:
                        node["conclusion"] = atom
            for premise in node['premises']:
                conflict = {
                    "premise": premise,
                    "conclusion": node['conclusion']
                }
                conflicting_arguments.append(conflict)

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
