# resume-radar

![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-hackathon--MVP-orange)
![Built with ❤️🤖](https://img.shields.io/badge/built%20with-%E2%9D%A4%EF%B8%8F%20%2B%20%F0%9F%A4%96-red)

Weekend solo hackathon project → AI that reviews & decorates your CV.  
- LLM-authored hover tips  
- Heatmap highlights of strengths & weaknesses  
- PDF in → PDF out 

## 🔑 Setup API Key

This project uses the [OpenAI Python client](https://github.com/openai/openai-python).  
For security, the API key is stored in a local `.env` file that is **not** committed to git.

1. Install dependencies:
   pip install -r requirements.txt

2. Create a .env file in the project root:

OPENAI_API_KEY=sk-your-real-key

3. Run the app:

python main.py inputs/CV_JohnDoe.pdf

