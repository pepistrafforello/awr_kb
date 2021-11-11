import sys
sys.dont_write_bytecode = True
import os
import glob
import re
import json

default_properties = {
    "dgraph.type",
    "QID",
    "name",
    "label",
    "description",
    "aliases"
}


wd_properties = []
wd_properties_dict = {}

def load_properties():
    global wd_properties

    with open("wd_properties.json", encoding='utf-8') as fp:
        wd_properties = json.load(fp)

load_properties()
for property in wd_properties:
    wd_properties_dict[property['id']] = property["label"]

counters = {}

input_folder = "."

filenames = glob.glob(os.path.join(input_folder, '*.rdf'))

p = re.compile('\s+\S+\s+<(\S+)>\s+')

for filename in filenames:
    #print(filename)
    with open(filename, encoding='utf-8') as fp:
        for line in fp:
            m = p.match(line)
            if m is not None:
                pred = m.groups()[0]
                if pred not in default_properties:
                    counters[pred] = (counters[pred] + 1) if pred in counters else 1
                    #print(pred)

results = [(k, counters[k]) for k in sorted(counters, key=counters.get, reverse=True)]
for result in results:
    print(result[0], result[1], wd_properties_dict[result[0]], sep='|')

