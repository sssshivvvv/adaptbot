import rdflib
from functions.actions import *
from functions.misc_funcs import *
import os
import argparse
import subprocess
import json

if os.path.exists("outputs"):
    delete_folder_contents("outputs")

os.makedirs("outputs", exist_ok=True)

if os.path.exists("feedback"):
    delete_folder_contents("feedback")
else:
    os.mkdir("feedback")

actions, funcs = fetch_actions()
total_token_used = 0

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

 - READ THIS INFORMATION I JUST GAVE YOU CAREFULLY. STICK TO THE DESCRIPTION OF THE ENVIRONMENT. 
 - STRICTLY USE THE OBJECTS, TOOLS, RECEPTACLES AND THE ACTIONS GIVEN IN THE ENVIRONMENT. 
 - IN THE NEXT PROMPTS, I WILL GIVE YOU SOME NEW ACTIONS FOR WHICH YOU HAVE TO COME UP WITH COT & ACTION SEQUENCE (IN THE SAME FORMAT I WROTE ABOVE).
 - MAKE SURE TO DIVIDE THE COT AND TASK SEQUENCE INTO THREE PARTS, 1. Fetching the ingredients and tools required for the cooking task, 2. Cooking process, 3. plating and serving.

 - SECOND ARGUMENT OF put_down FUNCTIONS SHOULD BE LOCATION ONLY.
 - SECOND ARGUMENT OF pour_contents FUNCTION SHOULD BE A LOCATION ONLY.

"""

    
    return main_prompt


def final(my_prompt, main_prompt):

    tokens = ask_gpt(main_prompt, my_prompt) 
    co = correct_LLM_output("LLM_orig_output.txt", "LLM_output.txt", 0, 0)

    if co:
        text_2_py("LLM_output.txt") # create final_run.py
        remove_indentation('final_run.py')
        run_py('final_run.py', "./outputs/output_1.txt", "./outputs/output_with_error.txt" )
    
    return tokens

                

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Takes the prompt and gives the LLM output")
    parser.add_argument("arg1", type=str, help="my_prompt")
    parser.add_argument("arg2", type=int, help="number of feedback")
    parser.add_argument("arg3", type=str, help="onto_file")

    args = parser.parse_args()

    main_prompt = prompt(args.arg3)
    
    if args.arg2 == 0: #no_feedback
        total_token_used = final(args.arg1, main_prompt)
        need_feedback = False


    else: #feedback
        
        #first_call
        tokens = ask_gpt(main_prompt, args.arg1) 
        total_token_used+=tokens
        co = correct_LLM_output("LLM_orig_output.txt", "LLM_output.txt", 0, 0) #tells if the LLM gave the action sequence or not
        need_feedback = False

        if co : #proceed and execute; wait for results
            print("\n")
            text_2_py("LLM_output.txt")
            remove_indentation('final_run.py')
            run_py('final_run.py', "./outputs/output_1.txt", "./outputs/output_with_error.txt" )

            if not os.path.exists("./outputs/output_with_error.txt"):
                print("feedback not needed!")
            else:
                need_feedback = True

        elif not co: #give feedback immediately
            need_feedback = True

        i = 0
        
        """
        After checking the conditions above, there are three possibilities:

        1. The LLM provided the action sequence, it passed cleanly through the refinement block, and we executed the actions. If the execution occurred without errors, then we don't need feedback; otherwise, we do. \\ need_feedback = true

        2. The LLM provided the action sequence, but the refinement block raised some errors, so we need feedback to handle them. \\ need_feedback = true

        3. The LLM did not provide the action sequence, so we need feedback to inform it of this.  \\ need_feedback = true

        """
  

        while need_feedback and i< int(args.arg2):

            need_feedback = False
            print(f"\n\nfeedback no {i+1} sending...\n")
            tokens = back_to_LLM(main_prompt, args.arg1, co, i)
            total_token_used+=tokens
            co = correct_LLM_output(f"./feedback/LLM_updated_orig_output_{i+1}.txt", f"./feedback/LLM_updated_output_{i+1}.txt", 1, i+1)

            if co:
                print("\n")
                text_2_py(f"./feedback/LLM_updated_output_{i+1}.txt")
                remove_indentation('final_run.py')
                run_py('final_run.py', f"./outputs/output_{i+2}.txt", "./outputs/output_with_error.txt" )

                if not os.path.exists("./outputs/output_with_error.txt"):
                    print("feedback not needed!")
                else:
                    need_feedback = True

            else:
                need_feedback = True

            i+=1

        print(f"Total number of tokens used: {total_token_used}")


        content = {
                    "#feedback_used": len(os.listdir("feedback"))//3,
                    "#execution_errors" : count_errors(),
                    "#human_involvement": 0,
                    "#token_used": total_token_used
                  }

        with open("results.json", "w") as file:
            json.dump(content, file, indent=4)
            

