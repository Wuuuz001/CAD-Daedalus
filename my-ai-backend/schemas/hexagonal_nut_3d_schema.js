export const hexagonalNut3dSchema = {
  // 基本信息
  shape: {
    type: 'string',
    value: 'hexagonal_nut',
    description: 'The geometric shape of the object, which is always "hexagonal_nut".'
  },

  // 主要参数
  parameters: {
    type: 'object',
    properties: {
      side_length: {
        type: 'number',
        description: 'The length of one of the six outer sides of the hexagon.'
      },
      side_length_tolerance: {
        type: 'string',
        description: 'The tolerance for the side length, e.g., "±0.1".'
      },
      height: {
        type: 'number',
        description: 'The overall height (thickness) of the nut.'
      },
      height_tolerance: {
        type: 'string',
        description: 'The tolerance for the height, e.g., "±0.05".'
      },
      hole: {
        type: 'object',
        properties: {
          diameter: {
            type: 'number',
            description: 'The diameter of the central threaded hole.'
          },
          diameter_tolerance: {
            type: 'string',
            description: 'The tolerance for the hole diameter, e.g., "±0.02".'
          }
        },
        description: 'Parameters of the central hole.'
      }
    },
    description: 'The main dimensional parameters of the hexagonal nut.'
  },
  
  // 绘图选项 (固定值，AI无需修改)
  drawing_options: {
    type: 'object',
    value: {
      insertion_point: [10.0, 10.0],
      spacing: 70.0,
      layers: {
        outline: { name: 'Outline', color: 7 },
        centerline: { name: 'Centerline', color: 1, linetype: 'CENTER' },
        hidden: { name: 'Hidden', color: 4, linetype: 'HIDDEN' },
        dimensions: { name: 'Dimensions', color: 2 },
        outline_hidden: { name: 'Outline_Hidden', color: 7, linetype: 'HIDDEN2' },
        annotations: { name: 'Annotations', color: 6, linetype: 'Continuous' }
      },
      dimension_options: { text_height: 3.5, arrow_size: 2.5 },
      hatch_options: { pattern: 'ANSI31', scale: 1.0 }
    },
    description: 'Pre-defined options for CAD drawing generation.'
  },

  // 基准 (固定值，AI无需修改)
  datums: {
    type: 'array_of_objects',
    item_schema: {
      properties: {
        label: { type: 'string' },
        attach_face: { type: 'string' }
      }
    },
    value: [
      { label: 'A', attach_face: 'bottom' },
      { label: 'B', attach_face: 'side_face_right_view' },
      { label: 'C', attach_face: 'inner_hole_top_view' }
    ],
    description: 'Datum reference points for geometric tolerances.'
  },

  // 几何公差 (部分值固定，AI填充null)
  geometric_tolerances: {
    type: 'array_of_objects',
    item_schema: {
      properties: {
        type: { type: 'string' },
        tolerance: { type: 'string' },
        datum_references: { type: 'array_of_strings' },
        attach_to: { type: 'string' }
      }
    },
    value: [
      {
        type: 'flatness',
        tolerance: null, // AI to fill
        datum_references: ['B'],
        attach_to: 'side_face_of_right_view'
      },
      {
        type: 'perpendicularity',
        tolerance: null, // AI to fill
        datum_references: ['A'],
        attach_to: 'side_face_of_front_view'
      },
      {
        type: 'position',
        tolerance: '%%c0.1', // This is a fixed value
        datum_references: ['C'],
        attach_to: 'inner_hole_top_view'
      }
    ],
    description: 'Geometric tolerances applied to the part.'
  },

  // 表面粗糙度 (AI填充符号，其他值固定)
  surface_finish: {
    type: 'object',
    properties: {
      top_face: {
        type: 'object',
        properties: {
          symbol: { type: 'string', description: 'The surface finish symbol, e.g., "Ra3.2".' },
          orientation: { type: 'number', value: 90 },
          position: { type: 'number', value: 5.0 }
        }
      },
      side_face_right_view: {
        type: 'object',
        properties: {
          symbol: { type: 'string', description: 'The surface finish symbol.' },
          orientation: { type: 'number', value: 0 },
          position: { type: 'number', value: 5.0 }
        }
      },
      inner_hole_top_view: {
        type: 'object',
        properties: {
          symbol: { type: 'string', description: 'The surface finish symbol.' },
          orientation: { type: 'number', value: 45 },
          position: { type: 'number', value: 5.0 }
        }
      }
    },
    description: 'Surface finish requirements for different faces.'
  },
    ai_analysis_notes: {
      type: 'string',
      description: 'Your brief analysis notes. Be concise.'
  },
};