import json
import math
import sys
import textwrap
import os
from dotenv import load_dotenv # 1. 导入 load_dotenv 函数

# --- 关键修复：使用绝对路径加载 .env ---
# 获取当前脚本文件所在的目录 (F:\cad.creat\0005)
current_dir = os.path.dirname(os.path.abspath(__file__))
# 构建 .env 文件的完整路径 (F:\cad.creat\0005\.env)
dotenv_path = os.path.join(current_dir, '.env')

# 检查 .env 文件是否存在并加载
if os.path.exists(dotenv_path):
    print(f"✅ 找到.env文件，正在从 '{dotenv_path}' 加载环境变量...")
    load_dotenv(dotenv_path=dotenv_path)
else:
    print(f"❌ [严重错误] 未在 '{dotenv_path}' 找到 .env 文件。请确认文件位置。")

# ==============================================================================
# 通用LISP代码生成模块
# ==============================================================================

# ==============================================================================
# 导入外部验证器模块
# ==============================================================================
try:
    from llm_validator import LLMValidator
    VALIDATOR_AVAILABLE = True
except ImportError:
    VALIDATOR_AVAILABLE = False
    print("[警告] 'llm_validator.py' 文件未找到，LLM验证功能将不可用。")

# 【已修正】这个函数现在可以动态创建所有需要的图层
def get_lisp_header(layers: dict, dim_opts: dict) -> str:
    """生成通用的LISP头部，现在能动态创建所有图层。"""
    layer_setup_commands = []
    # 创建一个包含所有图层信息的副本，并加入固定的参数表图层
    all_layers = layers.copy()
    all_layers['param_table'] = {'name': 'Parameter_Table', 'color': 7}

    for layer_info in all_layers.values():
        name = layer_info['name']
        color = layer_info['color']
        linetype = layer_info.get('linetype')  # 使用 .get() 安全地获取线型

        if linetype:
            # 如果指定了线型，先确保线型已加载，再创建图层
            cmd = (f'(if (not (tblsearch "LTYPE" "{linetype}")) '
                   f'(command "_.-LINETYPE" "_L" "{linetype}" "acad.lin" "" ""))'
                   f'(command "_.-LAYER" "_M" "{name}" "_C" "{color}" "" "_L" "{linetype}" "" "")')
        else:
            # 如果没有线型，只用名称和颜色创建图层
            cmd = f'(command "_.-LAYER" "_M" "{name}" "_C" "{color}" "" "")'
        layer_setup_commands.append(cmd)

    # 组合所有命令
    return textwrap.dedent(f"""
(defun C:DrawMyObject ()
  (command "_.UNDO" "Begin")
  (setvar "CMDECHO" 0)
  ;; --- 动态图层设置 ---
  {''.join(layer_setup_commands)}
  ;; --- 标注和系统变量设置 ---
  (setvar "LTSCALE" 5.0)
  (setvar "DIMTXT" {dim_opts['text_height']})
  (setvar "DIMASZ" {dim_opts['arrow_size']})
  (setvar "DIMCLRD" {layers['dimensions']['color']})
  (setvar "DIMCLRE" {layers['dimensions']['color']})
  (setvar "DIMCLRT" {layers['dimensions']['color']})
  (setvar "DIMDEC" 2)
""")


def get_lisp_footer(shape_name: str) -> str:
    """生成通用的LISP尾部。"""
    return f"""
  (setvar "CMDECHO" 1)(command "_.ZOOM" "_E")(command "_.UNDO" "End")
  (princ "\\n{shape_name} drawing completed!\\n")(princ))
(princ "\\nLISP file loaded. Type 'DrawMyObject' to run.")(princ)"""


def generate_lisp_utility_functions(layers: dict, dim_opts: dict) -> str:
    """生成用于绘制复杂标注和参数表的LISP辅助函数。"""
    annotations_layer = layers.get('annotations', {'name': 'Annotations', 'color': 6})
    dim_text_height = dim_opts.get('text_height', 3.5)
    lisp_functions_string = f"""
    ;; =============================================================================
    ;; == 辅助标注函数定义 (由Python生成)
    ;; =============================================================================
    (defun dtr (a) (* pi (/ a 180.0)))
    (defun draw-roughness-symbol (ins_pt text_val sym_size rotation / p1 p2 p3 p4 ang1 ang2 text_height text_pt) (setq text_height (* sym_size 0.4)) (setq ang1 (dtr (+ rotation 60.0))) (setq ang2 (dtr (+ rotation 120.0))) (setq p1 ins_pt) (setq p2 (polar p1 ang1 sym_size)) (setq p3 (polar p2 ang2 sym_size)) (setq p4 (polar p3 (dtr rotation) (* sym_size 1.5))) (command "_.-LAYER" "_S" "{annotations_layer['name']}" "") (command "_.PLINE" p1 p2 p3 "") (command "_.LINE" p3 p4 "") (setq text_pt (polar p2 (dtr (+ rotation 90)) (* text_height 0.4))) (command "_.TEXT" "_J" "_BL" text_pt text_height rotation text_val) )
    (defun draw-datum-symbol (attach_pt label_pt label / frame_size p1 p2) (setq frame_size (* {dim_text_height} 2.0)) (command "_.-LAYER" "_S" "{annotations_layer['name']}" "") (command "_.LEADER" attach_pt label_pt "" "" "_N") (setq p1 (list (- (car label_pt) (/ frame_size 2.0)) (- (cadr label_pt) (/ frame_size 2.0)))) (setq p2 (list (+ (car label_pt) (/ frame_size 2.0)) (+ (cadr label_pt) (/ frame_size 2.0)))) (command "_.RECTANG" p1 p2) (command "_.TEXT" "_J" "_MC" label_pt {dim_text_height} 0 (strcat "-" label "-")) )
    (defun draw-gdt-frame (attach_pt frame_loc gdt_sym tolerance datums leader_side / total_width current_x box_w box_h leader_start_pt) (setq box_w (* {dim_text_height} 2.5)) (setq box_h (* {dim_text_height} 2.0)) (setq current_x (car frame_loc)) (setq total_width (+ box_w (* box_w 2) (* (if datums (length datums) 0) box_w))) (command "_.-LAYER" "_S" "{annotations_layer['name']}" "") (if (or (not leader_side) (= (strcase leader_side) "LEFT")) (setq leader_start_pt (list (car frame_loc) (+ (cadr frame_loc) (/ box_h 2.0)))) (setq leader_start_pt (list (+ (car frame_loc) total_width) (+ (cadr frame_loc) (/ box_h 2.0))))) (command "_.LEADER" attach_pt leader_start_pt "" "" "_N") (command "_.RECTANG" (list current_x (cadr frame_loc)) (list (+ current_x box_w) (+ (cadr frame_loc) box_h))) (command "_.TEXT" "_J" "_MC" (list (+ current_x (/ box_w 2.0)) (+ (cadr frame_loc) (/ box_h 2.0))) {dim_text_height} 0 gdt_sym) (setq current_x (+ current_x box_w)) (command "_.RECTANG" (list current_x (cadr frame_loc)) (list (+ current_x (* box_w 2)) (+ (cadr frame_loc) box_h))) (command "_.TEXT" "_J" "_MC" (list (+ current_x box_w) (+ (cadr frame_loc) (/ box_h 2.0))) {dim_text_height} 0 tolerance) (setq current_x (+ current_x (* box_w 2))) (if datums (foreach datum datums (command "_.RECTANG" (list current_x (cadr frame_loc)) (list (+ current_x box_w) (+ (cadr frame_loc) box_h))) (command "_.TEXT" "_J" "_MC" (list (+ current_x (/ box_w 2.0)) (+ (cadr frame_loc) (/ box_h 2.0))) {dim_text_height} 0 datum) (setq current_x (+ current_x box_w)))) )
    (defun Draw-Parameter-Table (start_pt title data_list col_widths row_height text_height / num_rows total_height total_width header_height current_y p1 p2 p3 p4 text_mid_y row_data i col_div_x) (command "_.-LAYER" "_S" "Parameter_Table" "") (setq num_rows (length data_list)) (if (> num_rows 0) (progn (setq header_height (* row_height 1.5)) (setq total_height (+ header_height (* num_rows row_height))) (setq total_width (apply '+ col_widths)) (setq p1 start_pt) (setq p2 (list (+ (car p1) total_width) (cadr p1))) (setq p3 (list (+ (car p1) total_width) (- (cadr p1) total_height))) (setq p4 (list (car p1) (- (cadr p1) total_height))) (command "_.RECTANG" p1 p3) (command "_.LINE" (list (car p1) (- (cadr p1) header_height)) (list (car p2) (- (cadr p2) header_height)) "") (setq col_div_x (+ (car p1) (car col_widths))) (command "_.LINE" (list col_div_x (- (cadr p1) header_height)) (list col_div_x (cadr p3)) "") (setq text_mid_y (- (cadr p1) (/ header_height 2.0))) (command "_.TEXT" "_J" "_MC" (list (+ (car p1) (/ total_width 2.0)) text_mid_y) (* text_height 1.2) 0 title) (setq current_y (- (cadr p1) header_height)) (setq i 0) (foreach row_data data_list (setq text_mid_y (- current_y (/ row_height 2.0))) (command "_.TEXT" "_J" "_MC" (list (+ (car p1) (/ (car col_widths) 2.0)) text_mid_y) text_height 0 (car row_data)) (command "_.TEXT" "_J" "_MC" (list (+ col_div_x (/ (cadr col_widths) 2.0)) text_mid_y) text_height 0 (cadr row_data)) (setq current_y (- current_y row_height)) (setq i (1+ i)) (if (< i num_rows) (command "_.LINE" (list (car p1) current_y) (list (car p2) current_y) ""))) (princ))))
    (defun Draw-Bom-Table (start_pt title data_list col_widths row_height text_height / num_rows total_height total_width header_height current_y p1 p2 p3 p4 text_mid_y row_data i col_count current_x col_idx col_width temp_widths width) (command "_.-LAYER" "_S" "Parameter_Table" "" "") (setq num_rows (length data_list)) (setq col_count (length col_widths)) (if (> num_rows 0) (progn (setq header_height (* row_height 1.5)) (setq total_height (+ header_height (* num_rows row_height))) (setq total_width (apply '+ col_widths)) (setq p1 start_pt) (setq p2 (list (+ (car p1) total_width) (cadr p1))) (setq p3 (list (+ (car p1) total_width) (- (cadr p1) total_height))) (setq p4 (list (car p1) (- (cadr p1) total_height))) (command "_.RECTANG" p1 p3) (command "_.LINE" (list (car p1) (- (cadr p1) header_height)) (list (car p2) (- (cadr p2) header_height)) "") (setq current_x (car p1)) (setq temp_widths col_widths) (while (setq width (car temp_widths)) (setq current_x (+ current_x width)) (setq temp_widths (cdr temp_widths)) (if temp_widths (command "_.LINE" (list current_x (cadr p1)) (list current_x (cadr p3)) ""))) (setq text_mid_y (- (cadr p1) (/ header_height 2.0))) (command "_.TEXT" "_J" "_MC" (list (+ (car p1) (/ total_width 2.0)) text_mid_y) (* text_height 1.2) 0 title) (setq current_y (- (cadr p1) header_height)) (setq i 0) (foreach row_data data_list (setq text_mid_y (- current_y (/ row_height 2.0))) (setq current_x (car p1)) (setq col_idx 0) (foreach item row_data (setq col_width (nth col_idx col_widths)) (command "_.TEXT" "_J" "_MC" (list (+ current_x (/ col_width 2.0)) text_mid_y) text_height 0 (vl-princ-to-string item)) (setq current_x (+ current_x col_width)) (setq col_idx (1+ col_idx))) (setq current_y (- current_y row_height)) (setq i (1+ i)) (if (< i num_rows) (command "_.LINE" (list (car p1) current_y) (list (car p2) current_y) ""))) (princ))) )
    (defun Draw-Balloon (center_pt radius text_val text_height) (command "_.-LAYER" "_S" "{annotations_layer['name']}" "") (command "_.CIRCLE" center_pt radius) (command "_.TEXT" "_J" "_MC" center_pt text_height 0 text_val))
    """
    return textwrap.dedent(lisp_functions_string)


# ==============================================================================
# 参数表/BOM表 辅助函数
# ==============================================================================
def _generate_lisp_for_parameter_table(params: dict, dim_opts: dict, right_most_x: float, top_y: float,
                                       spacing: float) -> str:
    def escape(s):
        return str(s).replace('\\', '\\\\').replace('"', '\\"')

    flat_params = {}
    for key, value in params.items():
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                flat_key = f"{key}_{sub_key}".replace('_', ' ').title()
                flat_params[flat_key] = sub_value
        else:
            flat_key = key.replace('_', ' ').title()
            flat_params[flat_key] = value

    if not flat_params: return ""
    list_items = [f'(list "{escape(k)}" "{escape(v)}")' for k, v in flat_params.items()]
    lisp_data_list = f"(list {' '.join(list_items)})"
    table_start_x = right_most_x + spacing
    table_start_y = top_y
    text_height = dim_opts.get('text_height', 3.5)

    return f"""
  ;; --- 绘制参数表 (调用原始的Draw-Parameter-Table) ---
  (setq table_start_pt (list {table_start_x} {table_start_y}))
  (setq param_data {lisp_data_list})
  (Draw-Parameter-Table table_start_pt "Parameter List" param_data '(150 80) 15 {text_height})
"""


def _generate_lisp_for_bom_table(components: dict, dim_opts: dict, right_most_x: float, top_y: float,
                                 spacing: float) -> str:
    if not components: return ""
    rows = []
    item_num = 1
    for key, val in components.items():
        part_name = val.get('name', key.replace('_', ' ').title())
        quantity = val.get('quantity', 1)
        rows.append(f'(list "{item_num}" "{part_name}" "{quantity}")')
        item_num += 1
    lisp_data_list = f"(list {' '.join(rows)})"
    table_start_x = right_most_x + spacing
    table_start_y = top_y
    text_height = dim_opts.get('text_height', 3.5)
    return f"""
  ;; --- 绘制物料清单 (调用新的Draw-Bom-Table) ---
  (setq table_start_pt (list {table_start_x} {table_start_y}))
  (setq bom_data {lisp_data_list})
  (Draw-Bom-Table table_start_pt "Bill of Materials" bom_data '(40 150 50) 15 {text_height})
"""


# ==============================================================================
# 零件生成函数 (为简洁省略重复的函数体)
# ==============================================================================
def generate_lisp_for_cylinder(data: dict) -> str:
    # ... 此处代码与您提供的版本完全相同 ...
    params, opts = data['parameters'], data['drawing_options']
    layers, dim_opts = opts['layers'], opts['dimension_options']
    surface_finish, gts, datums = data.get('surface_finish', {}), data.get('geometric_tolerances', []), data.get(
        'datums', [])
    radius, height = params['radius'], params['height']
    ix, iy = opts['insertion_point']
    spacing = opts['spacing']
    front_p1_x, front_p1_y, front_p2_x, front_p2_y = ix, iy, ix + 2 * radius, iy + height
    right_p1_x, right_p2_x = ix + 2 * radius + spacing, ix + 4 * radius + spacing
    top_center_x, top_center_y = ix + radius, iy + height + spacing + radius
    right_view_center_x = right_p1_x + (right_p2_x - right_p1_x) / 2
    lisp_code = get_lisp_header(layers, dim_opts) + generate_lisp_utility_functions(layers, dim_opts)
    lisp_code += f"""
  (command "_.-LAYER" "_S" "{layers['outline']['name']}" "")(command "_.RECTANG" "{front_p1_x},{front_p1_y}" "{front_p2_x},{front_p2_y}")(command "_.RECTANG" "{right_p1_x},{iy}" "{right_p2_x},{iy + height}")(command "_.CIRCLE" "{top_center_x},{top_center_y}" "{radius}")
  (command "_.-LAYER" "_S" "{layers['centerline']['name']}" "")(command "_.LINE" "{ix + radius},{iy - 10}" "{ix + radius},{iy + height + 10}" "")(command "_.LINE" "{ix - 10},{top_center_y}" "{ix + 2 * radius + 10},{top_center_y}" "")(command "_.LINE" "{top_center_x},{top_center_y - radius - 10}" "{top_center_x},{top_center_y + radius + 10}" "")(command "_.LINE" "{right_view_center_x},{iy - 10}" "{right_view_center_x},{iy + height + 10}" "")(command "_.LINE" "{ix - 10},{iy + height / 2}" "{right_p2_x + 10},{iy + height / 2}" "")
  (command "_.-LAYER" "_S" "{layers['dimensions']['name']}" "")(command "_.DIMLINEAR" "{ix},{iy}" "{ix},{iy + height}" "_T" "<>{params.get('height_tolerance', '')}" "{ix - 20 - spacing / 2},{iy + height / 2}")(command "_.DIMLINEAR" "{top_center_x - radius},{top_center_y}" "{top_center_x + radius},{top_center_y}" "_T" "%%c<>{params.get('diameter_tolerance', '')}" "{top_center_x},{top_center_y + radius + 20}")"""
    lisp_code += "\n  ;; --- 高级标注 ---\n"
    for datum in datums:
        if datum['attach_face'] == 'bottom':
            lisp_code += f'  (draw-datum-symbol (list {front_p1_x + radius} {front_p1_y}) (list {front_p1_x + radius} {front_p1_y - 20}) "{datum["label"]}")\n'
        elif datum['attach_face'] == 'centerline':
            lisp_code += f'  (draw-datum-symbol (list {right_p1_x} {iy + height / 2}) (list {right_p1_x - 20} {iy + height / 2 - 10}) "{datum["label"]}")\n'
    gdt_symbols = {"perpendicularity": "\\\\U+22A5", "parallelism": "\\\\U+2225"}
    for gdt in gts:
        symbol_str = gdt_symbols.get(gdt["type"], "?")
        datums_str = " ".join([f'"{d}"' for d in gdt.get('datum_references', [])])
        datum_arg = f"(list {datums_str})" if datums_str else "nil"
        box_h = dim_opts['text_height'] * 2.0
        if gdt['leader_attach_point'] == 'left_side':
            lisp_code += f'  (draw-gdt-frame (list {front_p1_x} {front_p1_y + height / 2}) (list {front_p1_x - 40} {front_p1_y + height / 2 - box_h / 2}) "{symbol_str}" "{gdt["tolerance"]}" {datum_arg} "RIGHT")\n'
        elif gdt['leader_attach_point'] == 'right_side':
            lisp_code += f'  (draw-gdt-frame (list {right_p2_x} {iy + height / 2}) (list {right_p2_x + 20} {iy + height / 2 - box_h / 2}) "{symbol_str}" "{gdt["tolerance"]}" {datum_arg} "LEFT")\n'
    if 'side_surface' in surface_finish: ss = surface_finish[
        'side_surface']; lisp_code += f'  (draw-roughness-symbol (list {right_p2_x} {iy + height / 2}) "{ss[0]}" {ss[2]} {ss[1]})\n'
    if 'top_surface' in surface_finish: ts = surface_finish[
        'top_surface']; lisp_code += f'  (draw-roughness-symbol (list {front_p1_x + radius} {front_p2_y}) "{ts[0]}" {ts[2]} {ts[1]})\n'
    lisp_code += _generate_lisp_for_parameter_table(params, dim_opts, right_p2_x, 100, spacing)
    lisp_code += get_lisp_footer("Cylinder")
    return lisp_code

def generate_lisp_for_hex_nut(data: dict) -> str:
    # ... 此处代码与您提供的版本完全相同 ...
    params, opts = data['parameters'], data['drawing_options']
    layers, dim_opts = opts['layers'], opts['dimension_options']
    side_length, height, hole_diameter = params['side_length'], params['height'], params['hole']['diameter']
    hole_radius = hole_diameter / 2.0
    ix, iy = opts['insertion_point']
    spacing = opts['spacing']
    hatch_opts = opts.get('hatch_options', {'pattern': 'ANSI31', 'scale': 15.0})
    datums, gts, finish = data.get('datums', []), data.get('geometric_tolerances', []), data.get('surface_finish', {})
    flat_distance, vertex_distance, inner_edge_radius = side_length * math.sqrt(3), 2 * side_length, side_length / 2.0
    front_view_width, front_center_x = vertex_distance, ix + vertex_distance / 2
    right_view_width, right_start_x, right_center_x = flat_distance, ix + front_view_width + spacing, ix + front_view_width + spacing + flat_distance / 2
    top_view_center_y, top_view_bottom_y = iy + height + spacing + vertex_distance / 2, iy + height + spacing + vertex_distance / 2 - flat_distance / 2
    top_view_center = f"{front_center_x},{top_view_center_y}"
    section_start_y, section_center_x = iy + height + spacing, right_start_x + vertex_distance / 2
    lisp_code = get_lisp_header(layers, dim_opts)
    lisp_code += generate_lisp_utility_functions(layers, dim_opts)
    hatch_pick_points_str = ' '.join(
        [f'"{section_center_x - (hole_radius + inner_edge_radius) / 2},{section_start_y + height / 2}"',
         f'"{section_center_x + (hole_radius + inner_edge_radius) / 2},{section_start_y + height / 2}"',
         f'"{section_center_x - (inner_edge_radius + side_length) / 2},{section_start_y + height / 2}"',
         f'"{section_center_x + (inner_edge_radius + side_length) / 2},{section_start_y + height / 2}"']) if hole_radius < inner_edge_radius else ' '.join(
        [f'"{section_center_x - (hole_radius + side_length) / 2},{section_start_y + height / 2}"',
         f'"{section_center_x + (hole_radius + side_length) / 2},{section_start_y + height / 2}"'])
    lisp_code += f"""
  (command "_.-LAYER" "_S" "{layers['outline']['name']}" "")(command "_.POLYGON" "6" "{top_view_center}" "_Inscribed" "{side_length}")(command "_.CIRCLE" "{top_view_center}" "{hole_radius}")(command "_.RECTANG" "{ix},{iy}" "{ix + front_view_width},{iy + height}")(command "_.LINE" "{front_center_x - inner_edge_radius},{iy}" "{front_center_x - inner_edge_radius},{iy + height}" "")(command "_.LINE" "{front_center_x + inner_edge_radius},{iy}" "{front_center_x + inner_edge_radius},{iy + height}" "")(command "_.RECTANG" "{right_start_x},{iy}" "{right_start_x + right_view_width},{iy + height}")(command "_.LINE" "{right_center_x},{iy}" "{right_center_x},{iy + height}" "")
  (command "_.-LAYER" "_S" "{layers['hidden']['name']}" "")(command "_.LINE" "{front_center_x - hole_radius},{iy}" "{front_center_x - hole_radius},{iy + height}" "")(command "_.LINE" "{front_center_x + hole_radius},{iy}" "{front_center_x + hole_radius},{iy + height}" "")(command "_.LINE" "{right_center_x - hole_radius},{iy}" "{right_center_x - hole_radius},{iy + height}" "")(command "_.LINE" "{right_center_x + hole_radius},{iy}" "{right_center_x + hole_radius},{iy + height}" "")
  (command "_.-LAYER" "_S" "{layers['outline']['name']}" "")(command "_.RECTANG" "{right_start_x},{section_start_y}" "{right_start_x + vertex_distance},{section_start_y + height}")(command "_.LINE" "{section_center_x - hole_radius},{section_start_y}" "{section_center_x - hole_radius},{section_start_y + height}" "")(command "_.LINE" "{section_center_x + hole_radius},{section_start_y}" "{section_center_x + hole_radius},{section_start_y + height}" "")
  (command "_.-LAYER" "_S" "{layers['outline_hidden']['name']}" "")(command "_.LINE" "{section_center_x - inner_edge_radius},{section_start_y}" "{section_center_x - inner_edge_radius},{section_start_y + height}" "")(command "_.LINE" "{section_center_x + inner_edge_radius},{section_start_y}" "{section_center_x + inner_edge_radius},{section_start_y + height}" "")
  (command "_.SETVAR" "HPNAME" "{hatch_opts['pattern']}")(command "_.SETVAR" "HPSCALE" {hatch_opts['scale']})(command "_-HATCH" {hatch_pick_points_str} "")
  (command "_.-LAYER" "_S" "{layers['centerline']['name']}" "")(command "_.LINE" "{front_center_x},{iy - 5}" "{front_center_x},{iy + height + 5}" "")(command "_.LINE" "{ix - 5},{top_view_center_y}" "{ix + vertex_distance + 5},{top_view_center_y}" "")(command "_.LINE" "{front_center_x},{iy + height + spacing - 5}" "{front_center_x},{top_view_center_y + vertex_distance / 2 + 5}" "")(command "_.LINE" "{section_center_x},{section_start_y - 5}" "{section_center_x},{section_start_y + height + 5}" "")
  (command "_.-LAYER" "_S" "{layers['dimensions']['name']}" "")(command "_.DIMLINEAR" "{ix},{iy}" "{ix},{iy + height}" "_T" "<>{params.get('height_tolerance', '')}" "{ix - spacing / 2},{iy + height / 2}")(command "_.DIMLINEAR" "{ix},{iy + height}" "{ix + vertex_distance},{iy + height}" "{front_center_x},{iy + height + spacing / 2}")(command "_.DIMLINEAR" "{front_center_x - hole_radius},{top_view_center_y}" "{front_center_x + hole_radius},{top_view_center_y}" "_T" "%%c<>{params['hole'].get('diameter_tolerance', '')}" "{front_center_x},{top_view_center_y + vertex_distance / 2 + spacing / 2}")(command "_.DIMLINEAR" "{front_center_x - side_length / 2},{top_view_bottom_y}" "{front_center_x + side_length / 2},{top_view_bottom_y}" "_T" "<>{params.get('side_length_tolerance', '')}" "{front_center_x},{top_view_bottom_y - spacing / 2}")"""
    lisp_code += "\n  ;; --- 高级标注 ---\n"
    gdt_symbols = {"perpendicularity": "\\\\U+22A5", "parallelism": "\\\\U+2225", "flatness": "\\\\U+25B1",
                   "position": "\\\\U+2316"}
    for datum in datums:
        if datum.get('attach_face') == 'bottom':
            lisp_code += f'  (draw-datum-symbol (list {front_center_x} {iy}) (list {front_center_x} {iy - 20}) "{datum["label"]}")\n'
        elif datum.get('attach_face') == 'side_face_right_view':
            lisp_code += f'  (draw-datum-symbol (list {right_start_x + right_view_width} {iy + height / 2}) (list {right_start_x + right_view_width + 20} {iy + height / 2}) "{datum["label"]}")\n'
        elif datum.get('attach_face') == 'inner_hole_top_view':
            lisp_code += f'  (draw-datum-symbol (list {front_center_x + hole_radius} {top_view_center_y}) (list {front_center_x + hole_radius + 60} {top_view_center_y}) "{datum["label"]}")\n'
    for gdt in gts:
        symbol_str = gdt_symbols.get(gdt["type"], "?")
        datums_str = " ".join([f'"{d}"' for d in gdt.get('datum_references', [])])
        datum_arg = f"(list {datums_str})" if datums_str else "nil"
        if gdt.get('attach_to') == 'side_face_of_right_view':
            lisp_code += f'  (draw-gdt-frame (list {right_start_x + right_view_width} {iy + height * 0.75}) (list {right_start_x + right_view_width + 10} {iy + height * 0.75}) "{symbol_str}" "{gdt["tolerance"]}" {datum_arg} "LEFT")\n'
        elif gdt.get('attach_to') == 'side_face_of_front_view':
            lisp_code += f'  (draw-gdt-frame (list {ix} {iy + height * 0.25}) (list {ix - 100} {iy + height * 0.25}) "{symbol_str}" "{gdt["tolerance"]}" {datum_arg} "RIGHT")\n'
        elif gdt.get('attach_to') == 'inner_hole_top_view':
            lisp_code += f'  (draw-gdt-frame (list {front_center_x + hole_radius} {top_view_center_y}) (list {ix + 100} {top_view_center_y + 30}) "{symbol_str}" "{gdt["tolerance"]}" {datum_arg} "LEFT")\n'
    for key, val in finish.items():
        if key == 'top_face':
            lisp_code += f'  (draw-roughness-symbol (list {front_center_x} {iy + height}) "{val[0]}" {val[2]} {val[1]})\n'
        elif key == 'side_face_right_view':
            lisp_code += f'  (draw-roughness-symbol (list {right_start_x + right_view_width} {iy + height / 2}) "{val[0]}" {val[2]} {val[1]})\n'
        elif key == 'inner_hole_top_view':
            lisp_code += f'  (draw-roughness-symbol (list {front_center_x + hole_radius * math.cos(math.radians(45))} {top_view_center_y + hole_radius * math.sin(math.radians(45))}) "{val[0]}" {val[2]} {val[1]})\n'

    table_x, table_y = right_start_x + right_view_width, iy + height
    lisp_code += _generate_lisp_for_parameter_table(params, dim_opts, table_x, 100, spacing)
    lisp_code += get_lisp_footer("Hexagonal Nut")
    return lisp_code

def generate_lisp_for_hex_prism(data: dict) -> str:
    # ... 此处代码与您提供的版本完全相同 ...
    params, opts = data['parameters'], data['drawing_options']
    layers, dim_opts = opts['layers'], opts['dimension_options']
    datums, gts, finish = data.get('datums', []), data.get('geometric_tolerances', []), data.get('surface_finish', {})
    side_length, height = params['side_length'], params['height']
    height_tol, width_tol = params.get('height_tolerance', ''), params.get('width_tolerance', '')
    ix, iy = opts['insertion_point']
    spacing = opts['spacing']
    flat_distance, vertex_distance = side_length * math.sqrt(3), 2 * side_length
    front_w, front_cx = vertex_distance, ix + vertex_distance / 2
    right_w, right_sx, right_cx = flat_distance, ix + front_w + spacing, ix + front_w + spacing + flat_distance / 2
    top_cx, top_cy = front_cx, iy + height + spacing + side_length
    lisp_code = get_lisp_header(layers, dim_opts)
    lisp_code += generate_lisp_utility_functions(layers, dim_opts)
    lisp_code += f"""
  (command "_.-LAYER" "_S" "{layers['outline']['name']}" "")(command "_.POLYGON" "6" "{top_cx},{top_cy}" "_Inscribed" "{side_length}")(command "_.RECTANG" "{ix},{iy}" "{ix + front_w},{iy + height}")(command "_.LINE" "{front_cx - side_length / 2},{iy}" "{front_cx - side_length / 2},{iy + height}" "")(command "_.LINE" "{front_cx + side_length / 2},{iy}" "{front_cx + side_length / 2},{iy + height}" "")(command "_.RECTANG" "{right_sx},{iy}" "{right_sx + right_w},{iy + height}")(command "_.LINE" "{right_cx},{iy}" "{right_cx},{iy + height}" "")
  (command "_.-LAYER" "_S" "{layers['centerline']['name']}" "")(command "_.LINE" "{front_cx},{iy - 25}" "{front_cx},{top_cy + side_length + 10}" "")(command "_.LINE" "{right_cx},{iy - 45}" "{right_cx},{iy + height + 10}" "")(command "_.LINE" "{ix - 10},{iy + height / 2}" "{right_sx + right_w + 45},{iy + height / 2}" "")(command "_.LINE" "{top_cx - side_length - 10},{top_cy}" "{top_cx + side_length + 10},{top_cy}" "")
  (command "_.-LAYER" "_S" "{layers['dimensions']['name']}" "")(command "_.DIMLINEAR" "{ix},{iy}" "{ix},{iy + height}" "_T" "<>{height_tol}" "{ix - 30},{iy + height / 2}")(command "_.DIMLINEAR" "{ix},{iy + height}" "{ix + front_w},{iy + height}" "_T" "{vertex_distance:.2f}{width_tol}" "{front_cx},{iy + height + 20}")(command "_.DIMLINEAR" "{top_cx - side_length / 2},{top_cy + side_length * math.sqrt(3) / 2}" "{top_cx + side_length / 2},{top_cy + side_length * math.sqrt(3) / 2}" "_T" "{side_length:.2f}" "{top_cx},{top_cy + side_length * math.sqrt(3) / 2 + 20}")(command "_.DIMLINEAR" "{right_sx},{iy}" "{right_sx + right_w},{iy}" "_T" "{flat_distance:.2f}" "{right_cx},{iy - 40}")"""
    lisp_code += "\n  ;; --- 高级标注 ---\n"
    gdt_symbols = {"perpendicularity": "\\\\U+22A5", "parallelism": "\\\\U+2225"}
    for datum in datums:
        if datum['attach_to'] == 'front_view_centerline_bottom':
            lisp_code += f'  (draw-datum-symbol (list {front_cx} {iy}) (list {front_cx} {iy - 20}) "{datum["label"]}")\n'
        elif datum['attach_to'] == 'right_view_right_side_midpoint':
            lisp_code += f'  (draw-datum-symbol (list {right_sx + right_w} {iy + height / 2}) (list {right_sx + right_w + 40} {iy + height / 2}) "{datum["label"]}")\n'
    for gdt in gts:
        symbol_str = gdt_symbols.get(gdt["type"], "?")
        datums_str = " ".join([f'"{d}"' for d in gdt.get('datum_references', [])])
        datum_arg = f"(list {datums_str})" if datums_str else "nil"
        box_h, frame_w = dim_opts['text_height'] * 2.0, dim_opts['text_height'] * 7.5
        if gdt['attach_to'] == 'front_view_left_side':
            lisp_code += f'  (draw-gdt-frame (list {ix} {iy + height / 2}) (list {ix - 40 - frame_w} {iy + height / 2 - box_h / 2}) "{symbol_str}" "{gdt["tolerance"]}" {datum_arg} "RIGHT")\n'
        elif gdt['attach_to'] == 'right_view_top_surface':
            lisp_code += f'  (draw-gdt-frame (list {right_sx + right_w} {iy + height}) (list {right_sx + right_w + 15} {iy + height - box_h * 1.5}) "{symbol_str}" "{gdt["tolerance"]}" {datum_arg} "LEFT")\n'
    if 'top_surface' in finish: ts = finish[
        'top_surface']; lisp_code += f'  (draw-roughness-symbol (list {front_cx + side_length / 2 + 10} {iy + height}) "{ts[0]}" {ts[2]} {ts[1]})\n'
    lisp_code += _generate_lisp_for_parameter_table(params, dim_opts, right_sx + right_w, 100, spacing)
    return lisp_code + get_lisp_footer("Hexagonal Prism")

def generate_lisp_for_hex_screw(data: dict) -> str:
    # ... 此处代码与您提供的版本完全相同 ...
    params, opts = data['parameters'], data['drawing_options']
    layers, dim_opts = opts['layers'], opts['dimension_options']
    datums, gts, finish = data.get('datums', []), data.get('geometric_tolerances', []), data.get('surface_finish', {})
    head, shaft = params['head'], params['shaft']
    side_length, head_height, shaft_dia, shaft_len = head['side_length'], head['height'], shaft['diameter'], shaft[
        'length']
    height_tol, width_tol = params.get('total_height_tolerance', ''), params.get('head_width_tolerance', '')
    ix, iy = opts['insertion_point']
    spacing = opts['spacing']
    shaft_rad, total_h = shaft_dia / 2.0, head_height + shaft_len
    flat_dist, vertex_dist = side_length * math.sqrt(3), 2 * side_length
    front_w, front_cx = vertex_dist, ix + vertex_dist / 2
    right_w, right_sx, right_cx = flat_dist, ix + front_w + spacing, ix + front_w + spacing + flat_dist / 2
    top_cy, top_center_str = iy + total_h + spacing + side_length, f"{front_cx},{iy + total_h + spacing + side_length}"
    lisp_code = get_lisp_header(layers, dim_opts)
    lisp_code += generate_lisp_utility_functions(layers, dim_opts)
    lisp_code += f"""
  (command "_.-LAYER" "_S" "{layers['outline']['name']}" "")(command "_.POLYGON" "6" "{top_center_str}" "_Inscribed" "{side_length}")(command "_.CIRCLE" "{top_center_str}" "{shaft_rad}")(command "_.RECTANG" "{ix},{iy + shaft_len}" "{ix + front_w},{iy + total_h}")(command "_.RECTANG" "{front_cx - shaft_rad},{iy}" "{front_cx + shaft_rad},{iy + shaft_len}")(command "_.LINE" "{front_cx - side_length / 2},{iy + shaft_len}" "{front_cx - side_length / 2},{iy + total_h}" "")(command "_.LINE" "{front_cx + side_length / 2},{iy + shaft_len}" "{front_cx + side_length / 2},{iy + total_h}" "")(command "_.RECTANG" "{right_sx},{iy + shaft_len}" "{right_sx + right_w},{iy + total_h}")(command "_.RECTANG" "{right_cx - shaft_rad},{iy}" "{right_cx + shaft_rad},{iy + shaft_len}")(command "_.LINE" "{right_cx},{iy + shaft_len}" "{right_cx},{iy + total_h}" "")
  (command "_.-LAYER" "_S" "{layers['centerline']['name']}" "")(command "_.LINE" "{front_cx},{iy - 25}" "{front_cx},{top_cy + 25}" "")(command "_.LINE" "{right_cx},{iy - 10}" "{right_cx},{iy + total_h + 10}" "")(command "_.LINE" "{ix - 10},{iy + total_h / 2}" "{right_sx + right_w + 10},{iy + total_h / 2}" "")
  (command "_.-LAYER" "_S" "{layers['dimensions']['name']}" "")(command "_.DIMLINEAR" "{ix},{iy}" "{ix},{iy + total_h}" "_T" "<>{height_tol}" "{ix - 30},{iy + total_h / 2}")(command "_.DIMLINEAR" "{ix},{iy + total_h}" "{ix + vertex_dist},{iy + total_h}" "_T" "{vertex_dist:.2f}{width_tol}" "{front_cx},{iy + total_h + 20}")(command "_.DIMLINEAR" "{front_cx - shaft_rad},{iy}" "{front_cx + shaft_rad},{iy}" "_T" "%%c<>" "{front_cx},{iy - 20}")(command "_.DIMLINEAR" "{right_sx},{iy + total_h}" "{right_sx + right_w},{iy + total_h}" "_T" "{flat_dist:.2f}" "{right_cx},{iy + total_h + 20}")"""
    lisp_code += "\n  ;; --- 高级标注 ---\n"
    gdt_symbols = {"perpendicularity": "\\\\U+22A5", "parallelism": "\\\\U+2225"}
    for datum in datums:
        if datum['attach_to'] == 'bottom_surface':
            lisp_code += f'  (draw-datum-symbol (list {front_cx} {iy}) (list {front_cx} {iy - 20}) "{datum["label"]}")\n'
        elif datum['attach_to'] == 'centerline_of_right_view':
            lisp_code += f'  (draw-datum-symbol (list {right_sx} {iy + total_h / 2}) (list {right_sx - 20} {iy + total_h / 2}) "{datum["label"]}")\n'
    for gdt in gts:
        symbol_str = gdt_symbols.get(gdt["type"], "?")
        datums_str = " ".join([f'"{d}"' for d in gdt.get('datum_references', [])])
        datum_arg = f"(list {datums_str})" if datums_str else "nil"
        box_h, frame_w = dim_opts['text_height'] * 2.0, dim_opts['text_height'] * 7.5
        if gdt['attach_to'] == 'front_view_left_side_of_head':
            lisp_code += f'  (draw-gdt-frame (list {ix} {iy + shaft_len + head_height / 2}) (list {ix - 40 - frame_w} {iy + shaft_len + head_height / 2 - box_h / 2}) "{symbol_str}" "{gdt["tolerance"]}" {datum_arg} "RIGHT")\n'
        elif gdt['attach_to'] == 'right_view_top_surface':
            lisp_code += f'  (draw-gdt-frame (list {right_cx} {iy + total_h}) (list {right_sx + right_w + 15} {iy + total_h - box_h / 2}) "{symbol_str}" "{gdt["tolerance"]}" {datum_arg} "LEFT")\n'
    if 'top_surface' in finish: ts = finish[
        'top_surface']; lisp_code += f'  (draw-roughness-symbol (list {front_cx} {iy + total_h}) "{ts[0]}" {ts[2]} {ts[1]})\n'
    if 'side_surface' in finish: ss = finish[
        'side_surface']; lisp_code += f'  (draw-roughness-symbol (list {right_sx + right_w} {iy + shaft_len + head_height / 2}) "{ss[0]}" {ss[2]} {ss[1]})\n'
    lisp_code += _generate_lisp_for_parameter_table(params, dim_opts, right_sx + right_w, 100, spacing)
    return lisp_code + get_lisp_footer("Hexagonal Screw")

def generate_lisp_for_cuboid(data: dict) -> str:
    # ... 此处代码与您提供的版本完全相同 ...
    params, opts = data['parameters'], data['drawing_options']
    layers, dim_opts = opts['layers'], opts['dimension_options']
    datums, gts, finish = data.get('datums', []), data.get('geometric_tolerances', []), data.get('surface_finish', {})
    length, width, height = params['length'], params['width'], params['height']
    ix, iy = opts['insertion_point']
    spacing = opts['spacing']
    front_p1, front_p2 = (ix, iy), (ix + length, iy + height)
    top_p1, top_p2 = (ix, iy + height + spacing), (ix + length, iy + height + spacing + width)
    side_p1, side_p2 = (ix + length + spacing, iy), (ix + length + spacing + width, iy + height)
    lisp_code = get_lisp_header(layers, dim_opts)
    lisp_code += generate_lisp_utility_functions(layers, dim_opts)
    lisp_code += f"""
  (command "_.-LAYER" "_S" "{layers['outline']['name']}" "")(command "_.RECTANG" (list {front_p1[0]} {front_p1[1]}) (list {front_p2[0]} {front_p2[1]}))(command "_.RECTANG" (list {top_p1[0]} {top_p1[1]}) (list {top_p2[0]} {top_p2[1]}))(command "_.RECTANG" (list {side_p1[0]} {side_p1[1]}) (list {side_p2[0]} {side_p2[1]}))
  (command "_.-LAYER" "_S" "{layers['centerline']['name']}" "")(command "_.LINE" (list {ix + length / 2} {iy - 10}) (list {ix + length / 2} {top_p2[1] + 10}) "")(command "_.LINE" (list {ix - 10} {iy + height / 2}) (list {side_p2[0] + 10} {iy + height / 2}) "")(command "_.LINE" (list {ix - 10} {top_p1[1] + width / 2}) (list {top_p2[0] + 10} {top_p1[1] + width / 2}) "")(command "_.LINE" (list {side_p1[0] + width / 2} {iy - 10}) (list {side_p1[0] + width / 2} {iy + height + 10}) "")
  (command "_.-LAYER" "_S" "{layers['dimensions']['name']}" "")(command "_.DIMLINEAR" (list {front_p1[0]} {front_p1[1]}) (list {front_p1[0]} {front_p2[1]}) (list {front_p1[0] - spacing / 2} {iy + height / 2}))(command "_.DIMLINEAR" (list {front_p1[0]} {front_p1[1]}) (list {front_p2[0]} {front_p1[1]}) (list {ix + length / 2} {iy - spacing / 2}))(command "_.DIMLINEAR" (list {side_p1[0]} {side_p1[1]}) (list {side_p2[0]} {side_p1[1]}) (list {side_p1[0] + width / 2} {iy - spacing / 2}))"""
    lisp_code += "\n  ;; --- 高级标注 ---\n"
    gdt_symbols = {"perpendicularity": "\\\\U+22A5", "parallelism": "\\\\U+2225", "flatness": "\\\\U+25AF"}
    for datum in datums:
        if datum['attach_to'] == 'front_view_bottom_mid':
            lisp_code += f'  (draw-datum-symbol (list {ix + length / 2} {iy}) (list {ix + length / 2} {iy - 20}) "{datum["label"]}")\n'
        elif datum['attach_to'] == 'side_view_left_mid':
            lisp_code += f'  (draw-datum-symbol (list {side_p1[0]} {iy + height / 2}) (list {side_p1[0] - 20} {iy + height / 2}) "{datum["label"]}")\n'
    for gdt in gts:
        symbol_str = gdt_symbols.get(gdt["type"], "?")
        datums_str = " ".join([f'"{d}"' for d in gdt.get('datum_references', [])])
        datum_arg = f"(list {datums_str})" if datums_str else "nil"
        box_h = dim_opts['text_height'] * 2.0
        if gdt['attach_to'] == 'front_view_left_side':
            lisp_code += f'  (draw-gdt-frame (list {front_p1[0]} {iy + height / 2}) (list {front_p1[0] - 80} {iy + height / 2 - box_h / 2}) "{symbol_str}" "{gdt["tolerance"]}" {datum_arg} "RIGHT")\n'
        elif gdt['attach_to'] == 'side_view_right_side':
            lisp_code += f'  (draw-gdt-frame (list {side_p2[0]} {iy + height / 2}) (list {side_p2[0] + 20} {iy + height / 2 - box_h / 2}) "{symbol_str}" "{gdt["tolerance"]}" {datum_arg} "LEFT")\n'
    if 'top_surface' in finish: ts = finish[
        'top_surface']; lisp_code += f'  (draw-roughness-symbol (list {ix + length / 2} {front_p2[1]}) "{ts[0]}" {ts[2]} {ts[1]})\n'
    if 'right_side_surface' in finish: ss = finish[
        'right_side_surface']; lisp_code += f'  (draw-roughness-symbol (list {side_p2[0]} {iy + height * 0.75}) "{ss[0]}" {ss[2]} {ss[1]})\n'
    lisp_code += _generate_lisp_for_parameter_table(params, dim_opts, side_p2[0], 100, spacing)
    return lisp_code + get_lisp_footer("Cuboid")


# ==============================================================================
# 装配体生成函数
# ==============================================================================
def generate_lisp_for_screw_nut_assembly(data: dict) -> str:
    """
    根据定义的组件及其参数，生成一个装配体三视图LISP代码。
    【最终优化版 v4 - 带完整高级标注】
    """
    # ... 此处代码与您提供的版本完全相同 ...
    opts = data['drawing_options']
    components = data['components']
    layers, dim_opts = opts['layers'], opts['dimension_options']
    ix, iy = opts['insertion_point']
    spacing = opts['spacing']
    top_level_params = data.get('parameters', {})
    datums = data.get('datums', [])
    gts = data.get('geometric_tolerances', [])
    finish = data.get('surface_finish', {})
    total_height_tol = top_level_params.get('total_height_tolerance', '')
    head_width_tol = top_level_params.get('head_width_tolerance', '')
    hatch_opts = opts.get('hatch_options', {'pattern': 'ANSI31', 'scale': 1.5, 'color': 7})
    layers['hatch'] = {'name': 'Hatch', 'color': hatch_opts.get('color', 7)}
    screw_p = components['screw']['parameters']
    nut_p = components['nut']['parameters']
    if screw_p.get('shaft_diameter', 0) != nut_p.get('hole_diameter', 0):
        raise ValueError("尺寸不匹配: 螺钉直径与螺母孔径不同。")
    screw_head_w = screw_p['head_width']
    screw_side_len = screw_head_w / 2.0
    screw_flat_w = screw_side_len * 2
    screw_head_h = screw_p['head_height']
    screw_shaft_r = screw_p['shaft_diameter'] / 2.0
    screw_shaft_len = screw_p['shaft_length']
    nut_w, nut_h = nut_p['width'], nut_p['height']
    nut_side_len = nut_w / 2.0
    nut_flat_w = nut_side_len * 2
    total_h = screw_head_h + screw_shaft_len
    front_view_w = screw_head_w
    side_view_w = screw_flat_w / 2 * math.sqrt(3)
    front_cx = ix + front_view_w / 2
    y_shaft_bottom, y_nut_bottom = iy, iy
    y_nut_top = iy + nut_h
    y_head_bottom = iy + screw_shaft_len
    y_head_top = y_head_bottom + screw_head_h
    right_sx = ix + front_view_w + spacing
    right_cx = right_sx + side_view_w / 2
    top_sy = y_head_top + spacing
    top_cx = front_cx
    top_cy = top_sy + max(screw_head_w, nut_w) / 2
    lisp_code = get_lisp_header(layers, dim_opts)
    lisp_code += generate_lisp_utility_functions(layers, dim_opts)
    lisp_code += "\n  ;; --- 1. 绘制标准三视图 ---\n"
    lisp_code += '  ;; 主视图\n'
    lisp_code += f'  (command "_.-LAYER" "_S" "{layers["outline"]["name"]}" "")\n'
    lisp_code += f'  (command "_.RECTANG" (list {ix} {y_head_bottom}) (list {ix + front_view_w} {y_head_top}))\n'
    lisp_code += f'  (command "_.LINE" (list {front_cx - screw_side_len / 2} {y_head_bottom}) (list {front_cx - screw_side_len / 2} {y_head_top}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {front_cx + screw_side_len / 2} {y_head_bottom}) (list {front_cx + screw_side_len / 2} {y_head_top}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {front_cx - screw_shaft_r} {y_nut_top}) (list {front_cx - screw_shaft_r} {y_head_bottom}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {front_cx + screw_shaft_r} {y_nut_top}) (list {front_cx + screw_shaft_r} {y_head_bottom}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {front_cx - nut_w / 2} {y_nut_bottom}) (list {front_cx + nut_w / 2} {y_nut_bottom}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {front_cx - nut_w / 2} {y_nut_top}) (list {front_cx + nut_w / 2} {y_nut_top}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {front_cx - nut_w / 2} {y_nut_bottom}) (list {front_cx - nut_w / 2} {y_nut_top}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {front_cx + nut_w / 2} {y_nut_bottom}) (list {front_cx + nut_w / 2} {y_nut_top}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {front_cx - nut_side_len / 2} {y_nut_bottom}) (list {front_cx - nut_side_len / 2} {y_nut_top}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {front_cx + nut_side_len / 2} {y_nut_bottom}) (list {front_cx + nut_side_len / 2} {y_nut_top}) "")\n'
    lisp_code += f'  (command "_.-LAYER" "_S" "{layers["hidden"]["name"]}" "")\n'
    lisp_code += f'  (command "_.LINE" (list {front_cx - screw_shaft_r} {y_nut_bottom}) (list {front_cx - screw_shaft_r} {y_nut_top}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {front_cx + screw_shaft_r} {y_nut_bottom}) (list {front_cx + screw_shaft_r} {y_nut_top}) "")\n'
    lisp_code += '  ;; 右视图\n'
    lisp_code += f'  (command "_.-LAYER" "_S" "{layers["outline"]["name"]}" "")\n'
    lisp_code += f'  (command "_.RECTANG" (list {right_sx} {y_head_bottom}) (list {right_sx + side_view_w} {y_head_top}))\n'
    lisp_code += f'  (command "_.LINE" (list {right_cx - screw_shaft_r} {y_nut_top}) (list {right_cx - screw_shaft_r} {y_head_bottom}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {right_cx + screw_shaft_r} {y_nut_top}) (list {right_cx + screw_shaft_r} {y_head_bottom}) "")\n'
    nut_right_view_half_w = nut_flat_w / 4 * math.sqrt(3)
    lisp_code += f'  (command "_.LINE" (list {right_cx - nut_right_view_half_w} {y_nut_bottom}) (list {right_cx + nut_right_view_half_w} {y_nut_bottom}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {right_cx - nut_right_view_half_w} {y_nut_top}) (list {right_cx + nut_right_view_half_w} {y_nut_top}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {right_cx - nut_right_view_half_w} {y_nut_bottom}) (list {right_cx - nut_right_view_half_w} {y_nut_top}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {right_cx + nut_right_view_half_w} {y_nut_bottom}) (list {right_cx + nut_right_view_half_w} {y_nut_top}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {right_cx} {y_head_bottom}) (list {right_cx} {y_head_top}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {right_cx} {y_nut_bottom}) (list {right_cx} {y_nut_top}) "")\n'
    lisp_code += f'  (command "_.-LAYER" "_S" "{layers["hidden"]["name"]}" "")\n'
    lisp_code += f'  (command "_.LINE" (list {right_cx - screw_shaft_r} {y_nut_bottom}) (list {right_cx - screw_shaft_r} {y_nut_top}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {right_cx + screw_shaft_r} {y_nut_bottom}) (list {right_cx + screw_shaft_r} {y_nut_top}) "")\n'
    if y_nut_bottom > y_shaft_bottom:
        lisp_code += f'  (command "_.LINE" (list {right_cx - screw_shaft_r} {y_shaft_bottom}) (list {right_cx - screw_shaft_r} {y_nut_bottom}) "")\n'
        lisp_code += f'  (command "_.LINE" (list {right_cx + screw_shaft_r} {y_shaft_bottom}) (list {right_cx + screw_shaft_r} {y_nut_bottom}) "")\n'
    lisp_code += '  ;; 俯视图\n'
    lisp_code += f'  (command "_.-LAYER" "_S" "{layers["outline"]["name"]}" "")\n'
    if screw_head_w > nut_w:
        lisp_code += f'  (command "_.POLYGON" 6 (list {top_cx} {top_cy}) "_C" {screw_head_w / 4 * math.sqrt(3)})\n'
        lisp_code += f'  (command "_.-LAYER" "_S" "{layers["hidden"]["name"]}" "")\n'
        lisp_code += f'  (command "_.POLYGON" 6 (list {top_cx} {top_cy}) "_C" {nut_w / 4 * math.sqrt(3)})\n'
    elif nut_w > screw_head_w:
        lisp_code += f'  (command "_.POLYGON" 6 (list {top_cx} {top_cy}) "_C" {nut_w / 4 * math.sqrt(3)})\n'
        lisp_code += f'  (command "_.POLYGON" 6 (list {top_cx} {top_cy}) "_C" {screw_head_w / 4 * math.sqrt(3)})\n'
    else:
        lisp_code += f'  (command "_.POLYGON" 6 (list {top_cx} {top_cy}) "_C" {screw_head_w / 4 * math.sqrt(3)})\n'
    lisp_code += f'  (command "_.-LAYER" "_S" "{layers["outline"]["name"]}" "")\n'
    lisp_code += f'  (command "_.CIRCLE" (list {top_cx} {top_cy}) {screw_shaft_r})\n'
    draw_section = opts.get('draw_section_view', False)
    if draw_section:
        lisp_code += "\n  ;; --- 绘制剖视图 (精确绘制，最终版) ---\n"
        y_sec_base = y_head_top + spacing
        sec_y_head_bottom, sec_y_head_top, sec_y_shaft_top, sec_y_nut_bottom, sec_y_nut_top, sec_y_shaft_bottom = y_head_bottom - iy + y_sec_base, y_head_top - iy + y_sec_base, y_head_bottom - iy + y_sec_base, y_nut_bottom - iy + y_sec_base, y_nut_top - iy + y_sec_base, y_shaft_bottom - iy + y_sec_base
        sec_ix, sec_cx, sec_nut_right_view_half_w = right_sx, right_cx, nut_flat_w / 4 * math.sqrt(3)
        lisp_code += f'  (command "_.-LAYER" "_S" "{layers["outline"]["name"]}" "")\n'
        lisp_code += f'  (command "_.RECTANG" (list {sec_ix} {sec_y_head_bottom}) (list {sec_ix + side_view_w} {sec_y_head_top}))\n'
        lisp_code += f'  (command "_.LINE" (list {sec_cx} {sec_y_head_bottom}) (list {sec_cx} {sec_y_head_top}) "")\n'
        lisp_code += f'  (command "_.RECTANG" (list {sec_cx - screw_shaft_r} {sec_y_shaft_bottom}) (list {sec_cx + screw_shaft_r} {sec_y_shaft_top}))\n'
        lisp_code += f'  (command "_.LINE" (list {sec_cx - sec_nut_right_view_half_w} {sec_y_nut_top}) (list {sec_cx - screw_shaft_r} {sec_y_nut_top}) "")\n'
        lisp_code += f'  (command "_.LINE" (list {sec_cx + screw_shaft_r} {sec_y_nut_top}) (list {sec_cx + sec_nut_right_view_half_w} {sec_y_nut_top}) "")\n'
        lisp_code += f'  (command "_.LINE" (list {sec_cx - sec_nut_right_view_half_w} {sec_y_nut_bottom}) (list {sec_cx - screw_shaft_r} {sec_y_nut_bottom}) "")\n'
        lisp_code += f'  (command "_.LINE" (list {sec_cx + screw_shaft_r} {sec_y_nut_bottom}) (list {sec_cx + sec_nut_right_view_half_w} {sec_y_nut_bottom}) "")\n'
        lisp_code += f'  (command "_.LINE" (list {sec_cx - sec_nut_right_view_half_w} {sec_y_nut_bottom}) (list {sec_cx - sec_nut_right_view_half_w} {sec_y_nut_top}) "")\n'
        lisp_code += f'  (command "_.LINE" (list {sec_cx + sec_nut_right_view_half_w} {sec_y_nut_bottom}) (list {sec_cx + sec_nut_right_view_half_w} {sec_y_nut_top}) "")\n'
        lisp_code += f'  (command "_.-LAYER" "_S" "{layers["hidden"]["name"]}" "")\n'
        lisp_code += f'  (command "_.LINE" (list {sec_cx} {sec_y_nut_bottom}) (list {sec_cx} {sec_y_nut_top}) "")\n'
        hatch_pattern, hatch_scale = hatch_opts.get('pattern', 'ANSI31'), hatch_opts.get('scale', 1.5)
        pick_pt_head_left, pick_pt_head_right, pick_pt_nut_left, pick_pt_nut_right, pick_pt_shaft = f'(list {(sec_ix + sec_cx) / 2.0} {sec_y_head_bottom + screw_head_h / 2.0})', f'(list {(sec_cx + sec_ix + side_view_w) / 2.0} {sec_y_head_bottom + screw_head_h / 2.0})', f'(list {(sec_cx - sec_nut_right_view_half_w + sec_cx - screw_shaft_r) / 2.0} {sec_y_nut_bottom + nut_h / 2.0})', f'(list {(sec_cx + screw_shaft_r + sec_cx + sec_nut_right_view_half_w) / 2.0} {sec_y_nut_bottom + nut_h / 2.0})', f'(list {sec_cx} {sec_y_shaft_bottom + (sec_y_shaft_top - sec_y_shaft_bottom) / 2.0})'
        hatch_pick_points_str = f"{pick_pt_head_left} {pick_pt_head_right} {pick_pt_nut_left} {pick_pt_nut_right} {pick_pt_shaft}"
        lisp_code += f'  (command "_.-LAYER" "_S" "{layers["hatch"]["name"]}" "")\n'
        lisp_code += f'  (command "_.SETVAR" "HPNAME" "{hatch_pattern}")(command "_.SETVAR" "HPSCALE" {hatch_scale})\n'
        lisp_code += f'  (command "_-HATCH" {hatch_pick_points_str} "")\n'
        lisp_code += f'  (command "_.-LAYER" "_S" "{layers["hidden"]["name"]}" "")\n'
        lisp_code += f'  (command "_.LINE" (list {sec_cx - screw_shaft_r} {sec_y_nut_top}) (list {sec_cx + screw_shaft_r} {sec_y_nut_top}) "")\n'
    cl_ext = 15.0
    lisp_code += f'  (command "_.-LAYER" "_S" "{layers["centerline"]["name"]}" "")\n'
    lisp_code += f'  (command "_.LINE" (list {front_cx} {iy - cl_ext}) (list {front_cx} {top_cy + max(screw_head_w, nut_w) / 2 + cl_ext}) "")\n'
    y_highest_on_right = (y_sec_base + total_h) if draw_section else y_head_top
    lisp_code += f'  (command "_.LINE" (list {right_cx} {iy - cl_ext}) (list {right_cx} {y_highest_on_right + cl_ext}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {ix - cl_ext} {y_head_bottom - (y_head_bottom - y_nut_top) / 2}) (list {right_sx + side_view_w + cl_ext} {y_head_bottom - (y_head_bottom - y_nut_top) / 2}) "")\n'
    lisp_code += "\n  ;; --- 3. 尺寸标注和序号 ---\n"
    lisp_code += f'  (command "_.-LAYER" "_S" "{layers["dimensions"]["name"]}" "")\n'
    lisp_code += f'  (command "_.DIMLINEAR" (list {ix} {iy}) (list {ix} {y_head_top}) "_T" "<>{total_height_tol}" (list {ix - spacing / 2} {iy + total_h / 2}))\n'
    lisp_code += f'  (command "_.DIMLINEAR" (list {ix} {y_head_top}) (list {ix + front_view_w} {y_head_top}) "_T" "<>{head_width_tol}" (list {front_cx} {y_head_top + spacing / 2}))\n'
    balloon_r, balloon_txt_h = dim_opts['text_height'] * 1.5, dim_opts['text_height']
    lisp_code += f'  (command "_.LEADER" (list {ix + front_view_w * 0.8} {y_head_bottom + screw_head_h * 0.5}) (list {ix + front_view_w + 20} {y_head_top + 20}) "" "" "N")\n'
    lisp_code += f'  (Draw-Balloon (list {ix + front_view_w + 20 + balloon_r} {y_head_top + 20}) {balloon_r} "1" {balloon_txt_h})\n'
    lisp_code += f'  (command "_.LEADER" (list {front_cx - nut_w / 2 + 5} {y_nut_bottom + nut_h / 2}) (list {ix - 40} {y_nut_bottom + nut_h / 2}) "" "" "N")\n'
    lisp_code += f'  (Draw-Balloon (list {ix - 40 - balloon_r} {y_nut_bottom + nut_h / 2}) {balloon_r} "2" {balloon_txt_h})\n'
    lisp_code += "\n  ;; --- 4. 高级标注 (基准、形位公差、表面粗糙度) ---\n"
    gdt_symbols = {"perpendicularity": "\\\\U+22A5", "parallelism": "\\\\U+2225"}
    for datum in datums:
        if datum['attach_to'] == 'underside_of_screw_head':
            lisp_code += f'  (command "_.-LAYER" "_S" "{layers["dimensions"]["name"]}" "")\n'
            lisp_code += f'  (command "_.LINE" (list {front_cx} {y_head_bottom}) (list {front_cx} {y_head_bottom - 15}) "")\n'
            lisp_code += f'  (draw-datum-symbol (list {front_cx} {y_head_bottom - 15}) (list {front_cx} {y_head_bottom - 30}) "{datum["label"]}")\n'
        elif datum['attach_to'] == 'screw_axis_right_view':
            lisp_code += f'  (draw-datum-symbol (list {right_cx} {y_nut_top}) (list {right_cx - 20} {y_nut_top - 20}) "{datum["label"]}")\n'
    for gdt in gts:
        symbol_str = gdt_symbols.get(gdt["type"], "?")
        datums_str = " ".join([f'"{d}"' for d in gdt.get('datum_references', [])])
        datum_arg = f'(list {datums_str})' if datums_str else "nil"
        if gdt['attach_to'] == 'underside_of_screw_head_gdt':
            lisp_code += f'  (draw-gdt-frame (list {ix + front_view_w * 0.1} {y_head_bottom}) (list {ix - 50} {y_head_bottom - 30}) "{symbol_str}" "{gdt["tolerance"]}" {datum_arg} "RIGHT")\n'
        elif gdt['attach_to'] == 'nut_top_face':
            lisp_code += f'  (draw-gdt-frame (list {front_cx + nut_w / 2 * 0.8} {y_nut_top}) (list {ix + front_view_w + 30} {y_nut_top + 30}) "{symbol_str}" "{gdt["tolerance"]}" {datum_arg} "LEFT")\n'
    for key, val in finish.items():
        if key == 'underside_of_screw_head':
            lisp_code += f'  (draw-roughness-symbol (list {ix + front_view_w * 0.6} {y_head_bottom}) "{val[0]}" {val[2]} {val[1]})\n'
        elif key == 'top_of_screw_head':
            lisp_code += f'  (draw-roughness-symbol (list {ix + front_view_w * 0.4} {y_head_top}) "{val[0]}" {val[2]} {val[1]})\n'
    right_most_x_for_bom = right_sx + side_view_w
    top_most_y_for_bom = (y_sec_base + total_h) if draw_section else y_head_top
    lisp_code += "\n  ;; --- 5. 生成BOM表和参数表 ---\n"
    lisp_code += _generate_lisp_for_bom_table(components, dim_opts, right_most_x_for_bom, 100, spacing)
    unified_params = {comp_name.title(): comp_data.get('parameters', {}) for comp_name, comp_data in components.items()}
    if 'parameters' in data and data['parameters']: unified_params.update(data['parameters'])
    lisp_code += _generate_lisp_for_parameter_table(unified_params, dim_opts, ix, iy - spacing, 0)
    lisp_code += get_lisp_footer("Screw-Nut Assembly (with Advanced Annotations)")
    return lisp_code

def generate_lisp_for_cuboid_cylinder_assembly(data: dict) -> str:
    """
    生成一个“圆柱体放置/嵌入在长方体中心”的装配体三视图LISP代码。
    【最终修复版 v5 - 标注可靠性修复】
    """
    # ... 此处代码与您提供的版本完全相同 ...
    opts = data['drawing_options']
    components = data['components']
    layers, dim_opts = opts['layers'], opts['dimension_options']
    ix, iy = opts['insertion_point']
    spacing = opts['spacing']
    datums = data.get('datums', [])
    gts = data.get('geometric_tolerances', [])
    finish = data.get('surface_finish', {})
    hatch_scale_value = 1.5
    hatch_opts_cuboid = {'pattern': 'ANSI31', 'scale': hatch_scale_value}
    hatch_opts_cyl = {'pattern': 'ANSI32', 'scale': hatch_scale_value}
    layers['hatch'] = {'name': 'Hatch', 'color': 7}
    cuboid_p = components['cuboid']['parameters']
    cyl_p = components['cylinder']['parameters']
    cuboid_l, cuboid_w, cuboid_h = cuboid_p['length'], cuboid_p['width'], cuboid_p['height']
    cyl_r, cyl_h = cyl_p['radius'], cyl_p['height']
    height_tol = cuboid_p.get('height_tolerance', '')
    dia_tol = cyl_p.get('diameter_tolerance', '')
    draw_section = opts.get('draw_section_view', True)
    total_h = max(cuboid_h, cyl_h)
    y_top_overall = iy + total_h
    front_view_cx = ix + cuboid_l / 2
    y_top_view_start = y_top_overall + spacing
    top_view_center = (front_view_cx, y_top_view_start + cuboid_w / 2)
    side_view_sx = ix + cuboid_l + spacing
    side_view_cx = side_view_sx + cuboid_w / 2
    sec_view_sx = side_view_sx + cuboid_w + spacing
    sec_view_cx = sec_view_sx + cuboid_w / 2
    lisp_code = get_lisp_header(layers, dim_opts)
    lisp_code += generate_lisp_utility_functions(layers, dim_opts)
    lisp_code += f'\n  ;; --- 绘制主视图 ---\n'
    lisp_code += f'  (command "_.-LAYER" "_S" "{layers["outline"]["name"]}" "")\n'
    lisp_code += f'  (command "_.RECTANG" (list {ix} {iy}) (list {ix + cuboid_l} {iy + cuboid_h}))\n'
    if cyl_h > cuboid_h:
        lisp_code += f'  (command "_.RECTANG" (list {front_view_cx - cyl_r} {iy + cuboid_h}) (list {front_view_cx + cyl_r} {iy + cyl_h}))\n'
    lisp_code += f'  (command "_.-LAYER" "_S" "{layers["hidden"]["name"]}" "")\n'
    lisp_code += f'  (command "_.LINE" (list {front_view_cx - cyl_r} {iy}) (list {front_view_cx - cyl_r} {iy + min(cuboid_h, cyl_h)}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {front_view_cx + cyl_r} {iy}) (list {front_view_cx + cyl_r} {iy + min(cuboid_h, cyl_h)}) "")\n'
    if cuboid_h > cyl_h:
        lisp_code += f'  (command "_.LINE" (list {front_view_cx - cyl_r} {iy + cyl_h}) (list {front_view_cx + cyl_r} {iy + cyl_h}) "")\n'
    lisp_code += f'\n  ;; --- 绘制俯视图 ---\n'
    lisp_code += f'  (command "_.-LAYER" "_S" "{layers["outline"]["name"]}" "")\n'
    lisp_code += f'  (command "_.RECTANG" (list {ix} {y_top_view_start}) (list {ix + cuboid_l} {y_top_view_start + cuboid_w}))\n'
    lisp_code += f'  (command "_.CIRCLE" (list {top_view_center[0]} {top_view_center[1]}) {cyl_r})\n'
    lisp_code += "\n  ;; --- 绘制标准右视图 ---\n"
    lisp_code += f'  (command "_.-LAYER" "_S" "{layers["outline"]["name"]}" "")\n'
    lisp_code += f'  (command "_.RECTANG" (list {side_view_sx} {iy}) (list {side_view_sx + cuboid_w} {iy + cuboid_h}))\n'
    if cyl_h > cuboid_h:
        lisp_code += f'  (command "_.RECTANG" (list {side_view_cx - cyl_r} {iy + cuboid_h}) (list {side_view_cx + cyl_r} {iy + cyl_h}))\n'
    lisp_code += f'  (command "_.-LAYER" "_S" "{layers["hidden"]["name"]}" "")\n'
    lisp_code += f'  (command "_.LINE" (list {side_view_cx - cyl_r} {iy}) (list {side_view_cx - cyl_r} {iy + min(cuboid_h, cyl_h)}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {side_view_cx + cyl_r} {iy}) (list {side_view_cx + cyl_r} {iy + min(cuboid_h, cyl_h)}) "")\n'
    if cuboid_h > cyl_h:
        lisp_code += f'  (command "_.LINE" (list {side_view_cx - cyl_r} {iy + cyl_h}) (list {side_view_cx + cyl_r} {iy + cyl_h}) "")\n'
    if draw_section:
        lisp_code += f"\n  ;; --- 在右视图右侧绘制剖视图 ---\n"
        sec_base_y, sec_cuboid_top_y, sec_cyl_top_y = iy, iy + cuboid_h, iy + cyl_h
        contact_height = min(cuboid_h, cyl_h)
        lisp_code += f'  (command "_.-LAYER" "_S" "{layers["outline"]["name"]}" "")\n'
        lisp_code += f'  (command "_.RECTANG" (list {sec_view_sx} {sec_base_y}) (list {sec_view_cx - cyl_r} {sec_cuboid_top_y}))\n'
        lisp_code += f'  (command "_.RECTANG" (list {sec_view_cx + cyl_r} {sec_base_y}) (list {sec_view_sx + cuboid_w} {sec_cuboid_top_y}))\n'
        lisp_code += f'  (command "_.RECTANG" (list {sec_view_cx - cyl_r} {sec_base_y}) (list {sec_view_cx + cyl_r} {sec_cyl_top_y}))\n'
        lisp_code += f'  (command "_.LINE" (list {sec_view_cx - cyl_r} {sec_base_y}) (list {sec_view_cx - cyl_r} {sec_base_y + contact_height}) "")\n'
        lisp_code += f'  (command "_.LINE" (list {sec_view_cx + cyl_r} {sec_base_y}) (list {sec_view_cx + cyl_r} {sec_base_y + contact_height}) "")\n'
        lisp_code += f'  (command "_.-LAYER" "_S" "{layers["hatch"]["name"]}" "")\n'
        pick_pt_cuboid_left = f'(list {(sec_view_sx + sec_view_cx - cyl_r) / 2.0} {sec_base_y + cuboid_h / 2.0})'
        pick_pt_cuboid_right = f'(list {(sec_view_cx + cyl_r + sec_view_sx + cuboid_w) / 2.0} {sec_base_y + cuboid_h / 2.0})'
        lisp_code += f'  (command "_-HATCH" "_P" "{hatch_opts_cuboid["pattern"]}" {hatch_opts_cuboid["scale"]} "" {pick_pt_cuboid_left} {pick_pt_cuboid_right} "")\n'
        pick_pt_cylinder = f'(list {sec_view_cx} {sec_base_y + cyl_h / 2.0})'
        lisp_code += f'  (command "_-HATCH" "_P" "{hatch_opts_cyl["pattern"]}" {hatch_opts_cyl["scale"]} "" {pick_pt_cylinder} "")\n'
        if cuboid_h > cyl_h:
            lisp_code += f'  (command "_.-LAYER" "_S" "{layers["outline"]["name"]}" "")\n'
            lisp_code += f'  (command "_.LINE" (list {sec_view_cx - cyl_r} {sec_cuboid_top_y}) (list {sec_view_cx + cyl_r} {sec_cuboid_top_y}) "")\n'
        else:
            lisp_code += f'  (command "_.-LAYER" "_S" "{layers["hidden"]["name"]}" "")\n'
            lisp_code += f'  (command "_.LINE" (list {sec_view_cx - cyl_r} {sec_cuboid_top_y}) (list {sec_view_cx + cyl_r} {sec_cuboid_top_y}) "")\n'
    rightmost_x_for_centerline = (sec_view_sx + cuboid_w) if draw_section else (side_view_sx + cuboid_w)
    lisp_code += f'\n  ;; --- 绘制中心线 ---\n'
    cl_ext = 20.0
    lisp_code += f'  (command "_.-LAYER" "_S" "{layers["centerline"]["name"]}" "")\n'
    lisp_code += f'  (command "_.LINE" (list {front_view_cx} {iy - cl_ext}) (list {front_view_cx} {y_top_view_start + cuboid_w + cl_ext}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {side_view_cx} {iy - cl_ext}) (list {side_view_cx} {y_top_overall + cl_ext}) "")\n'
    if draw_section:
        lisp_code += f'  (command "_.LINE" (list {sec_view_cx} {iy - cl_ext}) (list {sec_view_cx} {y_top_overall + cl_ext}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {ix - cl_ext} {iy + cuboid_h / 2}) (list {rightmost_x_for_centerline + cl_ext} {iy + cuboid_h / 2}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {ix - cl_ext} {top_view_center[1]}) (list {ix + cuboid_l + cl_ext} {top_view_center[1]}) "")\n'
    lisp_code += "\n  ;; --- 2. 尺寸标注和序号 ---\n"
    dim_height_text_pt = (ix - spacing * 0.7, iy + total_h / 2.0)
    dim_length_text_pt = (front_view_cx, iy - spacing * 0.7)
    dim_dia_end_pt = (top_view_center[0] - cyl_r - 20, top_view_center[1] + cyl_r + 20)
    lisp_code += f'  (command "_.-LAYER" "_S" "{layers["dimensions"]["name"]}" "")\n'
    lisp_code += f'  (command "_.DIMLINEAR" (list {ix} {iy}) (list {ix} {iy + cuboid_h}) "_T" "<>{height_tol}" (list {dim_height_text_pt[0]} {dim_height_text_pt[1]}))\n'
    lisp_code += f'  (command "_.DIMLINEAR" (list {ix} {iy}) (list {ix + cuboid_l} {iy}) (list {dim_length_text_pt[0]} {dim_length_text_pt[1]}))\n'
    lisp_code += f'  (command "_.DIMDIAMETER" "" (list {top_view_center[0] - cyl_r * 0.707} {top_view_center[1] + cyl_r * 0.707}) "_T" "%%c<>{dia_tol}" (list {dim_dia_end_pt[0]} {dim_dia_end_pt[1]}))\n'
    balloon_r, balloon_txt_h = dim_opts['text_height'] * 1.5, dim_opts['text_height']
    lisp_code += f'  (command "_.LEADER" (list {ix + cuboid_l * 0.8} {iy + cuboid_h * 0.5}) (list {ix + cuboid_l + 20} {iy + cuboid_h * 0.5}) "" "" "N")\n'
    lisp_code += f'  (Draw-Balloon (list {ix + cuboid_l + 20 + balloon_r} {iy + cuboid_h * 0.5}) {balloon_r} "1" {balloon_txt_h})\n'
    leader_y_cyl = iy + min(cyl_h, cuboid_h) * 0.7
    lisp_code += f'  (command "_.LEADER" (list {front_view_cx + cyl_r * 0.7} {leader_y_cyl}) (list {front_view_cx + cyl_r + 20} {leader_y_cyl + 20}) "" "" "N")\n'
    lisp_code += f'  (Draw-Balloon (list {front_view_cx + cyl_r + 20 + balloon_r} {leader_y_cyl + 20}) {balloon_r} "2" {balloon_txt_h})\n'
    lisp_code += "\n  ;; --- 3. 高级标注 (基准、形位公差、表面粗糙度) ---\n"
    gdt_symbols = {"perpendicularity": "\\\\U+22A5", "parallelism": "\\\\U+2225"}
    for datum in datums:
        label = datum["label"]
        if datum['attach_to'] == 'front_view_bottom_mid':
            lisp_code += f'  (draw-datum-symbol (list {front_view_cx} {iy}) (list {front_view_cx} {iy - 20}) "{label}")\n'
        elif datum['attach_to'] == 'side_view_left_mid':
            lisp_code += f'  (draw-datum-symbol (list {side_view_sx} {iy + cuboid_h / 2}) (list {side_view_sx - 20} {iy + cuboid_h / 2}) "{label}")\n'
        elif datum['attach_to'] == 'front_view_left_mid':
            lisp_code += f'  (draw-datum-symbol (list {ix} {iy + cuboid_h / 2}) (list {ix - 20} {iy + cuboid_h / 2}) "{label}")\n'
    for gdt in gts:
        symbol_str = gdt_symbols.get(gdt["type"], "?")
        datums_str = " ".join([f'"{d}"' for d in gdt.get('datum_references', [])])
        datum_arg = f'(list {datums_str})' if datums_str else "nil"
        if gdt['attach_to'] == 'hole_outline_top_view':
            attach_pt_x = top_view_center[0] + cyl_r * math.cos(math.radians(135))
            attach_pt_y = top_view_center[1] + cyl_r * math.sin(math.radians(135))
            frame_loc_x, frame_loc_y = attach_pt_x - 40, attach_pt_y + 40
            lisp_code += f'  (draw-gdt-frame (list {attach_pt_x} {attach_pt_y}) (list {frame_loc_x} {frame_loc_y}) "{symbol_str}" "{gdt["tolerance"]}" {datum_arg} "RIGHT")\n'
        elif gdt['attach_to'] == 'front_view_top_surface':
            lisp_code += f'  (draw-gdt-frame (list {front_view_cx} {iy + cuboid_h}) (list {front_view_cx + 40} {iy + cuboid_h + 20}) "{symbol_str}" "{gdt["tolerance"]}" {datum_arg} "LEFT")\n'
    for key, val in finish.items():
        if key == 'top_surface':
            lisp_code += f'  (draw-roughness-symbol (list {ix + cuboid_l * 0.75} {iy + cuboid_h}) "{val[0]}" {val[2]} {val[1]})\n'
        elif key == 'hole_bottom' and draw_section:
            lisp_code += f'  (draw-roughness-symbol (list {sec_view_cx} {iy + cyl_h}) "{val[0]}" {val[2]} {val[1]})\n'
        elif key == 'hole_wall' and draw_section:
            lisp_code += f'  (draw-roughness-symbol (list {sec_view_cx - cyl_r} {iy + cyl_h / 2}) "{val[0]}" {val[2]} {val[1]})\n'
    bom_start_x = (sec_view_sx + cuboid_w) if draw_section else (side_view_sx + cuboid_w)
    bom_start_y = y_top_overall
    lisp_code += "\n  ;; --- 4. 生成BOM表和参数表 ---\n"
    lisp_code += _generate_lisp_for_bom_table(components, dim_opts, bom_start_x + spacing, 100, spacing)
    unified_params = {comp_name.title(): comp_data.get('parameters', {}) for comp_name, comp_data in components.items()}
    if 'parameters' in data and data['parameters']: unified_params.update(data['parameters'])
    param_table_start_x, param_table_start_y = ix, iy - spacing * 2.5
    lisp_code += _generate_lisp_for_parameter_table(unified_params, dim_opts, param_table_start_x, param_table_start_y, 0)
    lisp_code += get_lisp_footer("Cuboid-Cylinder Assembly (Annotation Fixed)")
    return lisp_code


# ==============================================================================
# 3D 实体模型生成函数
# ==============================================================================
def generate_3d_lisp_for_screw_nut_assembly(data: dict) -> str:
    """【3D生成版本】根据组件参数，生成一个三维的螺钉螺母装配体LISP代码。"""
    opts = data['drawing_options']
    components = data['components']
    ix, iy = opts['insertion_point']
    screw_p = components['screw']['parameters']
    nut_p = components['nut']['parameters']
    screw_head_width, screw_head_height = screw_p['head_width'], screw_p['head_height']
    screw_shaft_dia, screw_shaft_len = screw_p['shaft_diameter'], screw_p['shaft_length']
    nut_width, nut_height, nut_hole_dia = nut_p['width'], nut_p['height'], nut_p['hole_diameter']
    screw_head_radius, nut_radius = screw_head_width / 2.0, nut_width / 2.0

    lisp_code = textwrap.dedent(f"""
(defun C:DrawMyObject ()
  (command "_.UNDO" "Begin")
  (setvar "CMDECHO" 0)
  ;; --- 3D 建模过程 ---
  ;; 1. 创建螺钉头 (六棱柱)
  (setq screw_head_center (list {ix} {iy} {screw_shaft_len}))
  (command "_.POLYGON" 6 screw_head_center "_C" {screw_head_radius})
  (command "_.EXTRUDE" (entlast) "" {screw_head_height})
  (setq screw_head_obj (entlast))
  ;; 2. 创建螺钉杆 (圆柱)
  (setq screw_shaft_center (list {ix} {iy} 0))
  (command "_.CYLINDER" screw_shaft_center {screw_shaft_dia / 2.0} {screw_shaft_len})
  (setq screw_shaft_obj (entlast))
  ;; 3. 将螺钉头和杆合并为一个实体
  (command "_.UNION" screw_head_obj screw_shaft_obj "")
  (setq screw_obj (entlast))
  ;; 4. 创建螺母主体 (六棱柱)
  (setq nut_center (list {ix} {iy} 0))
  (command "_.POLYGON" 6 nut_center "_C" {nut_radius})
  (command "_.EXTRUDE" (entlast) "" {nut_height})
  (setq nut_body_obj (entlast))
  ;; 5. 创建用于给螺母打孔的圆柱
  (command "_.CYLINDER" nut_center {nut_hole_dia / 2.0} {nut_height})
  (setq nut_hole_obj (entlast))
  ;; 6. 从螺母主体中减去圆柱，形成孔
  (command "_.SUBTRACT" nut_body_obj "" nut_hole_obj "")
  (setq nut_obj (entlast))
  ;; 7. (可选) 将螺母向上移动到合适位置
  ;;(command "_.MOVE" nut_obj "" nut_center (list {ix} {iy} {screw_shaft_len - nut_height - 5}))
  ;; --- 视图和显示设置 ---
  (command "_.VPOINT" 1 -1 1) ; 切换到西南等轴测视图
  (command "_.SHADEMODE" "Realistic") ; 使用真实着色模式
  (setvar "CMDECHO" 1)
  (command "_.ZOOM" "_E")
  (command "_.UNDO" "End")
  (princ "\\n3D Screw-Nut Assembly drawing completed!\\n")(princ))
(princ "\\nLISP file loaded. Type 'DrawMyObject' to run.")(princ)
""")
    return lisp_code


def generate_3d_lisp_for_cuboid_cylinder_assembly(data: dict) -> str:
    """
    【3D生成版本 - 最终正确版】
    根据组件参数，生成一个三维的长方体-圆柱组合体的LISP代码。
    此版本将长方体和圆柱创建为两个独立的实体，正确模拟装配关系，
    确保在任何视觉样式下都能看到正确的通孔和穿出效果。
    """
    # 1. 提取参数
    opts = data['drawing_options']
    components = data['components']
    ix, iy = opts['insertion_point']

    cuboid_p = components['cuboid']['parameters']
    cyl_p = components['cylinder']['parameters']

    # 长方体尺寸
    cuboid_l = cuboid_p['length']
    cuboid_w = cuboid_p['width']
    cuboid_h = cuboid_p['height']

    # 圆柱尺寸
    cyl_r = cyl_p['radius']
    cyl_h = cyl_p['height']

    # 2. 坐标计算
    hole_center_x = ix + cuboid_l / 2.0
    hole_center_y = iy + cuboid_w / 2.0

    # LISP代码开始
    lisp_code = textwrap.dedent(f"""
(defun C:DrawMyObject ()
  (command "_.UNDO" "Begin")
  (setvar "CMDECHO" 0)

  ;; --- 3D 建模过程 (最终正确逻辑：分别建模，模拟装配) ---

  ;; --- 零件1: 带通孔的长方体 ---
  ;; 1a. 创建一个实心长方体
  (setq p1 (list {ix} {iy} 0))
  (command "_.BOX" p1 "_L" {cuboid_l} {cuboid_w} {cuboid_h})
  (setq cuboid_solid_obj (entlast))

  ;; 1b. 创建一个足够长的圆柱作为“钻头”工具，确保能完全打穿
  ;;     为了避免面重合问题，让它在Z方向上略微超出
  (setq hole_tool_center (list {hole_center_x} {hole_center_y} -1))
  (command "_.CYLINDER" hole_tool_center {cyl_r} {cuboid_h + 2})
  (setq hole_tool_obj (entlast))

  ;; 1c. 执行减法，得到最终的带孔长方体零件
  (command "_.SUBTRACT" cuboid_solid_obj "" hole_tool_obj "")
  ;; (setq pierced_cuboid_part (entlast)) ; 可以给它命名，但非必须

  ;; --- 零件2: 独立的圆柱体 ---
  ;; 2a. 在正确的位置创建最终的圆柱零件
  (setq cylinder_center (list {hole_center_x} {hole_center_y} 0))
  (command "_.CYLINDER" cylinder_center {cyl_r} {cyl_h})
  ;; (setq cylinder_part (entlast)) ; 可以给它命名，但非必须

  ;; --- 模型完成，不执行UNION ---
  ;; 现在模型中有两个独立的实体，它们在空间上装配在一起。

  ;; --- 视图和显示设置 ---
  (command "_.VPOINT" 1 -1 1) ; 切换到西南等轴测视图
  ;; 为了能看清内部，使用半透明的X-Ray模式会很有效
  (command "_.SHADEMODE" "X-Ray") 

  (setvar "CMDECHO" 1)
  (command "_.ZOOM" "_E")
  (command "_.UNDO" "End")
  (princ "\\n3D Cuboid-Cylinder Assembly (Correct Assembly) drawing completed!\\n")(princ))
(princ "\\nLISP file loaded. Type 'DrawMyObject' to run.")(princ)
""")

    return lisp_code
def generate_3d_lisp_for_hex_screw(data: dict) -> str:
    """
    【3D生成版本】
    根据参数，生成一个三维的六角头螺钉实体LISP代码。
    """
    # 1. 提取参数
    opts = data.get('drawing_options', {'insertion_point': [0, 0]})
    params = data['parameters']
    ix, iy = opts.get('insertion_point', [0, 0])

    # 从参数中获取螺钉尺寸
    head_p = params['head']
    shaft_p = params['shaft']

    # 螺钉头尺寸
    # 对于六角螺钉，通常用“对边距”(width across flats)或“对角距”(width across corners)定义。
    # 我们假设JSON中提供的是对角距 "side_length" * 2，即外接圆直径。
    # 如果JSON提供的是对边距，计算方式会不同。这里我们基于'hex_screw.json'的结构。
    head_side_length = head_p['side_length']
    head_height = head_p['height']
    head_radius = head_side_length # 对于内切圆的多边形，半径就是边长。这里用外接圆更常见。
                                   # 假设 side_length 是外接圆半径。

    # 螺钉杆尺寸
    shaft_dia = shaft_p['diameter']
    shaft_len = shaft_p['length']
    shaft_radius = shaft_dia / 2.0

    # LISP代码开始
    lisp_code = textwrap.dedent(f"""
(defun C:DrawMyObject ()
  (command "_.UNDO" "Begin")
  (setvar "CMDECHO" 0)

  ;; --- 3D 建模过程 ---

  ;; 1. 创建螺钉头 (六棱柱)
  ;; 中心点在 (ix, iy, shaft_len)，从这里向上拉伸
  ;; 我们使用 POLYGON 的外接圆模式 "_C"，半径就是 side_length
  (setq screw_head_center (list {ix} {iy} {shaft_len}))
  (command "_.POLYGON" 6 screw_head_center "_C" {head_side_length})
  (command "_.EXTRUDE" (entlast) "" {head_height})
  (setq screw_head_obj (entlast))

  ;; 2. 创建螺钉杆 (圆柱)
  ;; 基座中心点在 (ix, iy, 0)
  (setq screw_shaft_center (list {ix} {iy} 0))
  (command "_.CYLINDER" screw_shaft_center {shaft_radius} {shaft_len})
  (setq screw_shaft_obj (entlast))

  ;; 3. 将螺钉头和杆合并为一个实体
  (command "_.UNION" screw_head_obj screw_shaft_obj "")

  ;; --- 视图和显示设置 ---
  (command "_.VPOINT" 1 -1 1) ; 切换到西南等轴测视图
  (command "_.SHADEMODE" "Realistic") ; 使用真实着色模式

  (setvar "CMDECHO" 1)
  (command "_.ZOOM" "_E")
  (command "_.UNDO" "End")
  (princ "\\n3D Hexagonal Screw drawing completed!\\n")(princ))
(princ "\\nLISP file loaded. Type 'DrawMyObject' to run.")(princ)
""")

    return lisp_code


def generate_3d_lisp_for_hex_nut(data: dict) -> str:
    """
    【3D生成版本】
    根据参数，生成一个三维的、带中心孔的六角螺母实体LISP代码。
    """
    # 1. 提取参数
    opts = data.get('drawing_options', {'insertion_point': [0, 0]})
    params = data['parameters']
    ix, iy = opts.get('insertion_point', [0, 0])

    # 螺母尺寸
    nut_side_length = params['side_length']
    nut_height = params['height']
    hole_dia = params['hole']['diameter']
    hole_radius = hole_dia / 2.0

    # 假设 side_length 是外接圆半径
    nut_radius = nut_side_length

    # LISP代码开始
    lisp_code = textwrap.dedent(f"""
(defun C:DrawMyObject ()
  (command "_.UNDO" "Begin")
  (setvar "CMDECHO" 0)

  ;; --- 3D 建模过程 ---

  ;; 1. 创建螺母的六棱柱主体
  (setq nut_center (list {ix} {iy} 0))
  (command "_.POLYGON" 6 nut_center "_C" {nut_radius})
  (command "_.EXTRUDE" (entlast) "" {nut_height})
  (setq nut_body_obj (entlast))

  ;; 2. 创建用于给螺母打孔的圆柱“工具”
  ;;    为避免面重合问题，让它在Z方向上略微超出
  (setq hole_tool_center (list {ix} {iy} -1))
  (command "_.CYLINDER" hole_tool_center {hole_radius} {nut_height + 2})
  (setq hole_tool_obj (entlast))

  ;; 3. 从螺母主体中减去圆柱，形成中心孔
  (command "_.SUBTRACT" nut_body_obj "" hole_tool_obj "")

  ;; --- 视图和显示设置 ---
  (command "_.VPOINT" 1 -1 1)
  (command "_.SHADEMODE" "Realistic")

  (setvar "CMDECHO" 1)
  (command "_.ZOOM" "_E")
  (command "_.UNDO" "End")
  (princ "\\n3D Hexagonal Nut drawing completed!\\n")(princ))
(princ "\\nLISP file loaded. Type 'DrawMyObject' to run.")(princ)
""")
    return lisp_code

def generate_3d_lisp_for_cylinder(data: dict) -> str:
    """
    【3D生成版本】
    根据参数，生成一个三维的圆柱体实体LISP代码。
    """
    # 1. 提取参数
    opts = data.get('drawing_options', {'insertion_point': [0, 0]})
    params = data['parameters']
    ix, iy = opts.get('insertion_point', [0, 0])

    # 圆柱尺寸
    radius = params['radius']
    height = params['height']

    # LISP代码开始
    lisp_code = textwrap.dedent(f"""
(defun C:DrawMyObject ()
  (command "_.UNDO" "Begin")
  (setvar "CMDECHO" 0)

  ;; --- 3D 建模过程 ---
  ;; 使用 CYLINDER 命令直接创建圆柱体
  (setq cylinder_center (list {ix} {iy} 0))
  (command "_.CYLINDER" cylinder_center {radius} {height})

  ;; --- 视图和显示设置 ---
  (command "_.VPOINT" 1 -1 1)
  (command "_.SHADEMODE" "Realistic")

  (setvar "CMDECHO" 1)
  (command "_.ZOOM" "_E")
  (command "_.UNDO" "End")
  (princ "\\n3D Cylinder drawing completed!\\n")(princ))
(princ "\\nLISP file loaded. Type 'DrawMyObject' to run.")(princ)
""")
    return lisp_code

def generate_3d_lisp_for_cuboid(data: dict) -> str:
    """
    【3D生成版本】
    根据参数，生成一个三维的长方体实体LISP代码。
    """
    # 1. 提取参数
    opts = data.get('drawing_options', {'insertion_point': [0, 0]})
    params = data['parameters']
    ix, iy = opts.get('insertion_point', [0, 0])

    # 长方体尺寸
    length = params['length']
    width = params['width']
    height = params['height']

    # LISP代码开始
    lisp_code = textwrap.dedent(f"""
(defun C:DrawMyObject ()
  (command "_.UNDO" "Begin")
  (setvar "CMDECHO" 0)

  ;; --- 3D 建模过程 ---
  ;; 使用 BOX 命令直接创建长方体
  (setq start_point (list {ix} {iy} 0))
  (command "_.BOX" start_point "_L" {length} {width} {height})

  ;; --- 视图和显示设置 ---
  (command "_.VPOINT" 1 -1 1)
  (command "_.SHADEMODE" "Realistic")

  (setvar "CMDECHO" 1)
  (command "_.ZOOM" "_E")
  (command "_.UNDO" "End")
  (princ "\\n3D Cuboid drawing completed!\\n")(princ))
(princ "\\nLISP file loaded. Type 'DrawMyObject' to run.")(princ)
""")
    return lisp_code


def generate_3d_lisp_for_hex_prism(data: dict) -> str:
    """
    【3D生成版本】
    根据参数，生成一个三维的六棱柱实体LISP代码。
    """
    # 1. 提取参数
    opts = data.get('drawing_options', {'insertion_point': [0, 0]})
    params = data['parameters']
    ix, iy = opts.get('insertion_point', [0, 0])

    # 六棱柱尺寸
    side_length = params['side_length']
    height = params['height']

    # 假设 side_length 是外接圆半径
    prism_radius = side_length

    # LISP代码开始
    lisp_code = textwrap.dedent(f"""
(defun C:DrawMyObject ()
  (command "_.UNDO" "Begin")
  (setvar "CMDECHO" 0)

  ;; --- 3D 建模过程 ---
  ;; 1. 创建六边形基底
  (setq prism_center (list {ix} {iy} 0))
  (command "_.POLYGON" 6 prism_center "_C" {prism_radius})

  ;; 2. 将基底拉伸成六棱柱
  (command "_.EXTRUDE" (entlast) "" {height})

  ;; --- 视图和显示设置 ---
  (command "_.VPOINT" 1 -1 1)
  (command "_.SHADEMODE" "Realistic")

  (setvar "CMDECHO" 1)
  (command "_.ZOOM" "_E")
  (command "_.UNDO" "End")
  (princ "\\n3D Hexagonal Prism drawing completed!\\n")(princ))
(princ "\\nLISP file loaded. Type 'DrawMyObject' to run.")(princ)
""")
    return lisp_code


def generate_3d_lisp_for_socket_head_cap_screw(data: dict) -> str:
    """
    【3D生成版本 - 带简化螺纹】
    根据参数，生成一个三维的、带可视化螺纹的内六角圆柱头螺钉实体LISP代码。
    """
    # 1. 提取参数
    opts = data.get('drawing_options', {'insertion_point': [0, 0]})
    params = data['parameters']
    ix, iy = opts.get('insertion_point', [0, 0])

    # 螺钉尺寸
    head_diameter = params['head_diameter']
    head_height = params['head_height']
    shaft_diameter = params['shaft_diameter']
    shaft_length = params['shaft_length']
    socket_depth = params['socket_depth']
    socket_width = params['socket_width_across_flats']

    # [新增] 螺纹参数
    thread_pitch = params.get('thread_pitch', 1.0)  # 螺距, 默认1.0
    thread_depth = params.get('thread_depth', 0.5)  # 螺纹深度, 默认0.5

    # 计算半径等
    head_radius = head_diameter / 2.0
    shaft_radius = shaft_diameter / 2.0
    socket_half_width = socket_width / 2.0
    total_height = shaft_length + head_height

    # LISP代码开始
    lisp_code = textwrap.dedent(f"""
(defun C:DrawMyObject ()
  (command "_.UNDO" "Begin")
  (setvar "CMDECHO" 0)

  ;; --- 3D 建模过程 ---

  ;; 1. 创建螺钉杆 (圆柱)
  (setq screw_shaft_center (list {ix} {iy} 0))
  (command "_.CYLINDER" screw_shaft_center {shaft_radius} {shaft_length})
  (setq screw_shaft_obj (entlast))

  ;; 2. 创建螺钉头 (圆柱)
  (setq screw_head_center (list {ix} {iy} {shaft_length}))
  (command "_.CYLINDER" screw_head_center {head_radius} {head_height})
  (setq screw_head_obj (entlast))

  ;; 3. 将螺钉头和杆合并为一个实体
  (command "_.UNION" screw_head_obj screw_shaft_obj "")
  (setq screw_body_obj (entlast))

  ;; 4. 创建用于打孔的六棱柱“工具”
  (setq socket_center (list {ix} {iy} {total_height}))
  (command "_.POLYGON" 6 socket_center "_I" {socket_half_width})
  (command "_.EXTRUDE" (entlast) "" {-socket_depth})
  (setq socket_tool_obj (entlast))

  ;; 5. 从螺钉主体中减去六棱柱工具，形成内六角孔
  (command "_.SUBTRACT" screw_body_obj "" socket_tool_obj "")
  (setq screw_body_with_socket_obj (entlast))

  ;; --- [新增] 创建可视化螺纹 ---
  ;; 创建一系列圆环作为切割工具
  (setq cutter_set (ssadd)) ; 创建一个空的选择集来存放所有切割工具
  (setq current_z 0.0)
  (while (< current_z {shaft_length})
    (setq torus_center (list {ix} {iy} current_z))
    ;; 创建一个圆环，其大半径略小于杆半径，管半径为螺纹深度
    (command "_.TORUS" torus_center {shaft_radius - thread_depth / 2} {thread_depth / 2})
    (ssadd (entlast) cutter_set) ; 将新创建的圆环添加到选择集中
    (setq current_z (+ current_z {thread_pitch}))
  )

  ;; 6. 从带孔的螺钉主体上，一次性减去所有的圆环切割工具
  (if (> (sslength cutter_set) 0)
    (command "_.SUBTRACT" screw_body_with_socket_obj "" cutter_set "")
  )

  ;; --- 视图和显示设置 ---
  (command "_.VPOINT" 1 -1 1)
  (command "_.SHADEMODE" "Realistic")

  (setvar "CMDECHO" 1)
  (command "_.ZOOM" "_E")
  (command "_.UNDO" "End")
  (princ "\\n3D Socket Head Cap Screw with Threads drawing completed!\\n")(princ))
(princ "\\nLISP file loaded. Type 'DrawMyObject' to run.")(princ)
""")

    return lisp_code


def generate_lisp_for_socket_head_cap_screw(data: dict) -> str:
    """
    生成一个“内六角圆柱头螺钉”的二维工程图（主视图+右视图+俯视图）的LISP代码。
    【已修正 v9：补全了螺纹小径的终止线】
    """
    # 1. 提取参数 (并补充缺失的几何参数)
    params = data['parameters']
    opts = data['drawing_options']
    layers, dim_opts = opts['layers'], opts['dimension_options']

    # --- 螺纹和圆角参数 ---
    params.setdefault('thread_length', 18)
    params.setdefault('fillet_radius', 0.4)
    params.setdefault('socket_countersink_diameter', params['socket_width_across_flats'] + 1.0)
    params.setdefault('end_chamfer_size', params.get('thread_pitch', 1.0))

    # 从参数中获取所有尺寸
    head_diameter = params['head_diameter']
    head_height = params['head_height']
    shaft_diameter = params['shaft_diameter']
    shaft_length = params['shaft_length']
    socket_depth = params['socket_depth']
    socket_width_across_flats = params['socket_width_across_flats']
    socket_countersink_diameter = params['socket_countersink_diameter']
    end_chamfer_size = params['end_chamfer_size']
    thread_length = params['thread_length']  # b
    thread_depth = params['thread_depth']
    fillet_radius = params['fillet_radius']  # r
    datums = data.get('datums', [])

    # 2. 计算所有需要的投影尺寸和坐标
    ix, iy = opts['insertion_point']
    spacing = opts['spacing']

    head_radius = head_diameter / 2.0
    shaft_radius = shaft_diameter / 2.0
    thread_minor_radius = shaft_radius - thread_depth

    socket_half_width_flats = socket_width_across_flats / 2.0
    socket_half_width_corners = socket_half_width_flats / math.cos(math.radians(30))
    socket_countersink_half_width = socket_countersink_diameter / 2.0
    side_length = socket_width_across_flats / math.sqrt(3)
    socket_inner_edge_offset = side_length / 2.0

    # 视图坐标
    x_center = ix + head_radius
    y_shaft_bottom = iy
    y_head_bottom = iy + shaft_length
    y_head_top = y_head_bottom + head_height
    y_socket_bottom = y_head_top - socket_depth
    y_thread_end = y_shaft_bottom + thread_length
    y_fillet_start = y_head_bottom - fillet_radius

    right_view_start_x = ix + head_diameter + spacing
    right_view_cx = right_view_start_x + head_radius
    top_view_cx = x_center
    top_view_cy = y_head_top + spacing + head_radius
    total_height = head_height + shaft_length

    # 计算顶部120°沉孔交点
    countersink_angle_rad = math.radians(30)
    dx_flats = socket_countersink_half_width - socket_half_width_flats
    y_intersection_flats = y_head_top - (dx_flats * math.tan(countersink_angle_rad)) if dx_flats > 0 else y_head_top
    dx_corners = socket_countersink_half_width - socket_half_width_corners
    y_intersection_corners = y_head_top - (
                dx_corners * math.tan(countersink_angle_rad)) if dx_corners > 0 else y_head_top
    dx_inner = socket_countersink_half_width - socket_inner_edge_offset
    y_intersection_inner = y_head_top - (dx_inner * math.tan(countersink_angle_rad)) if dx_inner > 0 else y_head_top
    y_intersection_center_edge = y_intersection_flats

    # 计算底部120°锥形钻尖
    drill_point_angle_rad = math.radians(60)
    cone_height_flats = socket_half_width_flats / math.tan(drill_point_angle_rad)
    y_socket_tip_flats = y_socket_bottom - cone_height_flats
    cone_height_corners = socket_half_width_corners / math.tan(drill_point_angle_rad)
    y_socket_tip_corners = y_socket_bottom - cone_height_corners

    # 3. 生成LISP代码
    lisp_code = get_lisp_header(layers, dim_opts)
    lisp_code += generate_lisp_utility_functions(layers, dim_opts)

    # --- 封装绘图逻辑 ---
    def draw_view_outline(cx):
        # 绘制带圆角、螺纹和倒角的轮廓
        code = f'  (command "_.-LAYER" "_S" "{layers["outline"]["name"]}" "")\n'
        code += f'  (command "_.LINE" (list {cx - head_radius} {y_head_top}) (list {cx + head_radius} {y_head_top}) "")\n'
        code += f'  (command "_.LINE" (list {cx - head_radius} {y_head_top}) (list {cx - head_radius} {y_head_bottom}) "")\n'
        code += f'  (command "_.LINE" (list {cx + head_radius} {y_head_top}) (list {cx + head_radius} {y_head_bottom}) "")\n'
        code += f'  (command "_.LINE" (list {cx - head_radius} {y_head_bottom}) (list {cx - shaft_radius - fillet_radius} {y_head_bottom}) "")\n'
        code += f'  (command "_.LINE" (list {cx + head_radius} {y_head_bottom}) (list {cx + shaft_radius + fillet_radius} {y_head_bottom}) "")\n'
        code += f'  (command "_.LINE" (list {cx - shaft_radius} {y_shaft_bottom + end_chamfer_size}) (list {cx - shaft_radius} {y_fillet_start}) "")\n'
        code += f'  (command "_.LINE" (list {cx + shaft_radius} {y_shaft_bottom + end_chamfer_size}) (list {cx + shaft_radius} {y_fillet_start}) "")\n'
        code += f'  (command "_.LINE" (list {cx - shaft_radius} {y_shaft_bottom + end_chamfer_size}) (list {cx - (shaft_radius - end_chamfer_size)} {y_shaft_bottom}) "")\n'
        code += f'  (command "_.LINE" (list {cx + shaft_radius} {y_shaft_bottom + end_chamfer_size}) (list {cx + (shaft_radius - end_chamfer_size)} {y_shaft_bottom}) "")\n'
        code += f'  (command "_.LINE" (list {cx - (shaft_radius - end_chamfer_size)} {y_shaft_bottom}) (list {cx + (shaft_radius - end_chamfer_size)} {y_shaft_bottom}) "")\n'
        code += f'  (command "_.ARC" "_C" (list {cx - shaft_radius - fillet_radius} {y_fillet_start}) (list {cx - shaft_radius} {y_fillet_start}) (list {cx - shaft_radius - fillet_radius} {y_head_bottom}))\n'
        code += f'  (command "_.ARC" "_C" (list {cx + shaft_radius + fillet_radius} {y_fillet_start}) (list {cx + shaft_radius + fillet_radius} {y_head_bottom}) (list {cx + shaft_radius} {y_fillet_start}))\n'
        # 螺纹小径线
        code += f'  (command "_.LINE" (list {cx - (shaft_radius - end_chamfer_size)} {y_shaft_bottom}) (list {cx - (shaft_radius - end_chamfer_size)} {y_thread_end}) "")\n'
        code += f'  (command "_.LINE" (list {cx + (shaft_radius - end_chamfer_size)} {y_shaft_bottom}) (list {cx + (shaft_radius - end_chamfer_size)} {y_thread_end}) "")\n'
        # [新增] 螺纹小径的终止线
        code += f'  (command "_.LINE" (list {cx - shaft_radius} {y_shaft_bottom + end_chamfer_size}) (list {cx + shaft_radius} {y_shaft_bottom + end_chamfer_size}) "")\n'
        return code

    # --- 绘制主视图 ---
    lisp_code += "\n  ;; --- 绘制主视图 ---\n"
    lisp_code += draw_view_outline(x_center)
    # 绘制内部特征线
    lisp_code += f'  (command "_.-LAYER" "_S" "{layers["outline"]["name"]}" "")\n'
    lisp_code += f'  (command "_.LINE" (list {x_center - shaft_radius} {y_head_bottom}) (list {x_center + shaft_radius} {y_head_bottom}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {x_center - shaft_radius} {y_thread_end}) (list {x_center + shaft_radius} {y_thread_end}) "")\n'
    # 绘制内六角孔 (隐藏线)
    lisp_code += f'  (command "_.-LAYER" "_S" "{layers["hidden"]["name"]}" "")\n'
    lisp_code += f'  (command "_.LINE" (list {x_center - socket_half_width_flats} {y_socket_bottom}) (list {x_center} {y_socket_tip_flats}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {x_center} {y_socket_tip_flats}) (list {x_center + socket_half_width_flats} {y_socket_bottom}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {x_center - socket_half_width_flats} {y_socket_bottom}) (list {x_center - socket_half_width_flats} {y_intersection_flats}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {x_center - socket_half_width_flats} {y_intersection_flats}) (list {x_center - socket_countersink_half_width} {y_head_top}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {x_center + socket_half_width_flats} {y_socket_bottom}) (list {x_center + socket_half_width_flats} {y_intersection_flats}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {x_center + socket_half_width_flats} {y_intersection_flats}) (list {x_center + socket_countersink_half_width} {y_head_top}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {x_center - socket_inner_edge_offset} {y_socket_bottom}) (list {x_center - socket_inner_edge_offset} {y_intersection_inner}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {x_center + socket_inner_edge_offset} {y_socket_bottom}) (list {x_center + socket_inner_edge_offset} {y_intersection_inner}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {x_center - socket_half_width_flats} {y_socket_bottom}) (list {x_center + socket_half_width_flats} {y_socket_bottom}) "")\n'
    # --- 绘制右视图 ---
    lisp_code += "\n  ;; --- 绘制右视图 ---\n"
    lisp_code += draw_view_outline(right_view_cx)
    # 绘制内部特征线
    lisp_code += f'  (command "_.-LAYER" "_S" "{layers["outline"]["name"]}" "")\n'
    lisp_code += f'  (command "_.LINE" (list {right_view_cx - shaft_radius} {y_head_bottom}) (list {right_view_cx + shaft_radius} {y_head_bottom}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {right_view_cx - shaft_radius} {y_thread_end}) (list {right_view_cx + shaft_radius} {y_thread_end}) "")\n'
    # 绘制内六角孔 (隐藏线)
    lisp_code += f'  (command "_.-LAYER" "_S" "{layers["hidden"]["name"]}" "")\n'
    lisp_code += f'  (command "_.LINE" (list {right_view_cx - socket_half_width_corners} {y_socket_bottom}) (list {right_view_cx} {y_socket_tip_corners}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {right_view_cx} {y_socket_tip_corners}) (list {right_view_cx + socket_half_width_corners} {y_socket_bottom}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {right_view_cx - socket_half_width_corners} {y_socket_bottom}) (list {right_view_cx - socket_half_width_corners} {y_intersection_corners}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {right_view_cx - socket_half_width_corners} {y_intersection_corners}) (list {right_view_cx - socket_countersink_half_width} {y_head_top}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {right_view_cx + socket_half_width_corners} {y_socket_bottom}) (list {right_view_cx + socket_half_width_corners} {y_intersection_corners}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {right_view_cx + socket_half_width_corners} {y_intersection_corners}) (list {right_view_cx + socket_countersink_half_width} {y_head_top}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {right_view_cx} {y_socket_bottom}) (list {right_view_cx} {y_intersection_center_edge}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {right_view_cx - socket_half_width_corners} {y_socket_bottom}) (list {right_view_cx + socket_half_width_corners} {y_socket_bottom}) "")\n'
    # --- 绘制俯视图 ---
    lisp_code += "\n  ;; --- 绘制俯视图 ---\n"
    lisp_code += f'  (command "_.-LAYER" "_S" "{layers["outline"]["name"]}" "")\n'
    lisp_code += f'  (command "_.CIRCLE" (list {top_view_cx} {top_view_cy}) {head_radius})\n'
    lisp_code += f'  (command "_.POLYGON" 6 (list {top_view_cx} {top_view_cy}) "_I" {socket_half_width_flats})\n'
    lisp_code += f'  (command "_.CIRCLE" (list {top_view_cx} {top_view_cy}) {socket_countersink_half_width})\n'
    start_angle_deg, end_angle_deg = 135, 45
    p_start = f'(polar (list {top_view_cx} {top_view_cy}) (dtr {start_angle_deg}) {thread_minor_radius})'
    p_end = f'(polar (list {top_view_cx} {top_view_cy}) (dtr {end_angle_deg}) {thread_minor_radius})'
    lisp_code += f'  (command "_.ARC" "_C" (list {top_view_cx} {top_view_cy}) {p_start} {p_end})\n'

    # ... (中心线、标注和参数表部分的代码保持不变) ...
    lisp_code += "\n  ;; --- 绘制中心线 ---\n"
    lisp_code += f'  (command "_.-LAYER" "_S" "{layers["centerline"]["name"]}" "")\n'
    lisp_code += f'  (command "_.LINE" (list {x_center} {iy - 20}) (list {x_center} {top_view_cy + head_radius + 20}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {right_view_cx} {iy - 20}) (list {right_view_cx} {y_head_top + 20}) "")\n'
    lisp_code += f'  (command "_.LINE" (list {x_center - head_radius - 20} {top_view_cy}) (list {x_center + head_radius + 20} {top_view_cy}) "")\n'
    y_horizontal_cl = iy + shaft_length / 2
    lisp_code += f'  (command "_.LINE" (list {ix - 20} {y_horizontal_cl}) (list {right_view_cx + head_radius + 20} {y_horizontal_cl}) "")\n'

    lisp_code += "\n  ;; --- 尺寸标注 ---\n"
    lisp_code += f'  (command "_.-LAYER" "_S" "{layers["dimensions"]["name"]}" "")\n'
    lisp_code += f'  (command "_.DIMLINEAR" (list {x_center - head_radius} {y_shaft_bottom}) (list {x_center - head_radius} {y_head_top}) (list {ix - spacing} {iy + total_height / 2}))\n'
    lisp_code += f'  (command "_.DIMLINEAR" (list {x_center + head_radius} {y_head_bottom}) (list {x_center + head_radius} {y_head_top}) (list {x_center + head_radius + spacing / 2} {y_head_bottom + head_height / 2}))\n'
    lisp_code += f'  (command "_.DIMDIAMETER" "" (list {x_center - shaft_radius * 0.707} {y_head_bottom - 10}) (list {x_center - shaft_radius - spacing} {y_head_bottom - 10}))\n'
    lisp_code += f'  (command "_.DIMDIAMETER" "" (list {top_view_cx - head_radius * 0.707} {top_view_cy + head_radius * 0.707}) (list {top_view_cx - head_radius - spacing} {top_view_cy + head_radius + spacing}))\n'
    lisp_code += f'  (command "_.DIMLINEAR" (list {top_view_cx - socket_half_width_flats} {top_view_cy}) (list {top_view_cx + socket_half_width_flats} {top_view_cy}) (list {top_view_cx} {top_view_cy - head_radius - spacing}))\n'
    lisp_code += f'  (command "_.DIMLINEAR" (list {x_center + shaft_radius} {y_shaft_bottom}) (list {x_center + shaft_radius} {y_thread_end}) (list {x_center + shaft_radius + spacing} {y_shaft_bottom + thread_length / 2}))\n'

    lisp_code += "\n  ;; --- 高级标注 (示例) ---\n"
    for datum in datums:
        if datum['attach_to'] == 'head_underside':
            lisp_code += f'  (draw-datum-symbol (list {x_center + head_radius} {y_head_bottom}) (list {x_center + head_radius + spacing} {y_head_bottom}) "{datum["label"]}")\n'

    right_most_x = right_view_cx + head_radius
    top_y = y_head_top
    lisp_code += _generate_lisp_for_parameter_table(params, dim_opts, right_most_x, top_y, spacing)

    lisp_code += get_lisp_footer("Socket Head Cap Screw")
    return lisp_code
# ==============================================================================
# 主程序入口模块
# ==============================================================================
# ==============================================================================
# 主程序入口模块 (已根据您的要求进行扩展)
# ==============================================================================
# ==============================================================================
# 主程序入口模块 (最终完整版)
# ==============================================================================
if __name__ == "__main__":
    API_KEY = os.getenv("OPENAI_API_KEY")
    API_BASE_URL = os.getenv("OPENAI_API_BASE_URL")
    MODEL_NAME = os.getenv("AI_MODEL_NAME", "gemini-1.5-flash-latest")
    # 扩展 SHAPE_TO_FILE_MAP 字典以包含所有选项
    SHAPE_TO_FILE_MAP = {
        # --- 2D Drawings ---
        '1': 'cylinder_data.json',
        '2': 'hex_nut_data.json',
        '3': 'hex_prism_data.json',
        '4': 'hex_screw.json',
        '5': 'part_config.json',
        '6': 'screw_nut_assembly.json',
        '7': 'cuboid_cylinder_assembly.json',
        # [新增] 内六角圆柱头螺钉
        # --- 3D Models ---
        '8': 'screw_nut_assembly.json',
        '9': 'cuboid_cylinder_assembly.json',
        '10': 'hex_screw.json',
        '11': 'hex_nut_data.json',
        '12': 'cylinder_data.json',
        '13': 'part_config.json',
        '14': 'hex_prism_data.json',  # [新增] 3D 六棱柱
        '15': 'socket_head_cap_screw_data.json',
        '16': 'socket_head_cap_screw_data.json'  # [新增] 3D 内六角螺钉
    }

    # 注册所有生成器函数，包括所有3D零件
    shape_generators = {
        # --- 2D 生成器 ---
        'cylinder': generate_lisp_for_cylinder,
        'hexagonal_nut': generate_lisp_for_hex_nut,
        'hexagonal_prism': generate_lisp_for_hex_prism,
        'hexagonal_screw': generate_lisp_for_hex_screw,
        'cuboid': generate_lisp_for_cuboid,
        'screw_nut_assembly': generate_lisp_for_screw_nut_assembly,
        'cuboid_cylinder_assembly': generate_lisp_for_cuboid_cylinder_assembly,
        'socket_head_cap_screw': generate_lisp_for_socket_head_cap_screw,  # [新增]
        # --- 3D 生成器 ---
        'screw_nut_assembly_3d': generate_3d_lisp_for_screw_nut_assembly,
        'cuboid_cylinder_assembly_3d': generate_3d_lisp_for_cuboid_cylinder_assembly,
        'hex_screw_3d': generate_3d_lisp_for_hex_screw,
        'hex_nut_3d': generate_3d_lisp_for_hex_nut,
        'cylinder_3d': generate_3d_lisp_for_cylinder,
        'cuboid_3d': generate_3d_lisp_for_cuboid,
        'hex_prism_3d': generate_3d_lisp_for_hex_prism,  # [新增]
        'socket_head_cap_screw_3d': generate_3d_lisp_for_socket_head_cap_screw  # [新增]
    }

    # 确保所有必需的JSON文件都存在
    for fname in set(SHAPE_TO_FILE_MAP.values()):
        if not os.path.exists(fname):
            with open(fname, 'w', encoding='utf-8') as f:
                f.write('{"shape": "unknown"}')
            print(f"警告: '{fname}' 不存在, 已自动创建。请为该文件填入正确数据。")

    try:
        # 更新菜单提示，加入所有新选项
        menu_prompt = textwrap.dedent("""
        请选择要生成的图形：
        --- 2D 工程图 (2D Engineering Drawings) ---
          1: 圆柱体 (Cylinder)
          2: 六角螺母 (Hexagonal Nut)
          3: 六棱柱 (Hexagonal Prism)
          4: 六角螺钉 (Hexagonal Screw)
          5: 长方体 (Cuboid)
          6: 螺钉-螺母装配体 (Screw-Nut Assembly)
          7: 长方体-圆柱装配体 (Cuboid-Cylinder Assembly)
          15: 内六角圆柱头螺钉 (Socket Head Cap Screw)
        --- 3D 实体模型 (3D Solid Models) ---
          8: 3D 螺钉-螺母装配体 (3D Screw-Nut Assembly)
          9: 3D 长方体-圆柱装配体 (3D Cuboid-Cylinder Assembly)
         10: 3D 六角螺钉 (3D Hexagonal Screw)
         11: 3D 六角螺母 (3D Hexagonal Nut)
         12: 3D 圆柱体 (3D Cylinder)
         13: 3D 长方体 (3D Cuboid)
         14: 3D 六棱柱 (3D Hexagonal Prism)
         16: 3D 内六角圆柱头螺钉 (3D Socket Head Cap Screw)
        请输入选项 (1-14): """)

        user_choice = sys.argv[1] if len(sys.argv) > 1 else input(menu_prompt)

        input_json_file = SHAPE_TO_FILE_MAP.get(user_choice)
        if not input_json_file:
            raise ValueError(f"无效的选项 '{user_choice}'。请输入1到14之间的数字。")

        with open(input_json_file, "r", encoding="utf-8") as f:
            drawing_data = json.load(f)
        print(f"成功从 '{input_json_file}' 加载数据。")

        # 扩展调用逻辑的映射字典
        shape_type_mapping = {
            '8': 'screw_nut_assembly_3d',
            '9': 'cuboid_cylinder_assembly_3d',
            '10': 'hex_screw_3d',
            '11': 'hex_nut_3d',
            '12': 'cylinder_3d',
            '13': 'cuboid_3d',
            '14': 'hex_prism_3d',  # [新增]
            '16': 'socket_head_cap_screw_3d'  # [新增]
        }

        if user_choice in shape_type_mapping:
            shape_type = shape_type_mapping[user_choice]
            print(f"准备生成 3D 实体模型: {shape_type}...")
        else:
            shape_type = drawing_data.get('shape')
            if not shape_type:
                raise ValueError(f"'{input_json_file}' 中缺少 'shape' 键。")
            print(f"准备生成 2D 工程图: {shape_type}...")

        # 自定义参数输入部分 (保持不变)
        if shape_type.startswith('cuboid') or shape_type.startswith(
                'screw_nut') or '2d' in shape_type or user_choice in ['1', '2', '3', '4', '5', '6', '7','15']:
            print("\n--- 可选：添加自定义参数到参数表 ---")
            while True:
                user_input = input("请输入自定义参数 (格式: 参数名:值)，或直接按回车键完成: ")
                if not user_input:
                    print("--- 自定义参数输入完成 ---")
                    break
                parts = user_input.split(':', 1) if ':' in user_input else user_input.split('：', 1)
                if len(parts) == 2:
                    key, value = parts[0].strip(), parts[1].strip()
                    if key and value:
                        if 'parameters' not in drawing_data:
                            drawing_data['parameters'] = {}
                        drawing_data['parameters'][key] = value
                        print(f"  > 已添加: '{key}' = '{value}'")
                    else:
                        print("  [错误] 参数名或值不能为空，请重试。")
                else:
                    print("  [错误] 输入格式无效，请使用 '参数名:值' 格式。")

        # 调用生成器 (保持不变)
        generator_func = shape_generators.get(shape_type)
        if not generator_func:
            raise TypeError(f"未找到形状 '{shape_type}' 对应的生成器函数。")

        lisp_output = generator_func(drawing_data)
        # ==========================================================
        # ==           在这里调用独立的 LLM 验证器模块          ==
        # ==========================================================
        if VALIDATOR_AVAILABLE and API_KEY:
            llm_validator = LLMValidator(
                api_key=API_KEY,
                base_url=API_BASE_URL,
                model_name=MODEL_NAME
            )
            is_valid_by_llm = llm_validator.validate(lisp_output, drawing_data)

            if not is_valid_by_llm:
                proceed = input("LLM验证器发现严重错误或API调用失败。是否仍然要生成 .lsp 文件? (y/n): ")
                if proceed.lower() != 'y':
                    print("操作已取消。")
                    sys.exit(1)
        elif not API_KEY:
            print("\n[提示] 未在.env文件中找到或设置 OPENAI_API_KEY 环境变量，跳过LLM验证。")

        # 文件输出 (保持不变)
        output_lisp_file = "draw_object.lsp"
        with open(output_lisp_file, "w", encoding="utf-8") as f:
            f.write(lisp_output)

        print(f"\n已成功为 '{shape_type}' 生成LISP代码。")
        print(f"输出文件: '{output_lisp_file}'")
        print("在AutoCAD中，请使用 APPLOAD 命令加载该文件，然后输入命令 'DrawMyObject' 来运行。")

    except Exception as e:
        print(f"\n程序运行出错: {e}")
        import traceback

        traceback.print_exc()