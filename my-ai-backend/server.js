// server.js (最终修复版)

import express from 'express';
import { OpenAI } from 'openai';
import cors from 'cors';
import dotenv from 'dotenv';

// --- 导入所有 schemas ---
// (注意：我假设您已经将旧的 cylinder_schema.js 重命名为 cylinder_2d_schema.js)
import { cylinder2dSchema } from './schemas/cylinder_2d_schema.js';
import { cylinder3dSchema } from './schemas/cylinder_3d_schema.js';
import { cuboid2dSchema } from './schemas/cuboid_2d_schema.js'; 
import { cuboid3dSchema } from './schemas/cuboid_3d_schema.js'; // --- [新增] ---
import { hexagonalPrism2dSchema } from './schemas/hexagonal_prism_2d_schema.js';
import { hexagonalPrism3dSchema } from './schemas/hexagonal_prism_3d_schema.js'; // --- [新增] ---

import { hexagonalNut2dSchema } from './schemas/hexagonal_nut_2d_schema.js';
import { hexagonalNut3dSchema } from './schemas/hexagonal_nut_3d_schema.js'; // --- [新增] ---
import { hexagonalScrew2dSchema } from './schemas/hexagonal_screw_2d_schema.js';
import { hexagonalScrew3dSchema } from './schemas/hexagonal_screw_3d_schema.js'; // --- [新增] ---
// 假设装配体也只有2D版本
import { cuboidCylinderAssembly2dSchema } from './schemas/assembly_cuboid_cylinder_2d_schema.js';
import { cuboidCylinderAssembly3dSchema } from './schemas/assembly_cuboid_cylinder_3d_schema.js';
import { screwNutAssembly2dSchema } from './schemas/assembly_screw_nut_2d_schema.js';
import { screwNutAssembly3dSchema } from './schemas/assembly_screw_nut_3d_schema.js';
import { masterPromptTemplate } from './prompt_template.js';

// ... (您已有的 express, cors, openai, schemas 等所有代码保持不变) ...


// --- 初始化 ---
dotenv.config();
const app = express();
const port = process.env.PORT || 3001;
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
  baseURL: process.env.OPENAI_API_BASE_URL,
});
app.use(cors());
app.use(express.json({ limit: '10mb' }));

// --- 【核心】按维度组织的 Schema 映射 ---
const schemas = {
  '2d': {
    cylinder: cylinder2dSchema,
    cuboid: cuboid2dSchema,
    hexagonal_prism: hexagonalPrism2dSchema,
    hexagonal_nut: hexagonalNut2dSchema,
    hexagonal_screw: hexagonalScrew2dSchema,
    cuboid_cylinder_assembly: cuboidCylinderAssembly2dSchema,
    screw_nut_assembly: screwNutAssembly2dSchema,
  },
  '3d': {
    cylinder: cylinder3dSchema,
    cuboid: cuboid3dSchema, // --- [新增] ---
    hexagonal_prism: hexagonalPrism3dSchema,
    hexagonal_screw: hexagonalScrew3dSchema, // --- [新增] ---
    hexagonal_nut: hexagonalNut3dSchema, // --- [新增] ---
    cuboid_cylinder_assembly: cuboidCylinderAssembly3dSchema,
    screw_nut_assembly: screwNutAssembly3dSchema,
    // 将来可以在这里添加其他形状的3D schema
    // cuboid: cuboid3dSchema, 
  }
};

// --- 工具函数 (无变化) ---
function generateCleanJsonTemplate(schema) {
  if (!schema) { return {}; }
  const result = {};
  for (const key in schema) {
    const field = schema[key];
    if (field.value !== undefined) {
      result[key] = field.value;
      continue;
    }
    if (field.type.startsWith('array')) {
      if (field.item_schema && field.item_schema.properties) {
        result[key] = [generateCleanJsonTemplate(field.item_schema.properties)];
      } else {
        result[key] = [];
      }
    } else if (field.type === 'object' && field.properties) {
      result[key] = generateCleanJsonTemplate(field.properties);
    } else {
      result[key] = null;
    }
  }
  return result;
}

function postProcessJson(data) {
  // ... (此函数无变化)
  if (data.surface_finish && typeof data.surface_finish === 'object') {
    for (const surface in data.surface_finish) {
      const surfaceData = data.surface_finish[surface];
      if (surfaceData && typeof surfaceData === 'object' && 'symbol' in surfaceData) {
        const { symbol, orientation, position } = surfaceData;
        data.surface_finish[surface] = [symbol, orientation, position];
      }
    }
  }
  return data;
}

function preProcessIterationData(data) {
    // ... (此函数无变化)
    if (data.surface_finish && typeof data.surface_finish === 'object') {
        for (const surface in data.surface_finish) {
            const surfaceData = data.surface_finish[surface];
            if (Array.isArray(surfaceData)) {
                const [symbol, orientation, position] = surfaceData;
                data.surface_finish[surface] = { symbol, orientation, position };
            }
        }
    }
    return data;
}
// ==============================================================================
//  【【【 新增 API 端点：Python 函数生成器 】】】
// ==============================================================================
app.post('/api/generate_function', async (req, res) => {
  console.log('🤖 Received request to generate a new Python function...');
  
  const { description, imageBase64 } = req.body;

  if (!description && !imageBase64) {
    return res.status(400).json({ message: 'Request is empty. Please provide a text description or an image.' });
  }
  
  try {
    // 1. 从模板中构建最终的提示
    // 注意：我们用用户的真实需求替换掉了模板中的占位符 {{USER_SHAPE_DESCRIPTION}}
    const finalPrompt = masterPromptTemplate.replace('{{USER_SHAPE_DESCRIPTION}}', description || 'Analyze the provided image.');

    // 2. 准备发送给 OpenAI 的消息体
    const messages = [{
      role: 'user',
      content: [{ type: "text", text: finalPrompt }]
    }];
    
    // 如果用户上传了图片，也一并加入
    if (imageBase64) {
        messages[0].content.push({
            type: "image_url",
            image_url: { url: imageBase64, detail: "high" }
        });
    }

    // 3. 调用 OpenAI API
    console.log('Sending massive prompt to AI for code generation...');
    const response = await openai.chat.completions.create({
      model: process.env.AI_MODEL_NAME, // 建议使用能力更强的模型，如 gpt-4-turbo
      messages: messages,
      temperature: 0.2, // 使用较低的 temperature 让输出更稳定、更像代码
      max_tokens: 16384,
    });
    
    let generatedCode = response.choices[0].message.content;

    // 4. 清理 AI 返回的代码 (非常重要)
    // AI 经常会用 Markdown 的 ```python ... ``` 包裹代码，我们需要提取出来
    const codeBlockMatch = generatedCode.match(/```python\n([\s\S]*?)\n```/);
    if (codeBlockMatch && codeBlockMatch[1]) {
      generatedCode = codeBlockMatch[1];
    }
    
    console.log('✅ Successfully generated Python code snippet.');
    
    // 5. 将纯净的代码字符串返回给前端
    res.status(200).json({ python_code: generatedCode });

  } catch (error) {
    console.error('Error during Python function generation:', error);
    res.status(500).json({ message: 'Failed to generate Python function.', details: error.message });
  }
});

// --- API 路由 ---
// server.js

// ... (所有 imports, 初始化, schema映射, 工具函数都无变化) ...

// --- API 路由 (修复版) ---
app.post('/api/analyze', async (req, res) => {
  try {
    const { 
      image, 
      dimension, 
      initial_hint, 
      is_iteration, 
      previous_analysis, 
      user_text_prompt, 
      iteration_image 
    } = req.body;

    const targetDimension = dimension || '2d';

    if (!is_iteration && !image && !initial_hint) {
  // 只有在“首次分析”时，才检查“既没有图片也没有文本提示”的情况
  return res.status(400).json({ message: '请求无效，首次分析必须提供图片或文本提示' });
}

    let shapeName;

    if (is_iteration && previous_analysis && previous_analysis.shape) {
      shapeName = previous_analysis.shape;
      console.log(`🔄 开始迭代分析，形状: ${shapeName}, 目标维度: ${targetDimension.toUpperCase()}`);
    } else {
      // 首次分析逻辑 (这部分不变，保持您已有的)
      console.log(`🧐 开始首次分析..., 目标维度: ${targetDimension.toUpperCase()}`);
      let identifiedShapeName = 'unknown';
      if (initial_hint) {
        console.log(`📝 正在从文本提示 "${initial_hint}" 中解析形状...`);
        const shapeIdentificationPrompt = `From the user's text hint, identify the geometric shape name. The name must be one of: "cylinder", "cuboid", "hexagonal_prism", "hexagonal_nut", "hexagonal_screw", "cuboid_cylinder_assembly", "screw_nut_assembly". Your response MUST be a single JSON object: {"shape": "shape_name"}. User's Text Hint: "${initial_hint}"`;
        const shapeResponse = await openai.chat.completions.create({
            model: process.env.AI_MODEL_NAME,
            messages: [{ role: 'user', content: shapeIdentificationPrompt }],
            response_format: { type: "json_object" }
        });
        identifiedShapeName = JSON.parse(shapeResponse.choices[0].message.content).shape;
      }
      if (identifiedShapeName === 'unknown' && image) {
          console.log('🖼️ 文本提示无法确定形状，将使用图片进行AI识别...');
          const imageIdentificationPrompt = `Analyze the engineering drawing in the image. Identify the main object's geometric type. Your response MUST be a single JSON object: {"shape": "shape_name"}. The shape_name must be one of "cylinder", "cuboid", "hexagonal_prism", "hexagonal_nut", "hexagonal_screw", "cuboid_cylinder_assembly", "screw_nut_assembly", or "unknown".`;
          const imageResponse = await openai.chat.completions.create({
              model: process.env.AI_MODEL_NAME,
              messages: [{ role: 'user', content: [{ type: "text", text: imageIdentificationPrompt }, { type: "image_url", image_url: { url: image, detail: "low" } }] }],
              response_format: { type: "json_object" }
          });
          identifiedShapeName = JSON.parse(imageResponse.choices[0].message.content).shape;
      }
      shapeName = identifiedShapeName;
    }
    
    const selectedSchema = schemas[targetDimension]?.[shapeName];

    if (!selectedSchema) {
      const errorMessage = `无法确定零件类型或不支持。识别为: "${shapeName}"，目标维度: "${targetDimension.toUpperCase()}"。`;
      console.error(errorMessage);
      return res.status(400).json({ message: '无法处理您的请求', details: errorMessage });
    }
    console.log(`✅ 形状确定为 -> ${shapeName}, 将使用 ${targetDimension.toUpperCase()} Schema。`);

    const cleanTemplate = generateCleanJsonTemplate(selectedSchema);
    
    const extractionPrompt = `
      You are a hyper-rigorous data extraction robot. Your output MUST be a single, valid JSON object that strictly conforms to the provided JSON_SCHEMA.
      **CRITICAL GOAL**: Populate the "JSON_TO_FILL" template for a **${targetDimension.toUpperCase()} ${shapeName}**.
      - If an image is provided, extract data from it.
      - If only text is provided (in the initial user hint), extract parameters from the text.
      **==================== 最高指令: 零推断原则 (ZERO INFERENCE POLICY) ====================**
      You are **ABSOLUTELY FORBIDDEN** from guessing, inferring, or calculating any information not explicitly present in the provided content (image or text).
      **======================================================================================**
      **MANDATORY NOTE-TAKING (REQUIRED)**: You **MUST ALWAYS** fill the \`ai_analysis_notes\` field.
      --- JSON_SCHEMA (Your Rulebook) ---
      ${JSON.stringify(selectedSchema, null, 2)}
      --- JSON_TO_FILL (Your Answer Sheet, using the user's initial hint: "${initial_hint || 'No hint provided'}") ---
      ${JSON.stringify(cleanTemplate, null, 2)}
    `;

    const messages = [{
      role: 'user',
      content: [{ type: "text", text: extractionPrompt }]
    }];

    if (image) {
      messages[0].content.push({ type: "image_url", image_url: { url: image, detail: "high" } });
    }

    // --- 【【【核心修复点：将迭代逻辑放回正确位置】】】 ---
    if (is_iteration) {
      const processedPrevious = preProcessIterationData(JSON.parse(JSON.stringify(previous_analysis)));
      const iterationContext = `
        --- ITERATION CONTEXT: SMART UPDATE ---
        This is a **SMART UPDATE** task. Your goal is to **COMPLETE** the "Current JSON Data" by filling in the \`null\` values, based on the user's hints and the image.

        **RULES:**
        1.  **PRESERVE USER EDITS:** You **MUST** keep all non-null values from the "Current JSON Data". They are user-provided truths.
        2.  **FILL THE BLANKS:** Only find values for fields that are currently \`null\`.
        3.  **ZERO INFERENCE:** You must strictly follow the ZERO INFERENCE POLICY from the initial prompt. If a value isn't on the drawing, leave it as \`null\`.

        **Current JSON Data (with user's edits):**
        ${JSON.stringify(processedPrevious, null, 2)}

        **User's Textual Hints (if any):**
        ${user_text_prompt || "No specific text hints provided."}
      `;
      messages[0].content.push({ type: 'text', text: iterationContext });

      // 迭代时也可能附带补充图片
      if (iteration_image) {
        messages[0].content.push({ type: 'text', text: '--- SUPPLEMENTARY IMAGE ---' });
        messages[0].content.push({ type: 'image_url', image_url: { url: iteration_image, detail: "high" } });
      }
    }
    
    // --- 后续的AI调用和响应处理逻辑 (无变化) ---
    const extractionResponse = await openai.chat.completions.create({
      model: process.env.AI_MODEL_NAME,
      messages: messages,
      response_format: { type: "json_object" },
      max_tokens: 4096,
    });
    
    let aiResponseJson = JSON.parse(extractionResponse.choices[0].message.content);

    const notes = aiResponseJson.ai_analysis_notes || 'AI did not provide any analysis notes.';
    delete aiResponseJson.ai_analysis_notes;

    const finalData = postProcessJson(aiResponseJson); 

    console.log('✅ 数据提取成功! 将分离的数据和笔记发往前端。');

    res.status(200).json({
        notes: notes,
        data: finalData 
    });

  } catch (error) {
    console.error('API请求出错:', error);
    const errorMessage = error.response ? JSON.stringify(error.response.data) : error.message;
    res.status(500).json({ message: '分析图像时服务器内部出错', details: errorMessage });
  }
});

import http from 'http'; // 在文件顶部确保引入 http 模块

const server = http.createServer(app);

// 设置服务器超时时间为 5 分钟 (300,000 毫秒)
// 给予AI模型充分的思考和生成时间，避免服务器端主动断开
const SERVER_TIMEOUT = 300 * 1000;
server.setTimeout(SERVER_TIMEOUT);

server.listen(port, () => {
  console.log(`✅ 后端服务器已启动，正在监听 http://localhost:${port}`);
  console.log(`⏰ 服务器超时设置为: ${SERVER_TIMEOUT / 1000} 秒`);
  console.log(`🚀 使用模型: ${process.env.AI_MODEL_NAME}`);
});