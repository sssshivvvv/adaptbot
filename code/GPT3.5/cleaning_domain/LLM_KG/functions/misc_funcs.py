import rdflib
import networkx as nx
import matplotlib.pyplot as plt
import os
import openai
from openai import AzureOpenAI
import re
import subprocess
import contextlib
import io
import shutil
import random
import sys
import numpy as np
import json
import nltk
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer
import tiktoken



os.environ["AZURE_OPENAI_API_KEY"] = "ENTER-KEY"
os.environ["AZURE_OPENAI_ENDPOINT"] = "ENTER-ENDPOINT"

def token_counter(messages):
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

    total_tokens = 0
    for message in messages:
        tokens = encoding.encode(f"{message['role']}: {message['content']}")
        total_tokens += len(tokens)

    total_tokens += 2 * len(messages)

    return total_tokens

def plot_graph(onto_file):
    # Load the RDF graph
    g = rdflib.Graph()
    g.parse(onto_file, format="turtle")

    # Create a NetworkX graph
    nx_graph = nx.Graph()

    # Function to get the local name of a URI
    def get_local_name(uri):
        if isinstance(uri, rdflib.URIRef):
            return uri.split('/')[-1] if '/' in uri else uri
        return uri

    # Define the namespaces
    EX = rdflib.Namespace("http://example.org/")

    # Predicates to be excluded
    exclude_predicates = {
        EX.room_name,
        EX.rec_name,
        EX.obj_name,
        EX.tool_name
    }

    # Add only the instances to the NetworkX graph, excluding specific predicates
    for s, p, o in g:
        if p not in exclude_predicates:
            if isinstance(o, (str, bool, rdflib.URIRef, rdflib.Literal)):
                if (s.startswith(EX) and p.startswith(EX) and o.startswith(EX)) or \
                   (s.startswith(EX) and p.startswith(EX) and isinstance(o, rdflib.Literal)):
                    s_label = get_local_name(s)
                    p_label = get_local_name(p)
                    o_label = get_local_name(o)
                    nx_graph.add_edge(s_label, o_label, label=p_label)

    # Draw the graph
    plt.figure(figsize=(30, 20))
    pos = nx.spring_layout(nx_graph)
    nx.draw(nx_graph, pos, with_labels=True, node_size=5000, node_color="skyblue", font_size=10, font_weight="bold")
    labels = nx.get_edge_attributes(nx_graph, 'label')
    nx.draw_networkx_edge_labels(nx_graph, pos, edge_labels=labels)
    plt.show()



def plot_graph_circular(onto_file):
    # Load the RDF graph
    g = rdflib.Graph()
    g.parse(onto_file, format="turtle")

    # Create a NetworkX graph
    nx_graph = nx.Graph()

    # Function to get the local name of a URI
    def get_local_name(uri):
        if isinstance(uri, rdflib.URIRef):
            return uri.split('/')[-1] if '/' in uri else uri
        return uri

    # Define the namespaces
    EX = rdflib.Namespace("http://example.org/")

    # Predicates to be excluded
    exclude_predicates = {
        EX.room_name,
        EX.rec_name,
        EX.obj_name,
        EX.tool_name
    }

    # Add only the instances to the NetworkX graph, excluding specific predicates
    for s, p, o in g:
        if p not in exclude_predicates:
            if isinstance(o, (str, bool, rdflib.URIRef, rdflib.Literal)):
                if (s.startswith(EX) and p.startswith(EX) and o.startswith(EX)) or \
                   (s.startswith(EX) and p.startswith(EX) and isinstance(o, rdflib.Literal)):
                    s_label = get_local_name(s)
                    p_label = get_local_name(p)
                    o_label = get_local_name(o)
                    nx_graph.add_edge(s_label, o_label, label=p_label)

    # Draw the graph
    plt.figure(figsize=(30, 20))
    
    # Use circular layout
    pos = nx.circular_layout(nx_graph)
    
    # Draw nodes with custom attributes
    nx.draw_networkx_nodes(nx_graph, pos, node_size=7000, node_color="lightblue", alpha=0.9)
    
    # Draw edges with custom attributes
    nx.draw_networkx_edges(nx_graph, pos, width=2, edge_color="gray", alpha=0.5)
    
    # Draw labels with custom attributes
    nx.draw_networkx_labels(nx_graph, pos, font_size=12, font_weight="bold")
    
    # Draw edge labels
    labels = nx.get_edge_attributes(nx_graph, 'label')
    nx.draw_networkx_edge_labels(nx_graph, pos, edge_labels=labels, font_size=10)
    
    plt.title("RDF Graph Visualization - Circular Layout", fontsize=20)
    plt.show()


def fetch_details(onto_file):

    g = rdflib.Graph()
    g.parse(onto_file, format="turtle")

    tool_query = """
        PREFIX ex: <http://example.org/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?tool_name
        WHERE {
            ?tool rdf:type ex:tool.
            ?tool ex:tool_name ?tool_name.
        }
        """
    tls = g.query(tool_query)
    tool_list = []
    for o in tls:
        tool_list.append(str(o.tool_name))

    obj_query = """
        PREFIX ex: <http://example.org/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?obj_name
        WHERE {
            ?object rdf:type ex:object.
            ?object ex:obj_name ?obj_name.
        }
        """
    objs = g.query(obj_query)
    obj_list = []
    for o in objs:
        obj_list.append(str(o.obj_name))


    rec_query = """
        PREFIX ex: <http://example.org/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?rec_name
        WHERE {
            ?rec rdf:type ex:mreceptacle.
            ?rec ex:rec_name ?rec_name.
        }
        """
    recs = g.query(rec_query)
    rec_list = []
    for r in recs:
        rec_list.append(str(r.rec_name))


    imrec_query = """
        PREFIX ex: <http://example.org/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?rec_name
        WHERE {
            ?rec rdf:type ex:imreceptacle.
            ?rec ex:rec_name ?rec_name.
        }
        """
    imrecs = g.query(imrec_query)
    imrec_list = []
    for r in imrecs:
        imrec_list.append(str(r.rec_name))

    return obj_list, rec_list, tool_list, imrec_list


def remove_spacing(LLM_output):

    with open(LLM_output, "r") as file:
        lines = file.readlines()

    updated_lines = []
    for line in lines:
        start = line.find("(")
        end = line.find(")")

        if start != -1 and end != -1:
            arguments = line[start+1:end].split(",")
            updated_arguments = []

            for arg in arguments:
                updated_arg = arg.strip().replace(" ", "_")
                updated_arguments.append(updated_arg)

            updated_line = line[:start+1] + ", ".join(updated_arguments) + line[end:]
            updated_lines.append(updated_line)
        else:
            updated_lines.append(line)

    with open(LLM_output, "w") as file:
        file.writelines(updated_lines)


def correct_arguments(LLM_output):

    with open(LLM_output) as file:
        stuff = file.readlines()
        stuff = [a.replace("'", '"') for a in stuff]
        stuff = [a.replace("/", '') for a in stuff]
        stuff = [a.replace("\\", '') for a in stuff]
        stuff = [s.lower() for s in stuff]
        funcs_list = [i.replace('(', ' ').replace(')', ' ').replace(',',' ').split() for i in stuff]
        funcs = [i[0] for i in funcs_list]


    for i, f in enumerate(funcs_list):
        for j in range(1, len(f)):
            if not f[1].isdigit():
                if "'" in funcs_list[i][j]:
                    funcs_list[i][j] = funcs_list[i][j][funcs_list[i][j].find("'"):funcs_list[i][j].rfind("'")+1]
                elif '"' in funcs_list[i][j]:
                    funcs_list[i][j] = funcs_list[i][j][funcs_list[i][j].find('"'):funcs_list[i][j].rfind('"')+1]
                
    for i, f in enumerate(funcs_list):
        if len(f)==2:
            stuff[i]=f'{f[0]}({f[1]})\n'
        elif len(f)==3:
            stuff[i]=f'{f[0]}({f[1]}, {f[-1]})\n'
        elif len(f)==4:
            stuff[i]=f'{f[0]}({f[1]}, {f[2]}, {f[-1]})\n'

    with open(LLM_output, "w") as file:
        file.writelines(stuff)


def update_ontology(item):
        
        def quote(word):
            if "'" in word or '"' in word:
                pass
            else:
                word= f"'{word}'"
            
            return word



    
        kind = input(f"What kind of item is {item}? Choose from: 'object', 'mreceptacle', 'imrecpetacle', 'tool'\n")
        

        if kind =='object':

            obj_name = input("Please enter the object name.\n")
            obj_name = quote(obj_name)
            location = input("What's the location of object?\n")
            IsSliceable = input("Is object sliceable? Please reply in true and false\n")
            IsBoilable = input("Is object boilable? Please reply in true and false\n")
            IsLiquid = input("Is object liquid? Please reply in true and false\n")
            Fryable = input("Is object fryable? Please reply in true and false\n")
            need_cleaning = input("Does object usually needs cleaning? Please reply in true or false\n")
            

            addition = f""" 
            
ex:{item} rdf:type ex:object;
    ex:obj_name {obj_name};
    ex:obj_location ex:{location};
    ex:IsSliceable {IsSliceable};
    ex:IsCleaned false;
    ex:sliced false;
    ex:Boilable {IsBoilable};
    ex:IsBoiled false;
    ex:IsLiquid {IsLiquid};
    ex:Fryable {Fryable};
    ex:IsFried false;
    ex:NeedsToBeCleaned {need_cleaning}.

                """
            
            with open("./LLM_KG/initial_onto.ttl", "a") as file:
                file.write(addition)
            with open("./LLM_KG/updated_onto.ttl", "a") as file:
                file.write(addition)
            
            return True

        elif kind == 'mreceptacle':

            rec_name = input("Please enter the receptacle name.\n")
            rec_name = quote(rec_name)
            toggleable = input("Is receptacle toggleable? Please reply in true or false.\n")
            mrec_location = input("What's the location of receptacle?\n")
            IsSensitive = input("Is receptacle sensitive? Please reply in true and false\n")
            deep_rec = input("Is receptacle deep? Please reply in true and false\n")
            cantakerec = input("Can we put other receptacle to this receptacle? Please reply in true and false\n")
            useforslicing = input("Can this receptacle be used for slicing? Please reply in true and false\n")

            addition = f""" 
            
ex:{item} rdf:type ex:mreceptacle;
    ex:rec_name {rec_name};
    ex:toggleable {toggleable};
    ex:switched_on false;
    ex:mrec_location ex:{mrec_location};
    ex:IsRecCleaned false;
    ex:IsSensitive {IsSensitive};
    ex:ContStirred false;
    ex:cantakerec {cantakerec};
    ex:used_for_slicing {useforslicing};
    ex:deep_rec {deep_rec}.

                """
            
            with open("./LLM_KG/initial_onto.ttl", "a") as file:
                file.write(addition)
            with open("./LLM_KG/updated_onto.ttl", "a") as file:
                file.write(addition)
            

            return True

        elif kind == 'tool':

            tool_name = input("Please enter the tool name.\n")
            tool_name = quote(tool_name)
            IsEatingTool = input("Can this tool be used for eating?Please reply in true or false.\n")
            tool_location = input("What's the location of tool?\n")
            IsSlicingTool = input("Is this tool a slicing tool? Please reply in true and false\n")
            IsToolCleaned = input("Is tool cleaned? Please reply in true and false\n")

            addition = f""" 
            
ex:{item} rdf:type ex:tool;
    ex:tool_name {tool_name};
    ex:tool_location ex:{tool_location};
    ex:IsEatingTool {IsEatingTool};
    ex:IsSlicingTool {IsSlicingTool};
    ex:IsToolCleaned {IsToolCleaned}.

                """

            with open("./LLM_KG/initial_onto.ttl", "a") as file:
                file.write(addition)
            with open("./LLM_KG/updated_onto.ttl", "a") as file:
                file.write(addition)

            return True
            

        elif kind == 'imreceptacle':

            rec_name = input("Please enter the receptacle name.\n")
            rec_name = quote(rec_name)
            toggleable = input("Is receptacle toggleable? Please reply in true or false.\n")
            imrec_location = input("What's the location of receptacle?\n")
            serving_place= input("Is this receptacle a serving place? e.g. countertop, table. Please reply in true and false\n")
            common_rec = input("Is this receptacle a common receptacle? e.g. countertop. Please reply in true and false\n")
            open_rec = input("Is this receptacle an open receptacle? e.g countertop, table. Please reply in true and false\n")
            SuitableForEdibleStorage = input("Is this receptacle suitable for keeping food? reply in true and false\n")
            cantakerec = input("Can we put other receptacles to this receptacle? Please reply in true and false\n")
            isrecbig = input("Is this receptacle big? Please reply in true and false\n")

            addition = f""" 
    
ex:{item} rdf:type ex:imreceptacle;
    ex:rec_name {rec_name};
    ex:toggleable {toggleable};
    ex:switched_on false;
    ex:imrec_location ex:{imrec_location};
    ex:serving_place {serving_place};
    ex:common_rec {common_rec};
    ex:open_rec {open_rec};
    ex:cantakerec {cantakerec};
    ex:IsRecBig {isrecbig};
    ex:IsMopped false;
    ex:SuitableForEdibleStorage {SuitableForEdibleStorage}.

                """
            with open("./LLM_KG/initial_onto.ttl", "a") as file:
                file.write(addition)
            with open("./LLM_KG/updated_onto.ttl", "a") as file:
                file.write(addition)
            
            return True

        else:
            return False




def object_correction(LLM_output):
    O, R, T, IM = fetch_details("./LLM_KG/updated_onto.ttl")
    A = O+R+T+IM
    a, f = fetch_actions()
    fl = [k.split("_")[0] for k in f]
    g = rdflib.Graph()
    g.parse("./LLM_KG/updated_onto.ttl", format='turtle')

    with open(LLM_output) as file:
        stuff = file.readlines()
        stuff = [a.replace("'", '"') for a in stuff]
        stuff = [s.lower() for s in stuff]
        funcs_list = [i.replace('(', ' ').replace(')', ' ').replace('"', ' ').replace(',',' ').split() for i in stuff]
        funcs = [i[0] for i in funcs_list]

                    
    for index, i in enumerate(funcs_list):
            
        if i and len(i)>1:

            if i[1] not in A: #object_correction
                for obj in A: 
                    if obj.split("_")[0] in i[1]:

                        if len(i)==3:
                            stuff[index]=f'{i[0]}("{obj}", "{i[-1]}")\n'
                            funcs_list[index][1] = obj

                        elif len(i)==4:
                            stuff[index]=f'{i[0]}("{obj}", "{i[2]}", "{i[-1]}")\n'
                            funcs_list[index][1] = obj
        
            if 'put' in i[0] or 'pour' in i[0]:
                if i[2] not in R+IM:
                    for r in R+IM:
                        if r in i[2]:
                            stuff[index]=f'{i[0]}("{i[1]}", "{r}")\n'
                            funcs_list[index][2] = r


    with open(LLM_output, "w") as file:
        file.writelines(stuff)


def function_correction(LLM_output):

    O, R, T, IM = fetch_details("./LLM_KG/updated_onto.ttl")
    A = O+R+T+IM
    a, f = fetch_actions()
    fl = [k.split("_")[0] for k in f]
    g = rdflib.Graph()
    g.parse("./LLM_KG/updated_onto.ttl", format='turtle')

    goto_query = """
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?rec_name
    WHERE {
        ?rec ex:goto_utensil true.
        ?rec ex:rec_name ?rec_name.
        }
    """

    rq = g.query(goto_query)
    gtplaces = []

    for p in rq:
        gtplaces.append(str(p.rec_name))


    with open(LLM_output) as file:
        stuff = file.readlines()
        stuff = [a.replace("'", '"') for a in stuff]
        stuff = [s.lower() for s in stuff]
        funcs_list = [i.replace('(', ' ').replace(')', ' ').replace('"', ' ').replace(',',' ').split() for i in stuff]
        funcs = [i[0] for i in funcs_list]


    for index, fun in enumerate(funcs_list): #keeps check on number of arguments
            
        if fun and len(fun)>1:

            if not 'slice' in fun[0] and not 'wait' in fun[0]:
                if len(fun)>=2:
                    funcs_list[index] = [fun[0], fun[1], fun[-1]]
                    stuff[index] = f'{fun[0]}("{fun[1]}", "{fun[-1]}")\n'
            
            elif 'slice' in fun[0]:
                if len(fun)>=3:
                    funcs_list[index] = [fun[0], fun[1], fun[2], fun[-1]]
                    stuff[index] = f'{fun[0]}("{fun[1]}", "{fun[2]}", "{fun[-1]}")\n'

            elif 'wait' in fun[0]:
                if len(fun)>=2:
                    funcs_list[index] = [fun[0], fun[1]]
                    stuff[index] = f'{fun[0]}({fun[1]})\n'

                number = re.findall(r'\d+', stuff[index])
                
                if number:
                        stuff[index]=f'{fun[0]}({number[0]})\n'
                        funcs_list[index] = [fun[0], number[0]]

                # for t in fun[1].split("_"):
                #     if t.isdigit():
                #         stuff[index]=f'{fun[0]}({t})\n'
                #         funcs_list[index] = [fun[0], t]


    for index, i in enumerate(funcs_list):
            
        if i and len(i)>1:

            if i[0] not in f: #function_correction  \\ correcting function name
                for j, fn in enumerate(fl): 
                    if fn in i[0]:
                        funcs_list[index][0] = f[j]
                        if len(i)==2:
                            stuff[index]= f'{f[j]}("{i[-1]}")\n'
                        elif len(i)==3:
                            stuff[index]= f'{f[j]}("{i[1]}","{i[-1]}")\n'
                        elif len(i)==4:
                            stuff[index]= f'{f[j]}("{i[1]}", "{i[2]}", "{i[-1]}")\n'


            if 'slice' in i[0]: #tool_correction

                O, R, T, IM = fetch_details("./LLM_KG/updated_onto.ttl")
                A = O + R + T + IM   

                tool_query = f"""
                PREFIX ex: <http://example.org/>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

                SELECT ?tool_name
                WHERE {{
                    ?tool ex:IsSlicingTool true.
                    ?tool ex:tool_name ?tool_name.
                }}
                """
                env_tools = []
                tquery = g.query(tool_query)
                for t in tquery:
                    env_tools.append(str(t.tool_name))

                if i[2] not in A:
                        tool = random.sample(env_tools,1)[0]
                        stuff[index]= f'slice("{i[1]}", "{tool}","{i[-1]}")\n'
                        funcs_list[index][2] = tool                       

                elif i[2] not in env_tools:
                        tool = random.sample(env_tools,1)[0]
                        stuff[index]= f'slice("{i[1]}", "{tool}", "{i[-1]}")\n'
                        funcs_list[index][2] = tool 

            if 'pour' in i[0]: #receptacle_correction

                dr_query = f"""
                PREFIX ex: <http://example.org/>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

                SELECT ?rec_name
                WHERE {{
                    ?rec rdf:type ex:mreceptacle.
                    ?rec ex:deep_rec true.
                    ?rec ex:rec_name ?rec_name.
                }}
                """
                dr = g.query(dr_query)
                drs = []
                for c in dr:
                    drs.append(str(c.rec_name))
                
                drs = [d for d in drs if d!=i[1]]

                if i[2] not in R+IM or i[2]==i[1]:
                        tool = random.sample(drs,1)[0]
                        stuff[index]= f'pour_contents("{i[1]}", "{tool}")\n'

            if 'pick' in i[0]: #function_asscociation_correction
                
                if i[1] in R or i[1] in IM:
                    stuff[index]= f'pick_up_rec("{i[1]}", "{i[2]}")\n'
                    funcs_list[index][0] = 'pick_up_rec'

                elif i[1] in T:
                    stuff[index]= f'pick_up_tool("{i[1]}", "{i[2]}")\n'
                    funcs_list[index][0] = 'pick_up_tool'

                elif i[1] in O:
                    stuff[index]= f'pick_up_obj("{i[1]}", "{i[2]}")\n'
                    funcs_list[index][0] = 'pick_up_obj'

                else:
                    stuff[index]= f'pick_up_obj("{i[1]}", "{i[2]}")\n'
                    funcs_list[index][0] = 'pick_up_obj'

            if 'put' in i[0]: #function_asscociation_correction
                
                if i[1] in R or i[1] in IM:
                    stuff[index]= f'put_down_rec("{i[1]}", "{i[2]}")\n'
                    funcs_list[index][0] = 'put_down_rec'

                elif i[1] in T:
                    stuff[index]= f'put_down_tool("{i[1]}", "{i[2]}")\n'
                    funcs_list[index][0] = 'put_down_tool'

                elif i[1] in O:
                    stuff[index]= f'put_down_obj("{i[1]}", "{i[2]}")\n'
                    funcs_list[index][0] = 'put_down_obj'
                else:
                    stuff[index]= f'put_down_obj("{i[1]}", "{i[2]}")\n'
                    funcs_list[index][0] = 'put_down_obj'

                if i[1] in O and i[-1] not in R+IM+O:
                    stuff[index]=f'{i[0]}("{i[1]}","{random.sample(gtplaces, 1)[0]}")\n'
                    funcs_list[index][-1] = random.sample(gtplaces, 1)[0]
                elif i[1] not in O and i[-1] not in R+IM+O:
                    stuff[index]=f'{i[0]}("{i[1]}","{common_recep("./LLM_KG/updated_onto.ttl")}")\n'
                    funcs_list[index][-1] = common_recep("./LLM_KG/updated_onto.ttl")


    for index, fun in enumerate(funcs_list): #output of refinement block
            
        if fun:
        
            if len(fun)==2:
                if fun[0] not in f:
                    print(f'{fun[0]}("{fun[-1]}") #action "{fun[0]}" is not present in ther knowledge base!')
                if fun[1] not in A and not fun[1].isdigit():
                    print(f'{fun[0]}("{fun[-1]}") #item "{fun[1]}" not found! Please use the ingredients provided by the user')

            elif len(fun)==3:
                if fun[0] not in f:
                    print(f'{fun[0]}("{fun[1]}", "{fun[-1]}") #action "{fun[0]}" is not present in ther knowledge base!')
                if fun[1] not in A and not fun[1].isdigit():
                    print(f'{fun[0]}("{fun[1]}", "{fun[-1]}") #item "{fun[1]}" not found! Please use the ingredients provided by the user')


            elif len(fun)==4:
                if fun[0] not in f:
                    print(f'{fun[0]}("{fun[1]}", "{fun[2]}", "{fun[0]}") #action "{fun[0]}" is not present in ther knowledge base!')
                if fun[1] not in A and not fun[1].isdigit():
                    print(f'{fun[0]}("{fun[1]}", "{fun[2]}", "{fun[1]}") #item "{fun[1]}" not found! Please use the ingredients provided by the user')
                if fun[2] not in A and not fun[2].isdigit():
                    print(f'{fun[0]}("{fun[1]}", "{fun[2]}", "{fun[2]}") #item "{fun[2]}" not found! Please use the ingredients provided by the user')

            else:
                print(f"{stuff[index].split()} #Structure of the action is invalid!")
                

            if index>0: #removing redundant pick up actions
                if fun:
                    if 'pick' in fun[0]:
                            stuff[index]=''
                            funcs_list[index] = []

    with open(LLM_output, "w") as file:
        file.writelines(stuff)



def knowledge_expansion(LLM_output):


    O, R, T, IM = fetch_details("./LLM_KG/updated_onto.ttl")
    A = O+R+T+IM
    a, f = fetch_actions()
    fl = [k.split("_")[0] for k in f]
    g = rdflib.Graph()
    g.parse("./LLM_KG/updated_onto.ttl", format='turtle')

    def get_funcs(LLM_output):
        with open(LLM_output) as file:
            stuff = file.readlines()
            stuff = [a.replace("'", '"') for a in stuff]
            stuff = [s.lower() for s in stuff]
            funcs_list = [i.replace('(', ' ').replace(')', ' ').replace('"', ' ').replace(',',' ').split() for i in stuff]
            funcs = [i[0] for i in funcs_list]
        return stuff, funcs_list

    def add_obj(fun):
        up = False
        while not up:
            up = update_ontology(fun[1])
    
    def fix_item(wrong_item, correct_item, func_list, stuff):
        for i, f in enumerate(func_list):
            if len(f)==3:
                if f[1]==wrong_item:
                    func_list[i][1] = correct_item
                    stuff[i] = f'{f[0]}("{correct_item}", "{f[-1]}")\n'
            elif len(f)==4:
                if f[1]==wrong_item:
                    func_list[i][1] = correct_item
                    stuff[i] = f'{f[0]}("{correct_item}", "{f[2]}", "{f[-1]}")\n'               

        return func_list, stuff
    
    def fix_func(wrong_func, correct_func, func_list, stuff):
        for i, f in enumerate(func_list):
            if len(f)==3:
                if f[0]==wrong_func:
                    func_list[i][0] = correct_func
                    stuff[i] = f'{correct_func}("{f[1]}", "{f[-1]}")\n'
            elif len(f)==4:
                if f[0]==wrong_func:
                    func_list[i][0] = correct_func
                    stuff[i] = f'{correct_func}("{f[1]}", "{f[2]}", "{f[-1]}")\n'               

        return func_list, stuff
    

    def remove_item(item, func_list, stuff):

        for i, f in enumerate(func_list):
            if f:
                if f[1]==item:
                    func_list[i]=[]
                    stuff[i] = ''

        return func_list, stuff
    
    def remove_function(function, func_list, stuff):

        for i, f in enumerate(func_list):
            if f:
                if f[0]==function:
                    func_list[i]=[]
                    stuff[i] = ''

        return func_list, stuff
    

    stuff, funcs_list = get_funcs(LLM_output)

    def rectify_function(stuff, funcs_list):

        O, R, T, IM = fetch_details("./LLM_KG/updated_onto.ttl")
        A = O+R+T+IM

        for index, fun in enumerate(funcs_list):
    
            if fun and len(fun)>1:   
                #function correction
                if fun[0] not in f:
                    repeat = True
                    while repeat:
                        ask = input(f'{stuff[index].strip()} #The function "{fun[0]}" does not exist in my knowledge base!Is it present in the system? Please answer in "yes" or "no". If I am mistaking it for another function, please enter "correct_function".\n')
                    
                        if ask=='no':
                            funcs_list, stuff = remove_function(fun[0], funcs_list, stuff)
                            repeat = False
                            
                        elif ask=='yes':
                            
                            if fun[1] not in O+R+T+IM and not fun[1].isdigit():
                                repeat = True
                                while repeat:
                                    ask = input(f'{stuff[index].strip()} #Item "{fun[1]}" isnt present in my knoweldge base! Is it present in the system? Please answer in "yes" or "no".If I am mistaking it for another item, please enter "correct_item".\n')
                            
                                    if ask=='no':
                                        funcs_list, stuff = remove_item(fun[1], funcs_list, stuff)
                                        repeat = False
                                    elif ask=='yes':
                                        add_obj(fun)
                                        O, R, T, IM = fetch_details("./LLM_KG/updated_onto.ttl") 
                                        repeat = False
                                    elif ask=='correct_item':
                                        corr_item = input("Please enter the correct item\n")
                                        funcs_list, stuff = fix_item(fun[1], corr_item, funcs_list, stuff)
                                        repeat = False
                                    else:
                                        repeat = True

                            repeat = False

                        elif ask=='correct_function':
                            corr_func = input("Please enter the correct function\n")
                            funcs_list, stuff = fix_func(fun[0], corr_func, funcs_list, stuff)

                            if fun[1] not in O+R+T+IM and not fun[1].isdigit():
                                repeat = True
                                while repeat:
                                    ask = input(f'{stuff[index].strip()} #Item "{fun[1]}" isnt present in my knoweldge base! Is it present in the system? Please answer in "yes" or "no".If I am mistaking it for another item, please enter "correct_item".\n')

                                    if ask=='no':
                                        funcs_list, stuff = remove_item(fun[1], funcs_list, stuff)
                                        repeat = False

                                    elif ask=='yes':
                                        add_obj(fun)
                                        O, R, T, IM = fetch_details("./LLM_KG/updated_onto.ttl") 
                                        repeat = False
                                        
                                    elif ask=='correct_item':
                                        corr_item = input("Please enter the correct item")
                                        funcs_list, stuff = fix_item(fun[1], corr_item, funcs_list, stuff)
                                        repeat = False
                                    else:
                                        repeat = True

                            repeat = False

                        else:
                            repeat = True
                    
        with open(LLM_output, "w") as file:
                file.writelines(stuff)
    
    rectify_function(stuff, funcs_list)
    stuff, funcs_list = get_funcs(LLM_output)   

    def rectify_object(stuff, funcs_list):   

        O, R, T, IM = fetch_details("./LLM_KG/updated_onto.ttl")
        A = O+R+T+IM   
           
        for index, fun in enumerate(funcs_list):
                
            if fun and len(fun)>1:

                #object correction
                if fun[1] not in O+R+T+IM and not fun[1].isdigit():
                    repeat = True

                    while repeat:

                        ask = input(f'{stuff[index].strip()} #Item "{fun[1]}" isnt present in my knoweldge base! Is it present in the system? Please answer in "yes" or "no".If I am mistaking it for another item, please enter "correct_item".\n')

                    
                        if ask=='no':
                            funcs_list, stuff = remove_item(fun[1], funcs_list, stuff)
                            repeat = False

                        elif ask=='yes':
                            add_obj(fun)
                            O, R, T, IM = fetch_details("./LLM_KG/updated_onto.ttl")
                            repeat = False
                            
                        elif ask=='correct_item':
                            corr_item = input("Please enter the correct item\n")
                            funcs_list, stuff = fix_item(fun[1], corr_item, funcs_list, stuff)
                            repeat = False

                        else:
                            repeat = True

        with open(LLM_output, "w") as file:
            file.writelines(stuff)

    rectify_object(stuff, funcs_list)
    stuff, funcs_list = get_funcs(LLM_output)  

        

def correct_onto(LLM_output, change_initial_onto):

    # correcting onto
    with open(LLM_output) as file:
        stuff = file.readlines()
        stuff = [a.replace("'", '"') for a in stuff]
        stuff = [s.lower() for s in stuff]
        funcs_list = [i.replace('(', ' ').replace(')', ' ').replace('"', ' ').replace(',',' ').split() for i in stuff]
        funcs = [i[0] for i in funcs_list]

    

    for i, f in enumerate(funcs_list): #correct_onto
            
        if f:

            if len(f)>2 and not f[0].split("_")[0]=='put'and not f[0].split("_")[0]=='pour':
                if i==0:
                    if change_initial_onto==0:
                        if len(f)==3:
                            stuff[i]=f'{f[0]}("{f[1]}", "./LLM_KG/initial_onto.ttl")\n'
                        elif len(f)==4:
                            stuff[i]=f'{f[0]}("{f[1]}", "{f[2]}", "./LLM_KG/initial_onto.ttl")\n'
                    else:
                        if len(f)==3:
                            stuff[i]=f'{f[0]}("{f[1]}", "./LLM_KG/updated_onto.ttl")\n'
                        elif len(f)==4:
                            stuff[i]=f'{f[0]}("{f[1]}", "{f[2]}", "./LLM_KG/updated_onto.ttl")\n'
                else:
                    if len(f)==3:
                        stuff[i]=f'{f[0]}("{f[1]}", "./LLM_KG/updated_onto.ttl")\n'
                    elif len(f)==4:
                        stuff[i]=f'{f[0]}("{f[1]}", "{f[2]}", "./LLM_KG/updated_onto.ttl")\n'

    with open(LLM_output, "w") as file:
        file.writelines(stuff)


def self_correction(LLM_output, change_initial_onto):

    remove_spacing(LLM_output)
    correct_arguments(LLM_output)

    with open(LLM_output) as file:
        stuff = file.readlines()
        stuff = [a.replace("'", '"') for a in stuff]
        stuff = [s.lower() for s in stuff]
        funcs_list = [i.replace('(', ' ').replace(')', ' ').replace('"', ' ').replace(',',' ').split() for i in stuff]
        funcs = [i[0] for i in funcs_list]

    if not funcs:
        return False
    
    object_correction(LLM_output)
    function_correction(LLM_output)
    # knowledge_expansion(LLM_output)
    # function_correction(LLM_output)
    correct_onto(LLM_output, change_initial_onto)
                 
    return True


def ask_gpt(main_prompt, my_prompt):

    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"), 
        api_version="2024-02-01",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT") 
    )

    deployment_name = 'first' 

    response = client.chat.completions.create(
        model=deployment_name, 
        messages=[
            {"role": "system", "content": main_prompt},
            {"role": "user", "content": my_prompt },
        ]
    )

    messages=[
    {"role": "system", "content": main_prompt},
    {"role": "user", "content": my_prompt },
    ]

    with open("./LLM_KG/LLM_orig_output.txt", "w") as file:
        file.write(str(response.choices[0].message.content))

    token_used = token_counter(messages)

    return token_used


def remove_indentation(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    stripped_lines = [line.lstrip() for line in lines]
    
    with open(file_path, 'w') as file:
        file.writelines(stripped_lines)



def remove_serial_numbers(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    lines = [re.sub(r'^[\d+\)\-\*\s]+', '', line) for line in lines]
    cleaned_lines = [re.sub(r'^[\d+\.\-\*\s]+', '', line) for line in lines]
    
    with open(file_path, 'w') as file:
        file.writelines(cleaned_lines)


def remove_empty_lines(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()
    filtered_lines = [line for line in lines if line.strip()]
    with open(file_path, "w") as file:
        file.writelines(filtered_lines)



def triple(file):
    with open(file, "r") as file:
        content = file.read()
    return f"""\
            {content}\
        """


def back_to_LLM(main_prompt, my_prompt, RBO, co, i):

    issue = """ 
    There were some issue(s) in the action sequence you gave. The error is reflected below. Give me the cot and task sequence again. Make sure to strictly USE All THE INGREDIENTS GIVEN BY THE USER IN THE PROMPT.
    """
    
    # instruction = """ 
    # Additional instructions:
    # - STRICTLY USE THE OBJECTS, TOOLS, RECEPTACLES AND THE ACTIONS GIVEN IN THE ENVIRONMENT. 
    # """

    ll = ['error_occured']

    if os.path.exists("./LLM_KG/outputs/output_with_error.txt"):
            
        with open("./LLM_KG/outputs/output_with_error.txt", "r") as file:
            lines = file.readlines()

        ll = [l for l in lines if l.strip() != '' and 'Error' in l.split()[0]]

            
    with open (f"./LLM_KG/feedback/LLM_feedback_with_error_{i}.txt" , "w") as file:
        file.write(issue)

    remove_indentation(f"./LLM_KG/feedback/LLM_feedback_with_error_{i}.txt")
    with open (f"./LLM_KG/feedback/LLM_feedback_with_error_{i}.txt" , "a") as file:   
        file.write("\n")

        if not co and RBO=='':
            file.writelines("\nLLM failed to give the action sequence!\n")
        elif RBO == '' and co:
            file.writelines(ll[-1])
        else:
            file.writelines(RBO)

    # with open (f"./LLM_KG/feedback/LLM_feedback_with_error_{i}.txt" , "a") as file:
    #     file.write("\n")
    #     file.write(instruction)


    LLM_feedback_with_error = triple(f"./LLM_KG/feedback/LLM_feedback_with_error_{i}.txt")

    client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"), 
            api_version="2024-02-01",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT") 
        )

    deployment_name = 'first' 

    LLM_orig_output = triple("./LLM_KG/LLM_orig_output.txt")
    LLM_FB = LLM_feedback_with_error
    
    if i==0:
        response = client.chat.completions.create(
                model=deployment_name, 
                messages=[
                    {"role": "system", "content": main_prompt},
                    {"role": "user", "content": my_prompt },
                    {"role": "assistant", "content": LLM_orig_output},
                    {"role": "user", "content": triple(f"./LLM_KG/feedback/LLM_feedback_with_error_{i}.txt")}
                ]
            )
        
        messages=[
            {"role": "system", "content": main_prompt},
            {"role": "user", "content": my_prompt },
            {"role": "assistant", "content": LLM_orig_output},
            {"role": "user", "content": triple(f"./LLM_KG/feedback/LLM_feedback_with_error_{i}.txt")}
        ]
        token_used = token_counter(messages)
        
    else :
        response = client.chat.completions.create(
                model=deployment_name, 
                messages=[
                    {"role": "system", "content": main_prompt},
                    {"role": "user", "content": my_prompt },
                    {"role": "assistant", "content": triple(f"./LLM_KG/feedback/LLM_updated_orig_output_{i}.txt")},
                    {"role": "user", "content": triple(f"./LLM_KG/feedback/LLM_feedback_with_error_{i}.txt")}
                ]
            )
        
        messages=[
            {"role": "system", "content": main_prompt},
            {"role": "user", "content": my_prompt },
            {"role": "assistant", "content": triple(f"./LLM_KG/feedback/LLM_updated_orig_output_{i}.txt")},
            {"role": "user", "content": triple(f"./LLM_KG/feedback/LLM_feedback_with_error_{i}.txt")}
        ]

        token_used = token_counter(messages)

    # elif i==1:
    #     response = client.chat.completions.create(
    #             model=deployment_name, 
    #             messages=[
    #                 {"role": "system", "content": main_prompt},
    #                 {"role": "user", "content": my_prompt },
    #                 {"role": "assistant", "content": LLM_orig_output},
    #                 {"role": "user", "content": triple(f"./feedback/LLM_feedback_with_error_0.txt")},
    #                 {"role": "assistant", "content": triple(f"./feedback/LLM_updated_orig_output_1.txt")},
    #                 {"role": "user", "content": triple(f"./feedback/LLM_feedback_with_error_1.txt")}
    #             ]
    #         )

    # elif i==2:
    #     response = client.chat.completions.create(
    #             model=deployment_name, 
    #             messages=[
    #                 {"role": "system", "content": main_prompt},
    #                 {"role": "user", "content": my_prompt },
    #                 {"role": "assistant", "content": LLM_orig_output},
    #                 {"role": "user", "content": triple(f"./feedback/LLM_feedback_with_error_0.txt")},
    #                 {"role": "assistant", "content": triple(f"./feedback/LLM_updated_orig_output_1.txt")},
    #                 {"role": "user", "content": triple(f"./feedback/LLM_feedback_with_error_1.txt")},
    #                 {"role": "assistant", "content": triple(f"./feedback/LLM_updated_orig_output_2.txt")},
    #                 {"role": "user", "content": triple(f"./feedback/LLM_feedback_with_error_2.txt")}
    #             ]
    #         )


    with open(f"./LLM_KG/feedback/LLM_updated_orig_output_{i+1}.txt", "w") as file:
        file.write(str(response.choices[0].message.content))

    return token_used



def correct_LLM_output(orig_file, cleaned_file, change_initial_onto):

    copy_contents(orig_file, cleaned_file)
    remove_indentation(cleaned_file)
    remove_serial_numbers(cleaned_file)
    remove_comments(cleaned_file)
    remove_empty_lines(cleaned_file)

    with open(cleaned_file, "r") as file:
        lines = file.readlines()

    for i, l in enumerate(lines): #allows all the functions
        if not "(" in list(l.split()[0]):
            lines[i] = ''
        if len(l.split(" "))>20:
            lines[i] = ''

    for i, f in enumerate(lines):
        lines[i] = lines[i][:lines[i].find(')')+1] + '\n'
        lines[i] = lines[i].replace("'", '"')
        for i, f in enumerate(lines):
            if not any(char.isdigit() for char in f) and '"' not in lines[i]:
                lines[i]=''

    with open(cleaned_file, "w") as file:
        file.writelines(lines)


    remove_empty_lines(cleaned_file)
    remove_serial_numbers(cleaned_file)
    remove_comments(cleaned_file)
    so = self_correction(cleaned_file, change_initial_onto)
    if not so:
        print("\nLLM failed to give the action sequence!\n")
        return False  # no action sequence in llm output

    return True # action sequence present in llm output


def remove_comments(txt_file):

    with open(txt_file, "r") as file:
        lines = file.readlines()

    lines = [l.split() for l in lines]

    for i, l in enumerate(lines):
        
        for word in l:

            if word.startswith('#'):
                hash_index = l.index(word)
                lines[i] = l[:hash_index]

        lines[i] = ' '.join(lines[i]) + '\n'

    with open(txt_file, "w") as file:
        file.writelines(lines)

def copy_contents(orig_file, cleaned_file):

    with open(orig_file, 'r') as file:
        lines = file.readlines()

    with open(cleaned_file, 'w') as file:
        for l in lines:
            file.writelines(l)



def run_py(file, output_1, output_2):
    try:

        if os.path.exists(output_2):
            os.remove(output_2)
        
        with open(output_1, "w") as file_1:
            try:
                process = subprocess.Popen(
                    ['python3', file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                stdout, stderr = process.communicate()
                
                file_1.write(stdout) 
            
            except Exception as e:
                print(f"An error occurred while running the subprocess: {e}")
                stderr = f"Subprocess error: {e}\n"

        if stderr:
            with open(output_2, "w") as file_2:
                file_2.write(stdout)
                file_2.write(stderr)

        print(stdout)
        print(stderr)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def text_2_py(file):

    req = """
    import rdflib
    from functions.actions import *

    """



    with open(file,'r') as firstfile, open('./LLM_KG/final_run.py','w') as secondfile: 
        
        secondfile.write(req)

        
        for line in firstfile: 
                secondfile.write(line)



def success(dish):
     

     
     with open("./LLM_KG/kitchen.json", "r") as file:

        f = json.load(file)

     req_ingd = f[dish]

     def correct_everything(file):
          remove_empty_lines(file)
          remove_serial_numbers(file)
          remove_comments(file)
        #   correct_onto(file)
          self_correction(file)

     if os.path.exists("./LLM_KG/feedback/LLM_updated_orig_output_3.txt"):
          of = "./LLM_KG/feedback/LLM_updated_orig_output_3.txt"

     else:
          of = "./LLM_KG/LLM_orig_output.txt"

     copy_contents(of, "./LLM_KG/LLM_orig_output_copy.txt")
     
     remove_empty_lines("./LLM_KG/LLM_orig_output_copy.txt")

     with open("./LLM_KG/LLM_orig_output_copy.txt", 'r') as file:

          lines = file.readlines()

     for i, l in enumerate(lines):
          
          if l.startswith('1'):
               f_i = i

          if l.startswith('2'):
               s_i = i

          if l.startswith('3'):
               t_i = i

     f = []
     s = []
     t = []

     for i, l in enumerate(lines):

          if i>f_i and i<s_i:
               if "(" in list(l.split()[0]): #allowing every function now
                         f.append(l)

          if i>s_i and i<t_i:
               if "(" in list(l.split()[0]):
                         s.append(l)

          if i>t_i:
               if "(" in list(l.split()[0]):
                         t.append(l)      

    
     with open("./LLM_KG/for_metric/f.txt", "w") as file_1, open("./LLM_KG/for_metric/s.txt", "w") as file_2, open("./LLM_KG/for_metric/t.txt", "w") as file_3 :
          
          file_1.writelines(f)
          file_2.writelines(s)
          file_3.writelines(t)


     correct_everything("./LLM_KG/for_metric/f.txt")
     correct_everything("./LLM_KG/for_metric/s.txt")
     correct_everything("./LLM_KG/for_metric/t.txt")


     text_2_py("./LLM_KG/for_metric/f.txt") 
     remove_indentation('./LLM_KG/final_run.py')
     with io.StringIO() as buf, contextlib.redirect_stdout(buf):
          run_py('./LLM_KG/final_run.py', "./LLM_KG/for_metric/f_output.txt", "./LLM_KG/for_metric/f_output_with_error.txt" )


     text_2_py("./LLM_KG/for_metric/s.txt") 
     remove_indentation('./LLM_KG/final_run.py')
     with io.StringIO() as buf, contextlib.redirect_stdout(buf):
          run_py('./LLM_KG/final_run.py', "./LLM_KG/for_metric/s_output.txt", "./LLM_KG/for_metric/s_output_with_error.txt" )

     text_2_py("./LLM_KG/for_metric/t.txt") 
     remove_indentation('./LLM_KG/final_run.py')
     with io.StringIO() as buf, contextlib.redirect_stdout(buf):
          run_py('./LLM_KG/final_run.py', "./LLM_KG/for_metric/t_output.txt", "./LLM_KG/for_metric/t_output_with_error.txt" )



     ff = 1
     ss = 1
     tt = 1

     with open("./LLM_KG/for_metric/f_output.txt", "r") as file_1, open("./LLM_KG/for_metric/s_output.txt", "r") as file_2, open("./LLM_KG/for_metric/t_output.txt", "r") as file_3 :
          
          f_lines = file_1.readlines()
          s_lines = file_2.readlines()
          t_lines = file_3.readlines()

     if not f_lines or os.path.exists("./LLM_KG/for_metric/f_output_with_error.txt"):
           ff = 0

     if not s_lines or os.path.exists("./LLM_KG/for_metric/s_output_with_error.txt"):
           ss = 0

     if not t_lines or os.path.exists("./LLM_KG/for_metric/t_output_with_error.txt"):
           tt = 0
           

     for l in f_lines:
          if l.startswith("/"):
               ff = 0

     for l in s_lines:
          if l.startswith("/"):
               ss = 0

     for l in t_lines:
          if l.startswith("/"):
               tt = 0
          
               
     sum = ff + ss + tt
     os.remove("./LLM_KG/LLM_orig_output_copy.txt")

     return (sum/3)*100
     


def fetch_actions():
    with open("./LLM_KG/functions/actions.py", "r") as file:
        lines = file.readlines()

    ll = []

    for l in lines:
        if l.startswith("def"):
            ll.append(l.split()[1:])

    ll = [" ".join(i) for i in ll]
    actions = [i.replace(':', '') for i in ll]
    funcs = [i.replace('(', ' ').replace(')', '').replace('"', ' ').replace(',',' ').split()[0] for i in actions]

    return actions, funcs


def delete_folder_contents(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
    
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)  
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)  


# gives items used in the LLM output.
# ingredients will help us check if the minimum required ingredients have been used or not.
def ingd_used():

    gen_final()

    O, R, T, IM = fetch_details("./LLM_KG/initial_onto.ttl")
    A = O+R+T+IM
 
    with open("./LLM_KG/final_output.txt", "r") as file:
        stuff = file.readlines()

    stuff = [a.replace("'", '"') for a in stuff]
    stuff = [s.lower() for s in stuff]
    stuff = [i.replace('(', ' ').replace(')', ' ').replace('"', ' ').replace(',',' ').split() for i in stuff]

    ingredients = []

    for i, l in enumerate(stuff):
        for o in A:
            if o in l:
                ingredients.append(o)

    ingredients = list(set(ingredients))

    return ingredients



# removing the actions which are not using the items present in the env 
def remove_unknown(number_of_feedback):

    if os.path.exists("./LLM_KG/feedback/LLM_updated_orig_output.txt"):
        of = f"./LLM_KG/feedback/LLM_updated_output_{number_of_feedback+1}.txt"

    else:
        of = "./LLM_KG/LLM_output.txt"

    with open(of, "r") as file:
        lines  = file.readlines()

    O, R, T , IM = fetch_details("./LLM_KG/updated_onto.ttl")
    A = O + R + T + IM

    items, ingds = ingd_used()

    with open(of, "w") as file2:
        for i, l in enumerate(lines):
            if items[i] in A:
                file2.write(l)


def refine_block_op(file, change_initial_onto):
    buffer = io.StringIO()
    original_stdout = sys.stdout  
    sys.stdout = buffer

    try:
        self_correction(file, change_initial_onto)
    finally:
        sys.stdout = original_stdout  

    output = buffer.getvalue()
    return output


def common_recep(onto_file):

    g = rdflib.Graph()
    g.parse(onto_file, format="turtle")

    cr_query = """
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?place_name
    WHERE {
        ?place ex:common_rec true.
        ?place ex:rec_name ?place_name.
        }
    """

    sp = g.query(cr_query)
    cr = []

    for p in sp:
        cr = str(p.place_name)

    return cr



def find_similar_function(func, t):

    a, fl = fetch_actions()
    # nltk.download('wordnet')
    lemmatizer = WordNetLemmatizer()


    def lemmatize_word(word):
        return lemmatizer.lemmatize(word.lower(), pos='v')

    def extract_primary_verb(word):
        parts = word.split("_")
        return lemmatize_word(parts[0])

    def get_synonyms(word):
        synsets = wn.synsets(word, pos=wn.VERB)
        synonyms = set()
        for synset in synsets:
            synonyms.update(lemma.name() for lemma in synset.lemmas())
        return synonyms

    def calculate_similarity(word1, word2):
        synsets1 = wn.synsets(word1, pos=wn.VERB)
        synsets2 = wn.synsets(word2, pos=wn.VERB)
        max_similarity = 0
        
        for synset1 in synsets1:
            for synset2 in synsets2:
                similarity = synset1.wup_similarity(synset2)
                if similarity and similarity > max_similarity:
                    max_similarity = similarity
                    
        return max_similarity

    def is_strong_match(word, obj_list):
        primary_verb = extract_primary_verb(word)
        synonyms = get_synonyms(primary_verb)
        
        for action in obj_list:
            lemmatized_action = lemmatize_word(action)
            if primary_verb == lemmatized_action or lemmatized_action in synonyms:
                return action
        return None

    def compare_compound_words(word, obj_list):
        primary_verb = extract_primary_verb(word)
        for action in obj_list:
            action_primary_verb = extract_primary_verb(action)
            if primary_verb == action_primary_verb:
                return action
        return None

    def match_with_similarity_threshold(word, obj_list, threshold=t, margin=0.05):
        primary_verb = extract_primary_verb(word)
        best_match = None
        second_best_match = None
        max_similarity = 0
        second_max_similarity = 0
        
        for action in obj_list:
            action_primary_verb = extract_primary_verb(action)
            similarity = calculate_similarity(primary_verb, action_primary_verb)
            if similarity and similarity >= threshold:
                if similarity > max_similarity:
                    second_max_similarity = max_similarity
                    second_best_match = best_match
                    max_similarity = similarity
                    best_match = action
                elif similarity > second_max_similarity:
                    second_max_similarity = similarity
                    second_best_match = action
        
        if best_match and second_best_match and abs(max_similarity - second_max_similarity) <= margin:
            return None
        
        return best_match

    def find_best_match(word, obj_list):
        primary_verb = extract_primary_verb(word)
        
        best_match = is_strong_match(word, obj_list)
        if best_match:
            return best_match
        
        compound_match = compare_compound_words(word, obj_list)
        if compound_match:
            return compound_match
        
        similarity_match = match_with_similarity_threshold(word, obj_list)
        if similarity_match:
            return similarity_match
        
        return None



    best_match = find_best_match(func, fl)

    print(best_match)


def progress_lines():

    gen_final()

    def prog_lines(output):
        with open(output, "r") as file:
            lines = file.readlines()

        for i, l in enumerate(lines):
            if l.startswith("robot moved"):
                lines[i] = ''
        
        os.makedirs("./LLM_KG/prog_lines", exist_ok=True)
        with open("./LLM_KG/prog_lines/progress_lines.txt", "w") as file:
            file.writelines(lines)

    o,r,t,im = fetch_details("./LLM_KG/initial_onto.ttl")

    tool_used = []
    rec_used = []
    obj_used = []

    with open("./LLM_KG/final_output.txt") as file:
        lines = file.readlines()

    for i, f in enumerate(lines):
        for obj in o:
            if obj in lines[i] and obj.split("_")[0] in lines[i].replace("_", " ").replace("'", " ").split():
                obj_used.append(obj)
        for tool in t:
            if tool in lines[i] and tool.split("_")[0] in lines[i].replace("_", " ").replace("'", " ").split():
                tool_used.append(tool)
        for rec in r:
            if rec in lines[i] and rec.split("_")[0] in lines[i].replace("_", " ").replace("'", " ").split():
                rec_used.append(rec)
         
    tool_used = list(set(tool_used))
    rec_used = list(set(rec_used))
    obj_used = list(set(obj_used))


    prog_lines("./LLM_KG/final_output.txt")

    with open("./LLM_KG/prog_lines/progress_lines.txt", "r") as file:
        lines = file.readlines()

    olines = lines.copy()

    all_objs = []
    all_tls = []
    all_recs = []

    for o in obj_used:
        a = []
        for i,l in enumerate(lines):
        
            if o in lines[i] and o.split("_")[0] in lines[i].replace("_", " ").replace("'", " ").split():
                a.append(lines[i].strip())
        
        all_objs.append(a)

    for t in tool_used:
        a = []
        for i,l in enumerate(lines):
        
            if t in lines[i] and t.split("_")[0] in lines[i].replace("_", " ").replace("'", " ").split():
                a.append(lines[i].strip())
        
        all_tls.append(a)

    for r in rec_used:
        a = []
        for i,l in enumerate(lines):
        
            if r in lines[i] and r.split("_")[0] in lines[i].replace("_", " ").replace("'", " ").split():
                a.append(lines[i].strip())
        
        all_recs.append(a)


    with open("./LLM_KG/prog_lines/obj_prog_lines.txt", "w") as file:

        for o, obj in zip(all_objs, obj_used):
            file.write(f"[{obj}]" + "\n")
            for i, oi in enumerate(o):
                if i < len(o)-1:
                    file.write(oi + " ----> ")
                else:
                    file.write(oi)

            file.write("\n\n")

    with open("./LLM_KG/prog_lines/tool_prog_lines.txt", "w") as file:

        for t, tool in zip(all_tls, tool_used):
            file.write(f"[{tool}]" + "\n")
            for i, ti in enumerate(t):
                if i<len(t)-1:
                    file.write(ti + " ----> ")
                else:
                    file.write(ti)

            file.write("\n\n")

    with open("./LLM_KG/prog_lines/rec_prog_lines.txt", "w") as file:

        for r, rec in zip(all_recs, rec_used):
            file.write(f"[{rec}]" + "\n")
            for i, ri in enumerate(r):
                if i<len(r)-1:
                    file.write(ri + " ----> ")
                else:
                    file.write(ri)
            
            file.write("\n\n")


def gen_final():

    # Get all filenames
    file_names = [f for f in os.listdir("LLM_KG/outputs") if f.startswith('output_') and f.endswith('.txt')]

    # Sorting the files
    file_names.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))
    
    if os.path.exists("./LLM_KG/outputs/output_with_error.txt"):
        all_lines = []

        for f in file_names:
            with open(f"./LLM_KG/outputs/{f}", "r") as file:
                lines = file.readlines()
            all_lines = all_lines + lines

    else:
        all_lines = []

        for f in file_names:
            with open(f"./LLM_KG/outputs/{f}", "r") as file:
                lines = file.readlines()
            all_lines = all_lines + lines


    # The final output contains the actions the robot has done so far.
    with open("./LLM_KG/final_output.txt", "w") as file:
        file.writelines(all_lines)

def count_errors():
    i = 0
    if os.path.exists("./LLM_KG/outputs/output_with_error.txt"):
        i = 1

    return i