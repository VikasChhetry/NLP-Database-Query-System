from dotenv import load_dotenv
load_dotenv()

import os
import re
import mysql.connector
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify

# Configure Genai Key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class DatabaseChatbot:
    def __init__(self):
        self.initialize_database()
        self.prompt = self.create_prompt()
    
    def initialize_database(self):
        """Setup database connection and create initial database if needed"""
        try:
            # Connect without database to check/create database
            connection_params = {
                "host": os.getenv("MYSQL_HOST"),
                "user": os.getenv("MYSQL_USER"),
                "password": os.getenv("MYSQL_PASSWORD"),
            }
            
            conn = mysql.connector.connect(**connection_params)
            cursor = conn.cursor()
            
            # Get database name from env
            self.db_name = os.getenv("MYSQL_DATABASE", "nlp_assistant")
            
            # Create the database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_name}")
            print(f"Database '{self.db_name}' is ready.")
            
            conn.commit()
            conn.close()
            return True
        except mysql.connector.Error as e:
            print(f"Database initialization error: {e}")
            return False
    
    def connect_to_db(self, database=None):
        """Connect to MySQL, allowing database creation or selection"""
        connection_params = {
            "host": os.getenv("MYSQL_HOST"),
            "user": os.getenv("MYSQL_USER"),
            "password": os.getenv("MYSQL_PASSWORD"),
        }
        
        # Only add database parameter if it's specified
        if database:
            connection_params["database"] = database
        
        return mysql.connector.connect(**connection_params)
    
    def create_prompt(self):
        """Create the prompt for the AI model"""
        return [
            """
            You are a database expert who understands natural language queries and converts them to SQL.
            You help users create, modify, query, and manage MySQL databases without them needing to know SQL.
            
            RULES:
            1. Generate ONLY the SQL command without any explanation or markdown.
            2. Always end SQL statements with a semicolon.
            3. Only output the exact SQL command that should be executed.
            4. Remember to use proper SQL naming conventions.
            
            Examples:
            
            User: "Create a database called inventory"
            Output: CREATE DATABASE inventory;
            
            User: "Make a new table for products with columns for id, name, price and quantity"
            Output: CREATE TABLE products (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), price DECIMAL(10,2), quantity INT);
            
            User: "Show all entries in the customers table"
            Output: SELECT * FROM customers;
            
            User: "Add a new product called Laptop with price 999.99 and quantity 10"
            Output: INSERT INTO products (name, price, quantity) VALUES ('Laptop', 999.99, 10);
            
            User: "Update the price of Laptop to 899.99"
            Output: UPDATE products SET price = 899.99 WHERE name = 'Laptop';
            
            User: "Delete the product with id 5"
            Output: DELETE FROM products WHERE id = 5;
            
            User: "Show me a list of all databases"
            Output: SHOW DATABASES;
            
            User: "Show me all tables in the inventory database"
            Output: SHOW TABLES FROM inventory;
            
            User: "What's the structure of the products table?"
            Output: DESCRIBE products;
            """
        ]
    
    def generate_sql(self, user_query):
        """Convert natural language to SQL using Gemini"""
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content([self.prompt[0], user_query])
        return response.text.strip()
    
    def execute_sql(self, sql):
        """Execute SQL and return results"""
        try:
            # For CREATE DATABASE commands, connect without database
            if sql.strip().upper().startswith("CREATE DATABASE"):
                conn = self.connect_to_db(database=None)
            else:
                # For commands that use a specific database
                match = re.search(r'USE\s+(\w+)', sql, re.IGNORECASE)
                if match:
                    database = match.group(1)
                    conn = self.connect_to_db(database=database)
                else:
                    # Try to use the default database
                    conn = self.connect_to_db(database=self.db_name)
            
            cursor = conn.cursor()
            cursor.execute(sql)
            
            # Return results for SELECT queries
            if sql.strip().upper().startswith("SELECT") or sql.strip().upper().startswith("SHOW") or sql.strip().upper().startswith("DESCRIBE"):
                result = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]
                return {"success": True, "data": result, "columns": column_names, "message": "Query executed successfully"}
            else:
                # For non-SELECT queries
                conn.commit()
                return {"success": True, "message": f"Query executed successfully. Affected rows: {cursor.rowcount}"}
        
        except mysql.connector.Error as e:
            return {"success": False, "message": f"Error: {e}"}
        
        finally:
            if 'conn' in locals() and conn.is_connected():
                conn.close()
    
    def process_query(self, user_query):
        """Process a natural language query and generate the corresponding SQL"""
        sql = self.generate_sql(user_query)
        return sql

# Initialize Flask app
app = Flask(__name__)
chatbot = DatabaseChatbot()

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """Generate SQL from natural language"""
    user_query = request.json.get('query', '')
    if not user_query:
        return jsonify({"error": "No query provided"})
    
    sql = chatbot.process_query(user_query)
    return jsonify({"sql": sql})

@app.route('/execute', methods=['POST'])
def execute():
    """Execute SQL and return results"""
    sql = request.json.get('sql', '')
    if not sql:
        return jsonify({"error": "No SQL provided"})
    
    result = chatbot.execute_sql(sql)
    return jsonify(result)

if __name__ == '__main__':
    # Make sure templates folder exists
    os.makedirs('templates', exist_ok=True)
    app.run(debug=True) 