import bpy
import math
import random
from mathutils import Vector, noise

# Infinite 3D World — Day 09
# Blender 4.x | Floating island, creek, waterfall, cedar footbridge and riverbank flora

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


# Riverbank ferns, moss cushions and small wildflowers — Day 04
# Plants are anchored to the same procedural height field as the original island.
fern_green = material("Fern • deep emerald", (0.055, 0.25, 0.13))
fern_light = material("Fern • fresh leaf tips", (0.18, 0.40, 0.20))
fern_stem_mat = material("Fern • green rachis", (0.12, 0.28, 0.12))
moss_bank_mat = material("Moss • soft riverbank cushions", (0.16, 0.32, 0.13))
flower_lilac = material("Wildflower • pale lilac", (0.55, 0.38, 0.68), 0.62)
flower_gold = material("Wildflower • warm cream", (0.92, 0.72, 0.30), 0.62)

def make_bank_fern(x, y, scale=1.0, seed=0):
    rng = random.Random(seed)
    base_z = terrain_height(x, y) + 0.055
    leaf_verts, leaf_faces, leaf_materials = [], [], []

    # Five arching fronds form one low rosette. Each rosette's leaflets share one mesh.
    for frond_index in range(5):
        angle = (math.tau * frond_index / 5.0) + rng.uniform(-0.16, 0.16)
        dx, dy = math.cos(angle), math.sin(angle)
        side_x, side_y = -dy, dx
        length = scale * rng.uniform(0.58, 0.78)
        stem_points = []
        for step in range(7):
            t = step / 6.0
            px = x + dx * length * t
            py = y + dy * length * t
            pz = base_z + scale * (0.06 + 0.34 * math.sin(math.pi * t * 0.82) - 0.10 * t)
            stem_points.append((px, py, pz))
        make_water_curve(
            "Fern • arching riverbank rachis",
            stem_points,
            0.012 * scale,
            fern_stem_mat
        )

        for leaflet_index in range(1, 6):
            t = leaflet_index / 6.0
            px = x + dx * length * t
            py = y + dy * length * t
            pz = base_z + scale * (0.06 + 0.34 * math.sin(math.pi * t * 0.82) - 0.10 * t)
            leaflet_length = scale * 0.25 * (1.0 - 0.24 * t)
            for side in (-1.0, 1.0):
                sx, sy = side_x * side, side_y * side
                root = (px, py, pz)
                mid = (
                    px + sx * leaflet_length * 0.58 + dx * leaflet_length * 0.12,
                    py + sy * leaflet_length * 0.58 + dy * leaflet_length * 0.12,
                    pz + 0.025 * scale
                )
                tip = (
                    px + sx * leaflet_length + dx * leaflet_length * 0.28,
                    py + sy * leaflet_length + dy * leaflet_length * 0.28,
                    pz + 0.008 * scale
                )
                half_width = leaflet_length * 0.16
                width_x, width_y = dx * half_width, dy * half_width
                first = len(leaf_verts)
                leaf_verts.extend([
                    root,
                    (mid[0] + width_x, mid[1] + width_y, mid[2]),
                    tip,
                    (mid[0] - width_x, mid[1] - width_y, mid[2])
                ])
                leaf_faces.extend([(first, first + 1, first + 2), (first, first + 2, first + 3)])
                material_index = 1 if (frond_index + leaflet_index) % 3 == 0 else 0
                leaf_materials.extend([material_index, material_index])

    leaf_mesh = bpy.data.meshes.new("Fern • paired leaflet mesh")
    leaf_mesh.from_pydata(leaf_verts, [], leaf_faces)
    leaf_mesh.materials.append(fern_green)
    leaf_mesh.materials.append(fern_light)
    for polygon, material_index in zip(leaf_mesh.polygons, leaf_materials):
        polygon.material_index = material_index
    leaf_obj = bpy.data.objects.new("Day 04 • riverbank fern rosette", leaf_mesh)
    bpy.context.collection.objects.link(leaf_obj)

def make_moss_cushion(x, y, sx, sy, seed=0):
    rng = random.Random(seed)
    z = terrain_height(x, y) + 0.055
    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=2,
        radius=1.0,
        location=(x, y, z)
    )
    patch = bpy.context.object
    patch.name = "Day 04 • soft moss cushion"
    patch.scale = (sx, sy, rng.uniform(0.075, 0.12))
    patch.rotation_euler.z = rng.uniform(-0.5, 0.5)
    patch.data.materials.append(moss_bank_mat)

def make_wildflower(x, y, scale=1.0, petal_mat=None, seed=0):
    rng = random.Random(seed)
    base_z = terrain_height(x, y) + 0.06
    stem_height = 0.30 * scale
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=7,
        radius=0.018 * scale,
        depth=stem_height,
        location=(x, y, base_z + stem_height * 0.5)
    )
    stem = bpy.context.object
    stem.name = "Day 04 • wildflower stem"
    stem.data.materials.append(fern_stem_mat)

    head_z = base_z + stem_height
    for petal_index in range(5):
        angle = math.tau * petal_index / 5.0
        petal_x = x + math.cos(angle) * 0.072 * scale
        petal_y = y + math.sin(angle) * 0.072 * scale
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=10,
            ring_count=6,
            radius=1.0,
            location=(petal_x, petal_y, head_z)
        )
        petal = bpy.context.object
        petal.name = "Day 04 • wildflower petal"
        petal.scale = (0.082 * scale, 0.043 * scale, 0.027 * scale)
        petal.rotation_euler.z = angle
        petal.data.materials.append(petal_mat or flower_lilac)

    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=10,
        ring_count=6,
        radius=1.0,
        location=(x, y, head_z + 0.012 * scale)
    )
    center = bpy.context.object
    center.name = "Day 04 • wildflower center"
    center.scale = (0.038 * scale, 0.038 * scale, 0.032 * scale)
    center.data.materials.append(flower_gold)

# Ferns sit on alternating banks, leaving the bridge deck and stream channel readable.
fern_sites = [
    (5.25, 3.50, 0.82),
    (4.05, 2.05, 0.78),
    (6.75, 2.45, 0.76),
    (5.20, -1.40, 0.72),
    (8.55, -0.15, 0.78),
    (7.10, -1.80, 0.76),
    (8.05, -2.95, 0.70)
]
for index, (fx, fy, fs) in enumerate(fern_sites):
    make_bank_fern(fx, fy, fs, seed=410 + index)

# Low moss patches soften the transition between gravel, stones and grass.
moss_sites = [
    (4.75, 3.65, 0.42, 0.27),
    (4.00, 2.65, 0.34, 0.24),
    (6.80, 2.05, 0.38, 0.25),
    (5.45, -1.20, 0.36, 0.24),
    (8.55, -0.85, 0.42, 0.26),
    (7.35, -2.05, 0.35, 0.24),
    (8.35, -3.35, 0.38, 0.25)
]
for index, (mx, my, msx, msy) in enumerate(moss_sites):
    make_moss_cushion(mx, my, msx, msy, seed=430 + index)

# A few restrained lilac and cream flowers add scale without hiding the footbridge.
flower_sites = [
    (3.85, 4.25, 0.90, flower_lilac),
    (3.35, -2.55, 0.82, flower_gold),
    (7.95, 2.95, 0.86, flower_lilac),
    (8.25, -3.85, 0.78, flower_gold),
    (2.95, -4.20, 0.82, flower_lilac)
]
for index, (wx, wy, ws, petal_material) in enumerate(flower_sites):
    make_wildflower(wx, wy, ws, petal_material, seed=450 + index)

# Wooden exploration signpost beside the path to the creek bridge — Day 05
# Placed between the cabin trail and the existing bridge; all heights use the shared terrain sampler.
sign_x, sign_y = 4.05, -0.72
sign_ground_z = terrain_height(sign_x, sign_y) + 0.045
sign_face_mat = material("Signpost • sun-warmed cedar", (0.48, 0.27, 0.12), 0.78)
sign_ink_mat = material("Signpost • dark carved lettering", (0.075, 0.055, 0.035), 0.9)
sign_pin_mat = material("Signpost • aged brass pins", (0.48, 0.30, 0.10), 0.34)

# A low stone footing keeps the timber post visually anchored in the meadow.
bpy.ops.mesh.primitive_ico_sphere_add(
    subdivisions=2,
    radius=1.0,
    location=(sign_x, sign_y, sign_ground_z + 0.13)
)
sign_footing = bpy.context.object
sign_footing.name = "Day 05 • signpost stone footing"
sign_footing.scale = (0.43, 0.36, 0.19)
sign_footing.data.materials.append(stone)

# Upright cedar post with a simple carved cap.
bpy.ops.mesh.primitive_cylinder_add(
    vertices=10,
    radius=0.095,
    depth=2.30,
    location=(sign_x, sign_y, sign_ground_z + 1.23)
)
sign_post = bpy.context.object
sign_post.name = "Day 05 • cedar signpost upright"
sign_post.data.materials.append(wood)
sign_post_bevel = sign_post.modifiers.new("Worn post edges", "BEVEL")
sign_post_bevel.width = 0.025
sign_post_bevel.segments = 2

cube_obj(
    "Day 05 • signpost carved cap",
    (sign_x, sign_y, sign_ground_z + 2.40),
    (0.25, 0.24, 0.12),
    wood,
    0.035
)

def make_direction_board(name, center_z, direction, label):
    # One extruded arrow-shaped board; direction +1 points toward the creek bridge.
    half_height = 0.19
    if direction > 0:
        outline = [
            (-0.82, -half_height), (0.59, -half_height),
            (0.59, -0.31), (1.02, 0.0),
            (0.59, 0.31), (0.59, half_height),
            (-0.82, half_height)
        ]
        text_offset = -0.10
    else:
        outline = [
            (0.82, -half_height), (-0.59, -half_height),
            (-0.59, -0.31), (-1.02, 0.0),
            (-0.59, 0.31), (-0.59, half_height),
            (0.82, half_height)
        ]
        text_offset = 0.10

    depth = 0.14
    board_vertices = []
    for yy in (-depth * 0.5, depth * 0.5):
        for xx, zz in outline:
            board_vertices.append((sign_x + xx, sign_y + yy, center_z + zz))

    count = len(outline)
    board_faces = [tuple(range(count)), tuple(range(count, count * 2))[::-1]]
    for idx in range(count):
        nxt = (idx + 1) % count
        board_faces.append((idx, nxt, count + nxt, count + idx))

    board_mesh = bpy.data.meshes.new(name + " mesh")
    board_mesh.from_pydata(board_vertices, [], board_faces)
    board_mesh.materials.append(sign_face_mat)
    board_obj = bpy.data.objects.new(name, board_mesh)
    bpy.context.collection.objects.link(board_obj)
    board_bevel = board_obj.modifiers.new("Softly worn sign edges", "BEVEL")
    board_bevel.width = 0.025
    board_bevel.segments = 2
    board_obj.modifiers.new("Sign weighted corner normals", "WEIGHTED_NORMAL")

    # Text lies on the front face, facing the presentation camera's general direction.
    text_curve = bpy.data.curves.new(name + " lettering", "FONT")
    text_curve.body = label
    text_curve.align_x = "CENTER"
    text_curve.align_y = "CENTER"
    text_curve.size = 0.19
    text_curve.extrude = 0.002
    text_obj = bpy.data.objects.new(name + " • lettering", text_curve)
    bpy.context.collection.objects.link(text_obj)
    text_obj.location = (sign_x + text_offset, sign_y - depth * 0.5 - 0.008, center_z)
    text_obj.rotation_euler = (math.radians(90), 0.0, 0.0)
    text_obj.data.materials.append(sign_ink_mat)

    # Two small brass pins suggest hand-built joinery without crowding the label.
    for dz in (-0.125, 0.125):
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=10,
            ring_count=6,
            radius=0.027,
            location=(sign_x, sign_y - depth * 0.5 - 0.018, center_z + dz)
        )
        pin = bpy.context.object
        pin.name = name + " • brass fixing"
        pin.scale = (1.0, 0.45, 1.0)
        pin.data.materials.append(sign_pin_mat)

make_direction_board(
    "Day 05 • arrow board toward creek bridge",
    sign_ground_z + 1.88,
    1,
    "BROOK"
)
make_direction_board(
    "Day 05 • arrow board toward cabin",
    sign_ground_z + 1.37,
    -1,
    "CABIN"
)


# A small discovery chest with an open lid and an old trail map — Day 06
# Set beside, but not on, the signpost-to-bridge route. All placement uses the shared terrain sampler.
chest_x, chest_y = 3.18, -1.82
chest_ground_z = terrain_height(chest_x, chest_y) + 0.055
chest_base_z = chest_ground_z

chest_wood = material("Treasure chest • dark walnut", (0.19, 0.075, 0.032), 0.68)
chest_trim = material("Treasure chest • cedar edging", (0.36, 0.17, 0.065), 0.72)
chest_metal = material("Treasure chest • aged bronze", (0.42, 0.25, 0.09), 0.38)
map_paper = material("Old map • warm parchment", (0.72, 0.57, 0.34), 0.92)
map_ink = material("Old map • sepia ink", (0.18, 0.10, 0.045), 0.95)

# Four low feet and a solid floor lift the chest slightly above the meadow.
for dx in (-0.34, 0.34):
    for dy in (-0.22, 0.22):
        cube_obj(
            "Day 06 • chest foot",
            (chest_x + dx, chest_y + dy, chest_base_z + 0.075),
            (0.13, 0.13, 0.15),
            chest_wood,
            0.025
        )

cube_obj(
    "Day 06 • chest bottom",
    (chest_x, chest_y, chest_base_z + 0.14),
    (0.96, 0.66, 0.12),
    chest_wood,
    0.035
)

# Four separate walls leave the top open so the parchment map can be seen.
wall_center_z = chest_base_z + 0.36
cube_obj("Day 06 • chest front wall", (chest_x, chest_y - 0.28, wall_center_z),
         (0.96, 0.10, 0.42), chest_wood, 0.025)
cube_obj("Day 06 • chest rear wall", (chest_x, chest_y + 0.28, wall_center_z),
         (0.96, 0.10, 0.42), chest_wood, 0.025)
for side in (-1, 1):
    cube_obj("Day 06 • chest side wall",
             (chest_x + side * 0.43, chest_y, wall_center_z),
             (0.10, 0.48, 0.42), chest_wood, 0.025)

# Cedar bands decorate the front and sides; bronze plates reinforce the corners.
for dx in (-0.29, 0.0, 0.29):
    cube_obj("Day 06 • front cedar slat",
             (chest_x + dx, chest_y - 0.337, wall_center_z),
             (0.055, 0.025, 0.35), chest_trim, 0.012)
for side in (-1, 1):
    for dy in (-0.16, 0.16):
        cube_obj("Day 06 • bronze corner strap",
                 (chest_x + side * 0.485, chest_y + dy, wall_center_z),
                 (0.025, 0.055, 0.34), chest_metal, 0.008)

# The old map rests inside the open chest.
map_z = chest_base_z + 0.205
cube_obj(
    "Day 06 • unfolded parchment map",
    (chest_x, chest_y, map_z),
    (0.70, 0.43, 0.014),
    map_paper,
    0.012
)

# A winding sepia trail and a marked destination make the map legible from above.
make_water_curve(
    "Day 06 • inked trail on old map",
    [
        (chest_x - 0.27, chest_y - 0.13, map_z + 0.018),
        (chest_x - 0.13, chest_y - 0.04, map_z + 0.018),
        (chest_x - 0.03, chest_y + 0.08, map_z + 0.018),
        (chest_x + 0.12, chest_y + 0.045, map_z + 0.018),
        (chest_x + 0.23, chest_y + 0.14, map_z + 0.018)
    ],
    0.009,
    map_ink
)
# A small ring and crossed strokes mark the map's hidden destination.
bpy.ops.mesh.primitive_torus_add(
    major_segments=16,
    minor_segments=6,
    location=(chest_x + 0.22, chest_y + 0.14, map_z + 0.025),
    major_radius=0.052,
    minor_radius=0.008
)
map_marker = bpy.context.object
map_marker.name = "Day 06 • map destination marker"
map_marker.data.materials.append(map_ink)
for angle in (math.radians(45), math.radians(-45)):
    mark = cube_obj(
        "Day 06 • map X mark",
        (chest_x + 0.22, chest_y + 0.14, map_z + 0.03),
        (0.105, 0.012, 0.008),
        map_ink,
        0.002
    )
    mark.rotation_euler.z = angle

# The lid is propped open behind the box; two bronze hinge barrels suggest a working hinge.
lid_angle = math.radians(-55)
hinge_y = chest_y + 0.28
hinge_z = chest_base_z + 0.57
lid_center_y = hinge_y - 0.32 * math.cos(math.radians(55))
lid_center_z = hinge_z + 0.32 * math.sin(math.radians(55))
lid = cube_obj(
    "Day 06 • open chest lid",
    (chest_x, lid_center_y, lid_center_z),
    (1.02, 0.64, 0.10),
    chest_trim,
    0.035
)
lid.rotation_euler.x = lid_angle

for dx in (-0.30, 0.30):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=12,
        radius=0.045,
        depth=0.16,
        location=(chest_x + dx, hinge_y, hinge_z),
        rotation=(0.0, math.radians(90), 0.0)
    )
    hinge = bpy.context.object
    hinge.name = "Day 06 • bronze lid hinge"
    hinge.data.materials.append(chest_metal)

# A simple bronze clasp on the front completes the small explorer's find.
cube_obj(
    "Day 06 • front clasp plate",
    (chest_x, chest_y - 0.345, chest_base_z + 0.34),
    (0.16, 0.035, 0.18),
    chest_metal,
    0.018
)
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=12,
    ring_count=8,
    radius=0.045,
    location=(chest_x, chest_y - 0.37, chest_base_z + 0.34)
)
clasp = bpy.context.object
clasp.name = "Day 06 • clasp stud"
clasp.scale = (1.0, 0.45, 1.0)
clasp.data.materials.append(chest_trim)


# A small cedar-and-bronze lantern beside the map chest — Day 07
# It marks the discovery point without blocking the path or the bridge view.
lantern_x, lantern_y = 2.25, -2.95
lantern_ground_z = terrain_height(lantern_x, lantern_y) + 0.045

lantern_wood = material("Lantern • dark cedar frame", (0.16, 0.075, 0.035), 0.72)
lantern_bronze = material("Lantern • aged bronze fittings", (0.42, 0.25, 0.09), 0.38)
lantern_glass = material("Lantern • warm amber panes", (0.38, 0.19, 0.065), 0.32)

flame_mat = bpy.data.materials.new("Lantern • glowing golden flame")
flame_mat.use_nodes = True
flame_nodes = flame_mat.node_tree.nodes
flame_nodes.clear()
flame_emission = flame_nodes.new("ShaderNodeEmission")
flame_emission.inputs["Color"].default_value = (1.0, 0.43, 0.10, 1.0)
flame_emission.inputs["Strength"].default_value = 3.5
flame_output = flame_nodes.new("ShaderNodeOutputMaterial")
flame_mat.node_tree.links.new(flame_emission.outputs["Emission"], flame_output.inputs["Surface"])

# Stone footing, timber post and a broad lower plinth.
bpy.ops.mesh.primitive_ico_sphere_add(
    subdivisions=1, radius=1.0,
    location=(lantern_x, lantern_y, lantern_ground_z + 0.09)
)
lantern_foot = bpy.context.object
lantern_foot.name = "Day 07 • lantern stone footing"
lantern_foot.scale = (0.38, 0.34, 0.16)
lantern_foot.data.materials.append(stone)

bpy.ops.mesh.primitive_cylinder_add(
    vertices=10, radius=0.075, depth=0.82,
    location=(lantern_x, lantern_y, lantern_ground_z + 0.50)
)
lantern_post = bpy.context.object
lantern_post.name = "Day 07 • lantern cedar post"
lantern_post.data.materials.append(lantern_wood)
post_bevel = lantern_post.modifiers.new("Lantern post softened edges", "BEVEL")
post_bevel.width = 0.018
post_bevel.segments = 2

cube_obj(
    "Day 07 • lantern lower plinth",
    (lantern_x, lantern_y, lantern_ground_z + 0.91),
    (0.62, 0.62, 0.14), lantern_wood, 0.035
)

# Four amber panes sit inside a sturdy cedar frame.
body_center_z = lantern_ground_z + 1.285
body_height = 0.58
pane_height = 0.48
pane_center_z = body_center_z
frame_offset = 0.205
frame_width = 0.055

for dx in (-frame_offset, frame_offset):
    for dy in (-frame_offset, frame_offset):
        cube_obj(
            "Day 07 • lantern corner stile",
            (lantern_x + dx, lantern_y + dy, body_center_z),
            (frame_width, frame_width, body_height),
            lantern_wood, 0.012
        )

# Front and rear panes.
for dy in (-0.17, 0.17):
    cube_obj(
        "Day 07 • amber lantern glass",
        (lantern_x, lantern_y + dy, pane_center_z),
        (0.34, 0.018, pane_height),
        lantern_glass, 0.008
    )
# Left and right panes.
for dx in (-0.17, 0.17):
    cube_obj(
        "Day 07 • amber lantern glass",
        (lantern_x + dx, lantern_y, pane_center_z),
        (0.018, 0.34, pane_height),
        lantern_glass, 0.008
    )

# Bronze bands and the roof make the silhouette readable at a distance.
cube_obj(
    "Day 07 • lantern bottom bronze band",
    (lantern_x, lantern_y, lantern_ground_z + 0.985),
    (0.50, 0.50, 0.055), lantern_bronze, 0.012
)
cube_obj(
    "Day 07 • lantern top bronze band",
    (lantern_x, lantern_y, lantern_ground_z + 1.585),
    (0.50, 0.50, 0.055), lantern_bronze, 0.012
)

bpy.ops.mesh.primitive_cone_add(
    vertices=4, radius1=0.39, radius2=0.13, depth=0.24,
    location=(lantern_x, lantern_y, lantern_ground_z + 1.72),
    rotation=(0.0, 0.0, math.radians(45.0))
)
lantern_roof = bpy.context.object
lantern_roof.name = "Day 07 • cedar lantern roof"
lantern_roof.data.materials.append(lantern_wood)
roof_bevel = lantern_roof.modifiers.new("Lantern roof softened edges", "BEVEL")
roof_bevel.width = 0.018
roof_bevel.segments = 2

bpy.ops.mesh.primitive_uv_sphere_add(
    segments=12, ring_count=8, radius=0.075,
    location=(lantern_x, lantern_y, lantern_ground_z + 1.88)
)
lantern_finial = bpy.context.object
lantern_finial.name = "Day 07 • lantern roof finial"
lantern_finial.data.materials.append(lantern_bronze)

# A compact emissive flame and warm point light illuminate the nearby map chest.
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=16, ring_count=10, radius=1.0,
    location=(lantern_x, lantern_y, body_center_z)
)
lantern_flame = bpy.context.object
lantern_flame.name = "Day 07 • glowing lantern flame"
lantern_flame.scale = (0.105, 0.105, 0.22)
lantern_flame.data.materials.append(flame_mat)

bpy.ops.object.light_add(
    type="POINT",
    location=(lantern_x, lantern_y - 0.03, body_center_z)
)
lantern_light = bpy.context.object
lantern_light.name = "Day 07 • warm lantern point light"
lantern_light.data.energy = 55
lantern_light.data.color = (1.0, 0.48, 0.20)
lantern_light.data.shadow_soft_size = 0.48



# Small stone cairns follow the old map toward the south-eastern ridge — Day 08
# Four low, hand-stacked markers form a subtle trail from the map chest toward a future hidden-grotto area.
marker_stone_mat = material("Trail markers • weathered river stone", (0.27, 0.31, 0.30), 0.92)
marker_gem_mat = material("Trail markers • muted turquoise waystone", (0.08, 0.30, 0.32), 0.42)

def make_trail_cairn(x, y, scale=1.0, seed=0, destination=False):
    rng = random.Random(seed)
    ground_z = terrain_height(x, y) + 0.045

    # A flat, broad footing settles each cairn into the meadow.
    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=1,
        radius=1.0,
        location=(x, y, ground_z + 0.095 * scale)
    )
    footing = bpy.context.object
    footing.name = "Day 08 • cairn footing stone"
    footing.scale = (0.34 * scale, 0.28 * scale, 0.12 * scale)
    footing.data.materials.append(stone)

    # Three irregular stones are stacked with a slight overlap for a hand-built silhouette.
    stack_bottom = ground_z + 0.16 * scale
    for level, base_radius in enumerate((0.22, 0.165, 0.12)):
        radius = base_radius * scale * rng.uniform(0.92, 1.08)
        height = radius * 1.50
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=1,
            radius=1.0,
            location=(
                x + rng.uniform(-0.045, 0.045) * scale,
                y + rng.uniform(-0.045, 0.045) * scale,
                stack_bottom + height * 0.5
            )
        )
        rock = bpy.context.object
        rock.name = "Day 08 • stacked trail marker stone"
        rock.scale = (
            radius * rng.uniform(1.02, 1.22),
            radius * rng.uniform(0.88, 1.08),
            radius * 0.75
        )
        rock.rotation_euler = (
            rng.uniform(-0.16, 0.16),
            rng.uniform(-0.16, 0.16),
            rng.uniform(-math.pi, math.pi)
        )
        rock.data.materials.append(marker_stone_mat)
        stack_bottom += height * 0.72

    # The final cairn carries a small turquoise stone to identify the map's destination.
    if destination:
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=2,
            radius=0.075 * scale,
            location=(x, y, stack_bottom + 0.045 * scale)
        )
        waystone = bpy.context.object
        waystone.name = "Day 08 • turquoise destination waystone"
        waystone.scale = (0.90, 0.78, 1.18)
        waystone.data.materials.append(marker_gem_mat)

# Follow the south-eastern side of the existing creek route without blocking the bridge,
# signpost, map chest, or lantern. Every cairn is placed against the shared height field.
cairn_sites = [
    (4.55, -3.35, 0.92),
    (5.70, -4.05, 0.96),
    (6.85, -4.70, 1.00),
    (7.90, -5.35, 1.04)
]
for index, (cx, cy, cs) in enumerate(cairn_sites):
    make_trail_cairn(
        cx, cy, cs,
        seed=810 + index,
        destination=(index == len(cairn_sites) - 1)
    )



# Hidden grotto entrance at the end of the cairn trail — Day 09
# A shallow arched recess faces the presentation camera and sits just beyond the final turquoise cairn.
cave_x, cave_y = 8.35, -6.05
cave_ground_z = terrain_height(cave_x, cave_y) + 0.035

# The outward normal points toward the camera; the tangent defines the arch width.
cave_nx, cave_ny = 0.52, -0.854
cave_n_len = math.sqrt(cave_nx * cave_nx + cave_ny * cave_ny)
cave_nx, cave_ny = cave_nx / cave_n_len, cave_ny / cave_n_len
cave_tx, cave_ty = -cave_ny, cave_nx

def cave_position(along, depth, height):
    return (
        cave_x + cave_tx * along - cave_nx * depth,
        cave_y + cave_ty * along - cave_ny * depth,
        cave_ground_z + height
    )

cave_rock_mat = material("Grotto • weathered charcoal stone", (0.16, 0.19, 0.20), 0.94)
cave_inner_mat = material("Grotto • shadowed inner stone", (0.035, 0.047, 0.052), 0.98)
cave_floor_mat = material("Grotto • damp threshold", (0.095, 0.12, 0.12), 0.92)

# Build an arched polygon: straight jambs and a rounded crown.
cave_half_width = 0.66
cave_spring_height = 0.74
cave_outline = [(-cave_half_width, 0.0), (cave_half_width, 0.0)]
cave_outline.extend([
    (
        cave_half_width * math.cos(math.pi * index / 16.0),
        cave_spring_height + cave_half_width * math.sin(math.pi * index / 16.0)
    )
    for index in range(17)
])

# The tunnel shell extends inward, while a dark rear face makes the recess read as depth.
cave_front_depth, cave_back_depth = 0.10, 1.08
cave_count = len(cave_outline)
cave_shell_verts = (
    [cave_position(u, cave_front_depth, z) for u, z in cave_outline] +
    [cave_position(u, cave_back_depth, z) for u, z in cave_outline]
)
cave_shell_faces = []
for index in range(cave_count):
    next_index = (index + 1) % cave_count
    cave_shell_faces.append((
        index,
        next_index,
        cave_count + next_index,
        cave_count + index
    ))

cave_shell_mesh = bpy.data.meshes.new("Day 09 • arched tunnel lining mesh")
cave_shell_mesh.from_pydata(cave_shell_verts, [], cave_shell_faces)
cave_shell_mesh.materials.append(cave_inner_mat)
cave_shell = bpy.data.objects.new("Day 09 • recessed grotto lining", cave_shell_mesh)
bpy.context.collection.objects.link(cave_shell)

cave_back_verts = [cave_position(u, cave_back_depth + 0.012, z) for u, z in cave_outline]
cave_back_mesh = bpy.data.meshes.new("Day 09 • dark arched interior mesh")
cave_back_mesh.from_pydata(cave_back_verts, [], [tuple(range(cave_count))])
cave_back_mesh.materials.append(cave_inner_mat)
cave_back = bpy.data.objects.new("Day 09 • dark grotto interior", cave_back_mesh)
bpy.context.collection.objects.link(cave_back)

# A narrow threshold follows the same local orientation as the entrance.
cave_floor_verts = [
    cave_position(-cave_half_width, cave_front_depth, 0.025),
    cave_position(cave_half_width, cave_front_depth, 0.025),
    cave_position(cave_half_width, cave_back_depth, 0.025),
    cave_position(-cave_half_width, cave_back_depth, 0.025)
]
cave_floor_mesh = bpy.data.meshes.new("Day 09 • cave threshold mesh")
cave_floor_mesh.from_pydata(cave_floor_verts, [], [(0, 1, 2, 3)])
cave_floor_mesh.materials.append(cave_floor_mat)
cave_floor = bpy.data.objects.new("Day 09 • damp cave threshold", cave_floor_mesh)
bpy.context.collection.objects.link(cave_floor)

# Irregular boulders form a natural arch without covering the opening.
cave_rng = random.Random(909)
for index in range(11):
    if index < 9:
        angle = math.pi * index / 8.0
        along = 0.91 * math.cos(angle)
        height = cave_spring_height + 0.91 * math.sin(angle)
    else:
        side = -1.0 if index % 2 else 1.0
        along = side * cave_rng.uniform(0.78, 0.88)
        height = cave_rng.uniform(0.20, 0.72)

    radius = cave_rng.uniform(0.23, 0.31)
    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=1,
        radius=1.0,
        location=cave_position(along, -0.045, height)
    )
    boulder = bpy.context.object
    boulder.name = "Day 09 • rough grotto arch boulder"
    boulder.scale = (
        radius * cave_rng.uniform(1.00, 1.28),
        radius * cave_rng.uniform(0.82, 1.05),
        radius * cave_rng.uniform(1.05, 1.34)
    )
    boulder.rotation_euler = (
        cave_rng.uniform(-0.18, 0.18),
        cave_rng.uniform(-0.18, 0.18),
        math.atan2(cave_ty, cave_tx) + cave_rng.uniform(-0.35, 0.35)
    )
    boulder.data.materials.append(cave_rock_mat)

# Moss softens the crown and two thin roots hang just inside the left and right jambs.
for index, along in enumerate((-0.48, -0.12, 0.28, 0.53)):
    moss_z = 1.53 + (0.08 if index in (1, 2) else 0.0)
    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=2,
        radius=1.0,
        location=cave_position(along, -0.13, moss_z)
    )
    moss = bpy.context.object
    moss.name = "Day 09 • moss on grotto crown"
    moss.scale = (0.24, 0.18, 0.095)
    moss.data.materials.append(moss_bank_mat)

make_water_curve(
    "Day 09 • hanging moss root left",
    [
        cave_position(-0.48, -0.10, 1.48),
        cave_position(-0.50, -0.02, 1.30),
        cave_position(-0.46, 0.06, 1.12),
        cave_position(-0.43, 0.10, 1.02)
    ],
    0.018,
    moss_bank_mat
)
make_water_curve(
    "Day 09 • hanging moss root right",
    [
        cave_position(0.43, -0.10, 1.48),
        cave_position(0.40, -0.02, 1.34),
        cave_position(0.44, 0.06, 1.20)
    ],
    0.014,
    moss_bank_mat
)

# A restrained blue-green crystal glimmer hints that the grotto continues beyond the entrance.
cave_crystal_mat = bpy.data.materials.new("Grotto • faint turquoise crystal glow")
cave_crystal_mat.use_nodes = True
cave_crystal_nodes = cave_crystal_mat.node_tree.nodes
cave_crystal_nodes.clear()
cave_crystal_emission = cave_crystal_nodes.new("ShaderNodeEmission")
cave_crystal_emission.inputs["Color"].default_value = (0.10, 0.55, 0.68, 1.0)
cave_crystal_emission.inputs["Strength"].default_value = 1.6
cave_crystal_output = cave_crystal_nodes.new("ShaderNodeOutputMaterial")
cave_crystal_mat.node_tree.links.new(
    cave_crystal_emission.outputs["Emission"],
    cave_crystal_output.inputs["Surface"]
)

for index, (along, height, size) in enumerate((
    (-0.16, 0.29, 0.15),
    (0.02, 0.34, 0.23),
    (0.19, 0.27, 0.13)
)):
    bpy.ops.mesh.primitive_cone_add(
        vertices=6,
        radius1=size * 0.48,
        radius2=0.0,
        depth=size * 2.0,
        location=cave_position(along, 0.78, height)
    )
    crystal = bpy.context.object
    crystal.name = "Day 09 • faint grotto crystal"
    crystal.rotation_euler.y = math.radians(cave_rng.uniform(-12.0, 12.0))
    crystal.data.materials.append(cave_crystal_mat)

bpy.ops.object.light_add(
    type="POINT",
    location=cave_position(0.02, 0.72, 0.48)
)
cave_glow = bpy.context.object
cave_glow.name = "Day 09 • subtle grotto crystal light"
cave_glow.data.energy = 18
cave_glow.data.color = (0.18, 0.66, 0.82)
cave_glow.data.shadow_soft_size = 0.72


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
scene.render.filepath='//Screenshots/day09_hidden_grotto.png'

# Helpful viewport framing
bpy.context.view_layer.objects.active=island
island.select_set(True)
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        area.spaces.active.region_3d.view_distance=30

print("Infinite 3D World — Day 09 hidden grotto entrance added. Save as world.blend and render with F12.")
