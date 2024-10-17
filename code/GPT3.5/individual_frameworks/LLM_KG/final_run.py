import rdflib
from functions.actions import *
pick_up_obj("milk", "initial_onto.ttl")
put_down_obj("milk", "countertop")
put_down_obj("choco_powder", "countertop")
clean("glass", "updated_onto.ttl")
put_down_rec("glass", "countertop")
boil("milk", "updated_onto.ttl")
put_down_obj("milk", "glass")
put_down_obj("choco_powder", "glass")
stir_contents("glass", "updated_onto.ttl")
