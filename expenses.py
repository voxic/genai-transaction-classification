import csv
import json
from openai import OpenAI
from pymongo import MongoClient

# MongoDB Atlas connection details
atlas_uri = "mongodb+srv://XXXX:XXX@XXXX.mongodb.net/"
database_name = "expenses"  # Replace with your database name
# Replace with your transactions collection name
transactions_collection_name = "transactions"
# Collection for business to category mapping
category_collection_name = "category"
# Replace with your actual API key
api_key = ''
chunk_size = 10  # Number of rows to process at a time

# Validation function


def is_valid_transaction(transaction):
    required_keys = [
        "booking_date", "amount", "sender_account", "receiver_account",
        "name", "title", "balance", "currency", "category", "sub_category", "business"
    ]
    return all(key in transaction for key in required_keys)


def process_csv_chunks(csv_file_path):
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        chunk = []
        for row in reader:
            if row and not row[0].startswith("Bokföringsdag"):
                chunk.append(row)
                if len(chunk) == chunk_size:
                    yield chunk
                    chunk = []
        if chunk:
            yield chunk


def extract_mapping(data):
    mapping = {}
    for transaction in data:
        business = transaction.get('business', None)
        category = transaction.get('category', None)
        sub_category = transaction.get('sub_category', None)

        if business and category and sub_category:
            mapping[business] = {'category': category,
                                 'sub_category': sub_category}

    return mapping


def write_mapping_to_mongo(mapping, uri, db_name, collection_name):
    client = MongoClient(uri)
    db = client[db_name]
    collection = db[collection_name]

    for business, categories in mapping.items():
        document = {'business': business, **categories}
        collection.insert_one(document)


def parse_csv_with_openai(chunk):
    prompt = "\n".join([" ".join(row) for row in chunk])
    content = """
"You are a helpful assistant designed to parse CSV banking transactions and output them in a structured JSON format. Categorize the transactions with categories, sub-categories, and specific businesses. Use this as a template:             {
                booking_date: Reserved,
                amount: -387.33,
                sender_account: 1104 21 28286,
                receiver_account: ,
                name: ,
                title: Reservation,
                balance: ,
                currency: SEK,
                category: Shopping,
                sub_category: Groceries,
                business: HEMKOP TULLINGE
            }"
"""
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": content},
            {"role": "user", "content": prompt}
        ]
    )

    return json.loads(response.choices[0].message.content)


def write_to_mongo(data, uri, db_name, collection_name):
    client = MongoClient(uri)
    db = client[db_name]
    collection = db[collection_name]

    valid_transactions = [t for t in data if is_valid_transaction(t)]
    if valid_transactions:
        collection.insert_many(valid_transactions)


def process_and_save_to_json(csv_file_path, output_file_path):
    all_parsed_content = []
    for i, chunk in enumerate(process_csv_chunks(csv_file_path), start=1):
        parsed_content = parse_csv_with_openai(chunk)
        all_parsed_content.extend(parsed_content.get('transactions', []))
        print(f"Processed chunk {i}...")

    with open(output_file_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(all_parsed_content, jsonfile, ensure_ascii=False, indent=4)

    print(f"Output saved to {output_file_path}")

    # Extracting mapping and writing to MongoDB
    business_mapping = extract_mapping(all_parsed_content)
    write_mapping_to_mongo(business_mapping, atlas_uri,
                           database_name, category_collection_name)

    # Writing transaction data to MongoDB
    write_to_mongo(all_parsed_content, atlas_uri,
                   database_name, transactions_collection_name)
    print("Data written to MongoDB Atlas.")


csv_file_path = 'input.csv'
output_file_path = 'output.json'

process_and_save_to_json(csv_file_path, output_file_path)
