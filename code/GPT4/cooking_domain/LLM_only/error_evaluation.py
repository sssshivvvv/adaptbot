from functions.misc_funcs import *

orig_output_filepath = "LLM_output.txt"

def read_lines_from_LLM_output(orig_output_filepath):
    with open(orig_output_filepath, "r") as file:
        lines = file.readlines()
    return lines

def count_total_lines(orig_output_filepath):
    return len(read_lines_from_LLM_output(orig_output_filepath))

def count_error_lines(orig_output_filepath):
    lines = read_lines_from_LLM_output(orig_output_filepath)
    error_count = 0
    
    for index, line in enumerate(lines):
        try:
            eval(line)
            print(f"Line {index + 1}: Parsed successfully.")
        
        except Exception as e:
            error_count += 1
            print(f"Line {index + 1}: Error - {str(e)}")
    return (error_count)

def check_if_all_items_present(llm_items, orig_ingredients):
    llm_set = set(llm_items)
    not_present_items = [item for item in orig_ingredients if item not in llm_set]
    return len(not_present_items)

total_lines = count_total_lines(orig_output_filepath)
# self_correction(orig_output_filepath)
error_lines = count_error_lines(orig_output_filepath)
incorrect_llm_outputs = error_lines/total_lines
llm_items, orig_ingredients = ingd_used()
ingredients_not_present = check_if_all_items_present(llm_items, orig_ingredients) # how to quantify ingredients_not_present and incorrect_llm_lines
