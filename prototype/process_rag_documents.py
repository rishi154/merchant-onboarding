#!/usr/bin/env python3
"""
RAG Document Processing Tool
Converts downloaded PDFs to searchable text chunks for RAG implementation
"""

import os
import json
from pathlib import Path
import hashlib
from datetime import datetime

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠ PyPDF2 not installed. Run: pip install PyPDF2")

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file"""
    if not PDF_AVAILABLE:
        return "PDF processing not available - install PyPDF2"
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
            
            return text.strip()
    
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""

def clean_text(text):
    """Clean extracted text for RAG processing"""
    # Remove excessive whitespace
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        if len(line) > 10:  # Skip very short lines (likely headers/footers)
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def create_text_chunks(text, chunk_size=800, overlap=100):
    """Create overlapping text chunks for RAG"""
    words = text.split()
    chunks = []
    
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = ' '.join(words[start:end])
        
        if len(chunk.strip()) > 50:  # Only keep substantial chunks
            chunks.append({
                'text': chunk,
                'start_word': start,
                'end_word': end,
                'word_count': end - start
            })
        
        start += (chunk_size - overlap)
        if end >= len(words):
            break
    
    return chunks

def process_document(file_path, category):
    """Process single document into RAG format"""
    
    file_name = Path(file_path).stem
    
    # Extract text
    if file_path.endswith('.pdf'):
        raw_text = extract_text_from_pdf(file_path)
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_text = f.read()
    
    if not raw_text:
        return None
    
    # Clean text
    cleaned_text = clean_text(raw_text)
    
    # Create chunks
    chunks = create_text_chunks(cleaned_text)
    
    # Create metadata
    metadata = {
        'source_file': file_name,
        'category': category,
        'processed_date': datetime.now().isoformat(),
        'total_chunks': len(chunks),
        'total_words': len(cleaned_text.split()),
        'file_hash': hashlib.md5(raw_text.encode()).hexdigest()
    }
    
    return {
        'metadata': metadata,
        'raw_text': raw_text,
        'cleaned_text': cleaned_text,
        'chunks': chunks
    }

def process_all_documents():
    """Process all downloaded documents"""
    
    base_path = Path("rag_documents")
    output_path = Path("rag_processed")
    output_path.mkdir(exist_ok=True)
    
    processing_summary = {
        'processed_date': datetime.now().isoformat(),
        'categories': {},
        'total_documents': 0,
        'total_chunks': 0
    }
    
    for category_dir in base_path.iterdir():
        if not category_dir.is_dir() or category_dir.name.startswith('.'):
            continue
        
        category = category_dir.name
        category_output = output_path / category
        category_output.mkdir(exist_ok=True)
        
        category_stats = {
            'documents': 0,
            'chunks': 0,
            'files': []
        }
        
        print(f"\n📁 Processing category: {category}")
        
        for file_path in category_dir.iterdir():
            if file_path.is_file() and file_path.suffix in ['.pdf', '.txt']:
                
                print(f"   Processing: {file_path.name}")
                
                processed = process_document(str(file_path), category)
                
                if processed:
                    # Save processed document
                    output_file = category_output / f"{file_path.stem}_processed.json"
                    
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(processed, f, indent=2, ensure_ascii=False)
                    
                    # Update stats
                    category_stats['documents'] += 1
                    category_stats['chunks'] += processed['metadata']['total_chunks']
                    category_stats['files'].append({
                        'name': file_path.name,
                        'chunks': processed['metadata']['total_chunks'],
                        'words': processed['metadata']['total_words']
                    })
                    
                    print(f"   ✓ Created {processed['metadata']['total_chunks']} chunks")
                else:
                    print(f"   ✗ Failed to process {file_path.name}")
        
        processing_summary['categories'][category] = category_stats
        processing_summary['total_documents'] += category_stats['documents']
        processing_summary['total_chunks'] += category_stats['chunks']
    
    # Save processing summary
    with open(output_path / "processing_summary.json", 'w') as f:
        json.dump(processing_summary, f, indent=2)
    
    print(f"\n📊 Processing Summary:")
    print(f"   Total documents processed: {processing_summary['total_documents']}")
    print(f"   Total chunks created: {processing_summary['total_chunks']}")
    print(f"   Output directory: {output_path}")

def create_rag_index():
    """Create simple RAG index for testing"""
    
    processed_path = Path("rag_processed")
    index_data = []
    
    for category_dir in processed_path.iterdir():
        if not category_dir.is_dir():
            continue
        
        for json_file in category_dir.glob("*.json"):
            if json_file.name == "processing_summary.json":
                continue
            
            with open(json_file, 'r', encoding='utf-8') as f:
                doc_data = json.load(f)
            
            for i, chunk in enumerate(doc_data['chunks']):
                index_entry = {
                    'id': f"{doc_data['metadata']['source_file']}_{i}",
                    'text': chunk['text'],
                    'metadata': {
                        'source': doc_data['metadata']['source_file'],
                        'category': doc_data['metadata']['category'],
                        'chunk_index': i,
                        'word_count': chunk['word_count']
                    }
                }
                index_data.append(index_entry)
    
    # Save RAG index
    with open("rag_index.json", 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Created RAG index with {len(index_data)} chunks")

if __name__ == "__main__":
    print("🔄 RAG Document Processing Tool")
    print("=" * 50)
    
    # Check if documents exist
    if not Path("rag_documents").exists():
        print("❌ No rag_documents directory found!")
        print("   Run download_rag_documents.py first")
        exit(1)
    
    # Process all documents
    process_all_documents()
    
    # Create RAG index
    create_rag_index()
    
    print("\n✅ RAG processing complete!")
    print("📁 Processed files in: rag_processed/")
    print("📋 RAG index created: rag_index.json")