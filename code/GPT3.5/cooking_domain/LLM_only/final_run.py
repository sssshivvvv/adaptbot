import rdflib
from functions.actions import *
clean("pan", "./LLM_only/updated_onto.ttl")
put_down_rec("pan", "countertop")
put_down_rec("oil", "countertop")
put_down_obj("salt", "countertop")
put_down_obj("banana", "cutting_board")
slice("banana", "knife", "./LLM_only/updated_onto.ttl")
put_down_rec("banana_slice", "pan")
put_down_rec("oil", "pan")
fry("banana_chips", "./LLM_only/updated_onto.ttl")
put_down_obj("banana_chips", "plate")
