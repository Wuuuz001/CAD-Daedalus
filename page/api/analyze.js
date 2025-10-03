import { OpenAI } from 'openai';
import { cylinderSchema } from '../../schemas/cylinder_schema'; // Import the schema we just created

// Initialize the OpenAI client, reading the API key from environment variables for security
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export default async function handler(req, res) {
  // Only accept POST requests
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method Not Allowed' });
  }

  try {
    // Get the Base64 encoded image and the previous analysis result (for iteration) from the request body
    const { image, previousAnalysis } = req.body;

    // --- Core Prompt (Instructions for the AI) ---
    // This is the most critical part of the project. We define the AI's role, task, and provide precise formatting requirements.
    let userPrompt = `
      You are a professional AI assistant specializing in interpreting mechanical engineering drawings.
      Your task is to analyze the provided image of a cylinder part and extract all specified parameters.
      Your response must be a single, valid JSON object that strictly adheres to the JSON Schema provided below.
      For any value you cannot determine with high confidence from the image, you must use null. Do not guess or fabricate data.
      Pay special attention to Geometric Dimensioning and Tolerancing (GD&T) symbols, surface roughness symbols, and datums on the drawing.

      The JSON Schema you must adhere to is as follows:
      ${JSON.stringify(cylinderSchema, null, 2)}
    `;

    // If a previous analysis exists (user is iterating), add it to the prompt
    if (previousAnalysis) {
      userPrompt += `
      
      This is an iterative analysis. The user has provided their modified data or the previous analysis result.
      Use this information to refine your analysis, focusing on filling in fields that were previously null or incorrect.
      
      Previous analysis / User's corrections:
      ${JSON.stringify(previousAnalysis, null, 2)}
      `;
    }

    const response = await openai.chat.completions.create({
      model: "gpt-4o", // Use the latest and most powerful model
      messages: [
        {
          role: "user",
          content: [
            { type: "text", text: userPrompt },
            {
              type: "image_url",
              image_url: {
                url: image, // The Base64 image data from the frontend
                detail: "high" // Use high-resolution mode to read small text on the drawing
              },
            },
          ],
        },
      ],
      max_tokens: 2048, // Limit the maximum number of tokens to prevent run-on responses
      response_format: { type: "json_object" }, // Force the AI to output in JSON format, which is crucial!
    });

    // Parse the JSON string returned by the AI
    const aiResponseJson = JSON.parse(response.choices[0].message.content);
    
    // Return the parsed JSON object to the frontend
    res.status(200).json(aiResponseJson);

  } catch (error) {
    console.error('Error calling OpenAI:', error);
    res.status(500).json({ message: 'Error analyzing the image', details: error.message });
  }
}
