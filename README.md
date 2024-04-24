
# Financial Transactions Processor

## Overview
This Python script processes financial transactions from a CSV file, parses them into a structured JSON format, and stores the data in MongoDB. It uses OpenAI's GPT model to help with parsing the transactions. The script handles large files by processing transactions in chunks.

## Features
- Processes transactions from CSV in chunks.
- Parses transactions using OpenAI's GPT model.
- Validates the structure of transactions.
- Saves parsed data into JSON.
- Stores data in MongoDB Atlas.

## Requirements
- Python packages: `csv`, `json`, `pymongo`, `openai`
- MongoDB Atlas account
- OpenAI API key

## Usage
1. Replace the MongoDB Atlas URI, database name, and collection names in the script.
2. Replace the OpenAI API key in the script.
3. Prepare your CSV file with transactions.
4. Run the script by updating the `csv_file_path` and `output_file_path`.

## Configuration
- `csv_file_path`: Path to the input CSV file.
- `output_file_path`: Path to save the output JSON file.
- `atlas_uri`: MongoDB Atlas connection URI.
- `database_name`: Name of the MongoDB database.
- `transactions_collection_name`: Name of the MongoDB collection for transactions.
- `category_collection_name`: Name of the MongoDB collection for business to category mapping.
- `api_key`: Your OpenAI API key.
- `chunk_size`: Number of rows to process at a time (default is 10).

## Function Descriptions
- `is_valid_transaction`: Checks if a transaction has all required keys.
- `process_csv_chunks`: Generator to read and yield chunks of transactions from a CSV file.
- `extract_mapping`: Extracts business to category mapping from transaction data.
- `write_mapping_to_mongo`: Writes business to category mappings to MongoDB.
- `parse_csv_with_openai`: Uses OpenAI GPT to parse CSV transactions.
- `write_to_mongo`: Writes validated transaction data to MongoDB.
- `process_and_save_to_json`: Processes CSV file, parses, and saves output to JSON and MongoDB.

