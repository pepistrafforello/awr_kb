import sys
sys.dont_write_bytecode = True

import json
import requests
import time

wd_properties = {}

def get_properties(search_param):
    global wd_properties

    again = True
    offset = 0
    batch_size = 50
    while again:
        print(".", end="")
        url = "https://www.wikidata.org/w/api.php?action=wbsearchentities&language=en&search={}&type=property&limit={}&continue={}&format=json".format(search_param, batch_size, offset)
        done = False
        while not done:
            try: 
                res = requests.get(url)
                res.raise_for_status()
                done = True
            except:
                print("X", end="")
                time.sleep(5)

        res_obj = json.loads(res.text)
        res_properties = res_obj['search']
        if len(res_properties) > 0:
            offset += len(res_properties)
            for prop in res_properties:
                prop_id = prop['id']
                if not prop_id in wd_properties:
                    del prop['match']
                    wd_properties[prop_id] = prop
        else:
            again = False
    
    print("after \"{}\": {} properties retrieved.".format(search_param, len(wd_properties)))
    return list(wd_properties.values())

def write_properties(wd_properties):
    with open("wd_properties.json", 'w', encoding='utf-8') as fp:
        json.dump(wd_properties, fp, indent=2, ensure_ascii=False)
        fp.close()

def char_range(c1, c2):
    """Generates the characters from `c1` to `c2`, inclusive."""
    for c in range(ord(c1), ord(c2)+1):
        yield chr(c)

def search_loop():
    for src_param in list(char_range('a', 'z')) + list(char_range('0', '9')):
        write_properties(get_properties(src_param))

if __name__ == "__main__":
    search_loop()
