# AI Music Coach Frontend

A modern React application for the AI Music Coach platform that allows users to upload songs and generate spoken chord covers.

## Features

- 🎵 **File Upload**: Drag and drop or click to upload audio files (MP3, WAV, FLAC, M4A, OGG)
- 🔄 **Real-time Processing**: Visual progress indicator during audio processing
- 🎧 **Audio Playback**: Built-in HTML5 audio player for generated chord covers
- 📥 **Download**: Save generated audio files to your device
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile devices
- ⚡ **Error Handling**: Graceful error handling with user-friendly messages

## Getting Started

### Prerequisites

- Node.js (version 14 or higher)
- npm or yarn
- Backend server running on `http://localhost:8000`

### Installation

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm start
   ```

4. **Open your browser** and visit `http://localhost:3000`

### Building for Production

```bash
npm run build
```

This creates a `build` folder with optimized production files.

## Usage

1. **Upload a Song**: Click the file input or drag and drop an audio file
2. **Generate Chord Cover**: Click the "Generate Chord Cover" button
3. **Wait for Processing**: The app will show a progress bar during processing
4. **Listen to Results**: Use the built-in audio player to hear the chord cover
5. **Download**: Click "Download Chord Cover" to save the file

## API Integration

The frontend communicates with the backend API at `http://localhost:8000`:

- **POST** `/process-song/` - Upload and process audio files
- **GET** `/health` - Health check endpoint

### API Configuration

The API base URL is configured in `src/App.jsx`:

```javascript
const API_BASE_URL = 'http://localhost:8000';
```

For production, update this to your backend server URL.

## File Upload

### Supported Formats
- MP3 (audio/mpeg)
- WAV (audio/wav)
- FLAC (audio/flac)
- M4A (audio/mp4)
- OGG (audio/ogg)

### File Size Limit
- Maximum file size: 50MB

## Error Handling

The application handles various error scenarios:

- **Invalid file type**: Shows error message for unsupported formats
- **File too large**: Displays error for files exceeding 50MB
- **Network errors**: Shows connection error messages
- **Server errors**: Displays server-side error messages
- **Processing errors**: Shows processing failure messages

## Development

### Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── App.jsx          # Main application component
│   ├── App.css          # Application styles
│   └── index.js         # Application entry point
├── package.json         # Dependencies and scripts
└── README.md           # This file
```

### Key Components

- **App.jsx**: Main application component with all UI logic
- **File Upload**: Handles file selection and validation
- **Progress Indicator**: Shows processing status
- **Audio Player**: HTML5 audio element for playback
- **Download Button**: Triggers file download

### Styling

The application uses modern CSS with:
- CSS Grid and Flexbox for layout
- CSS custom properties for theming
- Responsive design with media queries
- Smooth animations and transitions
- Glassmorphism design elements

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Troubleshooting

### Common Issues

1. **Backend Connection Error**
   - Ensure the backend server is running on port 8000
   - Check CORS configuration in the backend

2. **File Upload Issues**
   - Verify file format is supported
   - Check file size is under 50MB
   - Ensure stable internet connection

3. **Audio Playback Issues**
   - Check browser supports HTML5 audio
   - Verify audio file was generated successfully

### Development Issues

1. **Port Conflicts**
   - If port 3000 is in use, React will suggest an alternative port
   - Update API_BASE_URL if using a different backend port

2. **CORS Issues**
   - Ensure backend has proper CORS configuration
   - Check proxy settings in package.json

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the AI Music Coach platform. 