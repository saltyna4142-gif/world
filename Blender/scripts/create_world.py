import bpy
import math
import random
from mathutils import Vector, noise

# Infinite 3D World — Day 03
# Blender 4.x | Floating island, creek, waterfall and cedar footbridge
# Blender 4.x | Floating island with a creek and waterfall

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
water_mat = material("Water • clear turquoise", (0.025, 0.22, 0.30), 0.22)
water_mat.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.12
foam_mat = material("Water • pale foam", (0.34, 0.72, 0.76), 0.28)

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

# Creek, waterfall and a small plunge pool — Day 02
# Sample the same procedural height field so the creek rests on the existing terrain.
def terrain_height(x, y):
    edge = max(abs(x), abs(y)) / (SIZE / 2)
    fade = max(0.0, 1.0 - edge ** 5)
    n1 = noise.multi_fractal(Vector((x * 0.22, y * 0.22, 1.7)), 1.0, 2.0, 4)
    n2 = noise.noise_vector(Vector((x * 0.48, y * 0.48, 4.2))).z
    return 1.0 + fade * (0.65 * n1 + 0.32 * n2)

def make_water_curve(name, points, thickness, mat):
    curve_data = bpy.data.curves.new(name + " path", "CURVE")
    curve_data.dimensions = "3D"
    curve_data.resolution_u = 16
    curve_data.bevel_depth = thickness
    curve_data.bevel_resolution = 5
    curve_data.use_fill_caps = True
    spline = curve_data.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for point, co in zip(spline.points, points):
        point.co = (co[0], co[1], co[2], 1.0)
    obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj

creek_xy = [
    (3.5, 3.8), (4.7, 2.8), (5.8, 1.5),
    (6.9, 0.2), (7.8, -0.9), (8.7, -1.8), (9.45, -2.4)
]
creek_points = [(x, y, terrain_height(x, y) + 0.10) for x, y in creek_xy]
make_water_curve("Water • winding island creek", creek_points, 0.20, water_mat)
make_water_curve(
    "Water • narrow sunlit ripple",
    [(x, y - 0.07, z + 0.12) for x, y, z in creek_points[1:-1]],
    0.028,
    foam_mat
)

# A gently folded vertical ribbon carries the creek over the island's front-right rim.
fall_centers = [
    (9.25, -2.47, terrain_height(9.25, -2.47) + 0.06),
    (9.55, -2.52, 0.34),
    (9.78, -2.56, -0.42),
    (9.76, -2.60, -1.30),
    (9.48, -2.63, -2.20),
    (9.14, -2.66, -3.02)
]
fall_widths = [0.62, 0.70, 0.58, 0.68, 0.56, 0.46]
water_verts, water_faces = [], []
for (x, y, z), width in zip(fall_centers, fall_widths):
    water_verts.extend([
        (x - width * 0.5, y, z),
        (x + width * 0.5, y + 0.045, z)
    ])
for i in range(len(fall_centers) - 1):
    a = i * 2
    water_faces.append((a, a + 1, a + 3, a + 2))

fall_mesh = bpy.data.meshes.new("Waterfall flowing ribbon mesh")
fall_mesh.from_pydata(water_verts, [], water_faces)
fall_mesh.materials.append(water_mat)
waterfall = bpy.data.objects.new("Water • island-edge waterfall", fall_mesh)
bpy.context.collection.objects.link(waterfall)
fall_solid = waterfall.modifiers.new("Thin flowing water sheet", "SOLIDIFY")
fall_solid.thickness = 0.035
for poly in fall_mesh.polygons:
    poly.use_smooth = True

# A soft turquoise pool and a few droplets make the landing point readable.
bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, location=(8.75, -2.72, -3.12))
pool = bpy.context.object
pool.name = "Water • plunge pool"
pool.scale = (1.25, 0.92, 0.19)
pool.data.materials.append(water_mat)
for poly in pool.data.polygons:
    poly.use_smooth = True

rng = random.Random(205)
for idx in range(8):
    radius = rng.uniform(0.045, 0.09)
    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=1,
        radius=radius,
        location=(
            8.85 + rng.uniform(-0.65, 0.65),
            -2.85 + rng.uniform(-0.35, 0.28),
            -2.88 + rng.uniform(-0.24, 0.22)
        )
    )
    droplet = bpy.context.object
    droplet.name = "Water • splash droplet"
    droplet.data.materials.append(foam_mat)

# Small cedar footbridge across the creek — Day 03
# The bridge crosses the existing stream near its bend, using the same terrain sampler.
bridge_cx, bridge_cy = 6.35, 0.85
bridge_angle = math.radians(40.0)
bridge_ux, bridge_uy = math.cos(bridge_angle), math.sin(bridge_angle)
bridge_vx, bridge_vy = -bridge_uy, bridge_ux
bridge_deck_z = terrain_height(bridge_cx, bridge_cy) + 0.62

def bridge_position(along, across, z):
    return (
        bridge_cx + bridge_ux * along + bridge_vx * across,
        bridge_cy + bridge_uy * along + bridge_vy * across,
        z
    )

# Two cedar stringers carry the deck above the water.
for side in (-0.48, 0.48):
    beam = cube_obj(
        "Bridge • cedar stringer",
        bridge_position(0.0, side, bridge_deck_z - 0.10),
        (3.55, 0.18, 0.20), wood, 0.035
    )
    beam.rotation_euler.z = bridge_angle

# Closely spaced cross-planks form a readable wooden walking surface.
for idx in range(11):
    along = -1.55 + idx * 0.31
    plank = cube_obj(
        "Bridge • weathered deck plank",
        bridge_position(along, 0.0, bridge_deck_z + 0.035),
        (1.16, 0.31, 0.07), wood, 0.018
    )
    plank.rotation_euler.z = bridge_angle + math.pi / 2

# Four short stone-side supports visually anchor the bridge to both banks.
for along in (-1.52, 1.52):
    for across in (-0.48, 0.48):
        px, py, _ = bridge_position(along, across, 0.0)
        bank_z = terrain_height(px, py)
        support_h = max(0.18, bridge_deck_z - 0.20 - bank_z)
        cube_obj(
            "Bridge • timber bank support",
            (px, py, bank_z + support_h * 0.5),
            (0.17, 0.17, support_h), wood, 0.025
        )

# Low handrails and evenly spaced posts make the crossing feel safe and crafted.
for side in (-0.66, 0.66):
    for along in (-1.62, 0.0, 1.62):
        cube_obj(
            "Bridge • handrail post",
            bridge_position(along, side, bridge_deck_z + 0.47),
            (0.14, 0.14, 0.86), wood, 0.025
        )
    rail = cube_obj(
        "Bridge • cedar handrail",
        bridge_position(0.0, side, bridge_deck_z + 0.89),
        (3.52, 0.13, 0.13), wood, 0.035
    )
    rail.rotation_euler.z = bridge_angle

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
scene.render.filepath='//Screenshots/day02_creek_waterfall.png'

# Helpful viewport framing
bpy.context.view_layer.objects.active=island
island.select_set(True)
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        area.spaces.active.region_3d.view_distance=30

print("Infinite 3D World — Day 02 creek and waterfall added. Save as world.blend and render with F12.")
