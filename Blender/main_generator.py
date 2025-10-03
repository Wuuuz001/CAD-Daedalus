# main_generator.py 
import json
import os
import textwrap

def get_blender_script_header():
    
    return textwrap.dedent("""
import bpy

def clear_scene():
    if bpy.ops.object.mode_set.poll(): bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
        if block.users == 0: bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0: bpy.data.materials.remove(block)

# --- 主执行逻辑开始 ---
clear_scene()
""")


# --- 所有单个零件的生成函数 (保持不变，为简洁省略) ---
def generate_cylinder_code(params, opts):
    radius, height = params['radius'], params['height'];
    ix, iy = opts.get('insertion_point', [0, 0])
    return f"bpy.ops.mesh.primitive_cylinder_add(radius={radius}, depth={height}, location=({ix}, {iy}, {height / 2.0}))"


def generate_cuboid_code(params, opts):
    length, width, height = params['length'], params['width'], params['height'];
    ix, iy = opts.get('insertion_point', [0, 0])
    code = f"bpy.ops.mesh.primitive_cube_add(size=1, location=({ix + length / 2.0}, {iy + width / 2.0}, {height / 2.0}))\n"
    code += f"bpy.context.object.dimensions = ({length}, {width}, {height})"
    return code


def generate_hex_prism_code(params, opts):
    side_length, height = params['side_length'], params['height'];
    ix, iy = opts.get('insertion_point', [0, 0])
    return f"bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius={side_length}, depth={height}, location=({ix}, {iy}, {height / 2.0}))"


def generate_hex_screw_code(params, opts):
    head_p, shaft_p = params['head'], params['shaft'];
    ix, iy = opts.get('insertion_point', [0, 0])
    head_radius, head_height = head_p['side_length'], head_p['height']
    shaft_radius, shaft_len = shaft_p['diameter'] / 2.0, shaft_p['length']
    code = f"bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius={head_radius}, depth={head_height}, location=({ix}, {iy}, {shaft_len + head_height / 2.0})); head_obj = bpy.context.active_object\n"
    code += f"bpy.ops.mesh.primitive_cylinder_add(radius={shaft_radius}, depth={shaft_len}, location=({ix}, {iy}, {shaft_len / 2.0})); shaft_obj = bpy.context.active_object\n"
    code += "bpy.ops.object.select_all(action='DESELECT'); head_obj.select_set(True); shaft_obj.select_set(True); bpy.context.view_layer.objects.active = head_obj; bpy.ops.object.join()"
    return code


def generate_hex_nut_code(params, opts):
    side_length, height, hole_dia = params['side_length'], params['height'], params['hole']['diameter'];
    ix, iy = opts.get('insertion_point', [0, 0])
    nut_radius, hole_radius = side_length, hole_dia / 2.0
    code = f"bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius={nut_radius}, depth={height}, location=({ix}, {iy}, {height / 2.0})); nut_obj = bpy.context.active_object\n"
    code += f"bpy.ops.mesh.primitive_cylinder_add(radius={hole_radius}, depth={height * 1.2}, location=({ix}, {iy}, {height / 2.0})); tool_obj = bpy.context.active_object\n"
    code += "mod = nut_obj.modifiers.new(name='Hole', type='BOOLEAN'); mod.operation = 'DIFFERENCE'; mod.object = tool_obj; bpy.context.view_layer.objects.active = nut_obj; bpy.ops.object.modifier_apply(modifier=mod.name); bpy.data.objects.remove(tool_obj, do_unlink=True)"
    return code


def generate_screw_nut_assembly_code(params_dict, opts):
    screw_params, nut_params = params_dict['screw']['parameters'], params_dict['nut']['parameters'];
    ix, iy = opts.get('insertion_point', [0, 0])
    screw_head_radius, screw_head_height = screw_params['head']['side_length'], screw_params['head']['height']
    screw_shaft_radius, screw_shaft_len = screw_params['shaft']['diameter'] / 2.0, screw_params['shaft']['length']
    nut_radius, nut_height, nut_hole_radius = nut_params['side_length'], nut_params['height'], nut_params['hole'][
                                                                                                   'diameter'] / 2.0
    return textwrap.dedent(f"""
# --- 创建螺钉-螺母装配体 ---
print("正在创建装配体...")
bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius={screw_head_radius}, depth={screw_head_height}, location=({ix}, {iy}, {screw_shaft_len + screw_head_height / 2.0})); head_obj = bpy.context.active_object
bpy.ops.mesh.primitive_cylinder_add(radius={screw_shaft_radius}, depth={screw_shaft_len}, location=({ix}, {iy}, {screw_shaft_len / 2.0})); shaft_obj = bpy.context.active_object
bpy.ops.object.select_all(action='DESELECT'); head_obj.select_set(True); shaft_obj.select_set(True); bpy.context.view_layer.objects.active = head_obj; bpy.ops.object.join(); screw_obj = bpy.context.active_object; screw_obj.name = "Screw"
bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius={nut_radius}, depth={nut_height}, location=({ix}, {iy}, 0)); nut_body_obj = bpy.context.active_object
bpy.ops.mesh.primitive_cylinder_add(radius={nut_hole_radius}, depth={nut_height * 1.2}, location=({ix}, {iy}, 0)); tool_obj = bpy.context.active_object
mod = nut_body_obj.modifiers.new(name='Hole', type='BOOLEAN'); mod.operation = 'DIFFERENCE'; mod.object = tool_obj; bpy.context.view_layer.objects.active = nut_body_obj; bpy.ops.object.modifier_apply(modifier=mod.name); bpy.data.objects.remove(tool_obj, do_unlink=True); nut_obj = nut_body_obj; nut_obj.name = "Nut"
nut_obj.location.z = {screw_shaft_len - nut_height - 5.0}
print("装配体创建完毕。")
""")


def generate_cuboid_cylinder_assembly_code(params_dict, opts):
    cuboid_params = params_dict['cuboid']['parameters']
    cylinder_params = params_dict['cylinder']['parameters']
    ix, iy = opts.get('insertion_point', [0, 0])
    cuboid_l, cuboid_w, cuboid_h = cuboid_params['length'], cuboid_params['width'], cuboid_params['height']
    cyl_r, cyl_h = cylinder_params['radius'], cylinder_params['height']
    center_x = ix + cuboid_l / 2.0;
    center_y = iy + cuboid_w / 2.0
    return textwrap.dedent(f"""
# --- 创建长方体-圆柱装配体 ---
print("正在创建装配体...")
# --- 1. 创建带孔的长方体 ---
print("  - 创建并正确缩放长方体...")
bpy.ops.mesh.primitive_cube_add(size=2, location=({center_x}, {center_y}, {cuboid_h / 2.0})); cuboid_obj = bpy.context.active_object; cuboid_obj.name = "Cuboid"
cuboid_obj.scale = ({cuboid_l / 2.0}, {cuboid_w / 2.0}, {cuboid_h / 2.0})
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
bpy.ops.mesh.primitive_cylinder_add(radius={cyl_r}, depth={cuboid_h * 1.2}, location=({center_x}, {center_y}, {cuboid_h / 2.0})); tool_obj = bpy.context.active_object
mod = cuboid_obj.modifiers.new(name='Hole', type='BOOLEAN'); mod.operation = 'DIFFERENCE'; mod.object = tool_obj
bpy.context.view_layer.objects.active = cuboid_obj; bpy.ops.object.modifier_apply(modifier=mod.name); bpy.data.objects.remove(tool_obj, do_unlink=True)
# --- 2. 创建独立的圆柱零件 ---
print("  - 创建圆柱零件...")
bpy.ops.mesh.primitive_cylinder_add(radius={cyl_r}, depth={cyl_h}, location=({center_x}, {center_y}, {cyl_h / 2.0})); cylinder_obj = bpy.context.active_object; cylinder_obj.name = "Cylinder"
mat_blue = bpy.data.materials.new(name="Blue"); mat_blue.diffuse_color = (0.1, 0.2, 0.8, 1.0)
if len(cylinder_obj.data.materials) == 0: cylinder_obj.data.materials.append(None)
cylinder_obj.data.materials[0] = mat_blue
print("装配体创建完毕。")
# --- 3. 脚本结束操作 ---
bpy.ops.object.select_all(action='DESELECT'); cuboid_obj.select_set(True); cylinder_obj.select_set(True); bpy.context.view_layer.objects.active = cuboid_obj
print("\\n脚本执行完成。请在3D视图中按 '.' (小键盘) 来聚焦。")
""")


def generate_full_assembly_code(params_dict, opts):
    """
    【新版】生成一个完整的装配体：长方体被螺钉和螺母固定在其末端。

    装配顺序 (从上到下):
    1. 螺钉头
    2. 螺钉杆 (大部分)
    3. 长方体 (被螺钉杆穿过)
    4. 螺母 (紧固在长方体下方)
    """
    # 提取所有需要的参数
    cuboid_p = params_dict['cuboid']['parameters']
    screw_p = params_dict['screw']['parameters']
    nut_p = params_dict['nut']['parameters']
    ix, iy = opts.get('insertion_point', [0, 0])

    # 尺寸参数
    cuboid_l, cuboid_w, cuboid_h = cuboid_p['length'], cuboid_p['width'], cuboid_p['height']
    screw_head_r, screw_head_h = screw_p['head']['side_length'], screw_p['head']['height']
    screw_shaft_r, screw_shaft_l = screw_p['shaft']['diameter'] / 2.0, screw_p['shaft']['length']
    nut_r, nut_h = nut_p['side_length'], nut_p['height']
    nut_hole_r = nut_p['hole']['diameter'] / 2.0

    # 检查尺寸是否合理 (物理上螺杆需要足够长)
    if screw_shaft_l < (cuboid_h + nut_h):
        print(f"警告: 螺杆长度 ({screw_shaft_l}) 可能不足以穿过长方体 ({cuboid_h}) 并固定螺母 ({nut_h})。")

    # 计算装配中心
    center_x = ix
    center_y = iy

    # 使用 textwrap.dedent 和 f-string 生成代码
    return textwrap.dedent(f"""
# --- 创建最终装配体 (长方体在螺钉末端) ---
print("正在创建完整装配体 (新版)...")

# --- 1. 创建螺钉 (作为参考基准) ---
# 螺钉将被创建并定位，使其杆的尖端在 Z=0 附近
print("  - 1. 创建螺钉...")
bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius={screw_head_r}, depth={screw_head_h}, location=(0, 0, 0))
head_obj = bpy.context.active_object
bpy.ops.mesh.primitive_cylinder_add(radius={screw_shaft_r}, depth={screw_shaft_l}, location=(0, 0, 0))
shaft_obj = bpy.context.active_object

# 先移动部件到相对于原点的位置，再合并
# 这样合并后的对象原点就在 (0,0,0)
head_obj.location.z = {screw_shaft_l + screw_head_h / 2.0}
shaft_obj.location.z = {screw_shaft_l / 2.0}

# 合并成一个螺钉对象
bpy.ops.object.select_all(action='DESELECT')
head_obj.select_set(True)
shaft_obj.select_set(True)
bpy.context.view_layer.objects.active = shaft_obj # 以杆为活动对象，原点更易于计算
bpy.ops.object.join()
screw_obj = bpy.context.active_object
screw_obj.name = "Screw_Assembly"
# 将螺钉原点设置到螺杆底部，便于定位
bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
bpy.context.scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')


# --- 2. 创建螺母 ---
print("  - 2. 创建螺母...")
bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius={nut_r}, depth={nut_h}, location=(0,0,0))
nut_body_obj = bpy.context.active_object
bpy.ops.mesh.primitive_cylinder_add(radius={nut_hole_r}, depth={nut_h * 1.2}, location=(0,0,0))
tool_obj_nut = bpy.context.active_object
mod_nut = nut_body_obj.modifiers.new(name='Hole', type='BOOLEAN')
mod_nut.operation = 'DIFFERENCE'
mod_nut.object = tool_obj_nut
bpy.context.view_layer.objects.active = nut_body_obj
bpy.ops.object.modifier_apply(modifier=mod_nut.name)
bpy.data.objects.remove(tool_obj_nut, do_unlink=True)
nut_obj = nut_body_obj
nut_obj.name = "Nut_Assembly"


# --- 3. 创建带孔的长方体 ---
print("  - 3. 创建带孔长方体...")
bpy.ops.mesh.primitive_cube_add(size=2, location=(0,0,0))
cuboid_obj = bpy.context.active_object
cuboid_obj.name = "Cuboid_Block"
cuboid_obj.scale = ({cuboid_l / 2.0}, {cuboid_w / 2.0}, {cuboid_h / 2.0})
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
bpy.ops.mesh.primitive_cylinder_add(radius={screw_shaft_r}, depth={cuboid_h * 1.5}, location=(0,0,0))
tool_obj_cuboid = bpy.context.active_object
mod = cuboid_obj.modifiers.new(name='Hole', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = tool_obj_cuboid
bpy.context.view_layer.objects.active = cuboid_obj
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.data.objects.remove(tool_obj_cuboid, do_unlink=True)


# --- 4. 定位所有零件进行最终装配 ---
# 参照系: Z=0 是螺母的底部。
print("  - 4. 定位所有零件...")

# a) 定位螺母: 它的中心在Z轴的 nut_h / 2.0 处
nut_z = {nut_h / 2.0}
nut_obj.location = ({center_x}, {center_y}, nut_z)

# b) 定位长方体: 它在螺母的正上方。其底部在 Z = nut_h 处。
cuboid_z = {nut_h} + {cuboid_h / 2.0}
cuboid_obj.location = ({center_x}, {center_y}, cuboid_z)

# c) 定位螺钉: 它的原点(我们已设为杆的底部)应该和螺母底部对齐
screw_z = 0 
screw_obj.location = ({center_x}, {center_y}, screw_z)

print("完整装配体 (新版) 创建完毕。")

# --- 5. 脚本结束操作 ---
bpy.ops.object.select_all(action='DESELECT')
cuboid_obj.select_set(True)
screw_obj.select_set(True)
nut_obj.select_set(True)
bpy.context.view_layer.objects.active = screw_obj

print("\\n脚本执行完成。请在3D视图中按 '.' (小键盘) 来聚焦。")
""")


# --- 【【【 新增的、正确的第9个装配体生成函数 】】】 ---
def generate_cylinder_screw_nut_assembly_code(params_dict, opts):
    """
    【正确版】生成一个装配体：一个完整的螺钉穿过一个带孔的圆柱，并由一个螺母在底部固定。
    """
    # 提取所有需要的参数
    cylinder_p = params_dict['cylinder']['parameters']
    screw_p = params_dict['screw']['parameters']
    nut_p = params_dict['nut']['parameters']
    ix, iy = opts.get('insertion_point', [0, 0])

    # 尺寸参数
    cyl_r, cyl_h = cylinder_p['radius'], cylinder_p['height']
    screw_head_r, screw_head_h = screw_p['head']['side_length'], screw_p['head']['height']
    screw_shaft_r, screw_shaft_l = screw_p['shaft']['diameter'] / 2.0, screw_p['shaft']['length']
    nut_r, nut_h = nut_p['side_length'], nut_p['height']

    # 检查螺杆长度是否足够
    required_length = cyl_h + nut_h
    if screw_shaft_l < required_length:
        print(f"警告: 螺杆长度 ({screw_shaft_l}) 可能不足以穿过圆柱 ({cyl_h}) 并固定螺母 ({nut_h})。")

    # 计算装配中心
    center_x = ix
    center_y = iy

    return textwrap.dedent(f"""
# --- 创建 螺钉-圆柱-螺母 装配体 ---
print("正在创建 螺钉-圆柱-螺母 装配体...")

# --- 策略：先在原点创建好各个独立的零件，最后统一移动到装配位置 ---
# --- 参考系：将圆柱体的底部平面设为 Z=0 ---

# --- 1. 创建带孔的中心圆柱体 ---
print("  - 1. 创建带孔圆柱...")
# 创建圆柱主体，使其底部在 Z=0
bpy.ops.mesh.primitive_cylinder_add(radius={cyl_r}, depth={cyl_h}, location=(0, 0, {cyl_h / 2.0}))
main_cyl_obj = bpy.context.active_object
main_cyl_obj.name = "Central_Cylinder"
# 创建打孔工具 (孔径与螺杆匹配)
bpy.ops.mesh.primitive_cylinder_add(radius={screw_shaft_r}, depth={cyl_h * 1.2}, location=(0, 0, {cyl_h / 2.0}))
tool_obj_cyl = bpy.context.active_object
# 执行布尔打孔
mod = main_cyl_obj.modifiers.new(name='Hole', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = tool_obj_cyl
bpy.context.view_layer.objects.active = main_cyl_obj
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.data.objects.remove(tool_obj_cyl, do_unlink=True)


# --- 2. 创建一个完整的螺钉 ---
print("  - 2. 创建完整螺钉...")
bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius={screw_head_r}, depth={screw_head_h}, location=(0, 0, 0))
head_obj = bpy.context.active_object
bpy.ops.mesh.primitive_cylinder_add(radius={screw_shaft_r}, depth={screw_shaft_l}, location=(0, 0, 0))
shaft_obj = bpy.context.active_object
# 先移动部件到相对于原点的位置，再合并
head_obj.location.z = {screw_shaft_l + screw_head_h / 2.0}
shaft_obj.location.z = {screw_shaft_l / 2.0}
# 合并
bpy.ops.object.select_all(action='DESELECT')
head_obj.select_set(True)
shaft_obj.select_set(True)
bpy.context.view_layer.objects.active = head_obj
bpy.ops.object.join()
screw_obj = bpy.context.active_object
screw_obj.name = "Full_Screw"


# --- 3. 创建螺母 ---
print("  - 3. 创建螺母...")
bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius={nut_r}, depth={nut_h}, location=(0, 0, 0))
nut_body_obj = bpy.context.active_object
bpy.ops.mesh.primitive_cylinder_add(radius={screw_shaft_r}, depth={nut_h * 1.2}, location=(0, 0, 0))
tool_obj_nut = bpy.context.active_object
mod_nut = nut_body_obj.modifiers.new(name='Hole', type='BOOLEAN')
mod_nut.operation = 'DIFFERENCE'
mod_nut.object = tool_obj_nut
bpy.context.view_layer.objects.active = nut_body_obj
bpy.ops.object.modifier_apply(modifier=mod_nut.name)
bpy.data.objects.remove(tool_obj_nut, do_unlink=True)
nut_obj = nut_body_obj
nut_obj.name = "Bottom_Nut"


# --- 4. 定位所有零件进行最终装配 ---
print("  - 4. 定位所有零件...")
# a) 定位中心圆柱
main_cyl_obj.location = ({center_x}, {center_y}, {cyl_h / 2.0})

# b) 定位螺钉: 螺钉头的底部要紧贴圆柱的顶部 (Z={cyl_h})
# 螺钉原点在其头部中心，距离头部底面的距离是 screw_head_h / 2.0
screw_z_pos = {cyl_h + screw_head_h / 2.0}
screw_obj.location = ({center_x}, {center_y}, screw_z_pos)

# c) 定位螺母: 螺母的顶部要紧贴圆柱的底部 (Z=0)
# 螺母原点在其中心，距离其顶部的距离是 nut_h / 2.0
nut_z_pos = -{nut_h / 2.0}
nut_obj.location = ({center_x}, {center_y}, nut_z_pos)


print("螺钉-圆柱-螺母 装配体创建完毕。")

# --- 5. 脚本结束操作 ---
bpy.ops.object.select_all(action='DESELECT')
main_cyl_obj.select_set(True)
screw_obj.select_set(True)
nut_obj.select_set(True)
bpy.context.view_layer.objects.active = main_cyl_obj

print("\\n脚本执行完成。请在3D视图中按 '.' (小键盘) 来聚焦。")
""")
# ==============================================================================
# 主程序
# ==============================================================================
if __name__ == "__main__":
    # (此处省略了之前的所有函数定义以保持简洁)
    # 你需要将上面的新函数 generate_cylinder_screwhead_nut_assembly_code 粘贴到主程序之前
    # 同时确保其他函数定义也存在

    # --- 配置字典，新增了选项 '9' ---
    config = {
        '1': {'file': 'cylinder_data.json', 'generator': generate_cylinder_code, 'type': 'part'},
        '2': {'file': 'part_config.json', 'generator': generate_cuboid_code, 'type': 'part'},
        '3': {'file': 'hex_prism_data.json', 'generator': generate_hex_prism_code, 'type': 'part'},
        '4': {'file': 'hex_screw.json', 'generator': generate_hex_screw_code, 'type': 'part'},
        '5': {'file': 'hex_nut_data.json', 'generator': generate_hex_nut_code, 'type': 'part'},
        '6': {'file': 'screw_nut_assembly.json', 'generator': generate_screw_nut_assembly_code,
              'type': 'assembly_screw_nut'},
        '7': {'file': 'cuboid_cylinder_assembly.json', 'generator': generate_cuboid_cylinder_assembly_code,
              'type': 'assembly_cuboid_cyl'},
        '8': {'file': 'full_assembly.json', 'generator': generate_full_assembly_code, 'type': 'assembly_full'},
        # 【【【 新增配置 】】】
        '9': {'file': 'cyl_head_nut_assembly.json', 'generator': generate_cylinder_screw_nut_assembly_code,
              'type': 'assembly_cyl_head_nut'}
    }

    # --- 默认数据，新增了新装配体的占位符 ---
    default_data_lib = {
        'cylinder_data.json': {"parameters": {"radius": 10, "height": 15}},
        'part_config.json': {"parameters": {"length": 20, "width": 20, "height": 10}},
        'hex_prism_data.json': {"parameters": {"side_length": 3, "height": 12}},
        'hex_screw.json': {
            "parameters": {"head": {"side_length": 8, "height": 5}, "shaft": {"diameter": 6, "length": 25}}},
        'hex_nut_data.json': {"parameters": {"side_length": 8, "height": 4, "hole": {"diameter": 6}}},
        'screw_nut_assembly.json': {"components": {"screw": {}, "nut": {}}},
        'cuboid_cylinder_assembly.json': {"components": {"cuboid": {}, "cylinder": {}}},
        'full_assembly.json': {"components": {"cuboid": {}, "screw": {}, "nut": {}}},
        # 【【【 新增默认数据 】】】
        'cyl_head_nut_assembly.json': {"components": {"cylinder": {}, "screw_head": {}, "nut": {}}}
    }

    # --- 更新菜单提示 ---
    menu_prompt = """
请选择您要生成的Blender脚本：
  1: 圆柱体 (Cylinder)
  2: 长方体 (Cuboid)
  3: 六棱柱 (Hexagonal Prism)
  4: 六角螺钉 (Hexagonal Screw)
  5: 六角螺母 (Hexagonal Nut)
  6: 螺钉-螺母装配体 (Screw-Nut Assembly)
  7: 长方体-圆柱装配体 (Cuboid-Cylinder Assembly)
  8: 完整装配体(螺母在长方体上) (Cuboid-Screw-Nut Assembly)
  9: 【新】圆柱-螺钉头-螺母装配体 (Cylinder-Head-Nut Assembly)
请输入选项 (1-9): """

    user_choice = input(menu_prompt).strip()

    if user_choice not in config:
        print("无效的选项。程序退出。")
    else:
        selected_config = config[user_choice]
        json_filename = selected_config['file']
        generator_func = selected_config['generator']
        output_filename = f"create_{json_filename.replace('_data', '').replace('.json', '')}.py"

        for fname, default in default_data_lib.items():
            if not os.path.exists(fname):
                print(f"警告: 文件 '{fname}' 不存在。将使用默认值创建一个。")
                data_with_opts = default.copy()
                data_with_opts.setdefault("drawing_options", {"insertion_point": [0, 0]})
                with open(fname, 'w', encoding='utf-8') as f:
                    json.dump(data_with_opts, f, indent=4)

        data_to_pass = {}
        # --- 数据加载逻辑 ---
        if selected_config['type'] == 'part':
            with open(json_filename, 'r', encoding='utf-8') as f:
                data_to_pass = json.load(f)
        elif selected_config['type'] == 'assembly_screw_nut':
            assembly_data = {}
            with open('hex_screw.json', 'r', encoding='utf-8') as f:
                assembly_data['screw'] = json.load(f)
            with open('hex_nut_data.json', 'r', encoding='utf-8') as f:
                assembly_data['nut'] = json.load(f)
            data_to_pass = assembly_data
        elif selected_config['type'] == 'assembly_cuboid_cyl':
            assembly_data = {}
            with open('part_config.json', 'r', encoding='utf-8') as f:
                assembly_data['cuboid'] = json.load(f)
            with open('cylinder_data.json', 'r', encoding='utf-8') as f:
                assembly_data['cylinder'] = json.load(f)
            data_to_pass = assembly_data
        elif selected_config['type'] == 'assembly_full':
            assembly_data = {}
            with open('part_config.json', 'r', encoding='utf-8') as f:
                assembly_data['cuboid'] = json.load(f)
            with open('hex_screw.json', 'r', encoding='utf-8') as f:
                assembly_data['screw'] = json.load(f)
            with open('hex_nut_data.json', 'r', encoding='utf-8') as f:
                assembly_data['nut'] = json.load(f)
            data_to_pass = assembly_data
        # 【【【 新增数据加载逻辑 】】】
        elif selected_config['type'] == 'assembly_cyl_head_nut':
            assembly_data = {}
            with open('cylinder_data.json', 'r', encoding='utf-8') as f:
                assembly_data['cylinder'] = json.load(f)
            with open('hex_screw.json', 'r', encoding='utf-8') as f:
                assembly_data['screw'] = json.load(f)
            with open('hex_nut_data.json', 'r', encoding='utf-8') as f:
                assembly_data['nut'] = json.load(f)
            data_to_pass = assembly_data

        # --- 提取全局选项 (例如插入点) ---
        opts = {}
        # 尝试从主零件的配置中获取插入点
        try:
            if 'part' in selected_config['type']:
                opts = data_to_pass.get('drawing_options', {"insertion_point": [0, 0]})
            elif 'assembly_full' in selected_config['type']:
                opts = data_to_pass['cuboid'].get('drawing_options', {"insertion_point": [0, 0]})
            elif 'assembly_cyl_head_nut' in selected_config['type']:
                opts = data_to_pass['cylinder'].get('drawing_options', {"insertion_point": [0, 0]})
            else:  # Fallback for other assemblies
                opts = {"insertion_point": [0, 0]}
        except (KeyError, AttributeError):
            opts = {"insertion_point": [0, 0]}

        header = get_blender_script_header()

        if 'assembly' in selected_config['type']:
            core_code = generator_func(data_to_pass, opts)
        else:
            params = data_to_pass['parameters']
            core_code = generator_func(params, opts)

        footer = ""
        final_script = header + core_code + footer

        with open(output_filename, "w", encoding='utf-8') as f:
            f.write(final_script)

        print("-" * 50)
        print(f"成功！已为您生成Blender脚本: '{output_filename}'")
        print(f"此脚本使用了以下配置文件的数据:")
        if 'part' in selected_config['type']: print(f" - {json_filename}")
        if 'assembly_cyl_head_nut' in selected_config['type']: print(
            " - cylinder_data.json\n - hex_screw.json\n - hex_nut_data.json")
        # Add other assembly print statements if you wish

        print("\n下一步：请打开Blender，进入'Scripting'工作区，打开并运行这个新文件。")
        print("-" * 50)
