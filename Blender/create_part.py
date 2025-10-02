
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

# 创建长方体
print("正在创建长方体...")
bpy.ops.mesh.primitive_cube_add(
    size=1,
    location=(4.0, 2.5, 1.5)
)
# 调整尺寸
bpy.context.object.dimensions = (8, 5, 3)
print("长方体创建完毕。")

# 调整视图
set_view_to_fit()
