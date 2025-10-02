export const hexagonalScrew3dSchema = {
  // 基本信息
  shape: {
    type: 'string',
    value: 'hexagonal_screw',
    description: 'The geometric shape of the object, which is always "hexagonal_screw".'
  },

  // 主要参数
  parameters: {
    type: 'object',
    properties: {
      head: {
        type: 'object',
        properties: {
          side_length: { type: 'number', description: 'The length of one of the six sides of the hexagonal head.' },
          height: { type: 'number', description: 'The height of the hexagonal head.' }
        }
      },
      shaft: {
        type: 'object',
        properties: {
          diameter: { type: 'number', description: 'The diameter of the screw shaft.' },
          length: { type: 'number', description: 'The length of the screw shaft (from under the head to the tip).' }
        }
      },
      total_height_tolerance: {
        type: 'string',
        description: 'The tolerance for the total height of the screw, e.g., "±0.1".'
      },
      head_width_tolerance: {
        type: 'string',
        description: 'The tolerance for the width across the flats of the head, e.g., "±0.05".'
      }
    },
    description: 'The main dimensional parameters of the hexagonal screw.'
  },
  
  // 绘图选项 (固定值)
  drawing_options: {
    type: 'object',
    value: {
      insertion_point: [10.0, 10.0],
      spacing: 80.0,
      layers: {
        outline: { name: 'Outline', color: 7 },
        centerline: { name: 'Centerline', color: 1, linetype: 'CENTER' },
        dimensions: { name: 'Dimensions', color: 2 },
        annotations: { name: 'Annotations', color: 6 }
      },
      dimension_options: {
        text_height: 3.5,
        arrow_size: 2.5
      }
    },
    description: 'Pre-defined options for CAD drawing generation.'
  },

  // 基准 (固定值)
  datums: {
    type: 'array_of_objects',
    item_schema: {
      properties: {
        label: { type: 'string' },
        attach_to: { type: 'string' }
      }
    },
    value: [
      { label: 'A', attach_to: 'bottom_surface' },
      { label: 'B', attach_to: 'centerline_of_right_view' }
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
        type: 'perpendicularity',
        tolerance: null, // AI to fill
        datum_references: ['A'],
        attach_to: 'front_view_left_side_of_head'
      },
      {
        type: 'parallelism',
        tolerance: null, // AI to fill
        datum_references: ['B'],
        attach_to: 'right_view_top_surface'
      }
    ],
    description: 'Geometric tolerances applied to the part.'
  },

  // 表面粗糙度 (AI填充符号，其他值固定)
  surface_finish: {
    type: 'object',
    properties: {
      top_surface: {
        type: 'object',
        properties: {
          symbol: { type: 'string', description: 'The surface finish symbol, e.g., "Ra3.2".' },
          orientation: { type: 'number', value: 0 },
          position: { type: 'number', value: 8.0 }
        }
      },
      side_surface: {
        type: 'object',
        properties: {
          symbol: { type: 'string', description: 'The surface finish symbol.' },
          orientation: { type: 'number', value: 90 },
          position: { type: 'number', value: 8.0 }
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