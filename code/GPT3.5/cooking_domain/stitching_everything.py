import rdflib
from LLM_KG_Human.functions.misc_funcs import *
from LLM_only.stitching_everything_exp import LLM_only
from LLM_KG.stitching_everything_exp import LLM_KG
from LLM_KG_Human.stitching_everything_exp import LLM_KG_Human
import os
import argparse
import subprocess
import shutil




actions, funcs = fetch_actions()

def prompt(onto_file):

    o,r,t,im = fetch_details(onto_file)

    main_prompt = f"""
- I am working on a project where I am using LLM along with knowledge graph to perform task planning in the given environment.
- Given is the ontology of the environment, where I define the classes named object, receptacle, tool and their properties. I instantiate these classes with the items present in my environment. I also define the set of actions that the robot can perform in the given environment.

- Given this information, LLM should give me two things in the output:
1) chain of thought: Like explaining why it came up with the task sequence that It came up with. The chain of though should decribe the cooking process by breaking it into three subproblems: 1. Fetching the ingredients and tools required for the cooking task, 2. Cooking process, 3. plating and serving.
2) The action sequence for the task.



- Here is the information of my environment

Environment Description:
- Rooms: ['kitchen']
- Objects: {o}
- Tools: {t}
- Receptacles: {r + im}
- Actions: {actions}


The first action would take initial ontology, initial_onto.ttl as the argument and then the next actions in the sequence would take updated_onto.ttl as the argument.



- I will give you an example. In order to make a hot coffee, the chain of thought and the sequence of actions would be the following:

COT & ACTION SEQUENCE: 

1. Fetching the ingredients and tools required for the cooking task:

To prepare the coffee, I will first fetch the items I need. I will bring the pan, milk, coffee and glass. If glass in not cleaned, I will clean it first.

pick_up_obj("milk", "updated_onto.ttl") #picking up the milk
put_down_obj("milk", "countertop") #putting down the milk on the countertop
pick_up_obj("coffee", "updated_onto.ttl") #picking up the coffee
put_down_obj("coffee", "countertop") #putting down the coffee on the countertop
clean("glass", "updated_onto.ttl") #cleaning the glass
pick_up_rec("glass", "updated_onto.ttl") #picking up the glass
put_down_rec("glass", "countertop") #putting down the glass on the countertop

2. Cooking process: 

To prepare coffee, milk should be boiled, so I will boil it.

boil("milk", "initial_onto.ttl") #boiling the milk for the coffee

3. plating and serving:

I will put the boiled milk into the glass, then I will put the coffee into the glass. I will stir the contents. The coffee is ready!

pick_up_obj("milk", "updated_onto.ttl") #picking up the milk
put_down_obj("milk", "glass") #putting #putting down the milk into the glass
pick_up_obj("coffee", "updated_onto.ttl") #picking up coffee
put_down_obj("coffee", "glass") #putting the coffee into glass filled with milk
stir_contents("glass", "updated_onto.ttl") #stirring the contents of the glass



STRICT GUIDELINES:

 - READ THIS INFORMATION I JUST GAVE YOU CAREFULLY. STICK TO THE DESCRIPTION & STRUCTURE OF THE ACTIONS. 
 - STRICTLY USE THE TOOLS, RECEPTACLES AND THE ACTIONS GIVEN IN THE ENVIRONMENT, AND THE MINIMUM IGREDIENTS PROVIDED BY THE USER IN THE PROMPT.
 - IN THE NEXT PROMPTS, I WILL GIVE YOU SOME NEW TASKS FOR WHICH YOU HAVE TO COME UP WITH COT & ACTION SEQUENCE (IN THE SAME FORMAT I WROTE ABOVE).
 - MAKE SURE TO DIVIDE THE COT AND TASK SEQUENCE INTO THREE PARTS, 1. Fetching the ingredients and tools required for the cooking task, 2. Cooking process, 3. plating and serving.

 - AFTER AN ACION IS PERFORMED ON AN ITEM, ITS NAME REMAINS SAME. MEANS, AFTER SLICING, apple WONT BECOME sliced_apple.
 - SECOND ARGUMENT OF put_down FUNCTIONS SHOULD BE LOCATION ONLY, NOT AN ONTO FILE.
 - SECOND ARGUMENT OF pour_contents FUNCTION SHOULD BE A LOCATION ONLY, NOT AN ONTO FILE.

"""

    
    return main_prompt

             

if __name__ == "__main__":


    with open("kitchen.json", "r") as file:
        content = json.load(file)
    
    parser = argparse.ArgumentParser(description="Takes the prompt and gives the LLM output")
    parser.add_argument("arg1", type=int, help="number of feedback")
    parser.add_argument("arg2", type=str, help="onto_file")

    args = parser.parse_args()

    main_prompt = prompt(args.arg2)

    for i, j in enumerate(content):

        tokens = ask_gpt(main_prompt, f"give me cot and action sequence to {list(content.keys())[i]}. The minimum requirements for this task are {content[j]}." )

        print(f"/////Running LLM only framework...for dish: {list(content.keys())[i]}\n")
        shutil.copy("LLM_orig_output.txt", "./LLM_only/LLM_orig_output.txt")
        total_token_used = LLM_only(main_prompt, f"give me cot and action sequence to prepare {list(content.keys())[i]}. The minimum ingredients for this dish are {content[j]}. Please use these ingredients only." , args.arg1, i, tokens, list(content.keys())[i], content[j])
        print(f"number of tokens used in LLM only framework: {total_token_used}")

        print(f"\n\n//////Running LLM + KG framework...for dish: {list(content.keys())[i]}\n")
        shutil.copy("LLM_orig_output.txt", "./LLM_KG/LLM_orig_output.txt")
        total_token_used = LLM_KG(main_prompt, f"give me cot and action sequence to prepare {list(content.keys())[i]}. The minimum ingredients for this dish are {content[j]}. Please use these ingredients only." , args.arg1, i, tokens, list(content.keys())[i], content[j])
        print(f"number of tokens used in LLM + KG framework: {total_token_used}")

        print(f"\n\n/////Running LLM + KG + Human framework...for dish: {list(content.keys())[i]}\n")
        shutil.copy("LLM_orig_output.txt", "./LLM_KG_Human/LLM_orig_output.txt")
        total_token_used = LLM_KG_Human(main_prompt, f"give me cot and action sequence to prepare {list(content.keys())[i]}. The minimum ingredients for this dish are {content[j]}. Please use these ingredients only.", args.arg1, i, tokens, list(content.keys())[i], content[j])
        print(f"number of tokens used in LLM + KG + Human framework: {total_token_used}")




    