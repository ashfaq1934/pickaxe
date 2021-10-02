from elasticsearch import Elasticsearch
from elasticsearch import helpers
import requests

arguments_list = []

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

documents_request = requests.get('http://admin:password@localhost:5984/sadface/_all_docs')
data = documents_request.json()
data_objects = data['rows']

for data_object in data_objects:
    nodeset_id = data_object['id']
    data_request = requests.get('http://admin:password@localhost:5984/sadface/' + nodeset_id)
    argument = data_request.json()
    arguments_list.append(argument)

resp = helpers.bulk(
    es,
    arguments_list,
    index="arguments",
)
print(resp)
