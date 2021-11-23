# PickAxe #

PickAxe is an argument based search engine built on Elasticsearch. It works with arguments that are in the SADFace argument format.

## Run locally ##

- Install the Elasticsearch search engine <https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html>.
- Start Elasticsearch.
```
$ sudo service elasticsearch start
```
- Start the server.

```
$ python app.py
```

- The project should start running at <http://0.0.0.0:5000/>.
