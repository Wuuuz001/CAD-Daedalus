
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

# --- 创建长方体-圆柱装配体 ---
print("正在创建装配体...")

# --- 1. 创建带孔的长方体 ---
print("  - 创建并正确缩放长方体...")
# 创建一个2x2x2的立方体，因为半径为1的圆柱直径是2
bpy.ops.mesh.primitive_cube_add(
    size=2,
    location=(4.0, 2.5, 1.5)
)
cuboid_obj = bpy.context.active_object
cuboid_obj.name = "Cuboid"

# 【【【 关键修正 】】】
# 通过设置 scale 来定义尺寸，而不是 dimensions
cuboid_obj.scale = (4.0, 2.5, 1.5)

# 应用缩放，将缩放值“烘焙”进模型，使其变为 (1, 1, 1)
# 这是进行布尔运算前的关键一步！
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# 创建打孔工具
bpy.ops.mesh.primitive_cylinder_add(
    radius=1.0,
    depth=3.5999999999999996, 
    location=(4.0, 2.5, 1.5)
)
tool_obj = bpy.context.active_object

# 打孔 (这部分逻辑现在可以稳定工作了)
mod = cuboid_obj.modifiers.new(name='Hole', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = tool_obj

bpy.ops.object.select_all(action='DESELECT')
cuboid_obj.select_set(True)
bpy.context.view_layer.objects.active = cuboid_obj
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.data.objects.remove(tool_obj, do_unlink=True)

# --- 2. 创建独立的圆柱零件 ---
print("  - 创建圆柱零件...")
bpy.ops.mesh.primitive_cylinder_add(
    radius=1.0,
    depth=10.0,
    location=(4.0, 2.5, 5.0)
)
cylinder_obj = bpy.context.active_object
cylinder_obj.name = "Cylinder"

# 上色
mat_blue = bpy.data.materials.new(name="Blue")
mat_blue.diffuse_color = (0.1, 0.2, 0.8, 1.0)
if len(cylinder_obj.data.materials) == 0:
    cylinder_obj.data.materials.append(None)
cylinder_obj.data.materials[0] = mat_blue

print("装配体创建完毕。")

# --- 3. 脚本结束操作 ---
bpy.ops.object.select_all(action='DESELECT')
cuboid_obj.select_set(True)
cylinder_obj.select_set(True)
bpy.context.view_layer.objects.active = cuboid_obj

print("\n脚本执行完成。请在3D视图中按 '.' (小键盘) 来聚焦。")
