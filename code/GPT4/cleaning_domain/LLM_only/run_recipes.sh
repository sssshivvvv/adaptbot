#!/bin/bash

# Define an array with 20 different recipe requests
recipes=(
    "give me cot and action sequence to prepare egg fry"
    "give me cot and action sequence to prepare vegetable fry using potato, tomato and lettuce. You can add spices in it as well."
    "give me cot and action sequence to prepare boiled egg"
    "give me cot and action sequence to prepare apple salad"
)

# Loop through each recipe and run the Python script
for recipe in "${recipes[@]}"
do
    python3 stitching_everything.py "$recipe" 0 "initial_onto.ttl"
done
