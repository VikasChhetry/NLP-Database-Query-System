# NLP Database Assistant

A natural language interface for database management using Google Gemini AI.

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/nlp-database-assistant.git
   cd nlp-database-assistant
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Edit `.env` with your MySQL credentials and Google API key

5. Run the application:
   ```bash
   python nlp_db_web.py
   ```
   Or use the batch file:
   ```bash
   ./run_web_chatbot.bat
   ```

## Features

- Create and manage databases using natural language
- Insert, update, and delete data without SQL knowledge
- Query database contents using plain English
- View database structure and contents
- Web-based interface for easy interaction

## Example Commands

- "Create a new database called inventory"
- "Make a table called products with columns: id, name, price, and quantity"
- "Show me all products that cost more than 50 dollars"
- "Update the price of product with id 1 to 29.99"
- "Delete all products with quantity less than 5"

## How It Works

The assistant uses Google's Gemini AI model to convert natural language queries into SQL commands. Each command is analyzed for safety and confirmed before execution on the MySQL database.

## Requirements

- Python 3.6 or higher
- MySQL Server
- Google Gemini AI API key
- Modern web browser

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Documentation

For detailed documentation, please see the [THESIS.md](THESIS.md) file. 