import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

def generate_sql(user_question: str, schema_description: str) -> str:
    """Generate SQL query based on natural language user question and 
    database schema description using the recommended Gemini Chats API."""

    system_message = """You are an expert SQL assistant. Your job is to translate natural language questions 
        into syntactically correct SQL queries based on the provided database schema. 
        Return ONLY the raw executable SQL query string, with no markdown code blocks 
        (do not include ```sql or ```), no explanations, no text before, and no text after."""
    
    prompt = f"""
    Schema Description:
    {schema_description}

    User Question:
    {user_question}
    """

    # Initializes client using environment variable GEMINI_API_KEY
    client = genai.Client()

    # Create a chat session to avoid the generate_content SDK architectural warning
    chat = client.chats.create(
        model="gemini-3.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=system_message,
            temperature=0.0
        )
    )
    
    response = chat.send_message(prompt)
    return response.text.strip()

# --- Example Usage ---
if __name__ == "__main__":
    db_schema = """
    Table: customers
      - customer_id (INT, PRIMARY KEY)
      - name (VARCHAR)
      - sign_up_date (DATE)

    Table: orders
      - order_id (INT, PRIMARY KEY)
      - customer_id (INT, FOREIGN KEY -> customers.customer_id)
      - total_amount (DECIMAL)
      - status (VARCHAR)
    """

    question = "Show me the total amount spent by each customer name for completed orders"
    
    if not os.getenv("GEMINI_API_KEY"):
        print("Error: Please set your GEMINI_API_KEY environment variable first.")
    else:
        sql_output = generate_sql(question, db_schema)
        print(sql_output)
