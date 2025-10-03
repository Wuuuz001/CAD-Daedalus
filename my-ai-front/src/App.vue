<script setup>
import { ref, reactive, computed } from 'vue';
import JsonEditor from './components/JsonEditor.vue';
import JsonValidator from './components/JsonValidator.vue';

const initialImageBase64 = ref('');
const iterationImageBase64 = ref('');
const userTextPrompt = ref('');
const analysisResult = ref(null);
const isLoading = ref(false);
const errorMessage = ref('');
const activeTab = ref('analyzer');
const initialUserHint = ref('');
const aiNotes = ref('');
const outputDimension = ref('2d');
const newShapeDescription = ref('');
const newShapeImageBase64 = ref('');
const isGeneratingFunction = ref(false);
const generatedPythonCode = ref('');
const pythonGenerationError = ref('');

const handleNewShapeImageChange = async (e) => {
  const file = e.target.files[0];
  if (!file) {
    newShapeImageBase64.value = '';
    return;
  }
  newShapeImageBase64.value = await fileToBase64(file);
};

const handleGenerateFunction = async () => {
  if (!newShapeDescription.value && !newShapeImageBase64.value) {
    alert('Please provide a text description or upload an image for the new shape.');
    return;
  }

  isGeneratingFunction.value = true;
  pythonGenerationError.value = '';
  generatedPythonCode.value = '# AI is thinking, please wait...';

  try {
    const response = await fetch('/api/generate_function', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        description: newShapeDescription.value,
        imageBase64: newShapeImageBase64.value,
      }),
    });

    if (!response.ok) {
      const errData = await response.json();
      throw new Error(errData.details || errData.message || 'Failed to generate function');
    }

    const result = await response.json();
    generatedPythonCode.value = result.python_code;

  } catch (error) {
    pythonGenerationError.value = error.message;
    generatedPythonCode.value = `# An error occurred:\n# ${error.message}`;
  } finally {
    isGeneratingFunction.value = false;
  }
};

const copyPythonCode = async () => {
  if (!generatedPythonCode.value) return;
  try {
    await navigator.clipboard.writeText(generatedPythonCode.value);
    alert('Python code copied to clipboard!');
  } catch (err) {
    alert('Failed to copy code.');
  }
};

function hasNullOrEmpty(data) {
  if (data === null || data === '') return true;
  if (Array.isArray(data)) {
    for (const item of data) {
      if (hasNullOrEmpty(item)) return true;
    }
  } else if (typeof data === 'object' && data !== null) {
    for (const key in data) {
      if (hasNullOrEmpty(data[key])) return true;
    }
  }
  return false;
}

const formattedJson = computed(() => {
  if (analysisResult.value) {
    return JSON.stringify(analysisResult.value, null, 2);
  }
  return 'No JSON data has been generated yet...';
});

const isFormIncomplete = computed(() => {
  if (!analysisResult.value) return true;
  return hasNullOrEmpty(analysisResult.value);
});

const resetForNewAnalysis = () => {
  console.log("🔄 Resetting analysis state for a new analysis!");
  analysisResult.value = null;
  errorMessage.value = '';
  aiNotes.value = '';
  userTextPrompt.value = '';
  iterationImageBase64.value = '';
  initialImageBase64.value = '';
  const mainFileInput = document.getElementById('file-upload');
  if (mainFileInput) mainFileInput.value = '';
  const iterationFileInput = document.getElementById('iteration-file-upload');
  if (iterationFileInput) iterationFileInput.value = '';
};

const fileToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = (error) => reject(error);
  });
};

const handleInitialImageChange = async (e) => {
  const file = e.target.files[0];
  if (!file) {
    resetForNewAnalysis();
    return;
  }
  resetForNewAnalysis();
  initialImageBase64.value = await fileToBase64(file);
};

const handleIterationImageChange = async (e) => {
  const file = e.target.files[0];
  if (!file) {
    iterationImageBase64.value = '';
    return;
  }
  iterationImageBase64.value = await fileToBase64(file);
};

const handleAnalysis = async (isIteration = false) => {
  if (!isIteration && !initialImageBase64.value && !initialUserHint.value) {
    alert('Please select a main image file or enter a text hint.');
    return;
  }
  if (isIteration && !analysisResult.value) {
    alert('Please perform the initial analysis first.');
    return;
  }

  isLoading.value = true;
  errorMessage.value = '';

  const payload = {
    image: initialImageBase64.value,
    dimension: outputDimension.value,
    initial_hint: isIteration ? '' : initialUserHint.value,
    is_iteration: isIteration,
    previous_analysis: isIteration ? JSON.parse(JSON.stringify(analysisResult.value)) : null,
    user_text_prompt: isIteration ? userTextPrompt.value : '',
    iteration_image: isIteration ? iterationImageBase64.value : '',
  };

  try {
    const response = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      const errData = await response.json();
      throw new Error(errData.details || errData.message || 'Analysis failed');
    }
    const responsePayload = await response.json();
    
    aiNotes.value = responsePayload.notes;
    analysisResult.value = reactive(responsePayload.data);
    if (!isIteration) {
      initialUserHint.value = '';
    }
    activeTab.value = 'analyzer';

    if (isIteration) {
      userTextPrompt.value = '';
      iterationImageBase64.value = '';
      const iterationFileInput = document.getElementById('iteration-file-upload');
      if (iterationFileInput) iterationFileInput.value = '';
    }
  } catch (error) {
    errorMessage.value = error.message;
  } finally {
    isLoading.value = false;
  }
};

const copyJsonToClipboard = async () => {
  if (isFormIncomplete.value) {
    alert('The form has incomplete items (marked with a red border). Please complete all fields before copying!');
    activeTab.value = 'analyzer';
    return;
  }
  if (!analysisResult.value) { alert('There is nothing to copy.'); return; }
  try {
    await navigator.clipboard.writeText(formattedJson.value);
    alert('JSON code copied to clipboard successfully!');
  } catch (err) {
    alert('Copy failed. Please copy manually.');
  }
};

const switchToJsonTab = () => {
  if (isFormIncomplete.value) {
    alert('The form has incomplete items (marked with a red border). Please complete all fields before viewing the final JSON!');
    return;
  }
  activeTab.value = 'json_code';
};
</script>

<template>
  <div id="app-container">
    <header class="app-header">
      <div class="logo">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2c5.52 0 10 4.48 10 10s-4.48 10-10 10S2 17.52 2 12 6.48 2 12 2zm-1 14.59L16.59 11 18 12.41 11.01 19.4 6 14.41 7.41 13l3.59 3.59z"/></svg>
        <span>AI Part Analyzer</span>
      </div>
      <p>Extract parameters from drawings and generate standardized JSON.</p>
    </header>
    
    <div class="main-layout">
      
      <div class="main-panel">
        <div class="tabs">
          <button :class="{ active: activeTab === 'analyzer' }" @click="activeTab = 'analyzer'">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path d="M10 3.5a1.5 1.5 0 013 0V4a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-.5a1.5 1.5 0 000 3h.5a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 00-1-1v-.5a1.5 1.5 0 01-3 0v.5a1 1 0 00-1 1H6a1 1 0 01-1-1v-3a1 1 0 011-1h.5a1.5 1.5 0 000-3H6a1 1 0 01-1-1V6a1 1 0 011-1h3a1 1 0 001-1v-.5z"/></svg>
            AI Extraction
          </button>
          <button :class="{ active: activeTab === 'json_code' }" @click="switchToJsonTab">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM6.39 6.39a.75.75 0 011.06 0l2.11 2.11a.75.75 0 010 1.06L7.45 11.61a.75.75 0 01-1.06-1.06l1.59-1.59-1.59-1.59a.75.75 0 010-1.06zM13.61 6.39a.75.75 0 010 1.06l-1.59 1.59 1.59 1.59a.75.75 0 01-1.06 1.06L10.44 9.56a.75.75 0 010-1.06l2.11-2.11a.75.75 0 011.06 0z" clip-rule="evenodd"/></svg>
            JSON Code
          </button>
          <button :class="{ active: activeTab === 'function_generator' }" @click="activeTab = 'function_generator'">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path d="M10.362 3.653a1 1 0 00-1.04-.344L4.36 5.562a1 1 0 00-.86 1.036l.732 4.418-1.54 1.232a1 1 0 00-.28 1.344l4.25 5.5a1 1 0 001.455.155l3.8-2.85a1 1 0 00.223-1.16l-1.334-3.001 3.428-1.904a1 1 0 00.556-1.328l-2.438-4.25a1 1 0 00-1.18-.543z" /></svg>
              Add New Shape
          </button>
        </div>
        
        <main class="content-wrapper">
          <div v-if="activeTab === 'analyzer'" class="tab-content">
            <div class="controls-panel card">
              <label for="file-upload" class="custom-file-upload">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path d="M9.25 13.25a.75.75 0 001.5 0V4.636l2.955 3.129a.75.75 0 001.09-1.03l-4.25-4.5a.75.75 0 00-1.09 0l-4.25 4.5a.75.75 0 101.09 1.03L9.25 4.636v8.614z"/><path d="M3.5 12.75a.75.75 0 00-1.5 0v2.5A2.75 2.75 0 004.75 18h10.5A2.75 2.75 0 0018 15.25v-2.5a.75.75 0 00-1.5 0v2.5c0 .69-.56 1.25-1.25 1.25H4.75c-.69 0-1.25-.56-1.25-1.25v-2.5z"/></svg>
                {{ initialImageBase64 ? 'Change Main Image' : 'Select Main Image' }}
              </label>
              <input id="file-upload" type="file" @change="handleInitialImageChange" accept="image/*" />
              <input 
                  type="text" 
                  v-model="initialUserHint" 
                  placeholder="Optional hint, e.g., 'hexagonal_screw'" 
                  class="hint-input"
                  :disabled="isLoading"
              />
              <button 
                @click="handleAnalysis(false)" 
                :disabled="isLoading || (!initialImageBase64 && !initialUserHint)" 
                class="primary-btn"
              >
                <span v-if="isLoading">Analyzing...</span>
                <span v-else>Initial Analysis</span>
              </button>
              <div class="dimension-switcher">
                <button :class="{ active: outputDimension === '2d' }" @click="outputDimension = '2d'" :disabled="isLoading">2D</button>
                <button :class="{ active: outputDimension === '3d' }" @click="outputDimension = '3d'" :disabled="isLoading">3D</button>
              </div>
              <button 
                v-if="analysisResult" 
                @click="resetForNewAnalysis" 
                class="iteration-btn" 
                style="background-color: #ef4444; margin-left: auto;"
                title="Clear all current analysis data and start a new part."
              >
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M15.312 5.312a.75.75 0 010 1.06L11.06 10.622l4.252 4.252a.75.75 0 11-1.06 1.06L10 11.682l-4.252 4.252a.75.75 0 01-1.06-1.06L8.94 10.622 4.688 6.37a.75.75 0 011.06-1.06L10 8.939l4.252-4.252a.75.75 0 011.06 0z" clip-rule="evenodd" /></svg>
                New Part
              </button>
            </div>
      
            <div v-if="isLoading" class="feedback-panel loading-indicator">
              <div class="spinner"></div>
              <p>Requesting AI analysis, please wait...</p>
            </div>
      
            <div v-if="errorMessage" class="feedback-panel error-message">
              <p><strong>Error:</strong> {{ errorMessage }}</p>
            </div>
      
            <div v-if="analysisResult" class="results-panel card">
              <h2>Analysis Result (Editable)</h2>
              <p v-if="isFormIncomplete" class="incomplete-form-notice">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-5a.75.75 0 01.75.75v4.5a.75.75 0 01-1.5 0v-4.5A.75.75 0 0110 5zm0 10a1 1 0 100-2 1 1 0 000 2z" clip-rule="evenodd" /></svg>
                Please fill in all required fields marked in red.
              </p>
              <div v-if="aiNotes" class="ai-notes-panel">
                <div class="notes-header">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path d="M10 2a6 6 0 00-6 6c0 1.887.832 3.535 2.089 4.654.17.159.322.33.45.512.13.188.242.384.333.587.093.204.16.416.205.633.045.217.068.438.068.662a.75.75 0 001.5 0A2.5 2.5 0 0113 13.25a.75.75 0 000-1.5 1 1 0 10-1.962-.392 3.483 3.483 0 00-.342-.682 6.423 6.423 0 00-.455-.632l-.007-.008-.006-.007a5.034 5.034 0 00-2.22-1.956A4.5 4.5 0 0110 3.5a.75.75 0 000-1.5z" /><path d="M15.5 10.5a.75.75 0 01.75.75v2.5a.75.75 0 01-1.5 0v-2.5a.75.75 0 01.75-.75z" /><path d="M17.5 7.5a.75.75 0 01.75.75v6a.75.75 0 01-1.5 0v-6a.75.75 0 01.75-.75z" /><path d="M2.5 7.5a.75.75 0 01.75.75v6a.75.75 0 01-1.5 0v-6a.75.75 0 01.75-.75z" /><path d="M4.5 10.5a.75.75 0 01.75.75v2.5a.75.75 0 01-1.5 0v-2.5a.75.75 0 01.75-.75z" /></svg>
                  <span>AI Analysis Summary</span>
                </div>
                <p class="notes-content">{{ aiNotes }}</p>
              </div>
              <div class="form-container">
                <JsonEditor :data="analysisResult" />
              </div>
              <div class="iteration-zone">
                <h3>Iteration & Refinement</h3>
                <p class="iteration-desc">Provide extra text hints or upload a supplementary image (e.g., a close-up detail), then click 'Submit & Re-analyze'.</p>
                <textarea v-model="userTextPrompt" placeholder="Enter text prompt..." class="iteration-textarea"></textarea>
                <div class="iteration-upload">
                  <label for="iteration-file-upload" class="custom-file-upload small">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path d="M10.75 4.75a.75.75 0 00-1.5 0v4.5h-4.5a.75.75 0 000 1.5h4.5v4.5a.75.75 0 001.5 0v-4.5h4.5a.75.75 0 000-1.5h-4.5v-4.5z" /></svg>
                    Upload Supplementary Image (Optional)
                  </label>
                  <input id="iteration-file-upload" type="file" @change="handleIterationImageChange" accept="image/*" />
                  <span v-if="iterationImageBase64" class="file-selected-badge">Selected</span>
                </div>
              </div>
              <div class="actions-panel">
                <button @click="handleAnalysis(true)" :disabled="isLoading" class="iteration-btn">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M15.312 11.424a5.5 5.5 0 01-9.201-4.42 5.5 5.5 0 017.48-7.023 5.5 5.5 0 013.824 9.388l2.58 2.58a.75.75 0 11-1.06 1.06l-2.58-2.58zM10 14a4 4 0 100-8 4 4 0 000 8z" clip-rule="evenodd" /></svg>
                  Submit & Re-analyze
                </button>
                <button @click="switchToJsonTab" class="confirm-btn">
                  View Final JSON
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M3 10a.75.75 0 01.75-.75h10.638L10.23 5.29a.75.75 0 111.04-1.08l5.5 5.25a.75.75 0 010 1.08l-5.5 5.25a.75.75 0 11-1.04-1.08l4.158-3.96H3.75A.75.75 0 013 10z" clip-rule="evenodd" /></svg>
                </button>
              </div>
            </div>
          </div>
          
          <div v-if="activeTab === 'json_code'" class="tab-content">
            <div class="json-code-wrapper card">
              <h2>Final JSON Code</h2>
              <p>This is the final JSON code generated based on the data you confirmed or modified in the form.</p>
              <div class="json-code-container">
                <pre><code>{{ formattedJson }}</code></pre>
              </div>
              <button @click="copyJsonToClipboard" class="primary-btn">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path d="M7 3.5A1.5 1.5 0 018.5 2h3.879a1.5 1.5 0 011.06.44l3.122 3.12A1.5 1.5 0 0117 6.622V16.5a1.5 1.5 0 01-1.5 1.5h-8A1.5 1.5 0 016 16.5v-13A1.5 1.5 0 017 3.5zM8.5 3.5a.5.5 0 00-.5.5v13a.5.5 0 00.5.5h8a.5.5 0 00.5-.5V6.622a.5.5 0 00-.146-.353l-3.122-3.122A.5.5 0 0012.379 3H8.5z"/><path d="M3 6.5A1.5 1.5 0 014.5 5h3a.75.75 0 000-1.5h-3A2.5 2.5 0 002 6v11A2.5 2.5 0 004.5 19.5h8A2.5 2.5 0 0015 17v-3a.75.75 0 00-1.5 0v3a1 1 0 01-1 1h-8a1 1 0 01-1-1V6z"/></svg>
                Copy JSON
              </button>
            </div>
          </div>

          <div v-if="activeTab === 'function_generator'" class="tab-content">
            <div class="card">
              <h2>Generate New Python Drawing Function</h2>
              <p style="margin-bottom: 1.5rem;">Describe a new part with text or an image. The AI will write the Python function for you, which you can then add to your Python generator script.</p>
              
              <div class="function-generator-form">
                <textarea 
                  v-model="newShapeDescription" 
                  placeholder="Describe the new shape here. E.g., 'A T-slot nut with overall dimensions 20x20x10mm. The T-slot is 8mm wide and 5mm deep...'"
                  class="iteration-textarea"
                  rows="5"
                ></textarea>

                <div class="iteration-upload" style="margin-top: 1rem;">
                  <label for="shape-image-upload" class="custom-file-upload">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path d="M9.25 13.25a.75.75 0 001.5 0V4.636l2.955 3.129a.75.75 0 001.09-1.03l-4.25-4.5a.75.75 0 00-1.09 0l-4.25 4.5a.75.75 0 101.09 1.03L9.25 4.636v8.614z"/><path d="M3.5 12.75a.75.75 0 00-1.5 0v2.5A2.75 2.75 0 004.75 18h10.5A2.75 2.75 0 0018 15.25v-2.5a.75.75 0 00-1.5 0v2.5c0 .69-.56 1.25-1.25 1.25H4.75c-.69 0-1.25-.56-1.25-1.25v-2.5z"/></svg>
                    Upload Sketch (Optional)
                  </label>
                  <input id="shape-image-upload" type="file" @change="handleNewShapeImageChange" accept="image/*" />
                  <span v-if="newShapeImageBase64" class="file-selected-badge">Image Selected</span>
                </div>

                <button @click="handleGenerateFunction" :disabled="isGeneratingFunction" class="primary-btn" style="margin-top: 1.5rem;">
                  <div v-if="isGeneratingFunction" class="spinner-small"></div>
                  {{ isGeneratingFunction ? 'Generating Code...' : 'Generate Python Function' }}
                </button>
              </div>
            </div>

            <div v-if="generatedPythonCode || isGeneratingFunction" class="card" style="margin-top: 2rem;">
              <h2>Generated Python Code:</h2>
              <p>Copy this code and paste it into your Python script.</p>
              <div class="json-code-container" style="max-height: 600px;">
                <pre><code class="language-python">{{ generatedPythonCode }}</code></pre>
              </div>
              <button @click="copyPythonCode" class="primary-btn" style="margin-top: 1rem;">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path d="M7 3.5A1.5 1.5 0 018.5 2h3.879a1.5 1.5 0 011.06.44l3.122 3.12A1.5 1.5 0 0117 6.622V16.5a1.5 1.5 0 01-1.5 1.5h-8A1.5 1.5 0 016 16.5v-13A1.5 1.5 0 017 3.5zM8.5 3.5a.5.5 0 00-.5.5v13a.5.5 0 00.5.5h8a.5.5 0 00.5-.5V6.622a.5.5 0 00-.146-.353l-3.122-3.122A.5.5 0 0012.379 3H8.5z"/><path d="M3 6.5A1.5 1.5 0 014.5 5h3a.75.75 0 000-1.5h-3A2.5 2.5 0 002 6v11A2.5 2.5 0 004.5 19.5h8A2.5 2.5 0 0015 17v-3a.75.75 0 00-1.5 0v3a1 1 0 01-1 1h-8a1 1 0 01-1-1V6z"/></svg>
                Copy Python Code
              </button>
              <div v-if="pythonGenerationError" class="error-message" style="margin-top: 1rem; text-align: left;">
                <p><strong>Error:</strong> {{ pythonGenerationError }}</p>
              </div>
            </div>
          </div>
        </main>
      </div>

      <div v-if="analysisResult" class="side-panel">
        <JsonValidator :jsonData="analysisResult" />
      </div>

    </div>
  </div>
</template>

<style>
:root {
  --primary-color: #4f46e5;
  --primary-color-hover: #4338ca;
  --secondary-color: #10b981;
  --secondary-color-hover: #059669;
  --warning-bg-color: #fffbeb;
  --warning-text-color: #b45309;
  --warning-border-color: #fcd34d;
  --iteration-color: #f97316;
  --iteration-color-hover: #ea580c;
  --text-color: #374151;
  --text-light-color: #6b7280;
  --bg-color: #f9fafb;
  --card-bg-color: #ffffff;
  --border-color: #e5e7eb;
  --font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  --border-radius: 0.75rem;
  --box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
}

body {
  font-family: var(--font-family);
  background-color: var(--bg-color);
  color: var(--text-color);
  margin: 0;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app-container {
  max-width: 1200px;
  margin: 2rem auto;
  padding: 1rem 2rem 2rem 2rem;
}

.card {
  background-color: var(--card-bg-color);
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  padding: 1.5rem;
  border: 1px solid var(--border-color);
}

.app-header {
  text-align: center;
  margin-bottom: 2rem;
}
.app-header .logo {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--primary-color);
}
.app-header .logo svg {
  width: 32px;
  height: 32px;
}
.app-header p {
  font-size: 1rem;
  color: var(--text-light-color);
  margin-top: 0.5rem;
}

.main-layout {
  display: flex;
  gap: 2rem;
  align-items: flex-start;
}
.main-panel {
  flex: 2;
  min-width: 0;
}
.side-panel {
  flex: 1;
  position: sticky;
  top: 2rem;
  animation: fadeInRight 0.5s ease-out;
}
@keyframes fadeInRight {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.tabs {
  display: flex;
  border-bottom: 2px solid var(--border-color);
  margin-bottom: 2rem;
}
.tabs button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  border: none;
  background-color: transparent;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  color: var(--text-light-color);
  border-bottom: 3px solid transparent;
  margin-bottom: -2px;
  transition: all 0.2s ease-in-out;
}
.tabs button svg {
  width: 20px;
  height: 20px;
}
.tabs button.active {
  color: var(--primary-color);
  border-bottom-color: var(--primary-color);
  font-weight: 600;
}
.tabs button:hover:not(.active) {
  background-color: #f3f4f6;
  color: var(--text-color);
}

.content-wrapper {
  animation: fadeIn 0.5s ease-in-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

button {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  border: 1px solid transparent;
  border-radius: 0.5rem;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}
button.primary-btn, .controls-panel .primary-btn {
  background-color: var(--primary-color);
  color: white;
}
button.primary-btn:hover {
  background-color: var(--primary-color-hover);
}
button.confirm-btn {
  background-color: var(--secondary-color);
  color: white;
}
button.confirm-btn:hover {
  background-color: var(--secondary-color-hover);
}
button.iteration-btn {
  background-color: var(--iteration-color);
  color: white;
}
button.iteration-btn:hover {
  background-color: var(--iteration-color-hover);
}
button:disabled {
  background-color: #d1d5db;
  color: #9ca3af;
  cursor: not-allowed;
}

input[type="file"] {
  display: none;
}
.custom-file-upload {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  cursor: pointer;
  background-color: var(--card-bg-color);
  transition: all 0.2s ease;
}
.custom-file-upload:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}
.custom-file-upload svg {
  width: 20px;
  height: 20px;
}

.controls-panel {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-bottom: 2rem;
}
.actions-panel {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-color);
}
.results-panel {
}
.form-container {
  padding-top: 1rem;
}

.feedback-panel {
  text-align: center;
  padding: 2rem;
  margin-top: 2rem;
  border-radius: var(--border-radius);
  border: 1px solid transparent;
}
.loading-indicator {
  color: var(--primary-color);
  background-color: #eef2ff;
  border-color: #c7d2fe;
}
.error-message {
  background-color: #fee2e2;
  color: #b91c1c;
  border-color: #fca5a5;
}
.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(79, 70, 229, 0.2);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

.incomplete-form-notice {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background-color: var(--warning-bg-color);
  color: var(--warning-text-color);
  border: 1px solid var(--warning-border-color);
  border-radius: 0.5rem;
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
}
.incomplete-form-notice svg {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.iteration-zone {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px dashed var(--border-color);
}
.iteration-zone h3 {
  margin-top: 0;
  font-size: 1.25rem;
  color: var(--primary-color);
}
.iteration-desc {
  font-size: 0.9rem;
  color: var(--text-light-color);
  margin-bottom: 1rem;
}
.iteration-textarea {
  width: 100%;
  min-height: 80px;
  padding: 0.75rem;
  border-radius: 0.5rem;
  border: 1px solid var(--border-color);
  font-family: var(--font-family);
  font-size: 0.9rem;
  resize: vertical;
  box-sizing: border-box;
  margin-bottom: 1rem;
}
.iteration-upload {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.custom-file-upload.small {
  padding: 0.5rem 1rem;
  font-size: 0.85rem;
  background-color: #f3f4f6;
}
.custom-file-upload.small:hover {
  background-color: #e5e7eb;
  border-color: #d1d5db;
  color: var(--text-color);
}
.file-selected-badge {
  background-color: var(--secondary-color);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.8rem;
  font-weight: 500;
}

.json-code-wrapper {
  display: flex;
  flex-direction: column;
}
.json-code-container {
  background-color: #1f2937;
  color: #d1d5db;
  padding: 1.5rem;
  border-radius: 0.5rem;
  margin: 1.5rem 0;
  max-height: 500px;
  overflow: auto;
  font-family: 'Fira Code', 'Courier New', monospace;
  border: 1px solid #374151;
}
.json-code-wrapper button {
  align-self: flex-start;
}

.ai-notes-panel {
  background-color: #f3f4f6;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1rem 1.25rem;
  margin-bottom: 1.5rem;
}
.notes-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 0.75rem;
}
.notes-header svg {
  width: 20px;
  height: 20px;
  color: var(--primary-color);
}
.notes-content {
  font-size: 0.9rem;
  color: var(--text-light-color);
  margin: 0;
  line-height: 1.6;
  white-space: pre-wrap;
}

.hint-input {
  flex-grow: 1; 
  padding: 0.625rem 0.75rem;
  border: 1px solid var(--border-color, #d1d5db);
  border-radius: 0.5rem;
  font-size: 0.9rem;
}
.hint-input:focus {
  outline: none;
  border-color: var(--primary-color, #4f46e5);
  box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.2);
}
.hint-input:disabled {
  background-color: #f3f4f6;
  cursor: not-allowed;
}

.dimension-switcher {
  display: flex;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  overflow: hidden;
  margin-left: 1rem;
}

.dimension-switcher button {
  padding: 0.625rem 1.25rem;
  border: none;
  background-color: transparent;
  color: var(--text-light-color);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border-radius: 0;
}

.dimension-switcher button:not(:last-child) {
  border-right: 1px solid var(--border-color);
}

.dimension-switcher button.active {
  background-color: var(--primary-color);
  color: white;
  font-weight: 600;
}

.dimension-switcher button:disabled {
  background-color: #e5e7eb;
  color: #9ca3af;
  cursor: not-allowed;
}

.dimension-switcher button:disabled.active {
    background-color: #9ca3af;
    color: #e5e7eb;
}

</style>
