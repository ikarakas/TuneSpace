#!/usr/bin/env python3
"""
Enterprise Data Preparation Pipeline for LLM Fine-tuning
This script demonstrates how to convert enterprise data into training format
"""

import json
import csv
import pandas as pd
from typing import List, Dict, Any
import re
from pathlib import Path

class EnterpriseDataProcessor:
    """Process various enterprise data sources for LLM fine-tuning"""
    
    def __init__(self):
        self.processed_data = []
    
    def process_support_tickets(self, tickets_csv: str) -> List[Dict]:
        """
        Convert support tickets to instruction-following format
        Expected CSV columns: ticket_id, subject, description, resolution, category
        """
        df = pd.read_csv(tickets_csv)
        processed = []
        
        for _, row in df.iterrows():
            # Skip tickets without resolutions
            if pd.isna(row['resolution']) or not row['resolution'].strip():
                continue
                
            instruction = f"Help resolve this {row['category']} issue: {row['subject']}"
            input_text = row['description']
            output_text = row['resolution']
            
            processed.append({
                "instruction": instruction,
                "input": input_text,
                "output": output_text,
                "source": "support_tickets",
                "category": row['category']
            })
        
        return processed
    
    def process_documentation(self, docs_folder: str) -> List[Dict]:
        """
        Convert documentation files to Q&A format
        Assumes markdown files with headers and content
        """
        processed = []
        docs_path = Path(docs_folder)
        
        for doc_file in docs_path.glob("*.md"):
            with open(doc_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split by headers (# or ##)
            sections = re.split(r'\n#+\s', content)
            
            for section in sections[1:]:  # Skip first empty section
                lines = section.split('\n', 1)
                if len(lines) >= 2:
                    title = lines[0].strip()
                    content = lines[1].strip()
                    
                    if content:
                        processed.append({
                            "instruction": f"Explain: {title}",
                            "input": "",
                            "output": content,
                            "source": "documentation",
                            "document": doc_file.name
                        })
        
        return processed
    
    def process_faq_data(self, faq_json: str) -> List[Dict]:
        """
        Convert FAQ data to training format
        Expected JSON: [{"question": "...", "answer": "...", "category": "..."}]
        """
        with open(faq_json, 'r', encoding='utf-8') as f:
            faq_data = json.load(f)
        
        processed = []
        for item in faq_data:
            processed.append({
                "instruction": item['question'],
                "input": "",
                "output": item['answer'],
                "source": "faq",
                "category": item.get('category', 'general')
            })
        
        return processed
    
    def process_chat_logs(self, chat_csv: str) -> List[Dict]:
        """
        Convert customer chat logs to conversational format
        Expected CSV: conversation_id, timestamp, role, message
        """
        df = pd.read_csv(chat_csv)
        conversations = {}
        
        # Group by conversation
        for _, row in df.iterrows():
            conv_id = row['conversation_id']
            if conv_id not in conversations:
                conversations[conv_id] = []
            
            conversations[conv_id].append({
                "role": "user" if row['role'] == 'customer' else "assistant",
                "content": row['message'],
                "timestamp": row['timestamp']
            })
        
        processed = []
        for conv_id, messages in conversations.items():
            # Sort by timestamp
            messages.sort(key=lambda x: x['timestamp'])
            
            # Create instruction-response pairs
            for i in range(0, len(messages)-1, 2):
                if i+1 < len(messages) and messages[i]['role'] == 'user':
                    processed.append({
                        "instruction": messages[i]['content'],
                        "input": "",
                        "output": messages[i+1]['content'],
                        "source": "chat_logs",
                        "conversation_id": conv_id
                    })
        
        return processed
    
    def clean_and_filter_data(self, data: List[Dict]) -> List[Dict]:
        """Clean and filter training data"""
        cleaned = []
        
        for item in data:
            # Skip items with very short responses
            if len(item['output'].strip()) < 10:
                continue
            
            # Skip items with very long inputs/outputs (adjust as needed)
            if len(item['instruction']) > 500 or len(item['output']) > 2000:
                continue
            
            # Clean text
            item['instruction'] = self._clean_text(item['instruction'])
            item['input'] = self._clean_text(item['input'])
            item['output'] = self._clean_text(item['output'])
            
            # Skip if cleaning removed too much content
            if len(item['output'].strip()) < 10:
                continue
                
            cleaned.append(item)
        
        return cleaned
    
    def _clean_text(self, text: str) -> str:
        """Clean text content"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove email addresses and phone numbers (privacy)
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
        text = re.sub(r'\b\d{3}-\d{3}-\d{4}\b', '[PHONE]', text)
        
        # Remove excessive punctuation
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        
        return text.strip()
    
    def create_training_dataset(self, output_file: str, test_split: float = 0.1):
        """Create final training dataset with train/test split"""
        if not self.processed_data:
            raise ValueError("No processed data available. Process some data sources first.")
        
        # Shuffle data
        import random
        random.shuffle(self.processed_data)
        
        # Split train/test
        split_idx = int(len(self.processed_data) * (1 - test_split))
        train_data = self.processed_data[:split_idx]
        test_data = self.processed_data[split_idx:]
        
        # Save training data
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(train_data, f, ensure_ascii=False, indent=2)
        
        # Save test data
        test_file = output_file.replace('.json', '_test.json')
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        print(f"Training dataset: {len(train_data)} examples -> {output_file}")
        print(f"Test dataset: {len(test_data)} examples -> {test_file}")
        
        return train_data, test_data

# Example usage
def main():
    processor = EnterpriseDataProcessor()
    
    # Process different data sources
    # processor.processed_data.extend(processor.process_support_tickets('support_tickets.csv'))
    # processor.processed_data.extend(processor.process_documentation('docs/'))
    # processor.processed_data.extend(processor.process_faq_data('faq.json'))
    # processor.processed_data.extend(processor.process_chat_logs('chat_logs.csv'))
    
    # Clean and filter
    # processor.processed_data = processor.clean_and_filter_data(processor.processed_data)
    
    # Create final dataset
    # processor.create_training_dataset('enterprise_training_data.json')
    
    print("Data preparation script ready!")
    print("Uncomment and modify the data processing calls in main() function")

if __name__ == "__main__":
    main()