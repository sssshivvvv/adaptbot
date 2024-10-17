import json
import subprocess
import time
import os
from functions.misc_funcs import *
from functions.actions import *

def load_recipes(json_path):
    with open(json_path, 'r') as f:
        return json.load(f)

def generate_prompts(recipe_names):
    return [f"give me cot and action sequence to prepare {recipe.replace('_', ' ')}" for recipe in recipe_names]

def run_stitching_script(prompt, stitching_file, feedback):
    command = f'python3 {stitching_file} "{prompt}" {feedback} "initial_onto.ttl"'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout + result.stderr

def read_lines_from_LLM_output(filepath):
    with open(filepath, "r") as file:
        return file.readlines()

def count_total_lines(filepath):
    return len(read_lines_from_LLM_output(filepath))

def count_error_lines(filepath):
    lines = read_lines_from_LLM_output(filepath)
    error_count = 0

    for index, line in enumerate(lines):
        try:
            eval(line)
        except Exception as e:
            error_count += 1
    return error_count

def check_if_all_items_present(llm_items, orig_ingredients):
    llm_set = set(llm_items)
    not_present_items = [item for item in orig_ingredients if item not in llm_set]
    return len(not_present_items)

def evaluate_llm_kg(prompt, output, orig_ingredients):
    start_time = time.time()
    
    if len(os.listdir("feedback"))>0:
        output_filepath = f"feedback/LLM_updated_output_{len(os.listdir('feedback')) // 3}.txt"
    else:
        output_filepath = "LLM_output.txt"

    total_lines = count_total_lines("LLM_output.txt")

    error_lines = count_error_lines(output_filepath)
    llm_items = ingd_used()
    correct_llm_outputs = (total_lines - error_lines) / total_lines if total_lines > 0 else 0
    ingredients_not_present = check_if_all_items_present(llm_items, orig_ingredients) / len(orig_ingredients) if len(orig_ingredients) > 0 else 0
    duration = time.time() - start_time

    summary = {
        "prompt": prompt,
        "total_lines": total_lines,
        "error_lines": error_lines,
        "correct_llm_outputs_percentage": correct_llm_outputs * 100,
        "ingredients_not_present_percentage": ingredients_not_present * 100,
        "llm_items": ", ".join(sorted(set(llm_items))),
        "orig_ingredients": ", ".join(sorted(set(orig_ingredients))),
        "output": output,
        "evaluation_time_seconds": duration
    }

    with open("LLM_kg_summary_output.json", 'a') as f:
        json.dump(summary, f, indent=4)
        f.write('\n')



if __name__ == "__main__":
    json_path = "kitchen.json"
    recipes_data = load_recipes(json_path)
    prompts = generate_prompts(recipes_data.keys())
    prompts = prompts[:2]


    for prompt in prompts:
        print(f"\n\n{prompt}\n")
        recipe_name = prompt.replace("give me cot and action sequence to prepare ", "").replace(" ", "_")
        orig_ingredients = recipes_data[recipe_name]

        last_output = run_stitching_script(prompt, "stitching_everything_exp.py", feedback=3)
        evaluate_llm_kg(prompt, last_output, orig_ingredients)
        print("LLM KG evaluation completed!")