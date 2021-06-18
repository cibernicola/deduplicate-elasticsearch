#!/usr/local/bin/python3

# A description and analysis of this code can be found at 
# https://alexmarquardt.com/2018/07/23/deduplicating-documents-in-elasticsearch/

import hashlib
from elasticsearch import Elasticsearch, helpers

ES_HOST = 'URL:9200'
ES_USER = 'USER'
ES_PASSWORD = 'PWD'

es = Elasticsearch([ES_HOST], http_auth=(ES_USER, ES_PASSWORD))
dict_of_duplicate_docs = {}

# The following line defines the fields that will be
# used to determine if a document is a duplicate
keys_to_include_in_hash = ["campo1","campo2"]


# Process documents returned by the current search/scroll
def populate_dict_of_duplicate_docs(hit):

    combined_key = ""
    for mykey in keys_to_include_in_hash:
        combined_key += str(hit['_source'][mykey])

    _id = hit["_id"]

    hashval = hashlib.md5(combined_key.encode('utf-8')).digest()

    # If the hashval is new, then we will create a new key
    # in the dict_of_duplicate_docs, which will be
    # assigned a value of an empty array.
    # We then immediately push the _id onto the array.
    # If hashval already exists, then
    # we will just push the new _id onto the existing array
    dict_of_duplicate_docs.setdefault(hashval, []).append(_id)


# Loop over all documents in the index, and populate the
# dict_of_duplicate_docs data structure.
def scroll_over_all_docs():
    for hit in helpers.scan(es, index='indexName'):
        populate_dict_of_duplicate_docs(hit)


def loop_over_hashes_and_remove_duplicates():
    # Search through the hash of doc values to see if any
    # duplicate hashes have been found
    for hashval, array_of_ids in dict_of_duplicate_docs.items():
      if len(array_of_ids) > 1:
        print("********** Duplicate docs hash=%s **********" % hashval)
        # Get the documents that have mapped to the current hasva
        matching_docs = es.mget(index="indexName", doc_type="_doc", body={"ids": array_of_ids})
        current = 0 #contador de iteraciones del dict que contiene los datos de los docs duplicados
        totalDocs = len(matching_docs) -1 #màximo de iteraciones equivale al total de documentos duplicados, menos uno 

        for doc in matching_docs['docs']:           
            current+=1
            if current <= totalDocs: #si el contador es menor o igual al contador de docs eliminados, el documento se elimina.
                es.delete(index="indexName", doc_type="_doc", id=doc.get('_id'))
                print("Eliminando doc=%s\n" % doc)



def main():
    scroll_over_all_docs()
    loop_over_hashes_and_remove_duplicates()


main()
