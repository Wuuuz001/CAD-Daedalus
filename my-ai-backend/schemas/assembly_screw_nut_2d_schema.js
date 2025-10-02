export const screwNutAssembly2dSchema = {
  // 基本信息
  shape: {
    type: 'string',
    value: 'screw_nut_assembly',
    description: 'The object type, which is an assembly of a screw and a nut.'
  },

  // 绘图选项 (固定值)
  drawing_options: {
    type: 'object',
    value: {
      insertion_point: [10, 10],
      spacing: 50,
      draw_section_view: true,
      hatch_options: { pattern: 'ANSI31', scale: 1.0, color: 7 },
      layers: {
        outline: { name: 'Outline', color: 7 },
        dimensions: { name: 'Dimensions', color: 2 },
        centerline: { name: 'Centerline', color: 1, linetype: 'CENTER' },
        hidden: { name: 'Hidden', color: 7, linetype: 'HIDDEN' },
        annotations: { name: 'Annotations', color: 6 }
      },
      dimension_options: { text_height: 3.5, arrow_size: 2.5 }
    },
    description: 'Pre-defined options for CAD drawing generation.'
  },

  // 组件 (AI填充参数)
  components: {
    type: 'object',
    properties: {
      screw: {
        type: 'object',
        properties: {
          name: { type: 'string', value: 'Hex Screw M10x50' },
          quantity: { type: 'number', value: 1 },
          parameters: {
            type: 'object',
            properties: {
              head_width: { type: 'number', description: 'Width across the flats of the screw head.' },
              head_height: { type: 'number', description: 'Height of the screw head.' },
              shaft_diameter: { type: 'number', description: 'Diameter of the screw shaft.' },
              shaft_length: { type: 'number', description: 'Length of the screw shaft.' }
            }
          }
        }
      },
      nut: {
        type: 'object',
        properties: {
          name: { type: 'string', value: 'Hex Nut M10' },
          quantity: { type: 'number', value: 1 },
          parameters: {
            type: 'object',
            properties: {
              width: { type: 'number', description: 'Width across the flats of the nut.' },
              height: { type: 'number', description: 'Height of the nut.' },
              hole_diameter: { type: 'number', description: 'Diameter of the nut\'s hole.' }
            }
          }
        }
      }
    },
    description: 'The individual components that make up the assembly.'
  },

  // 装配体总体参数 (AI填充)
  parameters: {
    type: 'object',
    properties: {
      total_height_tolerance: { type: 'string', description: 'The tolerance for the total assembled height.' },
      head_width_tolerance: { type: 'string', description: 'The tolerance for the screw head width.' }
    },
    description: 'Overall parameters and tolerances for the entire assembly.'
  },

  // 基准 (固定值)
  datums: {
    type: 'array_of_objects',
    item_schema: { properties: { label: { type: 'string' }, attach_to: { type: 'string' } } },
    value: [
      { label: 'A', attach_to: 'underside_of_screw_head' },
      { label: 'B', attach_to: 'screw_axis_right_view' }
    ],
    description: 'Datum reference points for the assembly.'
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
      { type: 'perpendicularity', tolerance: null, datum_references: ['B'], attach_to: 'underside_of_screw_head_gdt' },
      { type: 'parallelism', tolerance: null, datum_references: ['A'], attach_to: 'nut_top_face' }
    ],
    description: 'Geometric tolerances applied to the assembly.'
  },

  // 表面粗糙度 (AI填充符号，其他值固定)
  surface_finish: {
    type: 'object',
    properties: {
      underside_of_screw_head: {
        type: 'object',
        properties: {
          symbol: { type: 'string', description: 'Surface finish symbol for the underside of the screw head.' },
          orientation: { type: 'number', value: 180 },
          position: { type: 'number', value: 5 }
        }
      },
      top_of_screw_head: {
        type: 'object',
        properties: {
          symbol: { type: 'string', description: 'Surface finish symbol for the top face of the screw head.' },
          orientation: { type: 'number', value: 0 },
          position: { type: 'number', value: 5 }
        }
      }
    },
    description: 'Surface finish requirements for different faces of the assembly.'
  },
    ai_analysis_notes: {
      type: 'string',
      description: 'Your brief analysis notes. Be concise.'
  },
};