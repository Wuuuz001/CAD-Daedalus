export const cuboidCylinderAssembly3dSchema = {
  // 基本信息
  shape: {
    type: 'string',
    value: 'cuboid_cylinder_assembly',
    description: 'The object type, which is an assembly of a cuboid and a cylinder.'
  },

  // 绘图选项 (固定值)
  drawing_options: {
    type: 'object',
    value: {
      insertion_point: [10, 10],
      spacing: 50,
      draw_section_view: true,
      layers: {
        outline: { name: 'Outline', color: 7 },
        hidden: { name: 'Hidden', color: 7, linetype: 'HIDDEN' },
        centerline: { name: 'Centerline', color: 1, linetype: 'CENTER' },
        dimensions: { name: 'Dimensions', color: 2 },
        annotations: { name: 'Annotations', color: 6 },
        hatch: { name: 'Hatch', color: 7 }
      },
      dimension_options: { text_height: 3.5, arrow_size: 2.5 },
      hatch_options: { pattern: 'ANSI31', scale: 1.50 }
    },
    description: 'Pre-defined options for CAD drawing generation.'
  },

  // 组件 (核心部分，AI填充参数)
  components: {
    type: 'object',
    properties: {
      cuboid: {
        type: 'object',
        properties: {
          name: { type: 'string', value: 'Base Block' },
          parameters: {
            type: 'object',
            properties: {
              length: { type: 'number', description: 'Length of the base cuboid block.' },
              width: { type: 'number', description: 'Width of the base cuboid block.' },
              height: { type: 'number', description: 'Height of the base cuboid block.' },
              height_tolerance: { type: 'string', description: 'Tolerance for the cuboid height.' }
            }
          }
        }
      },
      cylinder: {
        type: 'object',
        properties: {
          name: { type: 'string', value: 'Embedded Post' },
          parameters: {
            type: 'object',
            properties: {
              radius: { type: 'number', description: 'Radius of the cylindrical post.' },
              height: { type: 'number', description: 'Height of the cylindrical post.' },
              diameter_tolerance: { type: 'string', description: 'Tolerance for the cylinder diameter.' }
            }
          }
        }
      }
    },
    description: 'The individual components that make up the assembly.'
  },
  
  // 基准 (固定值)
  datums: {
    type: 'array_of_objects',
    item_schema: { properties: { label: { type: 'string' }, attach_to: { type: 'string' } } },
    value: [
      { label: 'A', attach_to: 'front_view_bottom_mid' },
      { label: 'B', attach_to: 'side_view_left_mid' },
      { label: 'C', attach_to: 'front_view_left_mid' }
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
      { type: 'perpendicularity', tolerance: null, datum_references: ['A'], attach_to: 'hole_outline_top_view' },
      { type: 'parallelism', tolerance: null, datum_references: ['B'], attach_to: 'front_view_top_surface' }
    ],
    description: 'Geometric tolerances applied to the assembly.'
  },

  // 表面粗糙度 (AI填充符号，其他值固定)
  surface_finish: {
    type: 'object',
    properties: {
      top_surface: {
        type: 'object',
        properties: {
          symbol: { type: 'string', description: 'Surface finish symbol for the top face of the cuboid.' },
          orientation: { type: 'number', value: 0 },
          position: { type: 'number', value: 5 }
        }
      },
      hole_bottom: {
        type: 'object',
        properties: {
          symbol: { type: 'string', description: 'Surface finish symbol for the bottom of the hole in the cuboid.' },
          orientation: { type: 'number', value: 0 },
          position: { type: 'number', value: 5 }
        }
      },
      hole_wall: {
        type: 'object',
        properties: {
          symbol: { type: 'string', description: 'Surface finish symbol for the inner wall of the hole.' },
          orientation: { type: 'number', value: 90 },
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