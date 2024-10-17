import rdflib
from LLM_KG_Human.functions.actions import *
from LLM_KG_Human.functions.misc_funcs import *
import os
import argparse
import subprocess
import numpy as np


if os.path.exists("./LLM_KG_Human/feedback"):
    delete_folder_contents("./LLM_KG_Human/feedback")
else:
    os.mkdir("./LLM_KG_Human/feedback")



def LLM_KG_Human(main_prompt, my_prompt, n_fb, iter, maintok, dish_name, dish_ingd):

    total_token_used = 0
    Human_involvement = 0

    if n_fb == 0: #no_feedback
        co = correct_LLM_output("./LLM_KG_Human/LLM_orig_output.txt", "./LLM_KG_Human/LLM_output.txt", 0)
        # correct_onto("LLM_output.txt")

        if co:
            text_2_py("./LLM_KG_Human/LLM_output.txt") # create final_run.py
            remove_indentation('./LLM_KG_Human/final_run.py')
            run_py('./LLM_KG_Human/final_run.py', "./LLM_KG_Human/output.txt", "./LLM_KG_Human/output_with_error.txt" )


    else: #feedback
        smooth = 0
        co = correct_LLM_output("./LLM_KG_Human/LLM_orig_output.txt", "./LLM_KG_Human/LLM_output.txt", 0) #tells if the LLM gave the action sequence or not
        # correct_onto("LLM_output.txt")
        RBO = refine_block_op("./LLM_KG_Human/LLM_output.txt", 0) #gives the output of refinement block
        need_feedback = False

        if co and RBO == '': #proceed and execute; wait for results
            smooth+=1
            print("\n")
            text_2_py("./LLM_KG_Human/LLM_output.txt")
            remove_indentation('./LLM_KG_Human/final_run.py')
            run_py('./LLM_KG_Human/final_run.py', "./LLM_KG_Human/output.txt", "./LLM_KG_Human/output_with_error.txt" )

            if not os.path.exists("./LLM_KG_Human/output_with_error.txt"):
                print("feedback not needed!")
            else:
                need_feedback = True

        elif co and RBO!='': #give feedback immediately
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
            tokens = back_to_LLM(main_prompt, my_prompt, RBO, co, i)
            total_token_used +=tokens

            if smooth>0:
                co = correct_LLM_output(f"./LLM_KG_Human/feedback/LLM_updated_orig_output_{i+1}.txt", f"./LLM_KG_Human/feedback/LLM_updated_output_{i+1}.txt", 1)
                RBO = refine_block_op(f"./LLM_KG_Human/feedback/LLM_updated_output_{i+1}.txt", 1)
            else:
                co = correct_LLM_output(f"./LLM_KG_Human/feedback/LLM_updated_orig_output_{i+1}.txt", f"./LLM_KG_Human/feedback/LLM_updated_output_{i+1}.txt", 0)
                RBO = refine_block_op(f"./LLM_KG_Human/feedback/LLM_updated_output_{i+1}.txt", 0)
            
            if co and RBO=='':
                smooth+=1
                print("\n")
                text_2_py(f"./LLM_KG_Human/feedback/LLM_updated_output_{i+1}.txt")
                remove_indentation('./LLM_KG_Human/final_run.py')
                run_py('./LLM_KG_Human/final_run.py', "./LLM_KG_Human/output.txt", "./LLM_KG_Human/output_with_error.txt" )

                if not os.path.exists("./LLM_KG_Human/output_with_error.txt"):
                    print("feedback not needed!")
                else:
                    need_feedback = True

            else:
                need_feedback = True

            i+=1

        Human_involvement = 0
        additions_made = 0
        corrections_made = 0

        if need_feedback and i==int(n_fb): #human involvement
            
            if smooth>0:
                RBO = refine_block_op(f"./LLM_KG_Human/feedback/LLM_updated_output_{len(os.listdir('./LLM_KG_Human/feedback'))//3}.txt", 1)
            else:
                RBO = refine_block_op(f"./LLM_KG_Human/feedback/LLM_updated_output_{len(os.listdir('./LLM_KG_Human/feedback'))//3}.txt", 0)

            if RBO!='':
                print("\n\n")
                Human_involvement, additions_made, corrections_made = knowledge_expansion(f"./LLM_KG_Human/feedback/LLM_updated_output_{len(os.listdir('./LLM_KG_Human/feedback'))//3}.txt")
                function_correction(f"./LLM_KG_Human/feedback/LLM_updated_output_{len(os.listdir('./LLM_KG_Human/feedback'))//3}.txt")

                if smooth>0:
                    correct_onto(f"./LLM_KG_Human/feedback/LLM_updated_output_{len(os.listdir('./LLM_KG_Human/feedback'))//3}.txt", 1)
                else:
                    correct_onto(f"./LLM_KG_Human/feedback/LLM_updated_output_{len(os.listdir('./LLM_KG_Human/feedback'))//3}.txt", 0)

                text_2_py(f"./LLM_KG_Human/feedback/LLM_updated_output_{len(os.listdir('./LLM_KG_Human/feedback'))//3}.txt")
                remove_indentation('./LLM_KG_Human/final_run.py')
                print("\n")
                run_py('./LLM_KG_Human/final_run.py', "./LLM_KG_Human/output.txt", "./LLM_KG_Human/output_with_error.txt" )
                #perform final evaluation
            
            else:
                #perform final evaluation
                pass 


    ingdd_used = ingd_used()


    content = { "dish_name": dish_name,
                "dish_ingd": dish_ingd,
                "ingd_used": ingdd_used,
                "percentage_ingd_used": (len(list(np.intersect1d(dish_ingd, ingdd_used)))/len(dish_ingd))*100,
                "#feedback_used": len(os.listdir("./LLM_KG_Human/feedback"))//3,
                "#execution_errors" : count_errors(),
                "#human_involvement": Human_involvement,
                "#additions_made": additions_made,
                "#corrections_made": corrections_made,
                "#token_used": total_token_used + maintok
                }

    with open("./LLM_KG_Human/results.json", "w") as file:
        json.dump(content, file, indent=4)

    if os.path.exists(f"./LLM_KG_Human/experiment_results/results_{iter}"):
        shutil.rmtree(f"./LLM_KG_Human/experiment_results/results_{iter}")

    if os.path.exists("./LLM_KG_Human/output_with_error.txt"):
        os.remove("./LLM_KG_Human/output_with_error.txt")  

    os.makedirs(f"./LLM_KG_Human/experiment_results/results_{iter}/LLM_outputs_{iter}", exist_ok=True)
    os.makedirs(f"./LLM_KG_Human/experiment_results/results_{iter}/Feedbacks_{iter}", exist_ok=True)
    os.makedirs(f"./LLM_KG_Human/experiment_results/results_{iter}/Execution_outputs_{iter}", exist_ok=True)

    progress_lines()
    shutil.copytree("./LLM_KG_Human/prog_lines", f"./LLM_KG_Human/experiment_results/results_{iter}", dirs_exist_ok=True)

    shutil.copy("./LLM_KG_Human/LLM_orig_output.txt", f"./LLM_KG_Human/experiment_results/results_{iter}/LLM_outputs_{iter}")
    shutil.copy("./LLM_KG_Human/LLM_output.txt", f"./LLM_KG_Human/experiment_results/results_{iter}/LLM_outputs_{iter}")

    for j in range(0, (len(os.listdir("./LLM_KG_Human/feedback"))//3)):
        shutil.copy(f"./LLM_KG_Human/feedback/LLM_updated_orig_output_{j+1}.txt", f"./LLM_KG_Human/experiment_results/results_{iter}/LLM_outputs_{iter}")
        shutil.copy(f"./LLM_KG_Human/feedback/LLM_updated_output_{j+1}.txt", f"./LLM_KG_Human/experiment_results/results_{iter}/LLM_outputs_{iter}")

    for j in range(0, (len(os.listdir("./LLM_KG_Human/feedback"))//3)):
        shutil.copy(f"./LLM_KG_Human/feedback/LLM_feedback_with_error_{j}.txt", f"./LLM_KG_Human/experiment_results/results_{iter}/Feedbacks_{iter}")

    shutil.copy("./LLM_KG_Human/output.txt", f"./LLM_KG_Human/experiment_results/results_{iter}/Execution_outputs_{iter}")

    if os.path.exists("./LLM_KG_Human/output_with_error.txt"):
        shutil.copy("./LLM_KG_Human/output_with_error.txt", f"./LLM_KG_Human/experiment_results/results_{iter}/Execution_outputs_{iter}")


    shutil.copy("./LLM_KG_Human/results.json", f"./LLM_KG_Human/experiment_results/results_{iter}")
        
    print(f"Number of times human involved: {Human_involvement}")
    return total_token_used + maintok




            

