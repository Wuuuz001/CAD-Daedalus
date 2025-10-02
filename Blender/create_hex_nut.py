
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
bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=4, depth=3, location=(0, 0, 1.5)); nut_obj = bpy.context.active_object
bpy.ops.mesh.primitive_cylinder_add(radius=2.5, depth=3.5999999999999996, location=(0, 0, 1.5)); tool_obj = bpy.context.active_object
mod = nut_obj.modifiers.new(name='Hole', type='BOOLEAN'); mod.operation = 'DIFFERENCE'; mod.object = tool_obj; bpy.context.view_layer.objects.active = nut_obj; bpy.ops.object.modifier_apply(modifier=mod.name); bpy.data.objects.remove(tool_obj, do_unlink=True)