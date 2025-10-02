
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

# --- 创建最终装配体 (长方体在螺钉末端) ---
print("正在创建完整装配体 (新版)...")

# --- 1. 创建螺钉 (作为参考基准) ---
# 螺钉将被创建并定位，使其杆的尖端在 Z=0 附近
print("  - 1. 创建螺钉...")
bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=4, depth=3, location=(0, 0, 0))
head_obj = bpy.context.active_object
bpy.ops.mesh.primitive_cylinder_add(radius=1.5, depth=15, location=(0, 0, 0))
shaft_obj = bpy.context.active_object

# 先移动部件到相对于原点的位置，再合并
# 这样合并后的对象原点就在 (0,0,0)
head_obj.location.z = 16.5
shaft_obj.location.z = 7.5

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
bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=4, depth=3, location=(0,0,0))
nut_body_obj = bpy.context.active_object
bpy.ops.mesh.primitive_cylinder_add(radius=1.5, depth=3.5999999999999996, location=(0,0,0))
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
cuboid_obj.scale = (4.0, 2.5, 1.5)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
bpy.ops.mesh.primitive_cylinder_add(radius=1.5, depth=4.5, location=(0,0,0))
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
nut_z = 1.5
nut_obj.location = (0, 0, nut_z)

# b) 定位长方体: 它在螺母的正上方。其底部在 Z = nut_h 处。
cuboid_z = 3 + 1.5
cuboid_obj.location = (0, 0, cuboid_z)

# c) 定位螺钉: 它的原点(我们已设为杆的底部)应该和螺母底部对齐
screw_z = 0 
screw_obj.location = (0, 0, screw_z)

print("完整装配体 (新版) 创建完毕。")

# --- 5. 脚本结束操作 ---
bpy.ops.object.select_all(action='DESELECT')
cuboid_obj.select_set(True)
screw_obj.select_set(True)
nut_obj.select_set(True)
bpy.context.view_layer.objects.active = screw_obj

print("\n脚本执行完成。请在3D视图中按 '.' (小键盘) 来聚焦。")
