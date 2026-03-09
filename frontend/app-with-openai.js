// API Configuration
const API_BASE_URL = 'http://localhost:8000';
const ANALYZE_ENDPOINT = `${API_BASE_URL}/api/v1/analyze/code`;

// ⚠️ WARNING: Never expose API keys in frontend code in production!
// This is for demonstration only. Use environment variables and backend proxy.
const OPENAI_API_KEY = 'your-api-key-here'; // DO NOT COMMIT THIS!

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

// Analyze code using backend (recommended)
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
        // Use backend API (secure and recommended)
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

// Alternative: Direct OpenAI call (NOT RECOMMENDED for production)
async function analyzeCodeWithOpenAI(extractedCode) {
    // ⚠️ WARNING: This exposes your API key! Only use for local testing!
    
    if (!OPENAI_API_KEY || OPENAI_API_KEY === 'your-api-key-here') {
        throw new Error('OpenAI API key not configured');
    }

    const prompt = `Analyze the following code and provide a comprehensive explanation:

CODE:
\`\`\`
${extractedCode}
\`\`\`

Provide your analysis in JSON format with:
- overview: Brief overview
- step_by_step: Array of explanation steps
- complexity: {time, space, explanation}
- beginner_explanation: Simple explanation
- edge_cases: Array of edge cases
- common_mistakes: Array of common mistakes`;

    try {
        const response = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${OPENAI_API_KEY}`
            },
            body: JSON.stringify({
                model: 'gpt-4',
                messages: [
                    { role: 'user', content: prompt }
                ],
                temperature: 0.3,
                max_tokens: 2000
            })
        });

        if (!response.ok) {
            throw new Error('OpenAI API request failed');
        }

        const data = await response.json();
        const content = data.choices[0].message.content;
        
        // Parse JSON response
        const jsonMatch = content.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
            return JSON.parse(jsonMatch[0]);
        }
        
        throw new Error('Invalid response format');
        
    } catch (error) {
        console.error('OpenAI API error:', error);
        throw error;
    }
}

// Display results
function displayResults(data) {
    resultsSection.style.display = 'block';

    document.getElementById('extractedCode').textContent = data.extracted_code;
    document.getElementById('languageBadge').textContent = `Language: ${data.detected_language}`;
    document.getElementById('confidenceBadge').textContent = `Confidence: ${(data.confidence_score * 100).toFixed(1)}%`;

    const overview = data.beginner_explanation || data.step_by_step_explanation[0] || 'No overview available';
    document.getElementById('overview').textContent = overview;

    const stepByStepList = document.getElementById('stepByStep');
    stepByStepList.innerHTML = '';
    data.step_by_step_explanation.forEach(step => {
        const li = document.createElement('li');
        li.textContent = step;
        stepByStepList.appendChild(li);
    });

    document.getElementById('timeComplexity').textContent = data.complexity_analysis.time_complexity;
    document.getElementById('spaceComplexity').textContent = data.complexity_analysis.space_complexity;
    document.getElementById('complexityExplanation').textContent = data.complexity_analysis.explanation;

    document.getElementById('beginnerExplanation').textContent = data.beginner_explanation;

    const edgeCasesList = document.getElementById('edgeCases');
    edgeCasesList.innerHTML = '';
    data.edge_cases.forEach(edgeCase => {
        const li = document.createElement('li');
        li.textContent = edgeCase;
        edgeCasesList.appendChild(li);
    });

    const mistakesList = document.getElementById('commonMistakes');
    mistakesList.innerHTML = '';
    data.common_mistakes.forEach(mistake => {
        const li = document.createElement('li');
        li.textContent = mistake;
        mistakesList.appendChild(li);
    });

    document.getElementById('processingTime').textContent = `${data.processing_time_ms}ms`;
    document.getElementById('ocrConfidence').textContent = `${(data.ocr_confidence * 100).toFixed(1)}%`;

    resultsSection.scrollIntoView({ behavior: 'smooth' });
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
        if (!response.ok) {
            console.warn('API health check failed');
        }
    } catch (error) {
        console.warn('Could not connect to API:', error.message);
    }
}

// Initialize
checkAPIHealth();