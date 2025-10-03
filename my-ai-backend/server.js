import express from 'express';
import { OpenAI } from 'openai';
import cors from 'cors';
import dotenv from 'dotenv';
import http from 'http';

import { cylinder2dSchema } from './schemas/cylinder_2d_schema.js';
import { cylinder3dSchema } from './schemas/cylinder_3d_schema.js';
import { cuboid2dSchema } from './schemas/cuboid_2d_schema.js';
import { cuboid3dSchema } from './schemas/cuboid_3d_schema.js';
import { hexagonalPrism2dSchema } from './schemas/hexagonal_prism_2d_schema.js';
import { hexagonalPrism3dSchema } from './schemas/hexagonal_prism_3d_schema.js';
import { hexagonalNut2dSchema } from './schemas/hexagonal_nut_2d_schema.js';
import { hexagonalNut3dSchema } from './schemas/hexagonal_nut_3d_schema.js';
import { hexagonalScrew2dSchema } from './schemas/hexagonal_screw_2d_schema.js';
import { hexagonalScrew3dSchema } from './schemas/hexagonal_screw_3d_schema.js';
import { cuboidCylinderAssembly2dSchema } from './schemas/assembly_cuboid_cylinder_2d_schema.js';
import { cuboidCylinderAssembly3dSchema } from './schemas/assembly_cuboid_cylinder_3d_schema.js';
import { screwNutAssembly2dSchema } from './schemas/assembly_screw_nut_2d_schema.js';
import { screwNutAssembly3dSchema } from './schemas/assembly_screw_nut_3d_schema.js';
import { masterPromptTemplate } from './prompt_template.js';

dotenv.config();
const app = express();
const port = process.env.PORT || 3001;
const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
    baseURL: process.env.OPENAI_API_BASE_URL,
});
app.use(cors());
app.use(express.json({ limit: '10mb' }));

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
        cuboid: cuboid3dSchema,
        hexagonal_prism: hexagonalPrism3dSchema,
        hexagonal_screw: hexagonalScrew3dSchema,
        hexagonal_nut: hexagonalNut3dSchema,
        cuboid_cylinder_assembly: cuboidCylinderAssembly3dSchema,
        screw_nut_assembly: screwNutAssembly3dSchema,
    }
};

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

app.post('/api/generate_function', async (req, res) => {
    console.log('🤖 Received request to generate a new Python function...');
    const { description, imageBase64 } = req.body;

    if (!description && !imageBase64) {
        return res.status(400).json({ message: 'Request is empty. Please provide a text description or an image.' });
    }

    try {
        const finalPrompt = masterPromptTemplate.replace('{{USER_SHAPE_DESCRIPTION}}', description || 'Analyze the provided image.');
        const messages = [{
            role: 'user',
            content: [{ type: "text", text: finalPrompt }]
        }];

        if (imageBase64) {
            messages[0].content.push({
                type: "image_url",
                image_url: { url: imageBase64, detail: "high" }
            });
        }

        console.log('Sending massive prompt to AI for code generation...');
        const response = await openai.chat.completions.create({
            model: process.env.AI_MODEL_NAME,
            messages: messages,
            temperature: 0.2,
            max_tokens: 16384,
        });

        let generatedCode = response.choices[0].message.content;
        const codeBlockMatch = generatedCode.match(/```python\n([\s\S]*?)\n```/);
        if (codeBlockMatch && codeBlockMatch[1]) {
            generatedCode = codeBlockMatch[1];
        }

        console.log('✅ Successfully generated Python code snippet.');
        res.status(200).json({ python_code: generatedCode });

    } catch (error) {
        console.error('Error during Python function generation:', error);
        res.status(500).json({ message: 'Failed to generate Python function.', details: error.message });
    }
});

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
            return res.status(400).json({ message: 'Request invalid; initial analysis requires either an image or text prompt.' });
        }

        let shapeName;

        if (is_iteration && previous_analysis && previous_analysis.shape) {
            shapeName = previous_analysis.shape;
            console.log(`🔄 Starting iterative analysis for shape: ${shapeName}, Target dimension: ${targetDimension.toUpperCase()}`);
        } else {
            console.log(`🧐 Starting initial analysis..., Target dimension: ${targetDimension.toUpperCase()}`);
            let identifiedShapeName = 'unknown';
            if (initial_hint) {
                console.log(`📝 Parsing shape from text hint: "${initial_hint}"...`);
                const shapeIdentificationPrompt = `From the user's text hint, identify the geometric shape name. The name must be one of: "cylinder", "cuboid", "hexagonal_prism", "hexagonal_nut", "hexagonal_screw", "cuboid_cylinder_assembly", "screw_nut_assembly". Your response MUST be a single JSON object: {"shape": "shape_name"}. User's Text Hint: "${initial_hint}"`;
                const shapeResponse = await openai.chat.completions.create({
                    model: process.env.AI_MODEL_NAME,
                    messages: [{ role: 'user', content: shapeIdentificationPrompt }],
                    response_format: { type: "json_object" }
                });
                identifiedShapeName = JSON.parse(shapeResponse.choices[0].message.content).shape;
            }
            if (identifiedShapeName === 'unknown' && image) {
                console.log('🖼️ Could not determine shape from text hint, using image for AI recognition...');
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
            const errorMessage = `Could not determine or unsupported part type. Identified as: "${shapeName}", Target dimension: "${targetDimension.toUpperCase()}".`;
            console.error(errorMessage);
            return res.status(400).json({ message: 'Could not process your request', details: errorMessage });
        }
        console.log(`✅ Shape confirmed -> ${shapeName}, will use ${targetDimension.toUpperCase()} Schema.`);

        const cleanTemplate = generateCleanJsonTemplate(selectedSchema);

        const extractionPrompt = `
          You are a hyper-rigorous data extraction robot. Your output MUST be a single, valid JSON object that strictly conforms to the provided JSON_SCHEMA.
          **CRITICAL GOAL**: Populate the "JSON_TO_FILL" template for a **${targetDimension.toUpperCase()} ${shapeName}**.
          - If an image is provided, extract data from it.
          - If only text is provided (in the initial user hint), extract parameters from the text.
          **==================== HIGHEST DIRECTIVE: ZERO INFERENCE POLICY ====================**
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
            if (iteration_image) {
                messages[0].content.push({ type: 'text', text: '--- SUPPLEMENTARY IMAGE ---' });
                messages[0].content.push({ type: 'image_url', image_url: { url: iteration_image, detail: "high" } });
            }
        }

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

        console.log('✅ Data extraction successful! Sending separated data and notes to the frontend.');

        res.status(200).json({
            notes: notes,
            data: finalData
        });

    } catch (error) {
        console.error('API request error:', error);
        const errorMessage = error.response ? JSON.stringify(error.response.data) : error.message;
        res.status(500).json({ message: 'Internal server error during image analysis', details: errorMessage });
    }
});

const server = http.createServer(app);
const SERVER_TIMEOUT = 300 * 1000;
server.setTimeout(SERVER_TIMEOUT);

server.listen(port, () => {
    console.log(`✅ Backend server started, listening on http://localhost:${port}`);
    console.log(`⏰ Server timeout set to: ${SERVER_TIMEOUT / 1000} seconds`);
    console.log(`🚀 Using model: ${process.env.AI_MODEL_NAME}`);
});
