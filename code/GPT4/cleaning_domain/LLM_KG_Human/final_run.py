import rdflib
from functions.actions import *
pick_up_tool("spoon", "./LLM_KG_Human/initial_onto.ttl")
move("sink", "./LLM_KG_Human/updated_onto.ttl")
clean("spoon", "./LLM_KG_Human/updated_onto.ttl")
put_down_tool("spoon", "countertop")