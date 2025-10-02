
import bpy

# ==============================================================================
# Blender 3D模型生成脚本 (由主生成器创建)
# ==============================================================================

def clear_scene():
    """清空场景中的所有网格对象。"""
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
        if block.users == 0: bpy.data.meshes.remove(block)

def set_view_to_fit():
    """调整视图以适应所有对象。"""
    bpy.ops.view3d.view_all()

# --- 主执行逻辑开始 ---
clear_scene()

# 创建六角螺母
print("正在创建六角螺母...")

# 1. 创建六棱柱主体
bpy.ops.mesh.primitive_cylinder_add(
    vertices=6,
    radius=4,
    depth=3,
    location=(0, 0, 1.5)
)
nut_obj = bpy.context.active_object

# 2. 创建用于打孔的圆柱
bpy.ops.mesh.primitive_cylinder_add(
    radius=1.5,
    depth=3.5999999999999996,  # 确保能完全穿透
    location=(0, 0, 1.5)
)
tool_obj = bpy.context.active_object

# 3. 使用布尔修改器进行减法操作
mod = nut_obj.modifiers.new(name="Hole", type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = tool_obj

# 应用修改器
bpy.context.view_layer.objects.active = nut_obj
bpy.ops.object.modifier_apply(modifier=mod.name)

# 删除工具对象
bpy.data.objects.remove(tool_obj, do_unlink=True)

print("六角螺母创建完毕。")

# 调整视图
set_view_to_fit()
