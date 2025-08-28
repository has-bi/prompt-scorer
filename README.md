# 🎯 Penilai Prompt Engineering

AI-powered prompt analyzer dengan feedback yang supportif dan ramah ala Indonesia! Analisis prompt kamu dan dapatkan rekomendasi untuk jadi lebih kece! 🚀✨

## ✨ Fitur Keren

- **⚡ Quick Recommendations**: Tips kilat berdasarkan skor prompt kamu
- **🇮🇩 Indonesian Style**: Bahasa yang supportif dan ramah seperti teman baik
- **🎯 4 Teknik Utama**: Zero-Shot, Few-Shot, Chain of Thought, Tree of Thoughts
- **📊 Visual Scoring**: Meter skor dengan feedback yang encouraging
- **🎉 Interactive**: Sample prompts dan comparison tool
- **🌈 Fun Experience**: Balloons untuk skor tinggi!

## 🚀 Quick Start dengan UV (Recommended!)

### 1. Install UV (jika belum ada)
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone & Setup Project
```bash
git clone <repository-url>
cd prompt-scorer

# Install dependencies dengan uv (super cepet!)
uv sync
```

### 3. Setup Environment
```bash
# Copy template environment
cp .env.example .env

# Edit .env file dan tambahin OpenAI API key kamu
# OPENAI_API_KEY=your-api-key-here
```

### 4. Run the App!
```bash
# Run with uv
uv run streamlit run prompt_scorer.py

# Atau aktivasi environment dulu
source .venv/bin/activate  # Linux/Mac
# atau: .venv\Scripts\activate  # Windows
streamlit run prompt_scorer.py
```

## 📦 Alternative: Install dengan Pip

Jika belum mau pakai uv, masih bisa pakai cara lama:

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# atau: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run app
streamlit run prompt_scorer.py
```

## ⚙️ Configuration

### Local Development
Buat file `.env` (copy dari `.env.example`) dan isi:
```env
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.3
APP_TITLE=Penilai Prompt Engineering
```

### Streamlit Cloud
Tambahkan secrets di dashboard Streamlit Cloud:
```toml
[openai]
api_key = "your-openai-api-key-here"
model = "gpt-4"
temperature = 0.3

[app]
title = "Penilai Prompt Engineering"
debug = false
```

## 🎮 Cara Pakai

1. **Buka app** di browser (biasanya http://localhost:8501)
2. **Masukkan API key** OpenAI kamu
3. **Coba sample prompts** atau paste prompt sendiri
4. **Get feedback** yang supportif dan actionable!
5. **Improve your prompts** jadi makin powerful! 💪

## 🛠️ Development

### Project Structure
```
prompt-scorer/
├── prompt_scorer.py      # Main Streamlit app
├── requirements.txt      # Pip dependencies  
├── pyproject.toml       # UV configuration
├── .env.example         # Environment template
└── README.md           # Documentation
```

### Dependencies
- **Streamlit**: Web app framework
- **OpenAI**: AI API untuk analysis
- **python-dotenv**: Environment variables

## 🤝 Contributing

Feel free to contribute! Buat yang mau nambahin fitur atau improve feedback-nya, pull request aja! 

## 📄 License

MIT License - Feel free to use and modify! 

---

**Happy Prompting! Semoga jadi makin jago bikin prompt yang kece! 🎊**
