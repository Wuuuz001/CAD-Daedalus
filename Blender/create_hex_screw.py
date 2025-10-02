
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
bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=4, depth=3, location=(0, 0, 16.5)); head_obj = bpy.context.active_object
bpy.ops.mesh.primitive_cylinder_add(radius=1.5, depth=15, location=(0, 0, 7.5)); shaft_obj = bpy.context.active_object
bpy.ops.object.select_all(action='DESELECT'); head_obj.select_set(True); shaft_obj.select_set(True); bpy.context.view_layer.objects.active = head_obj; bpy.ops.object.join()