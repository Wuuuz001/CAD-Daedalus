// my-ai-backend/schemas/hexagonal_prism_schema.js (V3 - 最终精确填空版)

export const hexagonalPrism3dSchema = {
  // ... 其他字段保持不变 ...
  shape: { value: "hexagonal_prism" },
  view_type: { value: "three_view_with_dims" },
  parameters: {
    // ...
    label: "基本参数", type: "object",
    properties: {
      side_length: { label: "对边距", type: "number", description: "EXTRACT FROM IMAGE" },
      height: { label: "高度", type: "number", description: "EXTRACT FROM IMAGE" },
      height_tolerance: { label: "高度公差", type: "string", description: "EXTRACT FROM IMAGE" },
      width_tolerance: { label: "宽度公差", type: "string", description: "EXTRACT FROM IMAGE" }
    }
  },
  drawing_options: { /* ...此部分是固定的，保持不变... */ value: { /* ... */ } },
  datums: { /* ...此部分是固定的，保持不变... */ value: [ { "label": "A", "attach_to": "front_view_centerline_bottom" }, { "label": "B", "attach_to": "right_view_right_side_midpoint" } ] },


  // ====================【核心修正部分】====================
  // 我们将整个数组结构定义为固定值，其中包含需要被填充的 null
  geometric_tolerances: {
    label: "几何公差",
    value: [
      {
        "type": "perpendicularity",
        "tolerance": null, // 这里是需要AI填写的空
        "datum_references": ["A"],
        "attach_to": "front_view_left_side"
      },
      {
        "type": "perpendicularity",
        "tolerance": null, // 这里是需要AI填写的空
        "datum_references": ["B"],
        "attach_to": "right_view_top_surface"
      }
    ],
    // 这个描述现在是给AI的特殊指令
    description: "This is a fixed-template field. See RULE #5 in the prompt for special instructions on how to fill it."
  },

  surface_finish: {
    label: "表面粗糙度",
    value: {
      // 这里的 "top_surface" 整个也是一个固定模板
      "top_surface": [null, -90, 8.0]
    },
    description: "This is a fixed-template field. See RULE #5 in the prompt for special instructions on how to fill it."
  },
  // ==========================================================

    ai_analysis_notes: {
      type: 'string',
      description: 'Your brief analysis notes. Be concise.'
  },
  
};