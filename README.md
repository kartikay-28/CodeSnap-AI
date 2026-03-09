# CodeSnap AI 📸🤖

AI-powered code analysis from screenshots using EasyOCR and Google Gemini.

## 🌐 Live Demo

**🚀 Try it now:**
- **Frontend:** https://codesnap-ai-28.netlify.app/
- **Backend API:** https://codesnap-ai.onrender.com

## 🎯 Demo Screenshots

<div align="center">

### Upload Interface
![Upload Interface](Screenshot%202026-03-09%20152524.png)

### Code Analysis in Progress
![Code Analysis](Screenshot%202026-03-09%20152532.png)

### Detailed Results - Part 1
![Detailed Results](Screenshot%202026-03-09%20152539.png)

### Complete Analysis - Part 2
![Complete Analysis](Screenshot%202026-03-09%20152546.png)

</div>

## 🚀 Features

- **EasyOCR Integration** - Pure Python OCR (no Tesseract needed!)
- **Google Gemini AI** - Free, fast, and powerful code analysis
- **Comprehensive Analysis** - Step-by-step explanations, complexity analysis, edge cases
- **Modern UI** - Clean, responsive web interface
- **Production Ready** - FastAPI backend with proper error handling

## 📦 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Gemini API Key

1. Visit: https://aistudio.google.com/apikey
2. Create an API key (free)
3. Add to `.env`:

```env
GEMINI_API_KEY=your_key_here
```

### 3. Run the Server

```bash
python -m app.main
```

### 4. Open Frontend

Open `frontend/index.html` in your browser and start analyzing code!

## 🌐 Deployment

Ready to deploy? Check out [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guides on:

- **Render** (Free tier, recommended)
- **Railway** (Easy deployment)
- **Heroku** (Classic platform)
- **Google Cloud Run** (Scalable)
- **AWS EC2** (Full control)
- **Docker** (Containerized)

**Quick Deploy:**
```bash
# Make script executable (Linux/Mac)
chmod +x deploy.sh

# Run deployment helper
./deploy.sh
```

## 🛠️ Tech Stack

- **Backend**: FastAPI + Python
- **OCR**: EasyOCR (Pure Python)
- **AI**: Google Gemini 2.0 Flash
- **Frontend**: HTML + CSS + JavaScript

## 📋 API Endpoints

- `GET /health` - Health check
- `GET /docs` - API documentation
- `POST /api/v1/analyze/code` - Analyze code from screenshot

## 🎯 Project Structure

```
CodeSnap-AI/
├── app/
│   ├── api/v1/endpoints/    # API routes
│   ├── services/            # Business logic
│   ├── schemas/             # Data models
│   └── main.py             # FastAPI app
├── frontend/
│   ├── index.html          # Web interface
│   ├── style.css           # Styling
│   └── app.js              # Frontend logic
└── requirements.txt        # Dependencies
```

## 🐛 Troubleshooting

**First run is slow?**
- EasyOCR downloads models (~100MB) on first use
- Only happens once

**API key error?**
- Make sure `GEMINI_API_KEY` is set in `.env`
- Restart server after changes

## 📄 License

MIT License

---

Built with ❤️ using FastAPI, EasyOCR, and Google Gemini