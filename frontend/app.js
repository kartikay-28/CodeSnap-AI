// API Configuration
const API_BASE_URL = 'http://localhost:8000';
const ANALYZE_ENDPOINT = `${API_BASE_URL}/api/v1/analyze/code`;

// DOM Elements
const uploadBox = document.getElementById('uploadBox');
const fileInput = document.getElementById('fileInput');
const previewSection = document.getElementById('previewSection');
const imagePreview = document.getElementById('imagePreview');
const analyzeBtn = document.getElementById('analyzeBtn');
const clearBtn = document.getElementById('clearBtn');
const loading = document.getElementById('loading');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');
const retryBtn = document.getElementById('retryBtn');

let selectedFile = null;

// Event Listeners
uploadBox.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleFileSelect);
analyzeBtn.addEventListener('click', analyzeCode);
clearBtn.addEventListener('click', clearSelection);
retryBtn.addEventListener('click', clearError);

// Drag and drop
uploadBox.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadBox.classList.add('dragover');
});

uploadBox.addEventListener('dragleave', () => {
    uploadBox.classList.remove('dragover');
});

uploadBox.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadBox.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

// Handle file selection
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        handleFile(file);
    }
}

function handleFile(file) {
    if (!file.type.startsWith('image/')) {
        showError('Please select a valid image file');
        return;
    }

    if (file.size > 10 * 1024 * 1024) {
        showError('File size must be less than 10MB');
        return;
    }

    selectedFile = file;

    const reader = new FileReader();
    reader.onload = (e) => {
        imagePreview.src = e.target.result;
        uploadBox.style.display = 'none';
        previewSection.style.display = 'block';
        resultsSection.style.display = 'none';
        errorSection.style.display = 'none';
    };
    reader.readAsDataURL(file);
}

function clearSelection() {
    selectedFile = null;
    fileInput.value = '';
    uploadBox.style.display = 'block';
    previewSection.style.display = 'none';
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';
}

function clearError() {
    errorSection.style.display = 'none';
    previewSection.style.display = 'block';
}

// Analyze code
async function analyzeCode() {
    if (!selectedFile) {
        showError('Please select an image first');
        return;
    }

    previewSection.style.display = 'none';
    loading.style.display = 'block';
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';

    try {
        const formData = new FormData();
        formData.append('file', selectedFile);

        const response = await fetch(ANALYZE_ENDPOINT, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Analysis failed');
        }

        const data = await response.json();
        loading.style.display = 'none';
        displayResults(data);

    } catch (error) {
        loading.style.display = 'none';
        showError(error.message || 'Failed to analyze code. Please try again.');
    }
}

// Display results
function displayResults(data) {
    resultsSection.style.display = 'block';

    // Metadata
    document.getElementById('extractedCode').textContent = data.extracted_code;
    document.getElementById('languageBadge').textContent = `Language: ${data.detected_language}`;
    document.getElementById('confidenceBadge').textContent = `Confidence: ${(data.confidence_score * 100).toFixed(1)}%`;

    // Overview
    document.getElementById('overview').textContent = data.beginner_explanation || 'No overview available';

    // Step by step
    const stepByStepList = document.getElementById('stepByStep');
    stepByStepList.innerHTML = '';
    data.step_by_step_explanation.forEach(step => {
        const li = document.createElement('li');
        li.textContent = step;
        stepByStepList.appendChild(li);
    });

    // Complexity
    document.getElementById('timeComplexity').textContent = data.complexity_analysis.time_complexity;
    document.getElementById('spaceComplexity').textContent = data.complexity_analysis.space_complexity;
    document.getElementById('complexityExplanation').textContent = data.complexity_analysis.explanation;

    // Beginner explanation
    document.getElementById('beginnerExplanation').textContent = data.beginner_explanation;

    // Edge cases
    const edgeCasesList = document.getElementById('edgeCases');
    edgeCasesList.innerHTML = '';
    data.edge_cases.forEach(edgeCase => {
        const li = document.createElement('li');
        li.textContent = edgeCase;
        edgeCasesList.appendChild(li);
    });

    // Common mistakes
    const mistakesList = document.getElementById('commonMistakes');
    mistakesList.innerHTML = '';
    data.common_mistakes.forEach(mistake => {
        const li = document.createElement('li');
        li.textContent = mistake;
        mistakesList.appendChild(li);
    });

    // Stats
    document.getElementById('processingTime').textContent = `${data.processing_time_ms}ms`;
    document.getElementById('ocrConfidence').textContent = `${(data.ocr_confidence * 100).toFixed(1)}%`;

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Show error
function showError(message) {
    errorSection.style.display = 'block';
    document.getElementById('errorMessage').textContent = message;
    previewSection.style.display = 'none';
    resultsSection.style.display = 'none';
}

// Check API health on load
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            console.log('✅ API is healthy');
        }
    } catch (error) {
        console.warn('⚠️ Could not connect to API:', error.message);
    }
}

// Initialize
checkAPIHealth();