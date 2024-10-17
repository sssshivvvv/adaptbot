import rdflib
from functions.actions import *
clean("pot", "./LLM_only/updated_onto.ttl")
put_down_rec("pot", "countertop")
put_down_rec("oil", "countertop")
put_down_obj("salt", "countertop")
put_down_obj("banana", "cutting_board")
slice("banana", "knife", "./LLM_only/updated_onto.ttl")
put_down_rec("banana_slice", "pot")
put_down_rec("oil", "pot")
fry("banana_chips", "./LLM_only/updated_onto.ttl")
put_down_obj("banana_chips", "plate")
