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
                
                for page in reader.pages:
                    full_text += page.extract_text()
            
            # Split into individual posts (customize based on LinkedIn PDF format)
            post_sections = self._split_into_posts(full_text)
            
            for section in post_sections:
                post_data = {
                    'title': self._extract_title(section),
                    'content': self._extract_content(section),
                    'hashtags': self._extract_hashtags(section),
                    'date': self._extract_date(section),
                    'engagement': self._extract_engagement(section)
                }
                posts.append(post_data)
            
            return posts
        except Exception as e:
            raise Exception(f"Fehler beim Parsen der PDF: {str(e)}")
    
    def _split_into_posts(self, text: str) -> List[str]:
        """Split PDF text into individual posts"""
        # This is a simplified implementation - adjust based on LinkedIn's actual PDF format
        # Look for common separators or patterns that indicate post boundaries
        
        # Common patterns that might separate posts
        separators = [
            r'\n\n---\n\n',  # Horizontal line separator
            r'\n\n\d{1,2}\.\d{1,2}\.\d{4}',  # Date pattern
            r'\nPost \d+',  # Post numbering
            r'\n\n[A-Z][a-z]+\s+\d{1,2},\s+\d{4}',  # Date in text format
        ]
        
        # Try to split by common separators
        sections = [text]
        for separator in separators:
            new_sections = []
            for section in sections:
                new_sections.extend(re.split(separator, section))
            sections = new_sections
        
        # Filter out empty sections and very short ones
        return [section.strip() for section in sections if len(section.strip()) > 50]
    
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