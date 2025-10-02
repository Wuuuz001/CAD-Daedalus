# CAD-Daedalus
A neuro-symbolic framework for reliable, standardized engineering design using LLMs.
CAD-Daedalus: AI-Powered Engineering Parameter Extractor
CAD-Daedalus is a neuro-symbolic framework designed to bridge the gap between visual engineering drawings and structured, machine-readable data. This web application serves as the interactive frontend and intelligent backend for the framework, allowing users to extract key parameters from images of technical drawings, iteratively refine the results with AI assistance, and generate standardized, verifiable JSON for downstream CAD/CAM processes.

This project reframes the role of Large Language Models (LLMs) from unreliable end-to-end generators to interactive proposal engines within a deterministic and verifiable system.

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

You now have a standardized, machine-readable JSON file ready for use in other CAD software or manufacturing pipelines. To start over with a new part, simply click the "New Part" button.
