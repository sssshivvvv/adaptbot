import rdflib
from functions.actions import *
move("bedroom_floor", "./LLM_KG/initial_onto.ttl")
move("living_room_floor", "./LLM_KG/updated_onto.ttl")
put_down_rec("music_player", "countertop")
switch("music_player", "./LLM_KG/updated_onto.ttl")
