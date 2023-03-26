import pymesh
import numpy as np

def closest_face_deets(mesh, point):
    """
    Returns the closest face and its distance from a point
    """
    (squared_distances, face_indicies, closest_points) = pymesh.distance_to_mesh(mesh, point, engine="cgal")
    print("Closest face: {}".format(face_indicies[0]))
    print("Closest point: {}".format(closest_points))
    p1 = mesh.vertices[mesh.faces[face_indicies[0]][0]]
    p2 = mesh.vertices[mesh.faces[face_indicies[0]][1]]
    p3 = mesh.vertices[mesh.faces[face_indicies[0]][2]]
 
    magic_normal = np.cross(p2-p1, p3-p1)

    print("Magic normal: {}".format(magic_normal))

def get_cylinder_positions(moon_pos, com=False):
    # first normalise the moon position
    moon_pos_norm = moon_pos / np.linalg.norm(moon_pos)
    print("Moon pos norm: {}".format(moon_pos_norm))

    if com:
        inner_offset = 45
        outer_offset = 60
    else:
        inner_offset = 30
        outer_offset = 55

    cylinder_inner_point = moon_pos_norm * inner_offset
    print("cylinder_inner_point: {}".format(cylinder_inner_point))

    cylinder_outer_point = moon_pos_norm * outer_offset
    print("cylinder_outer_point: {}".format(cylinder_outer_point))

    return (cylinder_inner_point, cylinder_outer_point)



if __name__ == "__main__":
    moons = [np.array([369.1031776200334,-224.75639891013353,-323.8014907620764]),
            np.array([-43.084537066117655,-526.0828802247278,113.93211048801389]),
            np.array([317.7630114827334,-416.59894242101916,130.65982438038333]),
            np.array([255.2775989814185,143.04441243122423,226.43242596962094]),
            np.array([-91.31365635719341,200.02072888127825,-297.57944179745107]),
            np.array([258.4431641526227,248.53054256854284,-91.32195964479827]),
            np.array([-260.7443757907106,262.5035322951634,2.0654360495626647])
            ]


    com = np.array([92.3350327678572,-142.8676159017393,-14.370385005296756])

    sphere = pymesh.generate_icosphere(50, np.array([0.0,0.0,0.0]), 8)

    output_mesh = sphere

    for moon in moons:
        (cylinder_inner_point, cylinder_outer_point) = get_cylinder_positions(moon)
        mesh_C = pymesh.generate_cylinder(cylinder_inner_point, cylinder_outer_point, 10.25 / 2 , 10.25 / 2, num_segments=32)

        output_mesh = pymesh.boolean(output_mesh, mesh_C,
                                operation="difference",
                                engine="igl")
        
    # deal with the com
    (cylinder_inner_point, cylinder_outer_point) = get_cylinder_positions(com, com=True)
    mesh_C = pymesh.generate_cylinder(cylinder_inner_point, cylinder_outer_point, 50 , 50, num_segments=32)

    output_mesh = pymesh.boolean(output_mesh, mesh_C,
                                operation="difference",
                                engine="igl")

    pymesh.save_mesh("output.obj", output_mesh)

