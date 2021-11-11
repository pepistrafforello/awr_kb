"""
   Copyright 2021 Expert System USA, Inc.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

# property "name" is needed for showing a label in ratel
# "location" for showing in map

import sys
sys.dont_write_bytecode = True

import os
import json
import datetime
import requests
import time
import re
import rdflib
import csv


# pip install qwikidata
import qwikidata.claim
import qwikidata.json_dump
import qwikidata.entity

# pip install pydgraph
import pydgraph

"""
from https://doc.wikimedia.org/Wikibase/master/php/md_docs_topics_json.html:

The example below is for an Item.
{
  "id": "Q60",
  "type": "item",
  "labels": {},
  "descriptions": {},
  "aliases": {},
  "claims": {},
  "sitelinks": {},
  "lastrevid": 195301613,
  "modified": "2020-02-10T12:42:02Z"
}
Properties will not include sitelinks, but will include a datatype.
{
  "id": "P30",
  "type": "property",
  "datatype": "wikibase-item"
  "labels": {},
  "descriptions": {},
  "aliases": {},
  "claims": {},
  "lastrevid": 195301614,
  "modified": "2020-02-10T12:42:02Z"
}
"""

# def load_obj(obj):
#     obj_type = obj["type"]
#     # obj_type can be "item", "property", "lexeme"
#     # for description of lexeme, see:
#     # https://www.mediawiki.org/wiki/Extension:WikibaseLexeme/Data_Model

#     qid = obj["id"]
#     if "en" not in obj["labels"]:
#         print("NO EN LABEL: " + qid)

#     main_label = obj["labels"]["en"]["value"]

#     alt_labels = []
#     if "en" in obj["aliases"]:
#         alt_labels = [ l["value"] for l in obj["aliases"]["en"] if l["value"] != main_label ]

#     description = ""
#     if "en" in obj["descriptions"]:
#         description = obj["descriptions"]["en"]["value"]

#     # handle claims
#     """
# claims": {
#     "P1082": [
#                 { # _REQUIRED_KEYS = ["id", "type", "rank", "mainsnak"]
#                     "mainsnak": {
#                         "snaktype": "value",
#                         "property": "P1082",
#                         "datavalue": {
#                             "value": {
#                                 "amount": "+11150516",
#                                 "unit": "1"
#                             },
#                             "type": "quantity"
#                         },
#                         "datatype": "quantity"
#                     },
#                     "type": "statement",
#                     "qualifiers": {
#                         ...

#     ]
# }
#     """

#     claims_groups = {}
#     for claim_property in obj["claims"]:
#         # _REQUIRED_KEYS = ["id", "type", "rank", "mainsnak"]
#         #qwikidata.
#         claim_group = qwikidata.claim.WikidataClaimGroup(obj["claims"][claim_property])
#         claims_groups[claim_property] = claim_group

#     # FOR NOW: ignore claim references and sitelinks

#     print(qid, ":", main_label, ", ".join(alt_labels), ":", description)



# def load_file(filename):
#     with open(filename, encoding='utf-8') as fp:
#         objs = json.load(fp)

#     for obj in objs:
#         load_obj(obj)

def create_client_stub():
    return pydgraph.DgraphClientStub('localhost:18080')


# Create a client.
def create_client(client_stub):
    return pydgraph.DgraphClient(client_stub)


# Drop All - discard all data and start from a clean slate.
def drop_all(client):
    return client.alter(pydgraph.Operation(drop_all=True))


selected_properties = {
    "P279", # subclass of
    "P31",  # instance of
    "P361", # part of
    "P527", # has part
    "P749", # parent organization
    "P4330", # contains
    "P150", # contains administrative territorial entity
    "P131", # located in the administrative territorial entity
    "P276" # (location)
"""
contains administrative territorial entity (P150)
located in the administrative territorial entity (P131)
Use P276 (location) for specifying locations that are non-administrative places and for items about events
NOTE: P31, P279 need reverse index (find instances of and subclass of given vertex)
SAME APPLIES FOR THE OTHER EDGE TYPES
"""
}

def read_properties():
    chosen_properties = set()
    input_filename = "wd_properties_list.csv"
    with open(input_filename, encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        in_data = False
        for record in reader:
            if in_data and int(record[10]) >= 0:
                chosen_properties.add(record[0])
            if record[0].lower() == "code":
                in_data = True
    return chosen_properties

selected_properties = read_properties()
print("# chosen properties: ", len(selected_properties))

wd_properties = []

def load_properties():
    global wd_properties

    with open("wd_properties.json", encoding='utf-8') as fp:
        wd_properties = json.load(fp)

# NOTE: P31, P279 need reverse index
dgraph_query_find_instance_of_airport = """
{
  WD(
    func: eq(QID, "Q1248784")
  )
  {
    name
    label
    aliases
    description
    ~P31 {
      QID
      name
      label
      aliases
      description
    }
    P279 {
                        QID
      name
      label
      aliases
      description
    }
  }
}
"""

# # query: find an instance of any subclass of organization (Q43229)

# # Set schema.
# def set_schema(client):
#     schema = """
#     <QID>: string @index(exact) @upsert .
#     <name>: string .
#     <label>: string @index(term, fulltext) .
#     <aliases>: [string] .
#     <description>: string @index(term, fulltext).
#     <P279>: [uid] @reverse .
#     <P31>: [uid] @reverse .
#     """
#     for selected_property in selected_properties:
#         schema += "<{0}>: [uid] .\n".format(selected_property)

#     print(schema)

#     return client.alter(pydgraph.Operation(schema=schema))

#def upsert(client, name, state):
#    q = """query q($name: string)
#    {
#        NODE as q(func: eq(name, $name)) {
#            expand(_all_)
#        }
#    }"""
#
#    txn = client.txn()
#    state['uid'] = 'uid(NODE)'
#    m = txn.create_mutation(set_obj=state, cond='@if(eq(len(NODE), 1))')
#    request = txn.create_request(query=q,
#                                 mutations=(m,),
#                                 variables={'$name': name},
#                                 commit_now=True)
#
#    try:
#        result = txn.do_request(request)
#    finally:
#        txn.discard()
    
def load_item_dgraph(output_dict, all_items, set_items):

    query = """
    {qid} as var(func: eq(QID, "{qid}"))""".format(qid=output_dict["QID"])

    nquad = """
    uid({qid}) <dgraph.type> "awr.kb_item" .
    uid({qid}) <QID> "{qid}" .
    uid({qid}) <name> "{qid}" . """.format(
        qid=output_dict["QID"],
        )

    if "label" in output_dict:
        nquad += """
    uid({qid}) <label> {label} . """.format(
            qid=output_dict["QID"],
            label=output_dict["label"]
            )

    if "description" in output_dict:
        nquad += """
    uid({qid}) <description> {description} . """.format(
            qid=output_dict["QID"],
            description=output_dict["description"]
            )

    if "aliases" in output_dict:
        for alias in output_dict["aliases"]:
            nquad += """
    uid({qid}) <aliases> {alias} . """.format(
                qid=output_dict["QID"],
                alias=alias,
                )

    nquad += "\n"

    all_items.add(output_dict["QID"])
    set_items.add(output_dict["QID"])

    for claim_property_id in selected_properties:
        if claim_property_id in output_dict:
            for edge in output_dict[claim_property_id]:
                edge_qid = edge["QID"]
                nquad += """
        uid({qid}) <{claim_property}> uid({edge_qid}) . """.format(
                        qid=output_dict["QID"],
                        claim_property=claim_property_id,
                        edge_qid=edge_qid
                    )
                all_items.add(edge_qid)

    return query, nquad


def tie_loose_items(items):
    query = ""
    nquad = ""
    for qid in items:
        query += """
    {qid} as var(func: eq(QID, "{qid}")) """.format(qid=qid)
        nquad += """
    uid({qid}) <QID> "{qid}" .
    uid({qid}) <name> "{qid}" . """.format(qid=qid)
    return query, nquad


def load_claim_group(claim_group):
    edges = []
    linked_items = []

    for i in range(len(claim_group)):
        claim_item = claim_group[i]
        '''
datatype can be:
    "globecoordinate",
    "monolingualtext",
    "quantity",
    "string",
    "time",
    "wikibase-entityid",
    "external-id",
    `None`
        '''
        if claim_item.mainsnak.value_datatype == "wikibase-entityid": # linking property
            qid = claim_item.mainsnak.datavalue.value["id"]
            #blank_uid = "_:" + qid
            #print(claim_item.property_id, qid)
            edges.append({
                #"uid": blank_uid,
                "QID": qid
            })
            linked_items.append({
                #"uid": blank_uid,
                #"name": qid,
                "QID": qid
            })
        else: # non-linking property
            pass

    return edges, linked_items

item_num = 0

def rdf_encode(s):
    l = rdflib.Literal(s)
    return l.n3()

def load_item(item_dict, all_items, set_items):
    global item_num, wd_properties
    ###TESTTESTTEST###item_num += 1
    #return "", "" # TEST

    item = qwikidata.entity.WikidataItem(item_dict)
    qid = item.entity_id
    label = item.get_label()
    description = item.get_description()
    aliases = item.get_aliases()
    #print(qid, ":", label, ",", ", ".join(aliases), ":", description)
    output_dict = {
        "uid": "_:" + qid,
        "QID": qid,
        "name": qid
    }
    if label is not None and len(label) > 0:
        output_dict["label"] = rdf_encode(label)

    if aliases is not None and len(aliases) > 0:
        output_dict["aliases"] = [rdf_encode(alias) for alias in aliases]

    if description is not None and len(description) > 0:
        output_dict["description"] = rdf_encode(description)

    # DUMP ALL CLAIMS
    #s = ""
    #claim_groups = item.get_claim_groups()
    #for claim_property in claim_groups:
    #    claim_group = claim_groups[claim_property]
    #    load_claim_group(claim_group)
    #    s = s + claim_property + ","
    #print(s)
    # ALTERNATIVE: a set of preselected properties

    for property_id in selected_properties:
        #claim_property in wd_properties:
        claim_group = item.get_claim_group(property_id)
        edges, linked_items = load_claim_group(claim_group)
        if len(edges) > 0:
            output_dict[property_id] = edges
            #claim_property["_items_count"] = claim_property["_items_count"] + 1 if "_items_count" in claim_property else 1

    query, nquad = load_item_dgraph(output_dict, all_items, set_items)

    return query, nquad

property_num = 0

fp_properties = open("wd_properties_out.json", 'w', encoding='utf-8')
def load_property(item_dict, arg2, arg3):
    global property_num
    json.dump(item_dict, fp_properties, indent=2, ensure_ascii=False)
    property_num += 1
    return "", ""

lexeme_num = 0

def load_lexeme(item_dict, arg2, arg3):
    global lexeme_num
    lexeme_num += 1
    return "", ""

type_to_load = {
    "item": load_item,
    "property": load_property,
    "lexeme": load_lexeme
}

###### IMPORTANT: NEED UPSERT BLOCK
###### https://dgraph.io/docs/mutations/upsert-block/

"""
If the variable stores one or more than one UIDs, the uid function returns all the UIDs stored in the variable.
In this case, the operation is performed on all the UIDs returned, one at a time.

so, we need a query that returns all the QIDs involved in an operation?


val Function
The val function allows extracting values from value variables.
Value variables store a mapping from UIDs to their corresponding values.
Hence, val(v) is replaced by the value stored in the mapping for the UID (Subject) in the N-Quad.
If the variable v has no value for a given UID, the mutation is silently ignored.
The val function can be used with the result of aggregate variables as well,
in which case, all the UIDs in the mutation would be updated with the aggregate value.


{
  WD(
    func: eq(QID, ["Q2","Q949819","Q899"])
  )
  {
    name
    label
    P31 {
      QID
    }
  }
}


"""

#filename = "wd10000.json"
filename = "latest-all.json.bz2"
#filename = r"C:\dev\core-dev\WikiData\wd100.json"
max_item = 2000000000
min_item = 0

if __name__ == "__main__":
    load_properties()
    items = qwikidata.json_dump.WikidataJsonDump(filename)
    sep = ""
    compound_query = ""
    compound_nquad = ""
    all_items = set()
    set_items = set()
    nquad_limit = 10 * 1024
    out_prog = 0
    out_prefix = ""

    if len(sys.argv) == 4:
        min_item = int(sys.argv[1])
        max_item = int(sys.argv[2])
        out_prefix = sys.argv[3]
        print("from", min_item, "to", max_item, "prefix", out_prefix)

    time_start = datetime.datetime.now()
    for item in items:
        if item["type"] == "item":
            item_num += 1
            #if item_num < 91000000:
            #    item_num += 1
            #    continue
            if item_num % 100000 == 0:
                time_stop = datetime.datetime.now()
                time_delta = time_stop - time_start
                time_delta_secs = time_delta.seconds + 1e-6 * time_delta.microseconds
                print("items: {0}, elapsed time(s): {1}".format(item_num, str(time_delta_secs)))

        if item_num < min_item:
            continue

        if item_num > max_item:
            item_num -= 1 # we don't process this one
            break

        f = type_to_load[item["type"]]
        query, nquad = f(item, all_items, set_items)
        compound_query += query
        compound_nquad += nquad
        sep = ","
        if len(compound_nquad) > nquad_limit:
            dangling_items = all_items - set_items
            query, nquad = tie_loose_items(dangling_items)
            compound_query += query
            compound_nquad += nquad
            output_filename = filename.replace(".bz2", "").replace(".json", "." + str(out_prog).zfill(3) + ".dql")
            output_filename_nquad = filename.replace(".bz2", "").replace(".json", "." + out_prefix + str(out_prog).zfill(3) + ".rdf")
            #fp_out = open(output_filename, 'w', encoding='utf-8')
            fp_out_nquad = open(os.path.join("input_data", output_filename_nquad), 'w', encoding='utf-8')
            upsert = """
upsert {
    query {
""" + compound_query + """

    }
    mutation {
        set {
""" + compound_nquad + """
        }
    }
}
"""
            #fp_out.write(upsert)
            #fp_out.close()
            rdf_nquad = re.compile('uid\(([a-zA-Z0-9]+)\)').sub('_:\\1', compound_nquad)
            fp_out_nquad.write(rdf_nquad)
            fp_out_nquad.close()
            out_prog += 1
            sep = ""

            again = False #True #TESTTESTTEST
            while again:
                try:
                    response = requests.post("http://localhost:18080/mutate?commitNow=true",
                            data=upsert.encode('utf-8'), headers={
                                "Content-Type": "application/rdf"
                            })

                    again = False
                    if response.status_code != 200:
                        print(response.text)

                except:
                    print("request failed, waiting 1 minute and retrying")
                    time.sleep(60)

            all_items = set()
            set_items = set()
            compound_query = ""
            compound_nquad = ""

    time_stop = datetime.datetime.now()
    time_delta = time_stop - time_start
    time_delta_secs = time_delta.seconds + 1e-6 * time_delta.microseconds
    print("items: {0}, properties: {1}, lexemes: {2}, elapsed time(s): {3}".format(item_num, property_num, lexeme_num, str(time_delta_secs)))
    fp_properties2 = open("wd_properties_2.json", 'w', encoding='utf-8')
    json.dump(wd_properties, fp_properties2, ensure_ascii=False, indent=2)
    fp_properties2.close()
