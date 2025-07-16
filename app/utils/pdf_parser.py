import PyPDF2
import re
from datetime import datetime
from typing import List, Dict

class LinkedInPDFParser:
    def __init__(self):
        self.date_patterns = [
            r'\d{1,2}\.\d{1,2}\.\d{4}',
            r'\d{4}-\d{2}-\d{2}',
        ]
        self.hashtag_pattern = r'#\w+'
        self.engagement_pattern = r'(\d+)\s+(Likes?|Kommentare?|Comments?)'
    
    def parse_pdf(self, pdf_path: str) -> List[Dict]:
        """Parse LinkedIn PDF and extract posts"""
        posts = []
        
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                full_text = ""
                
                # Limit to first 50 pages to prevent timeout
                max_pages = min(len(reader.pages), 50)
                
                for i in range(max_pages):
                    try:
                        page_text = reader.pages[i].extract_text()
                        full_text += page_text + "\n"
                        
                        # Stop if we've extracted enough text (>100KB)
                        if len(full_text) > 100000:
                            break
                            
                    except Exception as e:
                        # Skip problematic pages
                        continue
            
            # If no text was extracted, create a sample post
            if not full_text.strip():
                return [{
                    'title': 'PDF Import Test',
                    'content': 'Dies ist ein Test-Post aus der importierten PDF-Datei. Der Textinhalt konnte nicht automatisch extrahiert werden.',
                    'hashtags': '#linkedin #import',
                    'date': '',
                    'engagement': ''
                }]
            
            # Split into individual posts (customize based on LinkedIn PDF format)
            post_sections = self._split_into_posts(full_text)
            
            # Limit number of posts to prevent overwhelming the user
            max_posts = min(len(post_sections), 20)
            
            for i in range(max_posts):
                section = post_sections[i]
                post_data = {
                    'title': self._extract_title(section),
                    'content': self._extract_content(section),
                    'hashtags': self._extract_hashtags(section),
                    'date': self._extract_date(section),
                    'engagement': self._extract_engagement(section)
                }
                posts.append(post_data)
            
            # If no posts were found, create a sample post
            if not posts:
                posts.append({
                    'title': 'Importierter Content',
                    'content': full_text[:500] + '...' if len(full_text) > 500 else full_text,
                    'hashtags': '',
                    'date': '',
                    'engagement': ''
                })
            
            return posts
        except Exception as e:
            # Return a sample post if parsing fails
            return [{
                'title': 'PDF Import Fehler',
                'content': f'Die PDF-Datei konnte nicht vollständig verarbeitet werden. Fehler: {str(e)[:200]}...',
                'hashtags': '#import #error',
                'date': '',
                'engagement': ''
            }]
    
    def _split_into_posts(self, text: str) -> List[str]:
        """Split PDF text into individual posts"""
        # Simplified and fast implementation
        
        # Split by double line breaks first (most common separator)
        sections = text.split('\n\n')
        
        # Combine small sections and filter
        posts = []
        current_post = ""
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
                
            current_post += section + "\n\n"
            
            # If we have enough content (>200 chars) and it looks like a complete thought
            if len(current_post) > 200 and (section.endswith('.') or section.endswith('!') or section.endswith('?')):
                posts.append(current_post.strip())
                current_post = ""
                
                # Limit to prevent too many posts
                if len(posts) >= 20:
                    break
        
        # Add remaining content as a post if substantial
        if current_post.strip() and len(current_post.strip()) > 100:
            posts.append(current_post.strip())
        
        # If no posts found, split by paragraphs
        if not posts:
            paragraphs = [p.strip() for p in text.split('\n') if len(p.strip()) > 100]
            return paragraphs[:10]  # Limit to 10 paragraphs
        
        return posts
    
    def _extract_title(self, text: str) -> str:
        """Extract title from post text"""
        lines = text.split('\n')
        # Take the first non-empty line as title, truncate if too long
        for line in lines:
            line = line.strip()
            if line:
                return line[:100] + '...' if len(line) > 100 else line
        return "Untitled Post"
    
    def _extract_content(self, text: str) -> str:
        """Extract main content from post text"""
        # Remove metadata and extract the main post content
        lines = text.split('\n')
        content_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not self._is_metadata_line(line):
                content_lines.append(line)
        
        content = '\n'.join(content_lines)
        return content[:3000]  # Limit to max content length
    
    def _is_metadata_line(self, line: str) -> bool:
        """Check if line is metadata (dates, engagement stats, etc.)"""
        metadata_patterns = [
            r'^\d{1,2}\.\d{1,2}\.\d{4}',  # Date
            r'^\d+\s+(Likes?|Kommentare?|Comments?)',  # Engagement
            r'^(Veröffentlicht|Published|Posted)',  # Publication info
            r'^(Bearbeitet|Edited)',  # Edit info
        ]
        
        for pattern in metadata_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                return True
        return False
    
    def _extract_hashtags(self, text: str) -> str:
        """Extract hashtags from text"""
        hashtags = re.findall(self.hashtag_pattern, text)
        return ' '.join(hashtags)
    
    def _extract_date(self, text: str) -> str:
        """Extract date from text"""
        for pattern in self.date_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group()
        return ""
    
    def _extract_engagement(self, text: str) -> str:
        """Extract engagement statistics from text"""
        matches = re.findall(self.engagement_pattern, text, re.IGNORECASE)
        if matches:
            return ', '.join([f"{count} {metric}" for count, metric in matches])
        return ""