import rdflib
from functions.actions import *
pick_up_rec("pan", "./LLM_KG/initial_onto.ttl")
put_down_rec("pan", "stove")
put_down_obj("egg", "countertop")
put_down_obj("milk", "countertop")
put_down_obj("cheese", "countertop")
put_down_obj("ham", "countertop")
put_down_obj("bread", "countertop")
put_down_obj("oil", "countertop")
put_down_obj("egg", "pan")
put_down_obj("milk", "pan")
mix_contents("pan", "./LLM_KG/updated_onto.ttl")
put_down_obj("bread", "countertop")
wait(2)
flip_contents("pan", "./LLM_KG/updated_onto.ttl")
wait(1)
put_down_obj("ham", "pan")
put_down_obj("cheese", "pan")
put_down_obj("bread", "plate")
