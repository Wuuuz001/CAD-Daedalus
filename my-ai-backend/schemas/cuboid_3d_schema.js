// my-ai-backend/schemas/cuboid_schema.js

export const cuboid3dSchema = {
  // --- 根级字段 ---
  shape: { 
    value: "cuboid", 
    description: "对象的形状类型，固定为 'cuboid'。" 
  },

  // --- 基本参数 (需要从图中提取) ---
  parameters: {
    label: "基本参数",
    type: "object",
    properties: {
      length: { label: "长度", type: "number", description: "EXTRACT FROM IMAGE - The primary length dimension of the cuboid." },
      width: { label: "宽度", type: "number", description: "EXTRACT FROM IMAGE - The primary width dimension of the cuboid." },
      height: { label: "高度", type: "number", description: "EXTRACT FROM IMAGE - The primary height dimension of the cuboid." }
    }
  },

  // --- 绘图选项 (固定值，AI无需修改) ---
  drawing_options: {
    label: "绘图选项",
    type: "object",
    properties: {
      insertion_point: { value: [10.0, 10.0], description: "Fixed insertion point." },
      spacing: { value: 50.0, description: "Fixed spacing between views." },
      layers: {
        label: "图层",
        type: "object",
        properties: {
          outline: { value: { "name": "Outline", "color": 7 }, description: "Fixed outline layer settings." },
          centerline: { value: { "name": "Centerline", "color": 1, "linetype": "CENTER" }, description: "Fixed centerline layer settings." },
          dimensions: { value: { "name": "Dimensions", "color": 2 }, description: "Fixed dimensions layer settings." },
          annotations: { value: { "name": "Annotations", "color": 6 }, description: "Fixed annotations layer settings." }
        }
      },
      dimension_options: {
        label: "尺寸标注选项",
        type: "object",
        properties: {
          text_height: { value: 3.5, description: "Fixed dimension text height." },
          arrow_size: { value: 2.5, description: "Fixed dimension arrow size." }
        }
      }
    }
  },

  // --- 基准 (需要从图中提取) ---
  datums: {
    label: "基准",
    type: "array",
    description: "EXTRACT FROM IMAGE - Find all datums (e.g., circled A, B) and their attachment points on the drawing.",
    item_schema: {
      type: "object",
      properties: {
        label: { label: "基准标签", type: "string", description: "EXTRACT FROM IMAGE - The datum letter, e.g., 'A'." },
        attach_to: { label: "附着点", type: "string", description: "EXTRACT FROM IMAGE - A semantic description of where the datum is attached, e.g., 'front_view_bottom_mid'." }
      }
    }
  },

  // --- 几何公差 (需要从图中提取) ---
  geometric_tolerances: {
    label: "几何公差",
    type: "array",
    description: "EXTRACT FROM IMAGE - Find all geometric tolerance control frames on the drawing.",
    item_schema: {
      type: "object",
      properties: {
        type: { label: "公差类型", type: "string", description: "EXTRACT FROM IMAGE - The type of tolerance, e.g., 'perpendicularity', 'parallelism'." },
        tolerance: { label: "公差值", type: "string", description: "EXTRACT FROM IMAGE - The tolerance value, as a string (e.g., '0.05')." },
        datum_references: {
          label: "参考基准",
          type: "array",
          description: "EXTRACT FROM IMAGE - The datum letters referenced in the frame, e.g., ['A', 'B'].",
          item_schema: { type: "string" }
        },
        attach_to: { label: "附着点", type: "string", description: "EXTRACT FROM IMAGE - A semantic description of where the tolerance frame is attached." }
      }
    }
  },

  // --- 表面粗糙度 (需要从图中提取符号) ---
  // 注意：我们使用对象结构让AI填充，然后在后端转换为数组，这与您现有的cylinder逻辑一致。
  surface_finish: {
    label: "表面粗糙度",
    type: "object",
    description: "EXTRACT FROM IMAGE - Find all surface finish symbols on the drawing.",
    properties: {
      top_surface: {
        label: "顶面",
        type: "object",
        properties: {
          symbol: { label: "符号", type: "string", description: "EXTRACT FROM IMAGE - The surface finish symbol value (e.g., 'Ra 3.2')." },
          orientation: { value: 0, description: "Fixed orientation value." },
          position: { value: 8.0, description: "Fixed position value." }
        }
      },
      right_side_surface: {
        label: "右侧面",
        type: "object",
        properties: {
          symbol: { label: "符号", type: "string", description: "EXTRACT FROM IMAGE - The surface finish symbol value." },
          orientation: { value: 90, description: "Fixed orientation value." },
          position: { value: 8.0, description: "Fixed position value." }
        }
      }
    }
  },
    ai_analysis_notes: {
      type: 'string',
      description: 'Your brief analysis notes. Be concise.'
  },
};