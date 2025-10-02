// schemas/cylinder_schema.js (v4 - 精确处理geometric_tolerances)
export const cylinder3dSchema = {
  
  shape: {
    type: "string",
    description: "Fixed value: The type of the shape.",
    value: "cylinder" 
  },
  parameters: {
    type: "object",
    description: "Core physical dimensions of the cylinder.",
    properties: {
      radius: { type: "number | null", description: "EXTRACT FROM IMAGE: The radius of the cylinder." },
      height: { type: "number | null", description: "EXTRACT FROM IMAGE: The total height/length of the cylinder." },
      height_tolerance: { type: "string | null", description: "EXTRACT FROM IMAGE: The tolerance for the height." },
      diameter_tolerance: { type: "string | null", description: "EXTRACT FROM IMAGE: The tolerance for the diameter." }
    }
  },
  drawing_options: {
    type: "object",
    description: "Fixed value: Default drawing settings.",
    value: {
      // ... (内容与之前版本完全相同)
      "insertion_point": [10.0, 10.0],
      "spacing": 60.0,
      "layers": {
        "outline": { "name": "Outline", "color": 7, "linetype": "Continuous" },
        "centerline": { "name": "Centerline", "color": 1, "linetype": "CENTER" },
        "dimensions": { "name": "Dimensions", "color": 2, "linetype": "Continuous" },
        "annotations": { "name": "Annotations", "color": 6, "linetype": "Continuous" }
      },
      "dimension_options": { "text_height": 3.5, "arrow_size": 2.5 }
    }
  },
  surface_finish: {
    type: "object",
    description: "Surface finish requirements.",
    properties: {
      side_surface: {
        type: "object",
        properties: {
            symbol: { type: "string | null", description: "EXTRACT FROM IMAGE: The side surface finish symbol, e.g., 'Ra 3.2'." },
            orientation: { type: "number", description: "Fixed value.", value: 90 },
            position: { type: "number", description: "Fixed value.", value: 5 }
        }
      },
      top_surface: {
        type: "object",
        properties: {
            symbol: { type: "string | null", description: "EXTRACT FROM IMAGE: The top surface finish symbol, e.g., 'Ra 1.6'." },
            orientation: { type: "number", description: "Fixed value.", value: 0 },
            position: { type: "number", description: "Fixed value.", value: 5 }
        }
      }
    }
  },
  geometric_tolerances: {
    type: "array<object>",
    description: "This is a fixed structure. The AI only needs to find the two tolerance values on the drawing and fill them in.",
    // 我们直接定义了包含两个对象的完整模板
    value: [
      {
        "type": "perpendicularity",
        "leader_attach_point": "left_side",
        // 用一个特殊标记来表示这个字段需要AI填充
        "tolerance": "EXTRACT_TOLERANCE_1",
        "datum_references": ["A"],
        "frame_location": "left_of_front_view"
      },
      {
        "type": "parallelism",
        "leader_attach_point": "right_side",
        // 第二个需要填充的字段
        "tolerance": "EXTRACT_TOLERANCE_2",
        "datum_references": ["B"],
        "frame_location": "right_of_right_view"
      }
    ]
  },
  datums: {
    type: "array<object>",
    description: "Fixed value: A list of datum features.",
    value: [
      { "label": "A", "attach_face": "bottom" },
      { "label": "B", "attach_face": "centerline" }
    ]
  },
    ai_analysis_notes: {
      type: 'string',
      description: 'Your brief analysis notes. Be concise.'
  },
};