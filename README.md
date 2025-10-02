# CAD-Daedalus
A neuro-symbolic framework for reliable, standardized engineering design using LLMs.
CAD-Daedalus: AI-Powered Engineering Parameter Extractor
CAD-Daedalus is a neuro-symbolic framework designed to bridge the gap between visual engineering drawings and structured, machine-readable data. This web application serves as the interactive frontend and intelligent backend for the framework, allowing users to extract key parameters from images, iteratively refine the results with AI assistance, and generate standardized, verifiable JSON for downstream CAD/CAM processes.

This project reframes the role of Large Language Models (LLMs) from unreliable end-to-end generators to interactive proposal engines within a deterministic and verifiable system.

!
(建议在此处替换为您的应用截图)

🚀 How to Use: Generating Standardized JSON
The entire process is designed as a straightforward, step-by-step workflow. Here is how you can generate your first standardized JSON file:

Step 1: Initial Analysis (初次分析)
You have two ways to start a new analysis:

Option A: By Image (图像识别)

Click the "Select Main Image" button.

Upload an image of a technical drawing (e.g., a .png or .jpg file).

The system will automatically identify the part type from the drawing.

Option B: By Text Hint (文本提示)

In the input field, type a keyword for the part you want to create, for example, cylinder or hexagonal_screw.

The system will use this hint to generate a basic data template for that specific part.

Once you have provided an image or a text hint, select the target output dimension (2D or 3D), and click the "Initial Analysis" button.

Step 2: Review and Edit (审查与编辑)
After a few moments, the AI will complete its analysis:

An "AI Analysis Summary" will appear, providing notes on the extraction process.

Below the summary, an editable form will be populated with all the parameters the AI identified.

Carefully review each field. If the AI was uncertain about a value, the input box will be marked in red, indicating that your input is required.

Manually correct any inaccuracies or fill in any missing values directly in the form.

As you make changes, the "JSON Structure & Data Validation" panel on the right side will provide real-time feedback, showing errors (❌), warnings (⚠️), or successes (✅) based on predefined engineering rules.

Step 3: Iterate and Refine (迭代与优化)
If the initial analysis is incomplete or requires correction for a complex part, use the "Iteration & Refinement" section:

Provide a corrective hint in the text area (e.g., "The height of the cylinder should be 120, not 100").

Optionally, upload a supplementary image (e.g., a close-up of a specific dimension or feature).

Click the "Submit & Re-analyze" button.

The AI will re-evaluate the data using your new input, preserving your previous manual edits while attempting to fill in only the remaining empty (null) fields.

Step 4: Finalize and Export (定稿与导出)
Once the form is complete and the Validation panel on the right shows no critical errors:

Click the "View Final JSON" button.

You will be switched to the "JSON Code" tab, which displays the final, structured, and validated JSON output.

Click the "Copy JSON" button to copy the code to your clipboard.

You now have a standardized, machine-readable JSON file ready for use in other CAD software or manufacturing pipelines.

🔬 How It Works: The Neuro-Symbolic Workflow
The application's intelligence comes from a carefully orchestrated workflow that combines the semantic understanding of LLMs with the rigidity of symbolic rules.

User Input (Frontend): The user uploads an image or provides a text hint via the Vue.js interface.

API Request: The frontend sends the data (image as base64, text, etc.) to the /api/analyze endpoint on the Node.js backend.

Shape Identification (Backend): The backend first performs a lightweight AI call to identify the basic shape of the part (e.g., "cylinder", "hexagonal_screw") from the input.

Schema Selection (Backend): Based on the identified shape and the user-selected dimension (2D/3D), the backend dynamically selects a predefined, rigid JSON schema. This schema acts as the "rulebook" for the AI.

Parameter Extraction (Backend): The backend constructs a highly detailed prompt for the LLM. This prompt includes:

The user's image and text.

The selected JSON schema.

An empty template to be filled.

A critical instruction: the ZERO INFERENCE POLICY, which forbids the AI from guessing or inferring any values not explicitly present in the source material.

Response & Post-processing: The AI returns a filled JSON object. The backend performs minor post-processing and sends the clean data and analysis notes back to the frontend.

Display & Validation (Frontend):

The JsonEditor.vue component recursively renders the JSON data into an interactive form.

The JsonValidator.vue component simultaneously receives this data and validates it against a set of hard-coded engineering logic, providing instant feedback.

Iteration Loop: If the user provides refinement hints, the entire process is repeated, but this time the backend instructs the AI to only fill the null values, preserving all previous user edits.

✨ Features
Frontend (Vue.js)
🎨 Dynamic Form Generation: Recursively renders complex JSON objects into user-friendly, editable forms.

👁️ Real-time Validation: An independent validation engine provides immediate feedback on data integrity and compliance with engineering rules.

🔄 Iterative Refinement: A dedicated UI for providing additional text and image hints to guide the AI in a human-in-the-loop process.

🖼️ Multimodal Input: Accepts both images and text as the starting point for analysis.

📋 Clipboard Integration: Easily copy the final, validated JSON with a single click.

Backend (Node.js / Express)
🤖 Multi-Step AI Pipeline: Decouples shape identification from parameter extraction for higher accuracy and efficiency.

📐 Schema-Driven Logic: Dynamically selects from a library of 2D and 3D schemas to ensure structured and predictable outputs.

🧠 Zero Inference Policy: A core prompting strategy that forces the AI to act as a pure data extractor rather than a creative agent, dramatically increasing reliability.

🧩 Smart Iteration: Preserves user-modified data during refinement, using AI only to fill in the missing gaps.

🔐 Secure Configuration: Uses .env files to manage sensitive API keys safely.

📁 Project Structure
/CAD-Daedalus/
├── my-ai-front/
│   ├── src/
│   │   ├── components/
│   │   │   ├── JsonEditor.vue      # Dynamically renders the editable form from JSON.
│   │   │   └── JsonValidator.vue   # Validates the JSON in real-time.
│   │   └── App.vue                 # Main application layout, state management, and API calls.
│   └── package.json
│
├── my-ai-backend/
│   ├── schemas/
│   │   ├── cylinder_2d_schema.js   # Rulebook for a 2D cylinder.
│   │   ├── cylinder_3d_schema.js   # Rulebook for a 3D cylinder.
│   │   └── ... (other schemas)
│   ├── server.js                   # Express server, API endpoint, and core AI logic.
│   ├── .env.example                # Example environment variables.
│   └── package.json
│
└── .gitignore                      # Specifies files for Git to ignore (e.g., node_modules).
🛠️ Setup and Installation
To run this project locally, you will need to set up both the backend and the frontend.

Backend Setup
Navigate to the backend directory:

Bash

cd my-ai-backend
Create an environment file:
Copy the .env.example file to a new file named .env and fill in your API credentials.

# .env
PORT=3001
OPENAI_API_KEY="sk-your-openai-api-key"
OPENAI_API_BASE_URL="https://api.openai.com/v1" # Or your proxy URL
AI_MODEL_NAME="gpt-4-vision-preview" # Or another compatible model
Install dependencies:

Bash

npm install
Start the server:

Bash

node server.js
The backend server should now be running on http://localhost:3001.

Frontend Setup
Open a new terminal and navigate to the frontend directory:

Bash

cd my-ai-front
Install dependencies:

Bash

npm install
Start the development server:

Bash

npm run dev
The frontend application will be available at http://localhost:5173 (or another port specified by Vite). Open this address in your browser to use the application.

📄 License
This project is licensed under the MIT License. See the LICENSE file for details.
