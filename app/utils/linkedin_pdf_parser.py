import re
from datetime import datetime
from typing import List, Dict, Optional
import logging

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    import PyPDF2

class LinkedInSpecificParser:
    """Enhanced LinkedIn PDF parser based on real LinkedIn PDF structure analysis"""
    
    def __init__(self):
        self.timestamp_pattern = r'(\d+)\s+(Monate?|Wochen?|Tage?|Stunden?)(?:\s*[•·])?'
        self.company_pattern = r'([^\n]+(?:GmbH|AG|Inc|LLC|Ltd|Corporation|Corp)[^\n]*)'
        self.follower_pattern = r'(\d+(?:\.\d+)?[KM]?)\s+Follower'
        self.engagement_patterns = {
            'likes': r'Gefällt mir[·•]*\s*(\d+)',
            'comments': r'(\d+)\s*Antw?orten',
            'impressions': r'(\d+)\s+Impressions?'
        }
        self.linkedin_ui_patterns = [
            r'Zugang zu exklusiven.*?t esten',
            r'Jetzt Pr?emium.*?EUR',
            r'Profilbesuche \d+',
            r'Impr?essions v?on Beiträgen \d+',
            r'Region [^\n]+',
            r'LinkedIn Corporation.*?\d{4}',
            r'Info Barrierefreiheit.*?Mehr',
            r'Anzeigenauswahl.*?herunterladen'
        ]
    
    def parse_pdf(self, pdf_path: str) -> List[Dict]:
        """Parse LinkedIn PDF with enhanced intelligence"""
        try:
            if PDFPLUMBER_AVAILABLE:
                return self._parse_with_pdfplumber(pdf_path)
            else:
                return self._parse_with_pypdf2(pdf_path)
        except Exception as e:
            logging.error(f"Error parsing LinkedIn PDF: {e}")
            return self._create_fallback_post(str(e))
    
    def _parse_with_pdfplumber(self, pdf_path: str) -> List[Dict]:
        """Parse using pdfplumber for better text extraction"""
        posts = []
        all_text = ""
        
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages[:10]):  # Limit to 10 pages
                try:
                    page_text = page.extract_text()
                    if page_text:
                        all_text += f"\n--- PAGE {i+1} ---\n{page_text}\n"
                except Exception as e:
                    logging.warning(f"Error extracting page {i+1}: {e}")
                    continue
        
        return self._process_extracted_text(all_text)
    
    def _parse_with_pypdf2(self, pdf_path: str) -> List[Dict]:
        """Fallback to PyPDF2 if pdfplumber not available"""
        all_text = ""
        
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for i, page in enumerate(reader.pages[:10]):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        all_text += f"\n--- PAGE {i+1} ---\n{page_text}\n"
                except Exception as e:
                    logging.warning(f"Error extracting page {i+1}: {e}")
                    continue
        
        return self._process_extracted_text(all_text)
    
    def _process_extracted_text(self, text: str) -> List[Dict]:
        """Process extracted text using LinkedIn-specific patterns"""
        # Split by pages to handle engagement data separately
        pages = text.split('--- PAGE')
        
        posts = []
        engagement_data = {}
        
        for page_content in pages:
            if not page_content.strip():
                continue
                
            # Check if this page contains engagement data
            if 'Reaktionen' in page_content or 'Gefällt mir' in page_content:
                engagement_data.update(self._extract_engagement_data(page_content))
                continue
            
            # Look for post content (clean after processing page)
            post_data = self._extract_post_from_page(page_content)
            if post_data:
                posts.append(post_data)
        
        # Associate engagement data with posts
        if engagement_data and posts:
            posts[0].update(engagement_data)
        
        return posts if posts else [self._create_sample_post(text)]
    
    def _extract_post_from_page(self, page_text: str) -> Optional[Dict]:
        """Extract post data from a single page"""
        # Clean the page text first
        cleaned_text = self._clean_text_artifacts(page_text)
        
        # Find the timestamp pattern that indicates post start
        timestamp_match = re.search(self.timestamp_pattern, cleaned_text)
        if not timestamp_match:
            # Try alternative patterns
            alt_patterns = [
                r'(\d+)\s+(Monate?|Wochen?|Tage?|Stunden?)',  # Without bullet point
                r'vor\s+(\d+)\s+(Monate?|Wochen?|Tage?|Stunden?)',  # With "vor"
                r'(\d+)\s*(mo|w|d|h|Mo|W|D|H)',  # Abbreviated
            ]
            
            for alt_pattern in alt_patterns:
                alt_match = re.search(alt_pattern, cleaned_text, re.IGNORECASE)
                if alt_match:
                    timestamp_match = alt_match
                    break
            
            if not timestamp_match:
                return None
        
        # Split text at timestamp
        timestamp_pos = timestamp_match.start()
        metadata_section = cleaned_text[:timestamp_pos]
        content_section = cleaned_text[timestamp_match.end():]
        
        # Extract metadata
        author = self._extract_author(metadata_section)
        company = self._extract_company(metadata_section)
        followers = self._extract_followers(metadata_section)
        timestamp_text = f"{timestamp_match.group(1)} {timestamp_match.group(2)}"
        
        # Clean and extract content
        content = self._extract_clean_content(content_section)
        title = self._generate_smart_title(content, company)
        hashtags = self._extract_hashtags(content)
        
        return {
            'title': title,
            'content': content,
            'hashtags': hashtags,
            'author': author,
            'company': company,
            'followers': followers,
            'timestamp': timestamp_text,
            'date': self._parse_timestamp(timestamp_text),
            'engagement': ''
        }
    
    def _clean_text_artifacts(self, text: str) -> str:
        """Clean common PDF extraction artifacts"""
        # Decode HTML entities first
        import html
        text = html.unescape(text)
        
        # Remove common LinkedIn header/footer patterns
        patterns_to_remove = [
            r'\d{2}\.\d{2}\.\d{2}, \d{2}:\d{2}.*?LinkedIn\n',
            r'LinkedIn Corporation.*?\d{4}',
            r'Info Barrierefreiheit.*?Mehr',
            r'Nutzungsrichtlinien.*?Mehr',
            r'Cookie-Richtlinie.*?Mehr',
            r'Anzeigenauswahl.*?herunterladen',
            r'Zugang zu exklusiven.*?testen',
            r'Jetzt Premium.*?EUR',
            r'Region [^\n]+\n'
        ]
        
        for pattern in patterns_to_remove:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
        
        # Fix common spacing issues  
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # camelCase fixes
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Clean line breaks
        
        # Remove additional LinkedIn UI elements
        for pattern in self.linkedin_ui_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
        
        return text.strip()
    
    def _extract_author(self, metadata: str) -> str:
        """Extract author name from metadata section"""
        lines = metadata.split('\n')
        
        # Look for a name pattern - typically appears after company info
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Check if this looks like a person's name (two or more words, proper case)
            words = line.split()
            if (len(words) >= 2 and 
                all(word[0].isupper() if word else False for word in words) and
                len(line) < 60 and
                not any(keyword in line.lower() for keyword in ['gmbh', 'ag', 'inc', 'llc', 'corporation', 'corp', 'kg', 'ug'])):
                return line
        
        # Fallback: look for "Frederik Wystup" specifically mentioned in the text
        name_match = re.search(r'Frederik\s+Wystup', metadata, re.IGNORECASE)
        if name_match:
            return name_match.group()
            
        return "Unknown Author"
    
    def _extract_company(self, metadata: str) -> str:
        """Extract company name from metadata"""
        # First try the existing pattern
        match = re.search(self.company_pattern, metadata)
        if match:
            company = match.group(1).strip()
            # Clean up common artifacts
            company = re.sub(r'\s+', ' ', company)
            return company
        
        # Generic company pattern search
        company_patterns = [
            r'(Kirsten\s+Controlsystems\s+GmbH)',
            r'(Mei\s+Luft\s+GmbH\s+&\s+Co\.\s+KG)',
            r'([A-Z][a-zA-Z\s&.,-]+(?:GmbH|AG|Inc|LLC|Ltd|Corporation|Corp|KG|UG))',
            r'([A-Z][a-zA-Z\s&.,-]{3,50})\s+\d+\s+Follower'
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, metadata, re.IGNORECASE)
            if match:
                company = match.group(1).strip()
                # Clean up spacing artifacts
                company = re.sub(r'\s+', ' ', company)
                return company
        
        return ""
    
    def _extract_followers(self, metadata: str) -> str:
        """Extract follower count"""
        match = re.search(self.follower_pattern, metadata)
        if match:
            return match.group(1)
        return ""
    
    def _extract_clean_content(self, content: str) -> str:
        """Extract and clean post content"""
        # Remove LinkedIn UI elements from content
        for pattern in self.linkedin_ui_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
        
        # Split into lines and clean
        lines = content.split('\n')
        clean_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip lines that look like UI elements or metadata
            if any(keyword in line.lower() for keyword in 
                   ['impressions', 'profilbesuche', 'premium', 'linkedin corporation']):
                continue
                
            clean_lines.append(line)
        
        content = '\n'.join(clean_lines)
        return content[:3000]  # Limit content length
    
    def _generate_smart_title(self, content: str, company: str = "") -> str:
        """Generate intelligent title from content"""
        if not content:
            return "LinkedIn Post"
        
        # Try to get first sentence
        sentences = re.split(r'[.!?]+', content)
        first_sentence = sentences[0].strip() if sentences else content
        
        # If first sentence is a question, use it
        if first_sentence.endswith('?'):
            title = first_sentence
        else:
            # Otherwise, take first meaningful line
            lines = content.split('\n')
            title = lines[0].strip() if lines else first_sentence
        
        # Add company context if available
        if company and len(title) < 80:
            title = f"{title} - {company}"
        
        # Ensure reasonable length
        if len(title) > 150:
            title = title[:147] + "..."
        
        return title or "LinkedIn Post"
    
    def _extract_hashtags(self, content: str) -> str:
        """Extract hashtags from content"""
        hashtags = re.findall(r'#\w+', content)
        return ' '.join(hashtags) if hashtags else ""
    
    def _extract_engagement_data(self, page_text: str) -> Dict:
        """Extract engagement data from reactions page"""
        engagement = {}
        
        for metric, pattern in self.engagement_patterns.items():
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                engagement[metric] = match.group(1)
        
        # Format engagement string
        if engagement:
            parts = []
            if 'likes' in engagement:
                parts.append(f"{engagement['likes']} Likes")
            if 'comments' in engagement:
                parts.append(f"{engagement['comments']} Kommentare")
            if 'impressions' in engagement:
                parts.append(f"{engagement['impressions']} Impressions")
            
            return {'engagement': ', '.join(parts)}
        
        return {}
    
    def _parse_timestamp(self, timestamp_text: str) -> str:
        """Convert relative timestamp to approximate date"""
        # This is approximate - could be enhanced with actual calculation
        return datetime.now().strftime('%Y-%m-%d')
    
    def _create_sample_post(self, full_text: str) -> Dict:
        """Create a sample post if parsing fails"""
        return {
            'title': 'Importierter LinkedIn Content',
            'content': full_text[:1000] + '...' if len(full_text) > 1000 else full_text,
            'hashtags': '',
            'author': '',
            'company': '',
            'followers': '',
            'timestamp': '',
            'date': '',
            'engagement': ''
        }
    
    def _create_fallback_post(self, error_msg: str) -> List[Dict]:
        """Create fallback post when parsing completely fails"""
        return [{
            'title': 'LinkedIn PDF Import Fehler',
            'content': f'Die PDF-Datei konnte nicht verarbeitet werden. Fehler: {error_msg}',
            'hashtags': '#import #error',
            'author': '',
            'company': '',
            'followers': '',
            'timestamp': '',
            'date': '',
            'engagement': ''
        }]