
import bpy

# ==============================================================================
# Blender - 创建圆柱体脚本 (最简可靠版)
#
# 使用方法:
# 1. 在Blender中打开此脚本。
# 2. 点击 "Run Script" 按钮。
#
# 这个脚本会先清空场景，然后创建一个圆柱体。
# ==============================================================================

# --- 1. 清空场景 ---
# 切换到对象模式以确保可以删除物体
if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')

# 选择场景中的所有对象
bpy.ops.object.select_all(action='SELECT')
# 删除所有被选中的对象
bpy.ops.object.delete(use_global=False)

# 清理孤立的数据块（好习惯）
for block in bpy.data.meshes:
    if block.users == 0:
        bpy.data.meshes.remove(block)

print("场景已清空。")

# --- 2. 创建圆柱体 ---
# 使用 bpy.ops.mesh.primitive_cylinder_add 命令
# 这是最直接、最像用户手动操作的方式。
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,  # 圆柱的平滑度，32是默认值
    radius=5.0,
    depth=20.0,
    location=(0, 0, 10.0)  # 将圆柱底部放在(ix, iy, 0)
)

print(f"已成功创建圆柱体！")
print(f"  - 半径 (Radius): 5.0")
print(f"  - 高度 (Height): 20.0")
print(f"  - 位置 (Location): (0, 0, 10.0)")

# --- 3. 调整视图 ---
# 让视图聚焦到所有对象上
bpy.ops.view3d.view_all()

print("\n脚本执行完毕。")

