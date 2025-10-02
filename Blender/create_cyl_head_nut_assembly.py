
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

# --- 创建 螺钉-圆柱-螺母 装配体 ---
print("正在创建 螺钉-圆柱-螺母 装配体...")

# --- 策略：先在原点创建好各个独立的零件，最后统一移动到装配位置 ---
# --- 参考系：将圆柱体的底部平面设为 Z=0 ---

# --- 1. 创建带孔的中心圆柱体 ---
print("  - 1. 创建带孔圆柱...")
# 创建圆柱主体，使其底部在 Z=0
bpy.ops.mesh.primitive_cylinder_add(radius=3.0, depth=8.0, location=(0, 0, 4.0))
main_cyl_obj = bpy.context.active_object
main_cyl_obj.name = "Central_Cylinder"
# 创建打孔工具 (孔径与螺杆匹配)
bpy.ops.mesh.primitive_cylinder_add(radius=1.5, depth=9.6, location=(0, 0, 4.0))
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
bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=4, depth=3, location=(0, 0, 0))
head_obj = bpy.context.active_object
bpy.ops.mesh.primitive_cylinder_add(radius=1.5, depth=15, location=(0, 0, 0))
shaft_obj = bpy.context.active_object
# 先移动部件到相对于原点的位置，再合并
head_obj.location.z = 16.5
shaft_obj.location.z = 7.5
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
bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=4, depth=3, location=(0, 0, 0))
nut_body_obj = bpy.context.active_object
bpy.ops.mesh.primitive_cylinder_add(radius=1.5, depth=3.5999999999999996, location=(0, 0, 0))
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
main_cyl_obj.location = (0, 0, 4.0)

# b) 定位螺钉: 螺钉头的底部要紧贴圆柱的顶部 (Z=8.0)
# 螺钉原点在其头部中心，距离头部底面的距离是 screw_head_h / 2.0
screw_z_pos = 9.5
screw_obj.location = (0, 0, screw_z_pos)

# c) 定位螺母: 螺母的顶部要紧贴圆柱的底部 (Z=0)
# 螺母原点在其中心，距离其顶部的距离是 nut_h / 2.0
nut_z_pos = -1.5
nut_obj.location = (0, 0, nut_z_pos)


print("螺钉-圆柱-螺母 装配体创建完毕。")

# --- 5. 脚本结束操作 ---
bpy.ops.object.select_all(action='DESELECT')
main_cyl_obj.select_set(True)
screw_obj.select_set(True)
nut_obj.select_set(True)
bpy.context.view_layer.objects.active = main_cyl_obj

print("\n脚本执行完成。请在3D视图中按 '.' (小键盘) 来聚焦。")
