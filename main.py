import sys
import os
import utils_ws as ut
from loguru import logger
import pymeshlab
import time
import mitsuba as mi

from mesh_meshlab2mitsuba import getMitsubaMesh


isDebug = True if sys.gettrace() else False

if __name__ == '__main__':
    ut.initLog()

    logger.info("================================")

    highModelPath = os.path.join(r"D:\assets\suzanne.obj")

    start_time = time.time()
    meshSet = pymeshlab.MeshSet()
    # load high mesh
    meshSet.load_new_mesh(highModelPath)
    highMesh = meshSet.current_mesh()
    highMeshGeometric = meshSet.get_geometric_measures()

    vertNum = highMesh.vertex_number()
    faceNum = highMesh.face_number()
    logger.info(f'{highModelPath} has {vertNum} verts, {faceNum} faces.')

    meshSet.meshing_poly_to_tri()  # 先转换为纯三角网格
    # 减面之前先对模型做一次清理
    # meshSet.meshing_merge_close_vertices()  # threshold value is 1/10000 of bounding box diagonal
    meshSet.meshing_remove_duplicate_vertices()
    meshSet.meshing_remove_duplicate_faces()
    meshSet.meshing_remove_folded_faces()
    meshSet.meshing_remove_null_faces()
    meshSet.meshing_remove_unreferenced_vertices()

    vertNumPurified = highMesh.vertex_number()
    faceNumPurified = highMesh.face_number()
    logger.info(f'After cleaning: now {highModelPath} has {vertNumPurified} verts, {faceNumPurified} faces.')

    #####################
    # Set the variant of the renderer
    mi.set_variant('scalar_rgb')
    # Load a scene
    # scene = mi.load_dict(mi.cornell_box())

    from mitsuba import ScalarTransform4f as T

    vertexMatrix = highMesh.vertex_matrix()
    faceMatrix = highMesh.face_matrix()

    scene = getMitsubaMesh( vertexMatrix.reshape(-1), faceMatrix.reshape(-1) );

    sensor = mi.load_dict({
        'type': 'perspective',
        'fov': 45,
        'to_world': T.look_at(target=[0, 0, 0], origin=[2.47, -2.46, 2.5], up=[-0.45, 0.43, 0.78]),
        'film': {
            'type': 'hdrfilm',
            'width': 128, 'height': 128,
            'filter': {'type': 'gaussian'},
            'sample_border': True,
        },
        'sampler': {
            'type': 'independent',
            'sample_count': 128
        },
    })

    if isDebug:
        params = mi.traverse(scene)
        print(params)

    # Render the scene
    img = mi.render(scene, sensor=sensor)

    duration = time.time() - start_time

    logger.info(f'Duration = {duration}')

    mi.util.write_bitmap("my_first_render.png", img)
    # mi.util.write_bitmap("my_first_render.exr", img)


    sys.exit(0)