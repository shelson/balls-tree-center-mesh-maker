import logging
import json
import pymesh
import numpy as np
import tempfile


import azure.functions as func

def get_cylinder_positions(moon_pos, depth, com=False):
    # first normalise the moon position
    moon_pos_norm = moon_pos / np.linalg.norm(moon_pos)
    print("Moon pos norm: {}".format(moon_pos_norm))

    if com:
        inner_offset = 45
        outer_offset = 60
    else:
        outer_offset = 55
        inner_offset = outer_offset - (depth + 5)
        

    cylinder_inner_point = moon_pos_norm * inner_offset
    logging.info("cylinder_inner_point: {}".format(cylinder_inner_point))

    cylinder_outer_point = moon_pos_norm * outer_offset
    logging.info("cylinder_outer_point: {}".format(cylinder_outer_point))

    return (cylinder_inner_point, cylinder_outer_point)


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if req.method == "OPTIONS":
        logging.info("Got an OPTIONS request")
        resp = func.HttpResponse("", \
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*",
                     "Access-Control-Allow-Headers": "Content-Type",
                     "Access-Control-Allow-Methods": "POST,OPTIONS"},
            status_code=200)
        return resp
    
    else:
        moon_data = None

        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            logging.info("Got a POST request")
            moon_data = req_body.get('moon_data')
            logging.info("Got moon data: {}".format(moon_data))

        if moon_data != None:
            moons = [np.array(moon["position"]) for moon in moon_data.get('moons')]
            masses = [moon["mass"] for moon in moon_data.get('moons')]
            com = np.array(moon_data.get('com'))

            sphere = pymesh.generate_icosphere(50, np.array([0.0,0.0,0.0]), 6)

            for i, moon in enumerate(moons):
                (cylinder_inner_point, cylinder_outer_point) = get_cylinder_positions(moon, 20)
                cylinder= pymesh.generate_cylinder(cylinder_inner_point, cylinder_outer_point, 10.25 / 2 , 10.25 / 2, num_segments=64)

                sphere = pymesh.boolean(sphere, cylinder,
                                    operation="difference",
                                    engine="igl")
                
                logging.info(np.linalg.norm(moon))
                if np.linalg.norm(moon) > 400:
                    (cylinder_inner_point, cylinder_outer_point) = get_cylinder_positions(moon, 0.5)
                    cylinder= pymesh.generate_cylinder(cylinder_inner_point, cylinder_outer_point, 20 , 20, num_segments=4)    

                    sphere = pymesh.boolean(sphere, cylinder,
                                    operation="difference",
                                    engine="igl")
                    
                # make a ring
                if masses[i] > 600:
                    (cylinder_inner_point, cylinder_outer_point) = get_cylinder_positions(moon, 1.5)
                    ring = pymesh.generate_tube(cylinder_inner_point, cylinder_outer_point, 9, 9, 8.5, 8.5, num_segments=64)

                    sphere = pymesh.boolean(sphere, ring,
                                    operation="difference",
                                    engine="igl")

            # deal with the com
            (cylinder_inner_point, cylinder_outer_point) = get_cylinder_positions(com, 15, com=True)
            cylinder = pymesh.generate_cylinder(cylinder_inner_point, cylinder_outer_point, 50 , 50, num_segments=64)

            sphere = pymesh.boolean(sphere, cylinder,
                                    operation="difference",
                                    engine="igl")
            
            with tempfile.NamedTemporaryFile(suffix=".obj") as f:
                pymesh.save_mesh(f.name, sphere, ascii=True)
                with open(f.name, "r") as f2:
                    objdata = f2.read()

            resp = func.HttpResponse(json.dumps({"status": "ok", "objdata": objdata}), \
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*",
                         "Access-Control-Allow-Headers": "Content-Type",
                         "Access-Control-Allow-Methods": "POST,OPTIONS"},
                status_code=200)
            return resp
        else:
            resp = func.HttpResponse(json.dumps({"status": "error", "message": "This HTTP triggered function executed successfully. Send me a POST body next time for amazing magic."}),
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*",
                         "Access-Control-Allow-Headers": "Content-Type",
                         "Access-Control-Allow-Methods": "POST,OPTIONS"},
                status_code=400)
            return resp