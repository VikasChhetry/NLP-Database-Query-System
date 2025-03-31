@echo off
echo Installing required packages...
python -m pip install flask google-generativeai python-dotenv mysql-connector-python
echo.
echo Starting Database NLP Web Assistant...
echo.
echo Open your browser and navigate to http://localhost:5000
python nlp_db_web.py
pause 