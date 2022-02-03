import json
import sys
import pandas as pd

disease_name = set()

kegg_disease = sys.argv[1]
hetionet_disease = sys.argv[2]
slot_type_file = sys.argv[3]
output = sys.argv[4]


df = pd.read_csv(kegg_disease)

disease_name = set(df["name"].tolist())

with open(hetionet_disease, 'r') as f:
    nodes = json.load(f)

    new_nodes = []
    for node in nodes:
        if node["kind"] == "Disease":
            disease_name.add(node["name"])

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
            for d in disease_name:
                temp = {"synonyms": None, "sampleValue": {"value": d}}
                slotTypeValues.append(temp)
            new_data[k] = slotTypeValues
        else:
            new_data[k] = data[k]

with open(output, 'w') as f:
    json.dump(new_data, f)
