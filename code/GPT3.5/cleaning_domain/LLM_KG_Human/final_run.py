import rdflib
from functions.actions import *
pick_up_tool("spoon", "./LLM_KG_Human/initial_onto.ttl")
put_down_obj("cleaning_solution", "plate")
clean("spoon", "./LLM_KG_Human/updated_onto.ttl")
pour_contents("water", "countertop")
put_down_tool("spoon", "countertop")