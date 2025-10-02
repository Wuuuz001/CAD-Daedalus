<!-- src/components/JsonEditor.vue (with v-model.number fix applied) -->
<script setup>
defineProps({
  data: {
    type: Object,
    required: true,
  }
});

// Helper function to check if a value is a recursible object
const isObject = (value) => {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
};

// Helper function to determine if a field should be treated as a number
const isNumericField = (key) => {
  const numericKeys = [
    // cylinder
    'radius', 
    // cuboid
    'length', 'width', 
    // hexagonal_nut & hexagonal_prism
    'side_length', 
    // screw_nut_assembly
    'head_width', 'head_height', 'shaft_diameter', 'shaft_length', 'hole_diameter', 'quantity',
    
    // common / shared
    'height', 'diameter', 
    'spacing', 'text_height', 'arrow_size', 'orientation', 'position'
  ];
  // Using a Set for optimization to improve lookup efficiency
  return new Set(numericKeys).has(key);
};
</script>

<template>
  <div class="editor-node">
    <div v-for="(value, key) in data" :key="key" class="field-block">
      
      <!-- Case 1: If the value is an object (but not an array) -->
      <div v-if="isObject(value)">
        <strong class="key-title">{{ key }}:</strong>
        <div class="object-container">
          <JsonEditor :data="value" />
        </div>
      </div>

      <!-- Case 2: If the value is an array -->
      <div v-else-if="Array.isArray(value)">
        <strong class="key-title">{{ key }}:</strong>
        <div v-if="value.length > 0 && isObject(value[0])" class="array-container">
          <div v-for="(item, index) in value" :key="index" class="array-item">
            <JsonEditor :data="item" />
          </div>
        </div>
        <div v-else class="simple-array-container">
          <input 
            v-for="(item, index) in value"
            :key="index"
            type="text"
            v-model="value[index]"
            class="simple-array-input"
            :class="{ 'is-null': item === null || item === '' }"
          />
        </div>
      </div>

      <!-- Case 3: For primitive types (string, number, boolean, null) -->
      <div v-else class="primitive-field">
        <label :for="key" class="key-label">{{ key }}:</label>
        
        <!-- Core change is here -->
        <!-- If it's a numeric field, use type="number" and v-model.number -->
        <input 
          v-if="isNumericField(key)"
          type="number" 
          :id="key"
          v-model.number="data[key]"
          :placeholder="value === null ? 'AI uncertain, please enter' : ''"
          :class="{ 'is-null': value === null || value === '' }"
          class="primitive-input"
        />
        <!-- Otherwise, use type="text" -->
        <input 
          v-else
          type="text" 
          :id="key"
          v-model="data[key]"
          :placeholder="value === null ? 'AI uncertain, please enter' : ''"
          :class="{ 'is-null': value === null || value === '' }"
          class="primitive-input"
        />
      </div>

    </div>
  </div>
</template>

<style scoped>
/* Styles remain unchanged */
.editor-node {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.field-block {
  /* No margin needed, using gap layout */
}

/* Title for objects and arrays */
.key-title {
  display: block;
  font-weight: 600;
  font-size: 1rem;
  color: var(--primary-color, #4f46e5);
  margin-bottom: 0.75rem;
}

/* Label for primitive fields */
.primitive-field {
  display: grid;
  grid-template-columns: 180px 1fr; /* Fixed width for the left label */
  gap: 1rem;
  align-items: center;
}
.key-label {
  font-family: monospace;
  font-size: 0.9rem;
  color: var(--text-light-color, #6b7280);
  text-align: right;
  padding-right: 1rem;
}

/* Containers for nested objects and arrays */
.object-container, .array-container {
  margin-left: 1.25rem;
  padding-left: 1.25rem;
  border-left: 2px solid var(--border-color, #e5e7eb);
}

.array-item {
  border: 1px solid var(--border-color, #e5e7eb);
  padding: 1rem;
  margin-bottom: 1rem;
  border-radius: 0.5rem;
  background-color: var(--bg-color, #f9fafb);
}
.array-item:last-child {
  margin-bottom: 0;
}

/* Common input styles */
input {
  padding: 0.625rem 0.75rem;
  border: 1px solid var(--border-color, #d1d5db);
  border-radius: 0.5rem;
  font-size: 0.9rem;
  width: 100%;
  box-sizing: border-box;
  transition: all 0.2s ease;
}
input:focus {
  outline: none;
  border-color: var(--primary-color, #4f46e5);
  box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.2);
}
input.is-null {
  border-color: #ef4444; /* red */
  background-color: #fee2e2;
}

/* Container for simple value arrays */
.simple-array-container {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}
.simple-array-input {
  flex-grow: 1; /* Fill available space */
}
</style>