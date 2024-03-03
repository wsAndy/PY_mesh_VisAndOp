# https://mitsuba.readthedocs.io/en/latest/src/how_to_guides/mesh_io_and_manipulation.html

# Wavy disk construction
#
# Let N define the total number of vertices, the first N-1 vertices will compose
# the fringe of the disk, while the last vertex should be placed at the center.
# The first N-1 vertices must have their height modified such that they oscillate
# with some given frequency and amplitude. To compute the face indices, we define
# the first vertex of every face to be the vertex at the center (idx=N-1) and the
# other two can be assigned sequentially (modulo N-2).

import mitsuba as mi
import drjit as dr

# Disk with a wavy fringe parameters
def getMitsubaMesh(vv, ff):
    # vertex_pos = mi.Point3f(vv)
    # # Generate the face indices
    # face_indices = mi.Vector3u(ff)

    # Create an empty mesh (allocates buffers of the correct size)
    mesh = mi.Mesh(
        "mesh",
        vertex_count= int(len(vv)/3),
        face_count= int(len(ff)/3),
        has_vertex_normals=False,
        has_vertex_texcoords=False,
    )
    mesh_params = mi.traverse(mesh)
    mesh_params["vertex_positions"] = dr.ravel(vv)
    mesh_params["faces"] = dr.ravel(ff)
    mesh_params.update()

    scene = mi.load_dict({
        "type": "scene",
        "integrator": {"type": "path"},
        "light": {"type": "constant"},
        "mesh": mesh,
    })

    return scene