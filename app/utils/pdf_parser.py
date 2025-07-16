import PyPDF2
import re
from datetime import datetime
from typing import List, Dict
from .linkedin_pdf_parser import LinkedInSpecificParser

class LinkedInPDFParser:
    def __init__(self):
        self.date_patterns = [
            r'\d{1,2}\.\d{1,2}\.\d{4}',
            r'\d{4}-\d{2}-\d{2}',
        ]
        self.hashtag_pattern = r'#\w+'
        self.engagement_pattern = r'(\d+)\s+(Likes?|Kommentare?|Comments?)'
    
    def parse_pdf(self, pdf_path: str) -> List[Dict]:
        """Parse LinkedIn PDF using enhanced LinkedIn-specific parser"""
        try:
            # Use the new LinkedIn-specific parser
            linkedin_parser = LinkedInSpecificParser()
            posts = linkedin_parser.parse_pdf(pdf_path)
            
            # Convert to legacy format for compatibility
            legacy_posts = []
            for post in posts:
                legacy_post = {
                    'title': post.get('title', 'LinkedIn Post'),
                    'content': post.get('content', ''),
                    'hashtags': post.get('hashtags', ''),
                    'date': post.get('date', ''),
                    'engagement': post.get('engagement', '')
                }
                
                # Add additional metadata as notes if available
                notes_parts = []
                if post.get('author'):
                    notes_parts.append(f"Autor: {post['author']}")
                if post.get('company'):
                    notes_parts.append(f"Unternehmen: {post['company']}")
                if post.get('followers'):
                    notes_parts.append(f"Follower: {post['followers']}")
                if post.get('timestamp'):
                    notes_parts.append(f"Zeitstempel: {post['timestamp']}")
                
                if notes_parts:
                    legacy_post['notes'] = ' | '.join(notes_parts)
                
                legacy_posts.append(legacy_post)
            
            return legacy_posts if legacy_posts else self._create_fallback_posts()
            
        except Exception as e:
            # Fallback to original parsing if new parser fails
            return self._fallback_parse(pdf_path, str(e))
    
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
    
    def _create_fallback_posts(self) -> List[Dict]:
        """Create fallback posts when no content is extracted"""
        return [{
            'title': 'PDF Import Test',
            'content': 'Dies ist ein Test-Post aus der importierten PDF-Datei. Der Textinhalt konnte nicht automatisch extrahiert werden.',
            'hashtags': '#linkedin #import',
            'date': '',
            'engagement': '',
            'notes': 'Automatisch generierter Test-Post'
        }]
    
    def _fallback_parse(self, pdf_path: str, error_msg: str) -> List[Dict]:
        """Fallback to basic parsing if enhanced parser fails"""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                full_text = ""
                
                for i, page in enumerate(reader.pages[:5]):  # Limit to 5 pages for fallback
                    try:
                        page_text = page.extract_text()
                        full_text += page_text + "\n"
                    except:
                        continue
                
                if full_text.strip():
                    return [{
                        'title': 'Importierter Content (Fallback)',
                        'content': full_text[:1000] + '...' if len(full_text) > 1000 else full_text,
                        'hashtags': '',
                        'date': '',
                        'engagement': '',
                        'notes': f'Fallback-Parser verwendet. Fehler: {error_msg}'
                    }]
                else:
                    return self._create_fallback_posts()
                    
        except Exception as fallback_error:
            return [{
                'title': 'PDF Import Fehler',
                'content': f'Die PDF-Datei konnte nicht verarbeitet werden. Ursprünglicher Fehler: {error_msg}. Fallback-Fehler: {str(fallback_error)}',
                'hashtags': '#import #error',
                'date': '',
                'engagement': '',
                'notes': 'Beide Parser fehlgeschlagen'
            }]
    
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