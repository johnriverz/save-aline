import PyPDF2
import json
from pathlib import Path
from typing import List, Dict
import openai
from api_key_manager import get_openai_api_key

class PDFProcessor:
    """
    Processes PDF files and extracts content using AI
    """
    
    def __init__(self):
        api_key = get_openai_api_key()
        self.client = openai.OpenAI(api_key=api_key)
    
    def process_pdf(self, pdf_path: str, title: str, max_chunks: int = 5) -> List[Dict]:
        """Process PDF and return structured content chunks"""
        
        print(f"📖 Processing PDF: {title}")
        
        # Extract text from PDF
        text_content = self._extract_pdf_text(pdf_path)
        
        if not text_content:
            print(f"❌ No text extracted from {pdf_path}")
            return []
        
        # Split into chunks (roughly by pages or sections)
        chunks = self._split_into_chunks(text_content, max_chunks)
        
        print(f"📄 Split into {len(chunks)} chunks")
        
        # Process each chunk with AI
        items = []
        for i, chunk in enumerate(chunks):
            print(f"🤖 Processing chunk {i+1}/{len(chunks)}...")
            
            try:
                item = self._ai_extract_pdf_chunk(chunk, title, i+1)
                if item:
                    items.append(item)
            except Exception as e:
                print(f"❌ Error processing chunk {i+1}: {e}")
                continue
        
        return items
    
    def _extract_pdf_text(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                # Extract text from all pages
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                return text.strip()
                
        except Exception as e:
            print(f"❌ Error reading PDF {pdf_path}: {e}")
            return ""
    
    def _split_into_chunks(self, text: str, max_chunks: int) -> List[str]:
        """Split text into manageable chunks"""
        
        # Try to split by chapters first
        if "Chapter" in text or "CHAPTER" in text:
            # Split by chapters
            import re
            chapters = re.split(r'Chapter \d+|CHAPTER \d+', text, flags=re.IGNORECASE)
            chunks = [chunk.strip() for chunk in chapters if chunk.strip()]
        else:
            # Split by approximate word count (2000 words per chunk)
            words = text.split()
            chunk_size = len(words) // max_chunks if len(words) > max_chunks * 1000 else 2000
            
            chunks = []
            for i in range(0, len(words), chunk_size):
                chunk = " ".join(words[i:i + chunk_size])
                if chunk.strip():
                    chunks.append(chunk.strip())
        
        # Limit to max_chunks
        return chunks[:max_chunks]
    
    def _ai_extract_pdf_chunk(self, chunk_text: str, book_title: str, chunk_num: int) -> Dict:
        """Use AI to extract structured data from PDF chunk"""
        
        system_prompt = """You are a technical content analyzer. Extract structured data from book chapters and technical content.

Always return valid JSON with these exact fields:
{
  "title": "string - descriptive title for this section/chapter",
  "content": "string - the key content in markdown format, including important concepts, code examples, and explanations",
  "content_type": "book",
  "author": "string - book author or 'Unknown'",
  "key_concepts": ["array", "of", "key", "technical", "concepts"],
  "code_snippets": ["array", "of", "important", "code", "examples"],
  "chapter_section": "string - chapter or section identifier"
}

Focus on extracting technical knowledge, algorithms, coding concepts, and educational content."""

        user_prompt = f"""Extract metadata and key content from this book section:

<BOOK_TITLE>
{book_title}
</BOOK_TITLE>

<SECTION_NUMBER>
Section {chunk_num}
</SECTION_NUMBER>

<CONTENT>
{chunk_text[:6000]}
</CONTENT>"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0,
                max_tokens=2000
            )
            
            extracted = json.loads(response.choices[0].message.content)
            
            # Format to match required output structure
            return {
                "title": extracted.get("title", f"{book_title} - Section {chunk_num}"),
                "content": extracted.get("content", chunk_text[:1000]),
                "content_type": "book",
                "source_url": "",  # No URL for PDFs
                "author": extracted.get("author", "Aline"),
                "user_id": ""
            }
            
        except Exception as e:
            print(f"❌ AI extraction error for chunk {chunk_num}: {e}")
            # Fallback: return basic structure
            return {
                "title": f"{book_title} - Section {chunk_num}",
                "content": chunk_text[:1000],
                "content_type": "book",
                "source_url": "",
                "author": "Aline",
                "user_id": ""
            } 