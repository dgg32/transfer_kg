

# Introduction

  

This repository contains code and data for my article "[Transfer Knowledge Graphs to Doctor.ai](https://medium.com/p/cc21765fa8a6)".

1. Both template.yaml files are for AWS SAM deployment.


2. Neo4j command is for data import.

  


# Prerequisite

Python with Neo4j module

AWS CLI and SAM

Chrome

# Data preparation

The kg.ipynb Jupyter notebook prepares the Hetionet and STRING data, while download_various_kegg.py and parse_disease.py prepares the KEGG data.

First, download the kegg disease database:

```console
python download_various_kegg.py ds [kegg_download_folder]

python parse_disease.py [kegg_download_folder]
```

Second, download the STRING database and hetionet-v1.0 (addresses in data/download_address.txt)

Then run all the cells in kg.ipynb.

Finally, run the four import scripts to import the data into Neo4j.
```console
python import_supplement_node.py /Users/dgg32/Documents/transfer_kg/data/to_s3/disease.csv [ip] [password] Disease
python import_supplement_node.py /Users/dgg32/Documents/transfer_kg/data/to_s3/pathogen_tmp.csv [ip] [password] Pathogen
python import_supplement_node.py /Users/dgg32/Documents/transfer_kg/data/to_s3/drug.csv [ip] [password] Compound
python import_supplement_node.py /Users/dgg32/Documents/transfer_kg/data/to_s3/gene_tmp.csv [ip] [password] Gene
python import_supplement_node.py /Users/dgg32/Documents/transfer_kg/data/to_s3/string_to_add_nodes.csv [ip] [password] Gene

python import_supplement_edge.py /Users/dgg32/Documents/transfer_kg/data/to_s3/drug_disease.csv [ip] [password] Compound Disease treats
python import_supplement_edge.py /Users/dgg32/Documents/transfer_kg/data/to_s3/pathogen_disease.csv [ip] [password] Pathogen Disease causes
python import_supplement_edge.py /Users/dgg32/Documents/transfer_kg/data/to_s3/gene_disease.csv [ip] [password] Gene Disease associates
python import_edges.py /Users/dgg32/Documents/transfer_kg/data/to_s3/string_to_add_edges.json [ip] [password]
```

# The definition of Lex

Currently, the deployment of Lex is a bit awkward. The source code in this repository needs to be uploaded to an S3. The bucket and file name are defined in Line 359 and 360 in the template.yaml file for CloudFormation before the sam build command. Otherwise, you will only deploy the same Lex from my s3://datathon-medium-file/doctorai-LexJson-hetionet.zip.

# For construction

## build the bundle
```console
sam build
```

## deployment in AWS
```console
sam deploy --guided --capabilities CAPABILITY_NAMED_IAM
```
## for destruction
```console
sam delete --stack-name sam-app
```


# Authors

*  **Sixing Huang** - *Concept and Coding*

  

## License

  

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
