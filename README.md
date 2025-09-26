# OMR Checker - Automated OMR Sheet Evaluation System

A full-stack web application for automated OMR (Optical Mark Recognition) sheet evaluation using OpenCV and machine learning techniques.

## 🚀 Features

- **Automated Bubble Detection**: Uses OpenCV for precise bubble detection and analysis
- **Real-time Processing**: Fast image processing with adaptive thresholding
- **Multiple Answer Keys**: Support for different exam templates
- **Detailed Analytics**: Question-wise analysis with visual feedback
- **Modern UI**: Clean, responsive interface built with React and TailwindCSS
- **Export Results**: Download evaluation results in JSON format
- **Error Handling**: Comprehensive error handling for edge cases

## 🏗️ Architecture

### Backend (FastAPI + OpenCV)
- **FastAPI**: High-performance API framework
- **OpenCV**: Computer vision for image processing
- **Pydantic**: Data validation and serialization
- **NumPy**: Numerical computations

### Frontend (React + Vite)
- **React 18**: Modern UI framework
- **Vite**: Fast build tool and dev server
- **TailwindCSS**: Utility-first CSS framework
- **Axios**: HTTP client for API communication
- **Lucide React**: Beautiful icons

## 📁 Project Structure

```
omr-checker/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── omr_utils.py            # OMR processing logic
│   ├── models.py               # Pydantic models
│   ├── requirements.txt        # Python dependencies
│   ├── answer_keys/
│   │   ├── exam1.json          # Sample answer key 1
│   │   └── exam2.json          # Sample answer key 2
│   ├── uploads/                # Temporary file storage
│   └── results/                # Processing results log
└── frontend/
    ├── src/
    │   ├── components/         # React components
    │   ├── App.jsx             # Main application
    │   ├── api.js              # API service
    │   └── main.jsx            # Entry point
    ├── package.json            # Node.js dependencies
    ├── tailwind.config.js      # TailwindCSS configuration
    └── vite.config.js          # Vite configuration
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start the FastAPI server:
```bash
python main.py
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 📖 Usage

1. **Start both servers** (backend and frontend)
2. **Open your browser** and navigate to `http://localhost:3000`
3. **Upload an OMR sheet** image (.jpg, .jpeg, .png)
4. **Select an answer key** from the dropdown
5. **Click "Process OMR Sheet"** to analyze
6. **View results** with detailed question-wise analysis
7. **Export results** if needed

## 🔧 Configuration

### OMR Processing Parameters

Edit `backend/omr_utils.py` to adjust processing parameters:

```python
class OMRProcessor:
    def __init__(self):
        self.questions_per_row = 5      # Answer choices per question
        self.total_questions = 10       # Total number of questions
        self.bubble_threshold = 0.65    # Filled bubble detection threshold
        self.gaussian_blur_kernel = (5, 5)
        self.threshold_value = 180
        self.min_contour_area = 20
        self.max_contour_area = 400
```

### Answer Keys

Add new answer keys in `backend/answer_keys/`:

```json
{
  "1": "A",
  "2": "B",
  "3": "C",
  "4": "D",
  "5": "A"
}
```

## 🎯 API Endpoints

### POST `/upload`
Upload and process OMR sheet
- **Parameters**: 
  - `file`: Image file (multipart/form-data)
  - `exam_key`: Answer key identifier (optional, default: "exam1")
- **Response**: Processing results with score and analysis

### GET `/answer-keys`
Get list of available answer keys
- **Response**: Array of answer key names

### GET `/`
Health check endpoint
- **Response**: Server status

## 🔍 Image Processing Pipeline

1. **Preprocessing**:
   - Convert to grayscale
   - Apply Gaussian blur
   - Adaptive thresholding

2. **Bubble Detection**:
   - Find contours
   - Filter by area and aspect ratio
   - Group into question rows

3. **Analysis**:
   - Calculate fill percentage for each bubble
   - Determine marked answers
   - Compare with answer key

4. **Evaluation**:
   - Calculate score and percentage
   - Generate detailed results

## 🚨 Error Handling

The system handles various edge cases:
- **Invalid file formats**: Only accepts .jpg, .jpeg, .png
- **File size limits**: Maximum 5MB per upload
- **Processing errors**: Graceful error handling with user feedback
- **Server connectivity**: Connection status monitoring
- **Missing answer keys**: Validation and error messages

## 🎨 UI Features

- **Drag & Drop Upload**: Intuitive file upload interface
- **Real-time Preview**: Image preview before processing
- **Progress Indicators**: Loading states and progress bars
- **Responsive Design**: Works on desktop and mobile devices
- **Color-coded Results**: Visual feedback for correct/incorrect answers
- **Export Functionality**: Download results as JSON

## 🔮 Future Enhancements

- [ ] Bulk processing for multiple OMR sheets
- [ ] Admin panel for answer key management
- [ ] PDF report generation
- [ ] OCR for student ID recognition
- [ ] Database integration (PostgreSQL)
- [ ] JWT authentication
- [ ] Docker containerization
- [ ] Advanced skew correction
- [ ] Machine learning-based bubble detection

## 🐛 Troubleshooting

### Common Issues

1. **Server Connection Failed**:
   - Ensure backend server is running on port 8000
   - Check firewall settings

2. **Image Processing Errors**:
   - Verify image quality and contrast
   - Ensure OMR sheet is properly aligned
   - Check bubble visibility

3. **Incorrect Detection**:
   - Adjust threshold parameters in `omr_utils.py`
   - Ensure consistent bubble marking

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the configuration options
