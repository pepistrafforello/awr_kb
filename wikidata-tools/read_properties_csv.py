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

import sys
sys.dont_write_bytecode = True

import csv

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

chosen_properties = read_properties()
print("chosen: ", len(chosen_properties))
