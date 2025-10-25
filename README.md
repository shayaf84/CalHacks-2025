# Material Analysis Platform

A versatile material/commodity analysis platform with multi-agent system architecture.

## Project Structure

```
CalHacks-2025/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── env.example            # Environment variables template
├── app/                   # Main application code
├── agents/                # Multi-agent system components
├── database/              # Database models and connections
├── static/                # Static web assets
├── templates/             # HTML templates
└── tests/                 # Test files
```

## Setup Instructions

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Copy environment template:
   ```bash
   cp env.example .env
   ```

3. Fill in your API keys and configuration in `.env`

4. Run the application:
   ```bash
   python main.py
   ```

The application will be available at `http://localhost:8000`
