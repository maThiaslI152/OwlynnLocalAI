# OwlynnLocalAI

A privacy-focused AI personal assistant that runs entirely on your local machine. Powered by Qwen3-14B and featuring document processing, OCR, and image captioning capabilities.

## Features

- **Local LLM**: Uses Qwen3-14B via LM Studio
- **Multilingual Support**: English and Thai (and other languages supported by Qwen3-14B)
- **Document Processing**: Supports multiple file formats:
  - Text: `.txt`, `.md`
  - Documents: `.pdf`, `.docx`, `.rtf`
  - Spreadsheets: `.csv`, `.xlsx`
  - Presentations: `.pptx`
  - Code: `.py`, `.js`, `.json`, `.yml`, `.yaml`, `.html`, `.xml`, `.css`
  - Images: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`
- **OCR**: Text extraction from images (English and Thai)
- **Image Captioning**: Using BLIP model
- **Memory Management**: Redis for short-term, PostgreSQL for long-term
- **Vector Storage**: ChromaDB for semantic search
- **Modern UI**: React frontend with CopilotKit

## Prerequisites

- Python 3.9+
- Docker and Docker Compose
- LM Studio with Qwen3-14B model
- Tesseract OCR
- Node.js 16+ (for frontend)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/OwlynnLocalAI.git
   cd OwlynnLocalAI
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install spaCy language model:
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. Start the required services using Docker Compose:
   ```bash
   docker-compose up -d
   ```

6. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```

## Configuration

1. Create a `.env` file in the root directory:
   ```env
   DEBUG=false
   LLM_BASE_URL=http://localhost:1234/v1
   LLM_MODEL=Qwen3-14B
   POSTGRES_USER=owlynn
   POSTGRES_PASSWORD=owlynn_password
   POSTGRES_DB=owlynn_db
   ```

2. Configure LM Studio:
   - Download and install LM Studio
   - Download Qwen3-14B model
   - Start the local server on port 1234

## Usage

1. Start the backend server:
   ```bash
   python -m Backend.main
   ```

2. Start the frontend development server:
   ```bash
   cd frontend
   npm run dev
   ```

3. Access the application at `http://localhost:3000`

## API Endpoints

- `POST /api/v1/chat`: Chat with the AI assistant
- `POST /api/v1/upload`: Upload and process files
- `GET /api/v1/search`: Search through processed documents
- `GET /api/v1/health`: Health check endpoint

## Development

### Project Structure

```
OwlynnLocalAI/
├── Backend/
│   ├── core/
│   │   ├── config.py
│   │   ├── memory.py
│   │   └── document_processor.py
│   ├── api/
│   │   ├── routes.py
│   │   ├── models.py
│   │   └── schemas.py
│   └── main.py
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
├── docker-compose.yml
├── requirements.txt
└── README.md
```

### Running Tests

```bash
pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Qwen3-14B](https://github.com/QwenLM/Qwen) for the base language model
- [LM Studio](https://lmstudio.ai/) for local model serving
- [CopilotKit](https://github.com/CopilotKit/CopilotKit) for the frontend framework
- [ChromaDB](https://github.com/chroma-core/chroma) for vector storage
- [BLIP](https://github.com/salesforce/BLIP) for image captioning
