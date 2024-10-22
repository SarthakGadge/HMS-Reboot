from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import mysql.connector
import google.generativeai as genai
import os
from decouple import config
# Load Google Generative AI API key from environment variables for security
genai.configure(api_key=config("GOOGLE_GENAI_API_KEY"))

# Database configuration
db_config = {
    "host": config("HOST"),
    "user": config("USER"),
    "password": config("PASSWORD"),
    "database": config("DATABASE")
}

# Function to get the schema (tables and columns) from the database


def get_db_schema(host, user, password, database):
    try:
        mydb = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        cursor = mydb.cursor()

        # Fetch all table names
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()

        schema = {}
        for table in tables:
            table_name = table[0]
            # Fetch columns for each table
            cursor.execute(f"SHOW COLUMNS FROM {table_name};")
            columns = cursor.fetchall()
            schema[table_name] = [column[0] for column in columns]

        cursor.close()
        mydb.close()
        return schema
    except mysql.connector.Error as error:
        return f"Error retrieving database schema: {error}"

# Function to generate SQL query using Google Generative AI (Gemini) based on user input and schema


def get_gemini_response(question, schema):
    # Convert the schema to a string format that can be understood by the AI model
    schema_info = "\n".join(
        [f"Table: {table}, Columns: {', '.join(columns)}" for table, columns in schema.items()])

    prompt = f"""
    You are an expert data analyst specializing in SQL. The user will ask questions in English, and your task is to translate these into precise SQL queries.

    The database has the following schema:
    {schema_info}

    Please follow these guidelines:
    1. Only respond with the SQL query, starting with "```sql" and ending with "```".
    2. If a question requires assumptions, make logical assumptions based on typical database content.
    3. Respond with SQL queries that retrieve the data requested, without providing additional explanations.
    4. If the user query is unrelated to SQL or the database, politely inform them you can only assist with SQL queries.
    """

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([prompt, question])

    # Ensure response contains SQL query between ```sql and ```
    if "```sql" in response.text:
        return response.text.split("```sql")[1].split("```")[0].strip()
    return "Error generating SQL query."

# Function to execute the SQL query and fetch results along with column names from the database


def read_sql_query(sql, host, user, password, database):
    try:
        mydb = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        cursor = mydb.cursor()

        cursor.execute(sql)

        # Fetch column names
        column_names = [desc[0] for desc in cursor.description]

        # Fetch rows
        rows = cursor.fetchall()

        cursor.close()  # Close the cursor after fetching the results
        mydb.close()  # Close the database connection

        # Combine column names and rows into a list of dictionaries
        results = [dict(zip(column_names, row)) for row in rows]

        return {
            "data": results
        }
    except mysql.connector.Error as error:
        return f"Error executing SQL query: {error}"

# Main function to process the user's input and execute the resulting SQL query


def process_user_input(question, host, user, password, database):
    # Get the database schema dynamically
    schema = get_db_schema(host, user, password, database)
    if isinstance(schema, str) and "Error" in schema:
        return schema  # If schema retrieval failed, return error message

    sql_query = get_gemini_response(question, schema)
    if "Error" in sql_query:
        return sql_query  # Return error if query generation failed

    return read_sql_query(sql_query, host, user, password, database)

# Create an API endpoint to accept queries


@api_view(['POST'])
def execute_query(request):
    # Get user query from the request data (assuming it's in JSON format)
    user_query = request.data.get('query', None)

    if not user_query:
        return Response({"error": "Query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Process the user input and get the results
    result = process_user_input(user_query, **db_config)

    if isinstance(result, str) and "Error" in result:
        return Response({"error": result}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({"result": result}, status=status.HTTP_200_OK)

# @api_view(['POST'])
# def chatbot(request):
#     user_query = request.data.get('query')

#     if user_query:
#         try:
#             # Communicate with OpenAI using the chat model (gpt-3.5-turbo)
#             response = openai.ChatCompletion.create(
#                 model="gpt-3.5-turbo",  # Use gpt-3.5-turbo or gpt-4
#                 messages=[
#                     {"role": "system", "content": "You are a helpful assistant for a hostel management system."},
#                     {"role": "user", "content": user_query},
#                 ],
#                 max_tokens=150,
#                 temperature=0.7,
#                 top_p=1,
#                 frequency_penalty=0.0,
#                 presence_penalty=0.6,
#             )
#             # Extract the chatbot's response from the API's return format
#             bot_response = response['choices'][0]['message']['content'].strip()
#             return Response({"response": bot_response}, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#     else:
#         return Response({"error": "No query provided"}, status=status.HTTP_400_BAD_REQUEST)
