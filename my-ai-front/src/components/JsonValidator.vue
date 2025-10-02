<script setup>
import { ref, watch, computed } from 'vue';

// --- Props ---
const props = defineProps({
  jsonData: {
    type: Object,
    required: true,
  }
});

// --- State Management ---
const validationResults = ref([]);
const isValidating = ref(false);

// --- Computed Properties ---
const hasErrors = computed(() => {
  return validationResults.value.some(r => r.type === 'error');
});

const hasWarnings = computed(() => {
  return validationResults.value.some(r => r.type === 'warning');
});


// --- Validation Helper Functions ---

/**
 * @description Recursively checks an object or array to find all paths with null or empty string values.
 */
function findEmptyFields(data, path = '') {
  let emptyFields = [];
  if (data === null || data === '') {
    if (!path) return ['The entire JSON data is empty'];
    return [path];
  }
  if (Array.isArray(data)) {
    data.forEach((item, index) => {
      emptyFields = emptyFields.concat(
        findEmptyFields(item, `${path}[${index}]`)
      );
    });
  } else if (typeof data === 'object' && data !== null) {
    for (const key in data) {
      if (key === 'ai_analysis_notes') continue; // Ignore notes field
      const newPath = path ? `${path}.${key}` : key;
      emptyFields = emptyFields.concat(
        findEmptyFields(data[key], newPath)
      );
    }
  }
  return emptyFields;
}

/**
 * @description Validates if a field is an array of objects, checking its length and content integrity.
 */
function validateObjectArray(arr, fieldName, minLength = 1) {
  const results = [];
  if (!Array.isArray(arr)) {
    results.push({ type: 'error', message: `Field '${fieldName}' must be an array, but its type is "${typeof arr}".` });
    return results;
  }
  
  results.push({ type: 'success', message: `Type check: '${fieldName}' has the correct type (array).` });

  if (arr.length < minLength) {
    results.push({ type: 'error', message: `Count check: '${fieldName}' should contain at least ${minLength} item(s), but it currently has ${arr.length}.` });
  } else {
     results.push({ type: 'success', message: `Count check: '${fieldName}' contains ${arr.length} item(s), which meets the requirement.` });
  }

  // Empty values inside the array are handled by the global findEmptyFields function.
  return results;
}


// --- Core Validation Method ---
const runValidation = () => {
  if (!props.jsonData) {
    validationResults.value = [{ type: 'warning', message: 'No data available for validation.' }];
    return;
  }
  
  isValidating.value = true;
  validationResults.value = [];

  setTimeout(() => {
    const data = props.jsonData;
    
    // **General Rule 1: Check 'shape' field**
    if (data.shape && typeof data.shape === 'string') {
      validationResults.value.push({ type: 'success', message: `Part type identified: "${data.shape}"` });
    } else {
      validationResults.value.push({ type: 'error', message: "Key field 'shape' is missing or has an incorrect type." });
      isValidating.value = false;
      return;
    }
    
    // **General Rule 2: Global integrity check for empty fields**
    const allEmptyFields = findEmptyFields(data);
    if(allEmptyFields.length === 0) {
        validationResults.value.push({ type: 'success', message: 'Integrity check: All fields are filled.' });
    } else {
        const generalEmptyFields = allEmptyFields.filter(path => !path.includes('geometric_tolerances['));
        generalEmptyFields.forEach(path => {
            validationResults.value.push({ type: 'error', message: `Field '${path}' is not filled, its value is null or empty.` });
        })
    }

    // --- Rule Dispatcher (now mainly for type and logic checks) ---
    if (data.shape === 'cylinder') {
      const params = data.parameters;
      if (params) {
        if (params.radius !== null && typeof params.radius !== 'number') { validationResults.value.push({ type: 'error', message: `Type error: 'parameters.radius' should be a number, but it is "${typeof params.radius}".` }); }
        if (params.height !== null && typeof params.height !== 'number') { validationResults.value.push({ type: 'error', message: `Type error: 'parameters.height' should be a number, but it is "${typeof params.height}".` }); }
      }
      if ('geometric_tolerances' in data) { validationResults.value.push(...validateObjectArray(data.geometric_tolerances, 'geometric_tolerances', 2)); }
    } 
    else if (data.shape === 'cuboid') {
      const params = data.parameters;
      if (params) {
        const dimensions = ['length', 'width', 'height'];
        dimensions.forEach(dim => { if (params[dim] !== null && typeof params[dim] !== 'number') { validationResults.value.push({ type: 'error', message: `Type error: 'parameters.${dim}' should be a number.` }); } });
        if (typeof params.length === 'number' && typeof params.width === 'number' && params.length < params.width) { validationResults.value.push({ type: 'error', message: `Logic error: Length (${params.length}) is less than width (${params.width}).` }); }
      }
      if ('geometric_tolerances' in data) { validationResults.value.push(...validateObjectArray(data.geometric_tolerances, 'geometric_tolerances', 1)); }
    }
    else if (data.shape === 'hexagonal_nut') {
      const params = data.parameters;
      if (params) {
        if (params.side_length !== null && typeof params.side_length !== 'number') { validationResults.value.push({ type: 'error', message: `Type error: 'parameters.side_length' should be a number.` }); }
        if (params.height !== null && typeof params.height !== 'number') { validationResults.value.push({ type: 'error', message: `Type error: 'parameters.height' should be a number.` }); }
        if (params.hole && params.hole.diameter !== null && typeof params.hole.diameter !== 'number') { validationResults.value.push({ type: 'error', message: `Type error: 'parameters.hole.diameter' should be a number.` }); }
      }
      if ('geometric_tolerances' in data) {
        validationResults.value.push(...validateObjectArray(data.geometric_tolerances, 'geometric_tolerances', 3));
        if (Array.isArray(data.geometric_tolerances) && data.geometric_tolerances[2]?.tolerance !== '%%c0.1') { validationResults.value.push({ type: 'warning', message: `Fixed value warning: The value of 'geometric_tolerances[2].tolerance' has been modified.` }); }
      }
    }
    else if (data.shape === 'hexagonal_prism') {
      const params = data.parameters;
      if (params) {
        if (params.side_length !== null && typeof params.side_length !== 'number') { validationResults.value.push({ type: 'error', message: `Type error: 'parameters.side_length' should be a number.` }); }
        if (params.height !== null && typeof params.height !== 'number') { validationResults.value.push({ type: 'error', message: `Type error: 'parameters.height' should be a number.` }); }
      }
      if ('geometric_tolerances' in data) { validationResults.value.push(...validateObjectArray(data.geometric_tolerances, 'geometric_tolerances', 2)); }
      if (data.surface_finish?.top_surface?.[0] === null) { validationResults.value.push({ type: 'error', message: "Content check: 'surface_finish.top_surface[0]' (symbol) is not filled." }); }
    }
    else if (data.shape === 'hexagonal_screw') {
      const params = data.parameters;
      if (params) {
        if (params.head?.side_length !== null && typeof params.head?.side_length !== 'number') { validationResults.value.push({ type: 'error', message: `Type error: 'parameters.head.side_length' should be a number.` }); }
        if (params.head?.height !== null && typeof params.head?.height !== 'number') { validationResults.value.push({ type: 'error', message: `Type error: 'parameters.head.height' should be a number.` }); }
        if (params.shaft?.diameter !== null && typeof params.shaft?.diameter !== 'number') { validationResults.value.push({ type: 'error', message: `Type error: 'parameters.shaft.diameter' should be a number.` }); }
        if (params.shaft?.length !== null && typeof params.shaft?.length !== 'number') { validationResults.value.push({ type: 'error', message: `Type error: 'parameters.shaft.length' should be a number.` }); }
      }
      if ('geometric_tolerances' in data) { validationResults.value.push(...validateObjectArray(data.geometric_tolerances, 'geometric_tolerances', 2)); }
    }
    else if (data.shape === 'cuboid_cylinder_assembly') {
      const components = data.components;
      if (components) {
        const cuboidParams = components.cuboid?.parameters;
        const cylinderParams = components.cylinder?.parameters;
        if (cuboidParams) {
            const dimensions = ['length', 'width', 'height'];
            dimensions.forEach(dim => { if (cuboidParams[dim] !== null && typeof cuboidParams[dim] !== 'number') { validationResults.value.push({ type: 'error', message: `Type error: 'components.cuboid.parameters.${dim}' should be a number.` }); } });
            if (typeof cuboidParams.length === 'number' && typeof cuboidParams.width === 'number' && cuboidParams.length < cuboidParams.width) { validationResults.value.push({ type: 'error', message: `Logic error (cuboid): Length (${cuboidParams.length}) < Width (${cuboidParams.width}).` }); }
        }
        if (cylinderParams) {
            if (cylinderParams.radius !== null && typeof cylinderParams.radius !== 'number') { validationResults.value.push({ type: 'error', message: `Type error: 'components.cylinder.parameters.radius' should be a number.` }); }
            if (cylinderParams.height !== null && typeof cylinderParams.height !== 'number') { validationResults.value.push({ type: 'error', message: `Type error: 'components.cylinder.parameters.height' should be a number.` }); }
        }
        if (cuboidParams && cylinderParams && typeof cuboidParams.width === 'number' && typeof cylinderParams.radius === 'number') {
            const cylinderDiameter = cylinderParams.radius * 2;
            if (cylinderDiameter > cuboidParams.width) { validationResults.value.push({ type: 'error', message: `Mating error: Cylinder diameter (${cylinderDiameter}) > Cuboid width (${cuboidParams.width}).` }); }
        }
      }
      if ('geometric_tolerances' in data) { validationResults.value.push(...validateObjectArray(data.geometric_tolerances, 'geometric_tolerances', 2)); }
    }
    else if (data.shape === 'screw_nut_assembly') {
      const components = data.components;
      if (components) {
        const screwParams = components.screw?.parameters;
        const nutParams = components.nut?.parameters;
        if(screwParams) {
          const screwDims = ['head_width', 'head_height', 'shaft_diameter', 'shaft_length'];
          screwDims.forEach(dim => { if (screwParams[dim] !== null && typeof screwParams[dim] !== 'number') { validationResults.value.push({ type: 'error', message: `Type error: 'components.screw.parameters.${dim}' should be a number.` }); } });
        }
        if(nutParams) {
          const nutDims = ['width', 'height', 'hole_diameter'];
          nutDims.forEach(dim => { if (nutParams[dim] !== null && typeof nutParams[dim] !== 'number') { validationResults.value.push({ type: 'error', message: `Type error: 'components.nut.parameters.${dim}' should be a number.` }); } });
        }
        if (screwParams && nutParams && typeof screwParams.shaft_diameter === 'number' && typeof nutParams.hole_diameter === 'number') {
            if (screwParams.shaft_diameter !== nutParams.hole_diameter) { validationResults.value.push({ type: 'error', message: `Mating error: Screw shaft diameter (${screwParams.shaft_diameter}) does not match nut hole diameter (${nutParams.hole_diameter})!` }); }
        }
      }
      if ('geometric_tolerances' in data) { validationResults.value.push(...validateObjectArray(data.geometric_tolerances, 'geometric_tolerances', 2)); }
    }
    else {
      validationResults.value.push({ type: 'warning', message: `Unknown part type "${data.shape}", cannot perform detailed validation.` });
    }
    
    // --- End of Validation ---
    if (validationResults.value.length > 0 && !validationResults.value.some(r => r.type === 'error')) {
        validationResults.value.unshift({ type: 'success', message: 'All key validation rules have passed!' });
    }

    isValidating.value = false;
  }, 300);
};

// --- Watcher ---
watch(() => props.jsonData, (newData) => {
  if (newData) {
    runValidation();
  }
}, { deep: true, immediate: true });

</script>

<template>
  <div class="validator-wrapper card">
    <div class="validator-header">
      <h2>JSON Structure & Data Validation</h2>
      <p>This tool checks the completeness and compliance of the analysis results based on predefined rules.</p>
    </div>

    <div class="actions">
      <button @click="runValidation" :disabled="isValidating" class="primary-btn">
        <svg v-if="!isValidating" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd" /></svg>
        <div v-if="isValidating" class="spinner-small"></div>
        {{ isValidating ? 'Validating...' : 'Re-validate' }}
      </button>
    </div>

    <div class="results-container">
      <h3>Validation Report:</h3>
      <div v-if="isValidating" class="loading-text">
        Analyzing JSON data...
      </div>
      <ul v-else-if="validationResults.length > 0" class="results-list">
        <li v-for="(result, index) in validationResults" :key="index" :class="['result-item', `result-item--${result.type}`]">
          <span class="icon">
            <template v-if="result.type === 'success'">✅</template>
            <template v-if="result.type === 'error'">❌</template>
            <template v-if="result.type === 'warning'">⚠️</template>
          </span>
          <span class="message">{{ result.message }}</span>
        </li>
      </ul>
      <p v-else class="no-results">
        No validation results available.
      </p>
    </div>

  </div>
</template>

<style scoped>
/* Styles remain unchanged */
.validator-wrapper {
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.validator-header h2 {
  margin-top: 0;
}
.validator-header p {
  color: var(--text-light-color);
  font-size: 0.95rem;
  margin-bottom: 1.5rem;
}

.actions {
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.spinner-small {
    width: 18px;
    height: 18px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top-color: #ffffff;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

.results-container h3 {
  margin-bottom: 1rem;
  color: var(--text-color);
}

.loading-text {
  color: var(--text-light-color);
  font-style: italic;
}

.results-list {
  list-style-type: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.result-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.9rem;
  border: 1px solid;
}
.result-item .icon {
  font-size: 1.1rem;
  margin-top: 1px;
}

.result-item--success {
  background-color: #f0fdf4;
  color: #15803d;
  border-color: #bbf7d0;
}
.result-item--error {
  background-color: #fef2f2;
  color: #b91c1c;
  border-color: #fecaca;
}
.result-item--warning {
  background-color: #fffbeb;
  color: #b45309;
  border-color: #fcd34d;
}

.no-results {
  color: var(--text-light-color);
}
</style>