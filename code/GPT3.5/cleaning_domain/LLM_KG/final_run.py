import rdflib
from functions.actions import *
pick_up_obj("cleaning_solution", "./LLM_KG/updated_onto.ttl")
put_down_obj("cleaning_solution", "countertop")
put_down_tool("spoon", "countertop")
clean("spoon", "./LLM_KG/updated_onto.ttl")
put_down_tool("spoon", "countertop")
