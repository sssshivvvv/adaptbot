import rdflib
from functions.actions import *
pick_up_obj("water", "./LLM_KG/initial_onto.ttl")
put_down_obj("water", "countertop")
put_down_obj("plant", "plate")
put_down_obj("water", "countertop")
pour_contents("water", "bowl")
