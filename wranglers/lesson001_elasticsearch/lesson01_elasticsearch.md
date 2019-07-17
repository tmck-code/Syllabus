# **||>** Elasticsearch

## --> What is Elasticsearch?

* "Search Cluster"
  * Multiple computers in network
  * Store data and communicate together
* Elasticsearch == elastic _storage_, not necessarily elastic _performance_.
* Allows multiple users to query large amounts of data quickly.
* Can store and handle many, many records.

---

## --> Who makes it?

* `elastic.co`
* Other products:
  * Kibana
  * Logstash
  * "ELK"
  * Graph
  * X-Pack
  * Beats
* Main use-case is consuming **logs**.

---

## --> Some core terms

> Exercise to the reader! These terms are all useful, search the elasticsearch docs for definitions.

* Shards, nodes, indexes
* Lucene
* Mapping
* Documents

---

### **</>** Inverted Indexes

In computing, an index is used to access specific data very fast.

_e.g. "Product ID 123 points to record -> {"id": 123, "colour": "green", "size": "regular"}_

When _inverted_ indexes, instead of requesting something via ID like you
usually would, you can use almost **_any part_** of the data that you want if
you have it configured correctly.

e.g. Finding a movie name in IMDB by searching a quote from that movie, as
opposed to the traditional setup which finds the movie via the name or an ID,
giving you the script or collection of quotes.

From Wikipedia:

> In computer science, an inverted index (also referred to as a postings file
> or inverted file) is a database index storing a mapping from content, such as
> words or numbers, to its locations in a table, or in a document or a set of
> documents (named in contrast to a forward index, which maps from documents to
> content).

> The purpose of an inverted index is to **allow fast full-text searches**, at a
> **cost of increased processing** when a document is added to the database. The
> inverted file may be the database file itself, rather than its index.

> It is the most popular data structure used in document retrieval systems,
> used on a **large scale** for example in **search engines.**

---

### **</>** Nodes & Shards

* `Nodes` == `data nodes` == `instances`
  * There are also `master nodes` and `coordinator nodes`
* `Shards` == `lucene indexes`
  * you can think of each `shard` like a search engine that indexes and queries for a subset of the data in the cluster.

---

## --> What does a mapping look like?

### **</>** Nested Mapping

Nested mappings are a good example of the power of elasticsearch, and of its
ability to easily confuse.

```json
{
  "settings": {
    "index": {
      "number_of_shards": 1,
      "number_of_replicas": 0
    }
  },
  "mappings": {
    "_doc": {
      "properties": {
        "valz": {
          "type": "nested",
          "dynamic": "strict",
          "properties": {
            "key": {
              "type": "keyword",
              "fields": {
                "path": {"type": "text"}
              }
            },
            "keyword_value": {"type": "keyword"},
            "boolean_value": {"type": "boolean"},
            "float_value": {"type": "double"},
            "date_value": {"type": "date"}
          }
        }
      }
    }
  }
}
```

---

## --> Example document

This is an example of a document, as returned by a query.

```json
{
  "_index": "my_index",
  "_type": "_doc",
  "_id": "029384028759384509437860983409568",
  "_source": {
    "balance_infoz": [
      {
        "key": "dvd_rental_due_date",
        "date_value": [
          "2014-10-11T00:00:00"
        ]
      },
      {
        "key": "n_days_rental_overdue",
        "keyword_value": [
          15
        ]
      },
      {
        "key": "fines_owing_on_account",
        "boolean_value": [
          true
        ]
      },
      {
        "key": "funds_owing",
        "float_value": [
          235.23
        ]
      }
    ]
  }
}
```

---

## Final note: respect search engines

Running intensive or large queries against massive search engines is dangerous
and can impact the experience of other users. This means slowness, timeouts and
even complete failures.

### Never run an ES query without first running it past a developer

Data wrangling is a high-pressure job, and _even_ you're not a trained
developer then you should always take extreme care when executing queries, 
find the appropriate someone and check before pulling the trigger.

This is the case even when the query is small or is expected to have little impact.
Best case, the query is fine and the team is aware in case anything goes awry. Worst case, search engine failures with no warning.

* **Make sure that you know the scope of your query, and how much work you are asking it to do.**
