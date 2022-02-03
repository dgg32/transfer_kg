import sys, re, os, json

rx_name = re.compile(r'NAME\s+(.+)')
rx_entry = re.compile(r'ENTRY\s+(\w+)')
rx_description = re.compile(r'DESCRIPTION\s+(.+)')
rx_category = re.compile(r'CATEGORY\s+(.+)')
rx_pathogen = re.compile(r'PATHOGEN\s+(.+)')
rx_drug = re.compile(r'DRUG\s+(.+)')
rx_gene = re.compile(r'GENE\s+(.+)')
rx_pathway = re.compile(r'^PATHWAY\s+hsa(\d+)')

rx_db = re.compile(r'DBLINKS\s+(.+)')

# DBLINKS     ICD-11: 2A83.1
#             ICD-10: C90.0
#             MeSH: D009101

rx_db_detail = re.compile(r'(\S+):\s+(.+)')

rx_pathogen_detail = re.compile(r'(.+)\[GN:(\w+)\]')
rx_drug_detail = re.compile(r'(.+)\[DR:(\w+)\]')

#CCND1-IgH (translocation) [HSA:595] [KO:K04503]
rx_gene_detail = re.compile(r'(?:\(.+\)\s+)*(\S+)\s+.+?\[KO:(\w+)\]')

rx_gene_detail_with_action = re.compile(r'(?:\(.+\)\s+)*(\S+)\s+\((.+)\).+?\[KO:(\w+)\]')

top_folder = sys.argv[1]


disease = {}

drug = {}

pathogen = {}

gene = {}

disease_id = {}

drug_disease_connections = set()

pathogen_disease_connections = set()

gene_disease_connections = set()

with open("disease.csv", "a") as output:
    output.write(",".join(["ko", "name", "description", "disease_category", "icd10"]) + "\n")

with open("drug.csv", "a") as output:
    output.write(",".join(["ko", "name",]) + "\n")

with open("pathogen_tmp.csv", "a") as output:
    output.write(",".join(["ko", "name"]) + "\n")

with open("gene_tmp.csv", "a") as output:
    output.write(",".join(["ko", "name"]) + "\n")

with open("drug_disease.csv", "a") as output:
    output.write(",".join(["from", "to"]) + "\n")

with open("pathogen_disease.csv", "a") as output:
    output.write(",".join(["from", "to"]) + "\n")

with open("gene_disease.csv", "a") as output:
    output.write(",".join(["from", "to", "action"]) + "\n")


def get_pathogen(pathogen_item, disease_entry):
    global pathogen, pathogen_disease_connections
    search_pathogen_detail = rx_pathogen_detail.search(pathogen_item)

    if search_pathogen_detail:
        pathogen_name = search_pathogen_detail.group(1).strip()
        pathogen_ko = search_pathogen_detail.group(2).strip()

        if pathogen_ko not in pathogen:
            pathogen[pathogen_ko] = ",".join([f'"{pathogen_ko}"', f'"{pathogen_name}"'])

        pathogen_disease_connections.add(",".join([f'"{pathogen_name}"', f'"{disease_entry}"']))

def get_drug(drug_item, disease_entry):
    global drug, drug_disease_connections
    search_drug_detail = rx_drug_detail.search(drug_item)

    if search_drug_detail:
        drug_name = search_drug_detail.group(1).strip()

        drug_ko = search_drug_detail.group(2)

        if drug_ko not in drug:
            drug[drug_ko] = ",".join([f'"{drug_ko}"', f'"{drug_name}"'])

        #with open("kegg.csv", "a") as output:
        #    output.write(",".join([f'"{drug_ko}"', f'"{drug_name}"', '""', '"drug"', '""']) + "\n")
        #drug.append([drug_name, drug_ko])

        drug_disease_connections.add(",".join([f'"{drug_name}"', f'"{disease_entry}"']))

def get_gene(gene_item, disease_entry):
    global gene, gene_disease_connections

    #print (gene_item)
    
    if "(" in gene_item and ")" in gene_item and not gene_item.startswith("("):

        search_gene_detail = rx_gene_detail_with_action.search(gene_item)

        if search_gene_detail:
            gene_name = search_gene_detail.group(1).strip()

            if gene_name.endswith(";"):
                gene_name = gene_name[:-1]

            gene_action = search_gene_detail.group(2).strip()

            gene_ko = search_gene_detail.group(3)

            #print (gene_name, gene_action, gene_ko)

            if gene_ko not in gene:
                #gene[gene_ko] = gene_name
                gene[gene_ko] = ",".join([f'"{gene_ko}"', f'"{gene_name}"'])

            gene_disease_connections.add(",".join([f'"{gene_name}"', f'"{disease_entry}"', f'"{gene_action}"']))
    
    else:
        search_gene_detail = rx_gene_detail.search(gene_item)

        if search_gene_detail:
            gene_name = search_gene_detail.group(1).strip()

            if gene_name.endswith(";"):
                gene_name = gene_name[:-1]

            gene_ko = search_gene_detail.group(2)

            #print (gene_name, gene_ko)

            if gene_ko not in gene:
                #gene[gene_ko] = gene_name
                gene[gene_ko] = ",".join([f'"{gene_ko}"', f'"{gene_name}"'])

            gene_disease_connections.add(",".join([f'"{gene_name}"', f'"{disease_entry}"', "unknown"]))
    #print ()

def get_dblink(link_item, disease_entry):
    global disease_id

    search_db_detail = rx_db_detail.search(link_item)

    if search_db_detail:
        db_name = search_db_detail.group(1).strip()
        db_ids = search_db_detail.group(2).strip().split(" ")

        if disease_entry not in disease_id:
            disease_id[disease_entry] = {}
        disease_id[disease_entry][db_name] = db_ids

def get_pathway(pathway_item, disease_entry):
    global disease_id


    if disease_entry not in disease_id:
        disease_id[disease_entry] = {}
    disease_id[disease_entry]["kegg"] = [pathway_item]

for (head, dirs, files) in os.walk(top_folder):
    
    for file in files:
        
        current_file_path = os.path.abspath(os.path.dirname(os.path.join(head, file)))
        with_name = os.path.join(current_file_path, file)

        disease_entry = ""
        disease_name = ""
        disease_description = ""
        disease_category = ""

        is_pathogen = False
        is_drug = False
        is_gene = False
        is_dblink = False
        

        for line in open(with_name, 'r'):
            search_entry = rx_entry.search(line)
            search_name = rx_name.search(line)
            search_description = rx_description.search(line)
            search_category = rx_category.search(line)
            search_pathogen = rx_pathogen.search(line)
            search_drug = rx_drug.search(line)
            search_pathway = rx_pathway.search(line)

            search_db = rx_db.search(line)
            search_gene = rx_gene.search(line)
            
            if not line.startswith(" "):
                is_pathogen = False
                is_drug = False
                is_gene = False
                is_dblink = False

            if search_entry:
                disease_entry = search_entry.group(1)
            
            elif search_name:
                disease_name = search_name.group(1)

                if disease_name.endswith(";"):
                    disease_name = disease_name[:-1]
            
            elif search_description:
                disease_description = search_description.group(1).replace('"', "'")
            
            elif search_category:
                disease_category = search_category.group(1)

            elif search_pathogen:
                pathogen_item = search_pathogen.group(1)

                get_pathogen(pathogen_item, disease_name)

                is_pathogen = True
            
            elif is_pathogen == True and line.startswith(" "):
                pathogen_item = line.strip()

                get_pathogen(pathogen_item, disease_name)


            elif search_drug:
                drug_item = search_drug.group(1)

                get_drug(drug_item, disease_name)

                is_drug = True
            
            elif is_drug == True and line.startswith(" "):
                drug_item = line.strip()

                get_drug(drug_item, disease_name)
            
            if search_gene:
                
                gene_item = search_gene.group(1)

                get_gene(gene_item, disease_name)

                is_gene = True

            elif  is_gene == True and line.startswith(" "):
                gene_item = line.strip()

                get_gene(gene_item, disease_name)

            if search_db:
                db_link_item = search_db.group(1)

                get_dblink(db_link_item, disease_name)

                is_dblink = True
            
            elif is_dblink == True and line.startswith(" "):
                db_link_item = line.strip()

                get_dblink(db_link_item, disease_name)

            if search_pathway:
                pathway_item = search_pathway.group(1)

                get_pathway(pathway_item, disease_name)




        if disease_entry:
            if disease_entry not in disease:

                icd10 = ""
                
                
                if disease_name in disease_id and "ICD-10" in disease_id[disease_name]:
                    #print (disease_id[disease_name])
                    icd10 = disease_id[disease_name]["ICD-10"]
                    #print (icd10)
                disease[disease_entry] = ",".join([f'"{disease_entry}"', f'"{disease_name}"', f'"{disease_description}"', f'"{disease_category}"', f'"{str(icd10)}"'])
            #with open("kegg.csv", "a") as output:
                #output.write(",".join([f'"{disease_entry}"', f'"{disease_name}"', f'"{disease_description}"', '"disease"', f'"{disease_category}"']) + "\n")


for node in disease:
    with open("disease.csv", "a") as output:
        output.write(disease[node] + "\n")

for node in drug:
    with open("drug.csv", "a") as output:
        output.write(drug[node] + "\n")

for node in pathogen:
    with open("pathogen_tmp.csv", "a") as output:
        output.write(pathogen[node] + "\n")

for node in gene:
    with open("gene_tmp.csv", "a") as output:
        output.write(gene[node] + "\n")

for c in pathogen_disease_connections:
    with open("pathogen_disease.csv", "a") as output:
        output.write(c + "\n")

for c in drug_disease_connections:
    with open("drug_disease.csv", "a") as output:
        output.write(c + "\n")

for c in gene_disease_connections:
    with open("gene_disease.csv", "a") as output:
        output.write(c + "\n")


with open("disease_kegg_id.json", "w") as f:
    json.dump(disease_id, f, indent=2)