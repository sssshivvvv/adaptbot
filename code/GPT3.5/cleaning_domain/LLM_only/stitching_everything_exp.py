import rdflib
import sys
from LLM_only.functions.actions import *
from LLM_only.functions.misc_funcs import *
import os
import argparse
import subprocess
import json
import numpy as np

if os.path.exists("./LLM_only/outputs"):
    delete_folder_contents("./LLM_only/outputs")
os.makedirs("./LLM_only/outputs", exist_ok=True)

if os.path.exists("./LLM_only/feedback"):
    delete_folder_contents("./LLM_only/feedback")
else:
    os.mkdir("./LLM_only/feedback")


def LLM_only(main_prompt, my_prompt, n_fb, iter, maintok, dish_name, dish_ingd):

    total_token_used = 0

    if n_fb == 0: #no_feedback
        co = correct_LLM_output("./LLM_only/LLM_orig_output.txt", "./LLM_only/LLM_output.txt", 0, 0)

        if co:
            text_2_py("./LLM_only/LLM_output.txt") # create final_run.py
            remove_indentation('./LLM_only/final_run.py')
            run_py('./LLM_only/final_run.py', "./LLM_only/outputs/output_1.txt", "./LLM_only/outputs/output_with_error.txt" )


    else: #feedback

        co = correct_LLM_output("./LLM_only/LLM_orig_output.txt", "./LLM_only/LLM_output.txt", 0, 0) #tells if the LLM gave the action sequence or not
        need_feedback = False

        if co : #proceed and execute; wait for results
            print("\n")
            text_2_py("./LLM_only/LLM_output.txt")
            remove_indentation('./LLM_only/final_run.py')
            run_py('./LLM_only/final_run.py', "./LLM_only/outputs/output_1.txt", "./LLM_only/outputs/output_with_error.txt" )

            if not os.path.exists("./LLM_only/outputs/output_with_error.txt"):
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
  

        while need_feedback and i< int(n_fb):

            need_feedback = False
            print(f"\n\nfeedback no {i+1} sending...\n")
            tokens = back_to_LLM(main_prompt, my_prompt, co, i)
            total_token_used +=tokens
            co = correct_LLM_output(f"./LLM_only/feedback/LLM_updated_orig_output_{i+1}.txt", f"./LLM_only/feedback/LLM_updated_output_{i+1}.txt", 1, i+1)

            if co:
                print("\n")
                text_2_py(f"./LLM_only/feedback/LLM_updated_output_{i+1}.txt")
                remove_indentation('./LLM_only/final_run.py')
                run_py('./LLM_only/final_run.py', f"./LLM_only/outputs/output_{i+2}.txt", "./LLM_only/outputs/output_with_error.txt" )

                if not os.path.exists("./LLM_only/outputs/output_with_error.txt"):
                    print("feedback not needed!")
                else:
                    need_feedback = True

            else:
                need_feedback = True

            i+=1


    gen_final()
    ingdd_used = ingd_used()


    content = { "dish_name": dish_name,
                "dish_ingd": dish_ingd,
                "ingd_used": ingdd_used,
                "percentage_ingd_used": (len(list(np.intersect1d(dish_ingd, ingdd_used)))/len(dish_ingd))*100,
                "#feedback_used": len(os.listdir("./LLM_only/feedback"))//3,
                "#execution_errors" : count_errors(),
                "#human_involvement": 0,
                "#token_used": total_token_used + maintok
                }

    with open("./LLM_only/results.json", "w") as file:
        json.dump(content, file, indent=4)

    if os.path.exists(f"./LLM_only/experiment_results/results_{iter}"):
        shutil.rmtree(f"./LLM_only/experiment_results/results_{iter}")

    if os.path.exists("./LLM_only/output_with_error.txt"):
        os.remove("./LLM_only/output_with_error.txt")  

    os.makedirs(f"./LLM_only/experiment_results/results_{iter}/LLM_outputs_{iter}", exist_ok=True)
    os.makedirs(f"./LLM_only/experiment_results/results_{iter}/Feedbacks_{iter}", exist_ok=True)
    os.makedirs(f"./LLM_only/experiment_results/results_{iter}/Execution_outputs_{iter}", exist_ok=True)

    progress_lines()
    shutil.copytree("./LLM_only/prog_lines", f"./LLM_only/experiment_results/results_{iter}", dirs_exist_ok=True)

    shutil.copy("./LLM_only/LLM_orig_output.txt", f"./LLM_only/experiment_results/results_{iter}/LLM_outputs_{iter}")
    shutil.copy("./LLM_only/LLM_output.txt", f"./LLM_only/experiment_results/results_{iter}/LLM_outputs_{iter}")

    for j in range(0, (len(os.listdir("./LLM_only/feedback"))//3)):
        shutil.copy(f"./LLM_only/feedback/LLM_updated_orig_output_{j+1}.txt", f"./LLM_only/experiment_results/results_{iter}/LLM_outputs_{iter}")
        shutil.copy(f"./LLM_only/feedback/LLM_updated_output_{j+1}.txt", f"./LLM_only/experiment_results/results_{iter}/LLM_outputs_{iter}")

    for j in range(0, (len(os.listdir("./LLM_only/feedback"))//3)):
        shutil.copy(f"./LLM_only/feedback/LLM_feedback_with_error_{j}.txt", f"./LLM_only/experiment_results/results_{iter}/Feedbacks_{iter}")

    for j in range(0, (len(os.listdir("./LLM_only/outputs"))-1)):
        shutil.copy(f"./LLM_only/outputs/output_{j+1}.txt", f"./LLM_only/experiment_results/results_{iter}/Execution_outputs_{iter}")

    shutil.copy(f"./LLM_only/final_output.txt", f"./LLM_only/experiment_results/results_{iter}/Execution_outputs_{iter}")

    if os.path.exists("./LLM_only/outputs/output_with_error.txt"):
        shutil.copy("./LLM_only/outputs/output_with_error.txt", f"./LLM_only/experiment_results/results_{iter}/Execution_outputs_{iter}")

    shutil.copy("./LLM_only/results.json", f"./LLM_only/experiment_results/results_{iter}")


    
    return total_token_used + maintok






            

