# 🏉️ Golf Ball Tracker with VisionAgent

![image](https://github.com/user-attachments/assets/df49a632-2899-4f65-b493-7351f3585a38)

![image](https://github.com/user-attachments/assets/a9244451-d1b4-44e2-a648-174dd414975a)

Track golf balls in swing videos with AI-powered object detection and motion analysis. Features real-time processing, adjustable sensitivity, and visual trail effects.

## 🚀 Quick Start

### ✅ 1. Clone the Repository

```bash
git clone https://github.com/jjmlovesgit/Golf_tracker.git
cd Golf_tracker
```

### ✅ 2. Run the Setup Script

```bash
python setup.py
```

This will:

- Create a Python virtual environment
- Install all dependencies
- Configure your VisionAgent API key
- Generate easy-launch scripts

## 🎯 Features

- 🎥 Video Processing: Analyze golf swing videos frame-by-frame
- 🏓 Motion Tracking: Follow only moving balls (ignores stationary objects)
- 🖍 Visual Trail: Fading tail effect shows ball trajectory
- ⚙ Adjustable Sensitivity: Fine-tune detection parameters
- 📊 Progress Tracking: Visual indicators for each processing stage
- 💾 Local Saving: Export processed videos with annotations

## 🖥 How to Run

### 📏 Windows (Recommended)

Double-click `golf_tracker.bat`

> *(Create shortcut on desktop for easy access)*

### 🍏 macOS/Linux

```bash
./launch_app.sh
```

## 🔧 Configuration

Your VisionAgent API key is stored in `.env`:

```ini
VISION_AGENT_API_KEY=your_api_key_here
```

Get your API key: https://va.landing.ai/settings/api-key

## 🛠️ Technical Details

### Requirements

- Python 3.8+
- VisionAgent API key
- FFmpeg (for video processing)

### File Structure

```text
Golf_tracker/
├── Golf_tracker.py       # Main application
├── setup.py              # Installation script
├── golf_tracker.bat      # Windows launcher
├── launch_app.sh         # macOS/Linux launcher
├── Tiger.mp4             # Sample input video
├── requirements.txt      # Dependencies
├── LICENSE               # MIT License
├── licensee.md           # License explanation (if separate)
└── README.md
```

## 📚 Usage Guide

1. Upload a golf swing video (MP4 format recommended)
2. Adjust parameters:
   - Output FPS: 15 (balance quality/speed)
   - Motion Sensitivity: 0.01 (lower = more sensitive)
3. Click Process Video
4. View/download the annotated result
   
## 💡 Tips

- For best results, use videos with:
  - Clear contrast between ball and background
  - Stable camera position
  - 720p resolution or higher
- Start with higher confidence thresholds (0.9+) and adjust down if needed
- Reduce FPS for faster processing on longer videos

## ⚠️ Troubleshooting

### API Errors:

- Verify your key at VisionAgent Dashboard
- Ensure `.env` contains the correct key

### Video Processing Issues:

- Install FFmpeg:
  - `conda install ffmpeg` or
  - `brew install ffmpeg`
- Convert videos to MP4 format before uploading

## 📜 License

MIT License - Not affiliated with VisionAgent/Landing AI

> Note: This app processes videos locally - your data never leaves your machine except for API calls to VisionAgent's services.


