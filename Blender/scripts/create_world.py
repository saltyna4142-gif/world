import bpy
import math
import random
from mathutils import Vector, noise

# Infinite 3D World — Day 01
# Blender 4.x | Procedural floating island starter scene

random.seed(14)

# Reset scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials):
    pass

def material(name, color, roughness=0.85):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = roughness
    return mat

grass = material("Moss • deep green", (0.12, 0.28, 0.16))
grass_light = material("Meadow • fresh green", (0.30, 0.48, 0.22))
soil = material("Island • warm earth", (0.20, 0.105, 0.065))
stone = material("Stone • slate", (0.22, 0.27, 0.29))
wood = material("Timber • cedar", (0.28, 0.12, 0.055))
roof_mat = material("Roof • terracotta", (0.36, 0.095, 0.055))
glass = material("Windows • blue glass", (0.12, 0.30, 0.38), 0.3)
leaf = material("Canopy • pine", (0.08, 0.24, 0.13))
leaf2 = material("Canopy • sunlit", (0.20, 0.36, 0.16))
path_mat = material("Path • pale gravel", (0.55, 0.43, 0.29))

# Height-field island with a softened edge
verts, faces = [], []
N, SIZE = 65, 20.0
for j in range(N):
    y = -SIZE / 2 + SIZE * j / (N - 1)
    for i in range(N):
        x = -SIZE / 2 + SIZE * i / (N - 1)
        edge = max(abs(x), abs(y)) / (SIZE / 2)
        fade = max(0.0, 1.0 - edge ** 5)
        n1 = noise.multi_fractal(Vector((x * 0.22, y * 0.22, 1.7)), 1.0, 2.0, 4)
        n2 = noise.noise_vector(Vector((x * 0.48, y * 0.48, 4.2))).z
        z = 1.0 + fade * (0.65 * n1 + 0.32 * n2)
        verts.append((x, y, z))
for j in range(N - 1):
    for i in range(N - 1):
        a = j * N + i
        faces.append((a, a + 1, a + N + 1, a + N))
mesh = bpy.data.meshes.new("Island terrain mesh")
mesh.from_pydata(verts, [], faces)
mesh.materials.append(grass)
island = bpy.data.objects.new("01 • Living island", mesh)
bpy.context.collection.objects.link(island)
for poly in mesh.polygons:
    poly.use_smooth = True
solid = island.modifiers.new("Deep earth beneath the meadow", "SOLIDIFY")
solid.thickness = 2.2
solid.offset = -1
bevel = island.modifiers.new("Soft eroded edges", "BEVEL")
bevel.width = 0.12
bevel.segments = 2

# Layered rocky underside
bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, location=(0, 0, -1.15))
under = bpy.context.object
under.name = "02 • Floating rocky heart"
under.scale = (9.1, 8.8, 2.3)
under.data.materials.append(soil)
for p in under.data.polygons: p.use_smooth = True

# Small cabin
def cube_obj(name, loc, scale, mat, bevel=0.04):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new("Rounded handmade edges", "BEVEL")
        mod.width, mod.segments = bevel, 2
        obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    return obj

cube_obj("03 • Cabin walls", (1.0, 1.2, 2.05), (3.0, 2.5, 2.0), wood)
# Gabled roof as a simple ridge mesh
roof_verts = [(-0.8,-0.2,3.0),(2.8,-0.2,3.0),(1.0,-0.2,4.15),
              (-0.8,2.6,3.0),(2.8,2.6,3.0),(1.0,2.6,4.15)]
roof_faces = [(0,1,2),(3,5,4),(0,2,5,3),(2,1,4,5),(0,3,4,1)]
rm = bpy.data.meshes.new("Cabin roof mesh"); rm.from_pydata(roof_verts, [], roof_faces); rm.materials.append(roof_mat)
ro = bpy.data.objects.new("04 • Pitched terracotta roof", rm); bpy.context.collection.objects.link(ro)
# Door and front windows
cube_obj("Cabin door", (1.0, -0.075, 1.55), (0.65, 0.12, 1.15), soil, 0.025)
for wx in (0.0, 2.0):
    cube_obj("Blue cabin window", (wx, -0.09, 2.25), (0.48, 0.10, 0.55), glass, 0.025)

# Pine trees
def make_tree(x, y, scale=1.0):
    ground_z = 1.0
    trunk_h = 1.0 * scale
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.13*scale, depth=trunk_h,
                                        location=(x, y, ground_z + trunk_h/2))
    trunk = bpy.context.object; trunk.name = "Pine • trunk"; trunk.data.materials.append(wood)
    for k, (h, r, zoff) in enumerate(((1.05,0.72,0.75),(0.85,0.58,1.35),(0.65,0.42,1.9))):
        bpy.ops.mesh.primitive_cone_add(vertices=9, radius1=r*scale, radius2=0,
                                        depth=h*scale, location=(x,y,ground_z+(zoff+0.35)*scale))
        crown = bpy.context.object; crown.name = "Pine • evergreen crown"
        crown.data.materials.append(leaf if k != 1 else leaf2)

for x, y, s in [(-6,-4,1.2),(-7,1,0.9),(-4,5,1.0),(5,5,1.15),(7,1,0.85),(6,-5,1.1),(-2,-7,0.8)]:
    make_tree(x, y, s)

# Winding gravel path made from stepping stones
for idx in range(18):
    t = idx / 17
    x = -5.0 + t * 5.2
    y = -5.0 + t * 4.0 + math.sin(t * math.pi * 2) * 0.35
    bpy.ops.mesh.primitive_cylinder_add(vertices=7, radius=0.23, depth=0.07,
                                        location=(x, y, 1.12))
    pebble = bpy.context.object; pebble.name = "Path • stepping stone"
    pebble.scale.x = random.uniform(0.8,1.35); pebble.scale.y = random.uniform(0.7,1.2)
    pebble.data.materials.append(path_mat)

# Scattered boulders
for x,y,s in [(-8,-1,0.7),(8,3,0.8),(-3,7,0.55),(4,-7,0.65)]:
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=s, location=(x,y,1.0+s*0.25))
    rock = bpy.context.object; rock.name = "Meadow • boulder"; rock.data.materials.append(stone)

# Lighting, world, camera
world = bpy.data.worlds.new("Soft blue morning") if not bpy.data.worlds else bpy.data.worlds[0]
bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.20,0.29,0.42,1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.45

bpy.ops.object.light_add(type='AREA', location=(1,-8,13))
key = bpy.context.object; key.name = "Morning • large softbox"; key.data.energy = 1700; key.data.shape='DISK'; key.data.size=9
key.rotation_euler = (math.radians(25),0,math.radians(-8))
bpy.ops.object.light_add(type='SUN', location=(-6,4,9))
sun = bpy.context.object; sun.name="Morning • sun"; sun.data.energy=1.2
sun.rotation_euler=(math.radians(25),math.radians(-25),math.radians(-35))

bpy.ops.object.camera_add(location=(23,-30,22))
cam=bpy.context.object; cam.name="World • presentation camera"
target=Vector((0,0,0.8)); cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO'; cam.data.ortho_scale=31
scene=bpy.context.scene; scene.camera=cam
scene.render.engine='BLENDER_EEVEE_NEXT'
scene.eevee.taa_render_samples=64
scene.render.resolution_x=1400; scene.render.resolution_y=1050; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'
scene.render.filepath='//Screenshots/day01_floating_island.png'

# Helpful viewport framing
bpy.context.view_layer.objects.active=island
island.select_set(True)
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        area.spaces.active.region_3d.view_distance=30

print("Infinite 3D World — Day 01 scene created. Save as world.blend and render with F12.")
