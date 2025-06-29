# AI Music Coach

An innovative AI-powered music learning tool that helps musicians internalize harmonic structures and chord progressions by ear.

## Concept

AI Music Coach transforms any song into a unique learning experience by:
1. **Upload**: Users upload a song file
2. **Analyze**: The system analyzes the audio to extract chord progressions and timing
3. **Generate**: An AI voice sings the original melody but replaces lyrics with chord names
4. **Learn**: Musicians can hear and internalize chord progressions naturally

## Project Structure

```
ai-music-coach/
├── backend/
│   ├── audio_processing/     # Chord detection, melody extraction
│   ├── synthesis/           # Vocal synthesis and melody mapping
│   ├── api/                 # FastAPI routes and models
│   └── main.py             # Main application entry point
├── frontend/
│   └── src/                # React frontend (placeholder)
├── ml_models/              # Pre-trained ML models
├── utils/                  # Shared utility functions
├── requirements.txt        # Python dependencies
├── setup.py               # Package setup
└── .env                   # Environment configuration
```

## Features

- 🎵 Audio file upload and processing
- 🎼 Automatic chord detection and analysis
- 🤖 AI voice synthesis with chord names
- ⏱️ Synchronized chord timing with original melody
- 🎸 Support for various guitar tunings
- 📱 Web-based interface
- 🎧 Real-time preview and playback

## Tech Stack

- **Backend**: Python with FastAPI
- **Audio Processing**: librosa, essentia, madmom
- **Chord Detection**: Machine learning models for chord recognition
- **AI Voice**: gTTS, pyttsx3 for text-to-speech
- **Frontend**: React/Next.js (placeholder)
- **Audio**: Web Audio API for real-time processing

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd ai-music-coach
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## Usage

### Running the Backend

1. **Start the FastAPI server**:
   ```bash
   cd backend
   python main.py
   ```

2. **Access the API**:
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - Health check: http://localhost:8000/health

### API Endpoints

- `POST /api/v1/upload` - Upload audio file
- `POST /api/v1/process` - Process audio for chord detection
- `GET /api/v1/jobs/{job_id}` - Get processing job status
- `GET /api/v1/jobs/{job_id}/download` - Download processed result

## Development

### Project Structure Details

#### Backend Modules

- **audio_processing/**: Handles chord detection, melody extraction, and audio utilities
- **synthesis/**: Manages vocal synthesis and mapping chord names to melody
- **api/**: Contains FastAPI routes and Pydantic models
- **utils/**: Shared configuration and logging utilities

#### Key Components

1. **ChordDetector**: Extracts chord progressions from audio using ML models
2. **VocalSynthesizer**: Generates AI voice singing chord names
3. **MelodyMapper**: Maps chord names to melody timing
4. **AudioProcessor**: General audio processing utilities

### Adding New Features

1. **Chord Detection Models**: Add pre-trained models to `ml_models/`
2. **Audio Processing**: Extend `audio_processing/` modules
3. **Synthesis**: Enhance `synthesis/` for better voice generation
4. **API**: Add new endpoints in `api/routes.py`

## Configuration

Environment variables in `.env`:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# Audio Processing
AUDIO_SAMPLE_RATE=22050
AUDIO_CHUNK_SIZE=1024

# Model Configuration
MODEL_PATH=./ml_models/
CHORD_DETECTION_MODEL=chord_detection_model.h5

# File Upload
UPLOAD_DIR=./uploads/
MAX_FILE_SIZE=50MB
ALLOWED_AUDIO_FORMATS=mp3,wav,flac,m4a

# Text-to-Speech
TTS_ENGINE=gtts
TTS_LANGUAGE=en
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

[To be determined]

## Roadmap

- [ ] Implement advanced chord detection models
- [ ] Add melody extraction algorithms
- [ ] Enhance vocal synthesis quality
- [ ] Build React frontend
- [ ] Add real-time processing
- [ ] Support for multiple instruments
- [ ] Mobile app development

---

*This project is in early development. Contributions and ideas are welcome!* 