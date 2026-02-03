# cloudcompare.CloudCompare -SILENT \
#     -O lake-wheeler.las \
#     -OCTREE_NORMALS 1.488 \
#     -ORIENT PLUS_Z \
#     -SAVE_MESHES FILE lake-wheeler-normals.ply

# cloudcompare.CloudCompare -SILENT \
#     -O lake-wheeler_OCTREE_NORMALS_2025-12-12_12h56_37_556.bin
#     -DELAUNAY BEST_FIT \
#     -SAVE_MESHES FILE lake-wheeler-triangulation.ply

cloudcompare.CloudCompare -SILENT \
    -O lake-wheeler.las \
    -OCTREE_NORMALS 1.488 \
    -ORIENT PLUS_Z \
    -DELAUNEY BEST_FIT \
    -PCD_OUTPUT_FORMAT ASCII \
    -SAVE_MESHES FILE lake-wheeler-triangulation.ply 
