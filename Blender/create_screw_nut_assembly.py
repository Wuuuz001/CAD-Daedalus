
import bpy

def clear_scene():
    if bpy.ops.object.mode_set.poll(): bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
        if block.users == 0: bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0: bpy.data.materials.remove(block)

def set_view_to_fit():
    bpy.ops.view3d.view_all()

# --- 主执行逻辑开始 ---
clear_scene()

# --- 创建螺钉-螺母装配体 ---
print("正在创建装配体...")

# --- 1. 创建螺钉零件 ---
print("  - 创建螺钉...")
# 创建头部
bpy.ops.mesh.primitive_cylinder_add(
    vertices=6, radius=4, depth=3,
    location=(0, 0, 16.5)
)
head_obj = bpy.context.active_object
# 创建杆部
bpy.ops.mesh.primitive_cylinder_add(
    radius=1.5, depth=15,
    location=(0, 0, 7.5)
)
shaft_obj = bpy.context.active_object
# 合并成一个螺钉对象
bpy.ops.object.select_all(action='DESELECT')
head_obj.select_set(True)
shaft_obj.select_set(True)
bpy.context.view_layer.objects.active = head_obj
bpy.ops.object.join()
screw_obj = bpy.context.active_object
screw_obj.name = "Screw"

# --- 2. 创建螺母零件 ---
print("  - 创建螺母...")
# 创建螺母主体
bpy.ops.mesh.primitive_cylinder_add(
    vertices=6, radius=4, depth=3,
    location=(0, 0, 0) # 先在原点创建
)
nut_body_obj = bpy.context.active_object
# 创建打孔工具
bpy.ops.mesh.primitive_cylinder_add(
    radius=1.5, depth=3.5999999999999996,
    location=(0, 0, 0)
)
tool_obj = bpy.context.active_object
# 打孔
mod = nut_body_obj.modifiers.new(name='Hole', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = tool_obj
bpy.context.view_layer.objects.active = nut_body_obj
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.data.objects.remove(tool_obj, do_unlink=True)
nut_obj = nut_body_obj
nut_obj.name = "Nut"

# --- 3. 定位螺母 (装配) ---
print("  - 装配零件...")
# 将螺母移动到杆部的某个位置
nut_obj.location.z = 7.0 # 留出5个单位的间隙

print("装配体创建完毕。")

# 调整视图
set_view_to_fit()
