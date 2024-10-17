# Agent actions in the given environment

import rdflib
from .misc_funcs import *
import random




def move(loc, onto_file):

    g = rdflib.Graph()
    g.parse(onto_file, format="turtle")
    o,r,t,im = fetch_details(onto_file)

    room_query = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?room_name
    WHERE {{
        ?loc rdf:type ex:room .
        ?loc ex:room_name ?room_name.
    }}
    """
    rloc = g.query(room_query)
    rooms = []
    for i in rloc:
        rooms.append(str(i.room_name))

    if loc in rooms:
        return True

    if loc in r:
        while loc not in im:
            mr_loc_query = f"""
            PREFIX ex: <http://example.org/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            SELECT ?im_name
            WHERE {{
                ex:{loc} rdf:type ex:mreceptacle .
                ex:{loc} ex:mrec_location ?im_loc .
                ?im_loc ex:rec_name ?im_name.
            }}
            """
            imloc = g.query(mr_loc_query)
            for i in imloc:
                imloc = str(i.im_name)

                loc = imloc

    elif loc in o:
        while loc not in im:

            if loc in o:
                o_loc_query = f"""
                PREFIX ex: <http://example.org/>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

                SELECT ?im_name
                WHERE {{
                    ex:{loc} rdf:type ex:object .
                    ex:{loc} ex:obj_location ?im_loc .
                    ?im_loc ex:rec_name ?im_name.
                }}
                """
                oloc = g.query(o_loc_query)
                for i in oloc:
                    ooloc = str(i.im_name)

            elif loc in r:
                o_loc_query = f"""
                PREFIX ex: <http://example.org/>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

                SELECT ?im_name
                WHERE {{
                    ex:{loc} rdf:type ex:mreceptacle .
                    ex:{loc} ex:mrec_location ?im_loc .
                    ?im_loc ex:rec_name ?im_name.
                }}
                """
                oloc = g.query(o_loc_query)
                for i in oloc:
                    ooloc = str(i.im_name)


            loc = ooloc

    elif loc in t:
        while loc not in im:

            if loc in t:
                o_loc_query = f"""
                PREFIX ex: <http://example.org/>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

                SELECT ?im_name
                WHERE {{
                    ex:{loc} rdf:type ex:tool .
                    ex:{loc} ex:tool_location ?im_loc .
                    ?im_loc ex:rec_name ?im_name.
                }}
                """
                oloc = g.query(o_loc_query)
                for i in oloc:
                    ooloc = str(i.im_name)

            elif loc in r:
                o_loc_query = f"""
                PREFIX ex: <http://example.org/>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

                SELECT ?im_name
                WHERE {{
                    ex:{loc} rdf:type ex:mreceptacle .
                    ex:{loc} ex:mrec_location ?im_loc .
                    ?im_loc ex:rec_name ?im_name.
                }}
                """
                oloc = g.query(o_loc_query)
                for i in oloc:
                    ooloc = str(i.im_name)


            loc = ooloc

    initial_loc_query = """
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?initial_loc
    WHERE {
        ex:robot ex:agent_near ?init_loc .
        ?init_loc ex:rec_name ?initial_loc .

    }
    """

    iloc = g.query(initial_loc_query)
    for i in iloc:
        iloc = str(i.initial_loc)

    if iloc==loc:
        delete_query = """
        PREFIX ex: <http://example.org/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        DELETE WHERE {
            ex:robot ex:agent_near ?loc .
            ex:robot_arm ex:mrec_location ?locc .
        }
        """

        g.update(delete_query)

        # Updating location
        insert_query = f"""
        PREFIX ex: <http://example.org/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        INSERT DATA {{
            ex:robot ex:agent_near <http://example.org/{loc}> .
            ex:robot_arm ex:mrec_location <http://example.org/{loc}> .
        }}
        """

        # Execute the insert query
        g.update(insert_query)
        g.serialize(destination="updated_onto.ttl", format="turtle")

        # print(f"robot already at {loc}")
        return True

    query = """
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?rec_name
    WHERE {
        ?rec rdf:type ex:imreceptacle .
        ?rec ex:rec_name ?rec_name.
    }
    """

    recs = g.query(query)
    rec_list = []
    for o in recs:
        rec_list.append(str(o.rec_name))

    if loc not in rec_list:
        raise RuntimeError(f"move({loc}, {onto_file}) #{loc} not present in the environment!")


    else:
        delete_query = """
        PREFIX ex: <http://example.org/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        DELETE WHERE {
            ex:robot ex:agent_near ?loc .
            ex:robot_arm ex:mrec_location ?locc .
        }
        """

        g.update(delete_query)

        # Updating location
        insert_query = f"""
        PREFIX ex: <http://example.org/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        INSERT DATA {{
            ex:robot ex:agent_near <http://example.org/{loc}> .
            ex:robot_arm ex:mrec_location <http://example.org/{loc}> .
        }}
        """

        # Execute the insert query
        g.update(insert_query)
        g.serialize(destination="updated_onto.ttl", format="turtle")

    print(f"robot moved from {iloc} to {loc}")
        
    return True


def pick_up_obj(obj, onto_file):

    obj_in_hand = None

    g = rdflib.Graph()
    g.parse(onto_file, format="turtle")

    o,r,t,im = fetch_details(onto_file)

    if obj in o:
        pass
    elif obj in r:
        raise RuntimeError(f"pick_up_obj({obj}, {onto_file}) #{obj} is a receptacle, not an object!")

    elif obj in t:
        raise RuntimeError(f"pick_up_obj({obj}, {onto_file}) #{obj} is a tool, not an object!")
    
    elif obj in im:
        print(f"Cant pick {obj}! skipping this action")
        return False
    
    else:
        raise RuntimeError(f"pick_up_obj({obj}, {onto_file}) #{obj} is not present in the environment!")
    


    big_query = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?status
    WHERE {{
        ex:{obj} ex:IsBig ?status.
    }}
    """
    b = g.query(big_query)

    for s in b:

        if s.status:
            print(f"{obj} is a big object, cant pick it! skipping this action")
            return False
            
        
    hold_query = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?obj_name
    WHERE {{
        ex:robot ex:obj_in_hand ?obj.
        ?obj ex:obj_name ?obj_name.
    }}
    """
    hq = g.query(hold_query)
    for h in hq:
        obj_in_hand = str(h.obj_name)

    if obj_in_hand:
        if obj_in_hand==obj:
            return True
    
    slice_query = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?obj_name ?slice_status
    WHERE {{
        ?object ex:IsSliceable true.
        ?object ex:obj_name  ?obj_name.
        ex:{obj} ex:sliced ?slice_status.
    }}
    """
    status = g.query(slice_query)

    for s in status:
        if s.slice_status:
            sliced = True
        else:
            sliced = False
    
    sliceable_objects = []
    for s in status:
        sliceable_objects.append(str(s.obj_name))


    loc_query = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?rec_name
    WHERE {{
        <http://example.org/{obj}> ex:obj_location ?rec.
        ?rec ex:rec_name ?rec_name.
    }}
    """
    loc = g.query(loc_query)

    loc_list = []
    for o in loc:
        loc_list.append(str(o.rec_name))

    if move(loc_list[0], onto_file):  # Agent first moves to the object location

        g = rdflib.Graph()
        g.parse("updated_onto.ttl", format="turtle")

        delete_query = f"""
        PREFIX ex: <http://example.org/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        DELETE WHERE {{
            ex:{obj} ex:obj_location ?loc .
        }}
        """

        # Execute the delete query
        g.update(delete_query)

        # Define the SPARQL update query to insert the new property value
        insert_query = f"""
        PREFIX ex: <http://example.org/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        INSERT DATA {{
            ex:{obj} ex:obj_location ex:robot_arm .
            ex:robot ex:obj_in_hand ex:{obj}.
        }}
        """

        g.update(insert_query)
        g.serialize(destination="updated_onto.ttl", format="turtle")
        
        if obj in sliceable_objects:
            if sliced:
                print(f"robot picks up sliced_{obj} from {loc_list[0]}")
            else:
                print(f"robot picks up {obj} from {loc_list[0]}")

        else:
            print(f"robot picks up {obj} from {loc_list[0]}")



def put_down_obj(obj, loc):

    O,R,T,IM = fetch_details("updated_onto.ttl")
    A = O+R+T+IM

    if obj==loc:
        return False

    if loc not in R+IM+O: 
        raise RuntimeError(f"put_down_obj({obj}, {loc}) #Second argument of put down function must be a location or object") 
        

    g = rdflib.Graph()
    g.parse("updated_onto.ttl", format="turtle")


    if obj not in A:
        raise RuntimeError(f"put_down_obj({obj}, {loc}) #{obj} not present in the environment!")
    if obj in R+T+IM:
        print(f"Wrong function choice! skipping this action")
        return False
        
    
    bighold_query = f"""

    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?status
    WHERE {{
        ex:{obj} ex:IsBig ?status.
    }}
    """
    hq = g.query(bighold_query)
    for h in hq:
        if h.status:
            print(f"couldnt pick {obj}! skipping this action")
            return False

    loc_query = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?loc_name
    WHERE {{
        ex:{obj} ex:obj_location ?loc.
        ?loc ex:rec_name ?loc_name.
        }}
    """

    lqry = g.query(loc_query)

    for l in lqry:
        location = str(l.loc_name)

    if location==loc:
        return True

    serve_query = """
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?place_name
    WHERE {
        ?place ex:serving_place true.
        ?place ex:rec_name ?place_name.
        }
    """

    sp = g.query(serve_query)
    splaces = []

    for p in sp:
        splaces.append(str(p.place_name))

    open_rec_query = """
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?place_name
    WHERE {
        ?place ex:open_rec true.
        ?place ex:rec_name ?place_name.
        }
    """

    rq = g.query(open_rec_query)
    orplaces = []

    for p in rq:
        orplaces.append(str(p.place_name))

    goto_query = """
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?rec_name
    WHERE {
        ?rec ex:goto_utensil true.
        ?rec ex:rec_name ?rec_name.
        }
    """

    rq = g.query(goto_query)
    gtplaces = []

    for p in rq:
        gtplaces.append(str(p.rec_name))

    
 
    inhand_query = """   
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?object_name
    WHERE {
        ex:robot ex:obj_in_hand ?object .
        ?object ex:obj_name ?object_name .
    }
    """

    objects = g.query(inhand_query)
    objs = []
    for o in objects:
        objs.append(str(o.object_name))

    if obj not in objs:

        pick_up_obj(obj, "updated_onto.ttl")


    if loc in R:

        loc_query = f"""
        PREFIX ex: <http://example.org/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?rec_name
        WHERE {{
            <http://example.org/{loc}> ex:mrec_location ?rec.
            ?rec ex:rec_name ?rec_name.
        }}
        """
        locn = g.query(loc_query)

        for o in locn:
            loc_locn = str(o.rec_name)

        if loc_locn not in orplaces and loc_locn not in R:

            if loc_locn=="robot_arm": #if the rec is in robots arm, then first put it on the countertop or on the table, then put the object into it.
                
                put_down_rec(loc, random.sample(splaces, 1)[0])

            else:
                put_down_rec(loc, random.sample(splaces, 1)[0])


        g = rdflib.Graph()
        g.parse("updated_onto.ttl", format="turtle")

        locn = g.query(loc_query)

        loc_list = []
        for o in locn:
            loc_list.append(str(o.rec_name))

        m = move(loc_list[0], "updated_onto.ttl")  # Agent first moves to the target_mrec location

    elif loc in O:

        loc_query = f"""
        PREFIX ex: <http://example.org/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?rec_name
        WHERE {{
            <http://example.org/{loc}> ex:obj_location ?rec.
            ?rec ex:rec_name ?rec_name.
        }}
        """
        locn = g.query(loc_query)

        for o in locn:
            loc_locn = str(o.rec_name)

        if loc_locn not in orplaces and loc_locn not in R:

            if loc_locn=="robot_arm": #if the rec is in robots arm, then first put it on the countertop or on the table, then put the object into it.
                
                put_down_obj(loc, random.sample(gtplaces, 1)[0])

            else:
                put_down_obj(loc, random.sample(gtplaces, 1)[0])


        g = rdflib.Graph()
        g.parse("updated_onto.ttl", format="turtle")

        locn = g.query(loc_query)

        loc_list = []
        for o in locn:
            loc_list.append(str(o.rec_name))

        m = move(loc_list[0], "updated_onto.ttl")  # Agent first moves to the target_object location


    else:
        
        m = move(loc, "updated_onto.ttl") #move to the target location
    

    if m:
        
        if loc in O:
            g = rdflib.Graph()
            g.parse("updated_onto.ttl", format="turtle")

            delete_query = f"""
            PREFIX ex: <http://example.org/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            DELETE WHERE {{
                ex:{obj} ex:obj_location ex:robot_arm .
                ex:robot ex:obj_in_hand ex:{obj}.
            }}
            """

            # Execute the delete query
            g.update(delete_query)

            # Define the SPARQL update query to insert the new property value
            insert_query = f"""
            PREFIX ex: <http://example.org/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            INSERT DATA {{
                ex:{obj} ex:obj_location ex:{loc_list[0]}.
            }}
            """

            g.update(insert_query)
            g.serialize(destination="updated_onto.ttl", format="turtle")
            print(f"robot puts down {obj} to {loc}")

        else:

            g = rdflib.Graph()
            g.parse("updated_onto.ttl", format="turtle")

            delete_query = f"""
            PREFIX ex: <http://example.org/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            DELETE WHERE {{
                ex:{obj} ex:obj_location ex:robot_arm .
                ex:robot ex:obj_in_hand ex:{obj}.
            }}
            """

            # Execute the delete query
            g.update(delete_query)

            # Define the SPARQL update query to insert the new property value
            insert_query = f"""
            PREFIX ex: <http://example.org/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            INSERT DATA {{
                ex:{obj} ex:obj_location ex:{loc}.
            }}
            """

            g.update(insert_query)
            g.serialize(destination="updated_onto.ttl", format="turtle")
            print(f"robot puts down {obj} to {loc}")




def pick_up_rec(rec, onto_file):

    rec_in_hand = None

    g = rdflib.Graph()
    g.parse(onto_file, format="turtle")

    o,r,t,im = fetch_details(onto_file)

    if rec in r:
        pass
    elif rec in o:
        raise RuntimeError(f"pick_up_rec({rec}, {onto_file}) #{rec} is an object, not a receptacle!")
        
    elif rec in t:
        raise RuntimeError(f"pick_up_rec({rec}, {onto_file}) #{rec} is a tool, not a receptacle!")
        
    elif rec in im:
        print(f"Cant pick {rec}! skipping this action")
        return False

        
    else:
        raise RuntimeError(f"pick_up_rec({rec}, {onto_file}) #{rec} is not present in the environment!")
        

    big_query = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?status
    WHERE {{
        ex:{rec} ex:IsRecBig ?status.
    }}
    """
    b = g.query(big_query)

    for s in b:

        if s.status:
            print(f"{rec} is a big receptacle, cant pick it! skipping this action")
            return False
        
    hold_query = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?rec_name
    WHERE {{
        ex:robot ex:rec_in_hand ?rec.
        ?rec ex:rec_name ?rec_name.
    }}
    """
    hq = g.query(hold_query)
    for h in hq:
        rec_in_hand = str(h.rec_name)

    if rec_in_hand==rec:
        return True

    loc_query = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?rec_name
    WHERE {{
        <http://example.org/{rec}> ex:mrec_location ?rec.
        ?rec ex:rec_name ?rec_name.
    }}
    """
    loc = g.query(loc_query)

    loc_list = []
    for o in loc:
        loc_list.append(str(o.rec_name))

    move(loc_list[0], onto_file)  # Agent first moves to the receptacle location
    
    g = rdflib.Graph()
    g.parse("updated_onto.ttl", format="turtle")

    delete_query = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    DELETE WHERE {{
        ex:{rec} ex:mrec_location ?loc .
    }}
    """

    # Execute the delete query
    g.update(delete_query)

    # Define the SPARQL update query to insert the new property value
    insert_query = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    INSERT DATA {{
        ex:{rec} ex:mrec_location ex:robot_arm .
        ex:robot ex:rec_in_hand ex:{rec}.
    }}
    """

    g.update(insert_query)
    g.serialize(destination="updated_onto.ttl", format="turtle")
    print(f"robot picks up {rec} from {loc_list[0]}")



def put_down_rec(rec, loc):

    O,R,T,IM = fetch_details("updated_onto.ttl")

    if rec==loc:
        return False

    if loc not in R+IM:
        raise RuntimeError(f"put_down_obj({rec}, {loc}) #Second argument of put down function must be a location")

    g = rdflib.Graph()
    g.parse("updated_onto.ttl", format="turtle")


    if rec not in O+R+T+IM:
        raise RuntimeError(f"put_down_rec({rec}, {loc}) #{rec} not present in the environment!")
    
    if rec in O+T:
        print(f"Wrong function choice! skipping this action")
        return False
    
    if rec in IM:
        print(f"couldnt pick {rec}! skipping this action")
        return False


    cantake_query = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?status
    WHERE {{
        ex:{loc} ex:cantakerec ?status.
        }}
    """
    cantake = g.query(cantake_query)

    for s in cantake:
        if not s.status:
            print(f"Cant put {rec} to {loc}! skipping this action")
            return False
        
 
    hold_query = f"""

    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?status
    WHERE {{
        ex:{rec} ex:IsRecBig ?status.
    }}
    """
    hq = g.query(hold_query)
    for h in hq:
        if h.status:
            print(f"couldnt pick {rec}! skipping this action")
            return False


    loc_query = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?loc_name
    WHERE {{
        ex:{rec} ex:mrec_location ?loc.
        ?loc ex:rec_name ?loc_name.
        }}
    """

    lqry = g.query(loc_query)

    for l in lqry:
        location = str(l.loc_name)

    if location==loc:
        return True
    
    serve_query = """
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?place_name
    WHERE {
        ?place ex:serving_place true.
        ?place ex:rec_name ?place_name.
        }
    """

    sp = g.query(serve_query)
    splaces = []

    for p in sp:
        splaces.append(str(p.place_name))


    open_rec_query = """
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?place_name
    WHERE {
        ?place ex:open_rec true.
        ?place ex:rec_name ?place_name.
        }
    """

    rq = g.query(open_rec_query)
    orplaces = []

    for p in rq:
        orplaces.append(str(p.place_name))

    query = """
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?rec_name
    WHERE {
        ex:robot ex:rec_in_hand ?recep .
        ?recep ex:rec_name ?rec_name .
    }
    """

    recs = g.query(query)
    objs = []
    for o in recs:
        objs.append(str(o.rec_name))

    if rec not in objs:
        pick_up_rec(rec, "updated_onto.ttl")

    q = """
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?rec_name
    WHERE {
        ?rec rdf:type ex:mreceptacle .
        ?rec ex:rec_name ?rec_name.
    }
    """
    mrec = g.query(q)
    mrec_list = []
    for m in mrec:
        mrec_list.append(str(m.rec_name))

    if loc in mrec_list:

        loc_query = f"""
        PREFIX ex: <http://example.org/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?rec_name
        WHERE {{
            <http://example.org/{loc}> ex:mrec_location ?rec.
            ?rec ex:rec_name ?rec_name.
        }}
        """
        locn = g.query(loc_query)

        loc_list = []
        for o in locn:
            loc_list.append(str(o.rec_name))


        if loc_list[0] not in orplaces:

            if loc_list[0]=="robot_arm": #if the rec is in robots arm, then first put it on the countertop or on the table, then put the object into it.
                
                put_down_rec(loc, random.sample(splaces, 1)[0])

            else:
                put_down_rec(loc, random.sample(splaces, 1)[0])

        g = rdflib.Graph()
        g.parse("updated_onto.ttl", format="turtle")
        
        locn = g.query(loc_query)

        loc_list = []
        for o in locn:
            loc_list.append(str(o.rec_name))

        m = move(loc_list[0], "updated_onto.ttl")  # Agent first moves to the target_mrec location

    else:
        
        m = move(loc, "updated_onto.ttl") #move to the target location
    

    if m:
        
        g = rdflib.Graph()
        g.parse("updated_onto.ttl", format="turtle")

        delete_query = f"""
        PREFIX ex: <http://example.org/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        DELETE WHERE {{
            ex:{rec} ex:mrec_location ex:robot_arm .
            ex:robot ex:rec_in_hand ex:{rec}.
        }}
        """

        # Execute the delete query
        g.update(delete_query)

        # Define the SPARQL update query to insert the new property value
        insert_query = f"""
        PREFIX ex: <http://example.org/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        INSERT DATA {{
            ex:{rec} ex:mrec_location ex:{loc}.
        }}
        """

        g.update(insert_query)
        g.serialize(destination="updated_onto.ttl", format="turtle")
        print(f"robot puts down {rec} to {loc}")




def pick_up_tool(tool, onto_file):

    tool_in_hand = None

    g = rdflib.Graph()
    g.parse(onto_file, format="turtle")

    o,r,t,im = fetch_details(onto_file)

    if tool in t:
        pass
    elif tool in o:
        raise RuntimeError(f"pick_up_tool({tool}, {onto_file}) #{tool} is an object, not a tool!")
    
    elif tool in r:
        raise RuntimeError(f"pick_up_tool({tool}, {onto_file}) #{tool} is a receptacle, not a tool!")
    
    elif tool in im:
        print(f"Cant pick {tool}! skipping this action")
        return False
    
    else:
        raise RuntimeError(f"pick_up_tool({tool}, {onto_file}) #{tool} is not present in the environment!")

    hold_query = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?tool_name
    WHERE {{
        ex:robot ex:tool_in_hand ?tool.
        ?tool ex:tool_name ?tool_name.
    }}
    """
    hq = g.query(hold_query)
    for h in hq:
        tool_in_hand = str(h.tool_name)

    if tool_in_hand==tool:
        return True

    loc_query = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?rec_name
    WHERE {{
        <http://example.org/{tool}> ex:tool_location ?rec.
        ?rec ex:rec_name ?rec_name.
    }}
    """
    loc = g.query(loc_query)

    loc_list = []
    for o in loc:
        loc_list.append(str(o.rec_name))

    move(loc_list[0], onto_file)  # Agent first moves to the tool location
    
    g = rdflib.Graph()
    g.parse("updated_onto.ttl", format="turtle")

    delete_query = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    DELETE WHERE {{
        ex:{tool} ex:tool_location ?loc .
    }}
    """

    # Execute the delete query
    g.update(delete_query)

    # Define the SPARQL update query to insert the new property value
    insert_query = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    INSERT DATA {{
        ex:{tool} ex:tool_location ex:robot_arm .
        ex:robot ex:tool_in_hand ex:{tool}.
    }}
    """

    g.update(insert_query)
    g.serialize(destination="updated_onto.ttl", format="turtle")
    print(f"robot picks up {tool} from {loc_list[0]}")



def put_down_tool(tool, loc):

    O,R,T,IM = fetch_details("updated_onto.ttl")
    A = O+R+T+IM

    if tool==loc:
        return False
    if loc not in R+IM:
        raise RuntimeError(f"put_down_obj({tool}, {loc}) #Second argument of put down function must be a location")

    g = rdflib.Graph()
    g.parse("updated_onto.ttl", format="turtle")

    if tool not in A:
        raise RuntimeError(f"put_down_tool({tool}, {loc}) #{tool} not present in the environment!")
    if tool in O+R+IM:
        print(f"Wrong function choice! skipping this action")
        return False
    
    loc_query = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?loc_name
    WHERE {{
        ex:{tool} ex:tool_location ?loc.
        ?loc ex:rec_name ?loc_name.
        }}
    """

    lqry = g.query(loc_query)

    for l in lqry:
        location = str(l.loc_name)

    if location==loc:
        return True
    


    serve_query = """
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?place_name
    WHERE {
        ?place ex:serving_place true.
        ?place ex:rec_name ?place_name.
        }
    """

    sp = g.query(serve_query)
    splaces = []

    for p in sp:
        splaces.append(str(p.place_name))


    open_rec_query = """
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?place_name
    WHERE {
        ?place ex:open_rec true.
        ?place ex:rec_name ?place_name.
        }
    """

    rq = g.query(open_rec_query)
    orplaces = []

    for p in rq:
        orplaces.append(str(p.place_name))


    query = """
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?tool_name
    WHERE {
        ex:robot ex:tool_in_hand ?tool .
        ?tool ex:tool_name ?tool_name .
    }
    """

    tls = g.query(query)
    objs = []
    for o in tls:
        objs.append(str(o.tool_name))

    if tool not in objs:
        pick_up_tool(tool, "updated_onto.ttl")

    q = """
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?rec_name
    WHERE {
        ?rec rdf:type ex:mreceptacle .
        ?rec ex:rec_name ?rec_name.
    }
    """
    mrec = g.query(q)
    mrec_list = []
    for m in mrec:
        mrec_list.append(str(m.rec_name))

    if loc in mrec_list:

        loc_query = f"""
        PREFIX ex: <http://example.org/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?rec_name
        WHERE {{
            <http://example.org/{loc}> ex:mrec_location ?rec.
            ?rec ex:rec_name ?rec_name.
        }}
        """
        locn = g.query(loc_query)

        loc_list = []
        for o in locn:
            loc_list.append(str(o.rec_name))

        if loc_list[0] not in orplaces:

            if loc_list[0]=="robot_arm": #if the rec is in robots arm, then first put it on the countertop or on the table, then put the object into it.
                
                put_down_rec(loc, random.sample(splaces, 1)[0])

            else:
                put_down_rec(loc, random.sample(splaces, 1)[0])


        g = rdflib.Graph()
        g.parse("updated_onto.ttl", format="turtle")
        
        locn = g.query(loc_query)

        loc_list = []
        for o in locn:
            loc_list.append(str(o.rec_name))

        m = move(loc_list[0], "updated_onto.ttl")  # Agent first moves to the target_mrec location

    else:
        
        m = move(loc, "updated_onto.ttl") #move to the target location
    

    if m:
        
        g = rdflib.Graph()
        g.parse("updated_onto.ttl", format="turtle")

        delete_query = f"""
        PREFIX ex: <http://example.org/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        DELETE WHERE {{
            ex:{tool} ex:tool_location ex:robot_arm .
            ex:robot ex:tool_in_hand ex:{tool}.
        }}
        """

        # Execute the delete query
        g.update(delete_query)

        # Define the SPARQL update query to insert the new property value
        insert_query = f"""
        PREFIX ex: <http://example.org/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        INSERT DATA {{
            ex:{tool} ex:tool_location ex:{loc}.
        }}
        """

        g.update(insert_query)
        g.serialize(destination="updated_onto.ttl", format="turtle")
        print(f"robot puts down {tool} to {loc}")



def clean(item, onto_file):

    g = rdflib.Graph()
    g.parse(onto_file, format='turtle')

    o,r,t,im = fetch_details(onto_file)
    A = o+r+t+im

    
    if item not in A:
        raise RuntimeError(f"clean({item}, {onto_file}) #{item} not present in the environment!")
    
    
    elif item in im: #If item is immobile
        mop(item, onto_file)
        return True
    
    cleanarea_query = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?loc_name
    WHERE {{
            ?loc ex:cleaning_area true.
            ?loc ex:rec_name ?loc_name.
    }}
    """
    castatus = g.query(cleanarea_query)
    for ca in castatus:
        cl_area = str(ca.loc_name)
    
    if item in o:

        cleanable_query = f"""
        PREFIX ex: <http://example.org/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?status
        WHERE {{
             ex:{item} rdf:type ex:object.
             ex:{item} ex:NeedsToBeCleaned ?status;
        }}
        """
        cstatus = g.query(cleanable_query)

        for s in cstatus:

            if not s.status:
                print(f"{item} doesnt need to be cleaned! skipping this action. ")
                return True
            

        clean_query = f"""
        PREFIX ex: <http://example.org/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?status ?loc_name
        WHERE {{
             ex:{item} rdf:type ex:object.
             ex:{item} ex:IsCleaned ?status.
             ex:{item} ex:obj_location ?loc.
             ?loc ex:rec_name ?loc_name.
        }}
        """
        status = g.query(clean_query)

        for s in status:

            loc = str(s.loc_name)

            if s.status:

                print(f"{item} already cleaned!")

            else:

                if loc != cl_area:
                    pick_up_obj(item, onto_file)
                    put_down_obj(item, cl_area)

                else:
                    print(f"{item} already in the sink!")
                    move(cl_area, onto_file)

                g = rdflib.Graph()
                g.parse("updated_onto.ttl", format='turtle')

                delete_query = f"""
                PREFIX ex: <http://example.org/>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

                DELETE WHERE {{
                        ex:{item} ex:IsCleaned false.
                }}
                """

                # Execute the delete query
                g.update(delete_query)

                insert_query = f"""
                PREFIX ex: <http://example.org/>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

                INSERT DATA {{
                    ex:{item} ex:IsCleaned true.
                }}
                """

                g.update(insert_query)
                g.serialize(destination="updated_onto.ttl", format="turtle")

                print(f"{item} successfully cleaned!")

    elif item in r:

        clean_query = f"""
        PREFIX ex: <http://example.org/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?status ?loc_name
        WHERE {{
             ex:{item} rdf:type ex:mreceptacle.
             ex:{item} ex:IsRecCleaned ?status.
             ex:{item} ex:mrec_location ?loc.
             ?loc ex:rec_name ?loc_name.
        }}
        """
        status = g.query(clean_query)

        for s in status:

            loc = str(s.loc_name)

            if s.status:

                print(f"{item} already cleaned!")

            else:

                if loc != cl_area:
                    pick_up_rec(item, onto_file)
                    put_down_rec(item, cl_area)

                else:
                    print(f"{item} already in the sink!")
                    move(cl_area, onto_file)

                g = rdflib.Graph()
                g.parse("updated_onto.ttl", format='turtle')

                delete_query = f"""
                PREFIX ex: <http://example.org/>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

                DELETE WHERE {{
                        ex:{item} ex:IsRecCleaned false.
                }}
                """

                # Execute the delete query
                g.update(delete_query)

                insert_query = f"""
                PREFIX ex: <http://example.org/>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

                INSERT DATA {{
                    ex:{item} ex:IsRecCleaned true.
                }}
                """

                g.update(insert_query)
                g.serialize(destination="updated_onto.ttl", format="turtle")

                print(f"{item} successfully cleaned!")


    elif item in t:

        clean_query = f"""
        PREFIX ex: <http://example.org/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?status ?loc_name
        WHERE {{
             ex:{item} rdf:type ex:tool.
             ex:{item} ex:IsToolCleaned ?status.
             ex:{item} ex:tool_location ?loc.
             ?loc ex:rec_name ?loc_name.
        }}
        """
        status = g.query(clean_query)

        for s in status:
            loc = str(s.loc_name)

            if s.status:

                print(f"{item} already cleaned!")

            else:

                if loc != cl_area:
                    pick_up_tool(item, onto_file)
                    put_down_tool(item, cl_area)

                else:
                    print(f"{item} already in the sink!")
                    move(cl_area, onto_file)

                g = rdflib.Graph()
                g.parse("updated_onto.ttl", format='turtle')

                delete_query = f"""
                PREFIX ex: <http://example.org/>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

                DELETE WHERE {{
                        ex:{item} ex:IsToolCleaned false.
                }}
                """

                # Execute the delete query
                g.update(delete_query)

                insert_query = f"""
                PREFIX ex: <http://example.org/>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

                INSERT DATA {{
                    ex:{item} ex:IsToolCleaned true.
                }}
                """

                g.update(insert_query)
                g.serialize(destination="updated_onto.ttl", format="turtle")

                print(f"{item} successfully cleaned!")



def slice(obj, tool, onto_file):

    g = rdflib.Graph()
    g.parse(onto_file, format='turtle')

    O, R, T, IM = fetch_details(onto_file)
    A = O + R + T + IM

    if obj not in O and obj in R+T+IM:
            print(f"{obj} cant be sliced! skipping this action")
            return False
    elif obj not in A:
            raise RuntimeError(f"slice({obj}, {tool}, {onto_file}) #{obj} not present int he environment!")
    


    board_query = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?rec_name
    WHERE {{
        ?rec  ex:used_for_slicing true.
        ?rec ex:rec_name ?rec_name.
    }}
    """
    slice_boards = []
    bquery = g.query(board_query)
    for b in bquery:
        slice_boards.append(str(b.rec_name))
 
    tool_query = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?tool_name
    WHERE {{
        ?tool ex:IsSlicingTool true.
        ?tool ex:tool_name ?tool_name.
    }}
    """
    env_tools = []
    tquery = g.query(tool_query)
    for t in tquery:
        env_tools.append(str(t.tool_name))


    if tool not in A:
            tool = random.sample(env_tools,1)[0]

    if tool not in env_tools:
            tool = random.sample(env_tools,1)[0]



    obj_query = """
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?obj_name
    WHERE {
        ?object rdf:type ex:object.
        ?object ex:IsSliceable true.
        ?object ex:obj_name ?obj_name.
    }
    """
    objs = g.query(obj_query)
    obj_list = []
    for o in objs:
        obj_list.append(str(o.obj_name))

    if obj not in obj_list:
        print(f"{obj} is not Sliceable! skipping this action")
        return False


    slice_query = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?status
    WHERE {{
            ex:{obj} ex:sliced ?status.
    }}
    """
    status = g.query(slice_query)

    for s in status:
        if s.status:

            print(f"{obj} already sliced!")

        else:
            clean_query = f"""
            PREFIX ex: <http://example.org/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            SELECT ?status ?cstatus ?loc_name
            WHERE {{
                    ex:{obj} ex:IsCleaned ?status.
                    ex:{obj} ex:obj_location ?loc.
                    ex:{obj} ex:NeedsToBeCleaned ?cstatus.
                    ?loc ex:rec_name ?loc_name.
            }}
            """
            status = g.query(clean_query)

            for s in status:

                if not s.status and s.cstatus:                
                    clean(obj, onto_file)
                    onto_file = "updated_onto.ttl"
                    g = rdflib.Graph()
                    g.parse("updated_onto.ttl", format='turtle')

                else:
                    pass

            
            status = g.query(clean_query)
            for s in status:
                locc = str(s.loc_name)

            if locc!=common_recep(onto_file):
                pick_up_obj(obj, onto_file)
                put_down_obj(obj, random.sample(slice_boards,1)[0])
            
            else:
                # print(f"cleaned {obj} already at countertop")
                pass

            
            pick_up_tool(tool, "updated_onto.ttl")
            move(random.sample(slice_boards,1)[0], "updated_onto.ttl")
            print(f"{obj} sliced!")
            put_down_tool(tool, common_recep(onto_file))
            
            g = rdflib.Graph()
            g.parse("updated_onto.ttl", format='turtle')

            delete_query = f"""
            PREFIX ex: <http://example.org/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            DELETE WHERE {{
                    ex:{obj} ex:sliced false.
            }}
            """

            # Execute the delete query
            g.update(delete_query)

            insert_query = f"""
            PREFIX ex: <http://example.org/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            INSERT DATA {{
                ex:{obj} ex:sliced true.
            }}
            """

            g.update(insert_query)
            g.serialize(destination="updated_onto.ttl", format="turtle")

    

def boil(obj, onto_file):

    g = rdflib.Graph()
    g.parse(onto_file, format='turtle')


    O, R, T, IM = fetch_details(onto_file)
    A = O+R+T+IM

    if obj not in A:
        raise RuntimeError(f"boil({obj}, {onto_file}) #{obj} is not present in the environment!")
    elif obj in R+T+IM:
        print(f"{obj} cant be boiled! skipping this action")
        return False
    
    u_query = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?rec_name
    WHERE {{
        ?rec ex:boiling_utensil true.
        ?rec ex:rec_name ?rec_name.
    }}
    """

    b_utensil = g.query(u_query)

    for f in b_utensil:
        utensil = str(f.rec_name)

    obj_query = """
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?obj_name
    WHERE {
        ?object rdf:type ex:object.
        ?object ex:Boilable true.
        ?object ex:obj_name ?obj_name.
    }
    """
    objs = g.query(obj_query)
    obj_list = []
    for o in objs:
        obj_list.append(str(o.obj_name))

    if obj not in obj_list:

       print(f"{obj} is not boilable! skipping this action")
       return False
    

    boil_query = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?status ?loc_name
    WHERE {{
        ex:{obj} ex:IsBoiled ?status.
        ex:{obj} ex:obj_location ?loc.
        ?loc ex:rec_name ?loc_name.
    }}
    """

    boil = g.query(boil_query)

    for b in boil:
        locc = str(b.loc_name)
        if b.status:
            print(f"{obj} already boiled!")

        else:
            IsL_query = f"""
            PREFIX ex: <http://example.org/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            SELECT ?status 
            WHERE {{
                ex:{obj} ex:IsLiquid ?status.
            }}
            """
            IsL = g.query(IsL_query)

            for i in IsL:

                if i.status:

                    pick_up_rec(utensil, onto_file)
                    put_down_rec(utensil, "stove")
                    put_down_obj(obj, utensil)
                    switch("stove", "updated_onto.ttl")


                else:
                                    
                    pick_up_rec(utensil, onto_file)
                    put_down_rec(utensil, "stove")
                    put_down_obj("water", utensil)
                    put_down_obj(obj, utensil)
                    switch("stove", "updated_onto.ttl")



            g = rdflib.Graph()
            g.parse("updated_onto.ttl", format='turtle')

            delete_query = f"""
            PREFIX ex: <http://example.org/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            DELETE WHERE {{
                    ex:{obj} ex:IsBoiled false.
            }}
            """

            # Execute the delete query
            g.update(delete_query)

            insert_query = f"""
            PREFIX ex: <http://example.org/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            INSERT DATA {{
                ex:{obj} ex:IsBoiled true.
            }}
            """

            g.update(insert_query)
            g.serialize(destination="updated_onto.ttl", format="turtle")

            print(f"{obj} is boiled!")



def fry(obj, onto_file):

    g = rdflib.Graph()
    g.parse(onto_file, format='turtle')

    O, R, T, IM = fetch_details(onto_file)
    A = O+R+T+IM

    if obj not in A:
        raise RuntimeError(f"fry({obj}, {onto_file}) #{obj} is not present in the environment!")
    elif obj in R+T+IM:
        print(f"{obj} cant be fried! skipping this action")
        return False
    
    u_query = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?rec_name
    WHERE {{
        ?rec ex:frying_utensil true.
        ?rec ex:rec_name ?rec_name.
    }}
    """

    fry_utensil = g.query(u_query)

    for f in fry_utensil:
        utensil = str(f.rec_name)
    
    obj_query = """
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?obj_name
    WHERE {
        ?object rdf:type ex:object.
        ?object ex:Fryable true.
        ?object ex:obj_name ?obj_name.
    }
    """
    objs = g.query(obj_query)
    obj_list = []
    for o in objs:
        obj_list.append(str(o.obj_name))

    if obj not in obj_list:

        print(f"{obj} is not Fryable! skipping this action")
        return False
    

    fry_query = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?status ?loc_name
    WHERE {{
        ex:{obj} ex:IsFried ?status.
        ex:{obj} ex:obj_location ?loc.
        ?loc ex:rec_name ?loc_name.
    }}
    """

    fry = g.query(fry_query)

    for f in fry:
        locc = str(f.loc_name)
        if f.status:
            print(f"{obj} already fried!")

        else:
          
            pick_up_rec(utensil, onto_file)
            put_down_rec(utensil, "stove")
            put_down_obj("oil", utensil)
            put_down_obj(obj, utensil)
            switch("stove", "updated_onto.ttl")

            g = rdflib.Graph()
            g.parse("updated_onto.ttl", format='turtle')

            delete_query = f"""
            PREFIX ex: <http://example.org/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            DELETE WHERE {{
                    ex:{obj} ex:IsFried false.
            }}
            """

            # Execute the delete query
            g.update(delete_query)

            insert_query = f"""
            PREFIX ex: <http://example.org/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            INSERT DATA {{
                ex:{obj} ex:IsFried true.
            }}
            """

            g.update(insert_query)
            g.serialize(destination="updated_onto.ttl", format="turtle")

            print(f"{obj} Fried!")


def mix_contents(rec, onto_file):

    g = rdflib.Graph()
    g.parse(onto_file, format='turtle')

    O, R, T, IM = fetch_details(onto_file)
    A = O+R+T+IM

    if rec not in A:
        raise RuntimeError(f"mix_contents({rec}, {onto_file}) #{rec} is not present in the environment!")
    if rec in O+T+IM:
        raise RuntimeError(f"mix_contents({rec}, {onto_file}) #Invalid action!")

    IsStirred = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?status
    WHERE {{
            ex:{rec} ex:ContStirred ?status
    }}
    """
    sss = g.query(IsStirred)
    for s in sss:
        if s.status:
            print(f"contents of {rec} already stirred!")
            return False
    
    content_query = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?obj_name
    WHERE {{
        ?object ex:obj_location ex:{rec}.
        ?object ex:obj_name ?obj_name.
    }}
    """
    cts = g.query(content_query)
    contents = []
    for c in cts:
        contents.append(str(c.obj_name))

    if not contents:

        cp_query = f"""
        PREFIX ex: <http://example.org/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?obj_name
        WHERE {{
            ?obj rdf:type ex:object.
            ?obj ex:IsBig false.
            ?obj ex:obj_location ex:{common_recep(onto_file)}.
            ?obj ex:obj_name ?obj_name
        }}
        """
        obj_on_countertop = []
        tquery = g.query(cp_query)
        for t in tquery:
            obj_on_countertop.append(str(t.obj_name))

        in_hand_query = f"""
        PREFIX ex: <http://example.org/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?obj_name
        WHERE {{
            ex:robot ex:obj_in_hand ?obj.
            ?obj ex:obj_name ?obj_name.
        }}
        """
        obj_in_hand= []
        inhand = g.query(in_hand_query)
        for t in inhand:
            obj_in_hand.append(str(t.obj_name))

        for o in obj_on_countertop + obj_in_hand:
            put_down_obj(o, rec)

        if not obj_on_countertop + obj_in_hand:
            raise RuntimeError(f"mix_contents({rec}, {onto_file}) #{rec} is empty!")
        else:
            print(f"contents of {rec} are {obj_on_countertop+obj_in_hand}")

    else:
        print(f"contents of {rec} are {contents}")

    
    g = rdflib.Graph()
    g.parse("updated_onto.ttl", format='turtle')

    delete_query = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    DELETE WHERE {{
            ex:{rec} ex:ContStirred false.
    }}
    """

    # Execute the delete query
    g.update(delete_query)

    insert_query = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    INSERT DATA {{
        ex:{rec} ex:ContStirred true.
    }}
    """

    g.update(insert_query)
    g.serialize(destination="updated_onto.ttl", format="turtle")

    print(f"contents of {rec} are mixed!")


def pour_contents(from_rec, to_rec):

    g = rdflib.Graph()
    g.parse("updated_onto.ttl", format='turtle')

    O, R, T, IM = fetch_details("updated_onto.ttl")
    A = R + IM

    if from_rec in O:
        put_down_obj(from_rec, to_rec)
        return True
    elif from_rec in T:
        put_down_tool(from_rec, to_rec)
        return True
    
    if to_rec in O+T:
        raise RuntimeError(f"pour_contents({from_rec}, {to_rec}) #contents are only poured to a receptacle! {to_rec} is not a receptacle")
    
    if from_rec not in R:
        raise RuntimeError(f"pour_contents({from_rec}, {to_rec}) #{from_rec} is not a valid receptacle for this action!")
    
    if to_rec not in R:
        raise RuntimeError(f"pour_contents({from_rec}, {to_rec}) #{to_rec} is not a valid receptacle for this action!")
    

    content_query = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?obj_name
    WHERE {{
        ?object ex:obj_location ex:{from_rec}.
        ?object ex:obj_name ?obj_name.
    }}
    """
    cts = g.query(content_query)
    contents = []
    for c in cts:
        contents.append(str(c.obj_name))

    if not contents:
        print(f"{from_rec} is empty! skipping this action.")
        return False

    open_rec_query = """
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?place_name
    WHERE {
        ?place ex:open_rec true.
        ?place ex:rec_name ?place_name.
        }
    """

    rq = g.query(open_rec_query)
    orplaces = []

    for p in rq:
        orplaces.append(str(p.place_name))

    serve_query = """
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?place_name
    WHERE {
        ?place ex:serving_place true.
        ?place ex:rec_name ?place_name.
        }
    """

    sp = g.query(serve_query)
    splaces = []

    for p in sp:
        splaces.append(str(p.place_name))


    loc_query = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?rec_name
    WHERE {{
        <http://example.org/{to_rec}> ex:mrec_location ?rec.
        ?rec ex:rec_name ?rec_name.
    }}
    """
    locn = g.query(loc_query)

    for o in locn:
        loc_locn = str(o.rec_name)

    if loc_locn not in orplaces and loc_locn not in R:
        put_down_rec(to_rec, common_recep("updated_onto.ttl"))
        put_down_rec(from_rec, common_recep("updated_onto.ttl"))
    
    else:       
        put_down_rec(from_rec, loc_locn)
        

    g = rdflib.Graph()
    g.parse("updated_onto.ttl", format='turtle')
     
    
    for c in contents:

        delete_query = f"""
        PREFIX ex: <http://example.org/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        DELETE WHERE {{
                ex:{c} ex:obj_location ex:{from_rec}.
        }}
        """

        # Execute the delete query
        g.update(delete_query)

        insert_query = f"""
        PREFIX ex: <http://example.org/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        INSERT DATA {{
            ex:{c} ex:obj_location ex:{to_rec}.
        }}
        """

        g.update(insert_query)

    g.serialize(destination="updated_onto.ttl", format="turtle")
    
    print(f"contents of {from_rec} are {contents}")
    print(f"contents of {from_rec} poured to {to_rec} ")




def stir_contents(rec, onto_file):

    g = rdflib.Graph()
    g.parse(onto_file, format='turtle')

    O, R, T, IM = fetch_details(onto_file)
    A = O+R+T+IM

    if rec not in A:
        raise RuntimeError(f"stir_contents({rec}, {onto_file}) #{rec} is not present in the environment!")
    if rec in O+T+IM:
        raise RuntimeError(f"stir_contents({rec}, {onto_file}) #Invalid action!")


    IsStirred = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?status
    WHERE {{
            ex:{rec} ex:ContStirred ?status
    }}
    """
    sss = g.query(IsStirred)
    for s in sss:
        if s.status:
            print(f"contents of {rec} already stirred!")
            return False
        
    
    content_query = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?obj_name
    WHERE {{
        ?object ex:obj_location ex:{rec}.
        ?object ex:obj_name ?obj_name.
    }}
    """
    cts = g.query(content_query)
    contents = []
    for c in cts:
        contents.append(str(c.obj_name))

    if not contents:
        cp_query = f"""
        PREFIX ex: <http://example.org/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?obj_name
        WHERE {{
            ?obj rdf:type ex:object.
            ?obj ex:IsBig false.
            ?obj ex:obj_location ex:{common_recep(onto_file)}.
            ?obj ex:obj_name ?obj_name
        }}
        """
        obj_on_countertop = []
        tquery = g.query(cp_query)
        for t in tquery:
            obj_on_countertop.append(str(t.obj_name))


        in_hand_query = f"""
        PREFIX ex: <http://example.org/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?obj_name
        WHERE {{
            ex:robot ex:obj_in_hand ?obj.
            ?obj ex:obj_name ?obj_name.
        }}
        """
        obj_in_hand= []
        inhand = g.query(in_hand_query)
        for t in inhand:
            obj_in_hand.append(str(t.obj_name))

        for o in obj_on_countertop + obj_in_hand:
            put_down_obj(o, rec)

        

        if not obj_on_countertop + obj_in_hand:
            raise RuntimeError(f"stir_contents({rec}, {onto_file}) #{rec} is empty!")
        
        else:
            print(f"contents of {rec} are {obj_on_countertop+obj_in_hand}")

    else:
        print(f"contents of {rec} are {contents}")

    g = rdflib.Graph()
    g.parse("updated_onto.ttl", format='turtle')

    delete_query = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    DELETE WHERE {{
            ex:{rec} ex:ContStirred false.
    }}
    """

    # Execute the delete query
    g.update(delete_query)

    insert_query = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    INSERT DATA {{
        ex:{rec} ex:ContStirred true.
    }}
    """

    g.update(insert_query)
    g.serialize(destination="updated_onto.ttl", format="turtle")

    print(f"contents of {rec} are stirred!")


def wait(t):
    if not str(t).isdigit():
        return True
    print(f"waiting for {t} minutes")


def switch(rec, onto_file):

    g = rdflib.Graph()
    g.parse(onto_file, format="turtle")

    O, R, T, IM = fetch_details(onto_file)
    A = O+R+T+IM
    
    if rec not in A:
        raise RuntimeError(f"switch({rec}, {onto_file}) #{rec} not present in the environment!")
    
    elif rec in O+T:
        print(f"{rec} not toggleable! skipping this action")
        return False

    
    squery = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?status
    WHERE {{
        ex:{rec} ex:toggleable ?status.
    }}
    """
    sstatus = g.query(squery)

    for s in sstatus:
        if not s.status:
            print(f"{rec} not toggleable! skipping this action")
            return False
        


    move(rec, onto_file)

    g = rdflib.Graph()
    g.parse("updated_onto.ttl", format="turtle")

    query = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?status
    WHERE {{
        ex:{rec} ex:toggleable true.
        ex:{rec} ex:switched_on ?status.
    }}
    """
    status = g.query(query)
    
    for s in status:
        if s.status:

            delete_query = f"""
            PREFIX ex: <http://example.org/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            DELETE WHERE {{
                    ex:{rec} ex:switched_on true.
            }}
            """

            # Execute the delete query
            g.update(delete_query)

            insert_query = f"""
            PREFIX ex: <http://example.org/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            INSERT DATA {{
                ex:{rec} ex:switched_on false.
            }}
            """

            g.update(insert_query)
            g.serialize(destination="updated_onto.ttl", format="turtle")
            print(f"{rec} switched off!")

        else:

            delete_query = f"""
            PREFIX ex: <http://example.org/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            DELETE WHERE {{
                    ex:{rec} ex:switched_on false.
            }}
            """

            # Execute the delete query
            g.update(delete_query)

            insert_query = f"""
            PREFIX ex: <http://example.org/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            INSERT DATA {{
                ex:{rec} ex:switched_on true.
            }}
            """

            g.update(insert_query)
            g.serialize(destination="updated_onto.ttl", format="turtle")
            print(f"{rec} switched on!")

        

def mop(rec, onto_file):

    g = rdflib.Graph()
    g.parse(onto_file, format="turtle")

    O, R, T, IM = fetch_details(onto_file)
    A = O+R+T+IM
    
    if rec not in A:
        raise RuntimeError(f"switch({rec}, {onto_file}) #{rec} not present in the environment!")
    
    elif rec in O+T+R:
        print(f"{rec} cant be mopped! skipping this action")
        return False

    query = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?obj_name
    WHERE {{
        ?obj ex:mopping_material true.
        ?obj ex:obj_name ?obj_name.
    }}
    """
    m = g.query(query)

    for i in m:
        mopping_item = str(i.obj_name)
    
    pick_up_obj(mopping_item, onto_file)
    put_down_obj(mopping_item, rec)
    print(f"agent mopped the {rec} successfully!")

    g = rdflib.Graph()
    g.parse("updated_onto.ttl", format='turtle')

    delete_query = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    DELETE WHERE {{
            ex:{rec} ex:IsMopped false.
    }}
    """

    # Execute the delete query
    g.update(delete_query)

    insert_query = f"""
    PREFIX ex: <http://example.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    INSERT DATA {{
        ex:{rec} ex:IsMopped true.
    }}
    """

    g.update(insert_query)
    g.serialize(destination="updated_onto.ttl", format="turtle")

        
