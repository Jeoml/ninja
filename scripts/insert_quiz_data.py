#!/usr/bin/env python3
"""
Script to insert quiz data from data.csv into PostgreSQL database.
Creates the table if it doesn't exist and inserts all quiz questions.
"""

import csv
import psycopg2
from psycopg2.extras import RealDictCursor
import sys
import os

# Database connection string
DATABASE_URL = "postgresql://neondb_owner:npg_gbCZGkeq8f7W@ep-small-forest-ad89jah2-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def create_table(cursor):
    """Create the quiz_questions table if it doesn't exist."""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS quiz_questions (
        id SERIAL PRIMARY KEY,
        question TEXT NOT NULL,
        option_a TEXT NOT NULL,
        option_b TEXT NOT NULL,
        option_c TEXT NOT NULL,
        option_d TEXT NOT NULL,
        answer TEXT NOT NULL,
        difficulty VARCHAR(10) NOT NULL CHECK (difficulty IN ('easy', 'medium', 'hard')),
        topic VARCHAR(50) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    cursor.execute(create_table_sql)
    print("✅ Table 'quiz_questions' created or verified successfully")

def clean_text(text):
    """Clean text data by removing extra quotes and handling special characters."""
    if text is None:
        return ""
    
    # Remove surrounding quotes if they exist
    text = text.strip()
    if text.startswith('"') and text.endswith('"'):
        text = text[1:-1]
    
    # Replace double quotes with single quotes inside the text
    text = text.replace('""', '"')
    
    return text

def insert_quiz_data(cursor, csv_file_path):
    """Read CSV file and insert data into the database."""
    
    insert_sql = """
    INSERT INTO quiz_questions (question, option_a, option_b, option_c, option_d, answer, difficulty, topic)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    inserted_count = 0
    skipped_count = 0
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 because row 1 is header
                try:
                    # Clean all text fields
                    question = clean_text(row['question'])
                    option_a = clean_text(row['option_a'])
                    option_b = clean_text(row['option_b'])
                    option_c = clean_text(row['option_c'])
                    option_d = clean_text(row['option_d'])
                    answer = clean_text(row['answer'])
                    difficulty = clean_text(row['difficulty']).lower()
                    topic = clean_text(row['topic'])
                    
                    # Skip rows with invalid data (like error placeholders)
                    if any('#' in field for field in [question, option_a, option_b, option_c, option_d, answer]):
                        print(f"⚠️  Skipping row {row_num}: Contains error placeholders")
                        skipped_count += 1
                        continue
                    
                    # Validate difficulty
                    if difficulty not in ['easy', 'medium', 'hard']:
                        print(f"⚠️  Skipping row {row_num}: Invalid difficulty '{difficulty}'")
                        skipped_count += 1
                        continue
                    
                    # Skip empty questions
                    if not question.strip():
                        print(f"⚠️  Skipping row {row_num}: Empty question")
                        skipped_count += 1
                        continue
                    
                    # Insert the row
                    cursor.execute(insert_sql, (
                        question, option_a, option_b, option_c, option_d, 
                        answer, difficulty, topic
                    ))
                    
                    inserted_count += 1
                    
                    if inserted_count % 10 == 0:
                        print(f"📝 Inserted {inserted_count} questions...")
                
                except Exception as e:
                    print(f"❌ Error processing row {row_num}: {str(e)}")
                    skipped_count += 1
                    continue
    
    except FileNotFoundError:
        print(f"❌ Error: Could not find file '{csv_file_path}'")
        return False
    except Exception as e:
        print(f"❌ Error reading CSV file: {str(e)}")
        return False
    
    print(f"\n✅ Data insertion completed!")
    print(f"   📊 Successfully inserted: {inserted_count} questions")
    print(f"   ⚠️  Skipped: {skipped_count} rows")
    
    return True

def verify_data(cursor):
    """Verify the inserted data by showing some statistics."""
    
    # Count total records
    cursor.execute("SELECT COUNT(*) as total FROM quiz_questions")
    total = cursor.fetchone()['total']
    
    # Count by difficulty
    cursor.execute("""
        SELECT difficulty, COUNT(*) as count 
        FROM quiz_questions 
        GROUP BY difficulty 
        ORDER BY difficulty
    """)
    difficulty_counts = cursor.fetchall()
    
    # Count by topic
    cursor.execute("""
        SELECT topic, COUNT(*) as count 
        FROM quiz_questions 
        GROUP BY topic 
        ORDER BY count DESC 
        LIMIT 10
    """)
    topic_counts = cursor.fetchall()
    
    print(f"\n📊 Database Statistics:")
    print(f"   Total Questions: {total}")
    
    print(f"\n   By Difficulty:")
    for row in difficulty_counts:
        print(f"     {row['difficulty'].capitalize()}: {row['count']}")
    
    print(f"\n   Top Topics:")
    for row in topic_counts:
        print(f"     {row['topic']}: {row['count']}")

def main():
    """Main function to execute the data insertion process."""
    
    print("🚀 Starting quiz data insertion process...")
    
    # Check if CSV file exists
    csv_file = "data.csv"
    if not os.path.exists(csv_file):
        print(f"❌ Error: CSV file '{csv_file}' not found in current directory")
        sys.exit(1)
    
    try:
        # Connect to database
        print("🔌 Connecting to PostgreSQL database...")
        connection = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        connection.autocommit = True
        
        with connection.cursor() as cursor:
            # Create table
            create_table(cursor)
            
            # Clear existing data (optional - comment out if you want to keep existing data)
            cursor.execute("DELETE FROM quiz_questions")
            print("🧹 Cleared existing data from quiz_questions table")
            
            # Insert new data
            print(f"📂 Reading data from '{csv_file}'...")
            success = insert_quiz_data(cursor, csv_file)
            
            if success:
                # Verify the insertion
                verify_data(cursor)
                print("\n🎉 All done! Quiz data has been successfully inserted into the database.")
            else:
                print("\n❌ Data insertion failed!")
                sys.exit(1)
    
    except psycopg2.Error as e:
        print(f"❌ Database error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        sys.exit(1)
    finally:
        if 'connection' in locals():
            connection.close()
            print("🔌 Database connection closed")

if __name__ == "__main__":
    main()
