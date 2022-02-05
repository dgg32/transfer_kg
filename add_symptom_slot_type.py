import json
import sys
import pandas as pd

symptom_name = set()

hetionet_disease = sys.argv[1]
slot_type_file = sys.argv[2]
output = sys.argv[3]



with open(hetionet_disease, 'r') as f:
    nodes = json.load(f)

    new_nodes = []
    for node in nodes:
        if node["kind"] == "Symptom":
            symptom_name.add(node["name"])

"""
{
      "synonyms": null,
      "sampleValue": {
        "value": "Talaromycosis"
      }
    }
"""

with open(slot_type_file, 'r') as f:
    data = json.load(f)

    new_data = {}
    for k in data:
        if k == "slotTypeValues":
            slotTypeValues = []
            for d in symptom_name:
                temp = {"synonyms": None, "sampleValue": {"value": d}}
                slotTypeValues.append(temp)
            new_data[k] = slotTypeValues
        else:
            new_data[k] = data[k]

with open(output, 'w') as f:
    json.dump(new_data, f)
