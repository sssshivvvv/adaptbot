import rdflib
from functions.actions import *
clean("plate", "initial_onto.ttl")
put_down_rec("plate", "countertop")
put_down_obj("bread", "countertop")
put_down_obj("egg", "countertop")
put_down_tool("knife", "countertop")
put_down_rec("pan", "stove")
put_down_obj("egg", "pan")
fry("egg", "updated_onto.ttl")
put_down_obj("bread", "cutting_board")
slice("bread", "knife", "updated_onto.ttl")
put_down_obj("egg", "plate")
put_down_obj("bread", "plate")
