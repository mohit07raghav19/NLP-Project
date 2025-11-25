"""
Text Cleaning Utilities

Handles text preprocessing and normalization for CVE descriptions.
"""

import re
import html
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class TextCleaner:
    """
    Clean and normalize text for NLP processing.
    """
    
    def __init__(
        self,
        lowercase: bool = False,
        remove_html: bool = True,
        remove_urls: bool = False,
        remove_special_chars: bool = False,
        preserve_cve_ids: bool = True,
        preserve_version_numbers: bool = True
    ):
        """
        Initialize text cleaner.
        
        Args:
            lowercase: Convert text to lowercase
            remove_html: Remove HTML tags
            remove_urls: Remove URLs
            remove_special_chars: Remove special characters
            preserve_cve_ids: Keep CVE ID patterns (CVE-YYYY-NNNNN)
            preserve_version_numbers: Keep version numbers
        """
        self.lowercase = lowercase
        self.remove_html = remove_html
        self.remove_urls = remove_urls
        self.remove_special_chars = remove_special_chars
        self.preserve_cve_ids = preserve_cve_ids
        self.preserve_version_numbers = preserve_version_numbers
        
        # Compile regex patterns
        self.cve_pattern = re.compile(r'CVE-\d{4}-\d{4,}')
        self.url_pattern = re.compile(r'https?://\S+|www\.\S+')
        self.version_pattern = re.compile(r'\d+\.\d+[\.\d]*')
        self.html_pattern = re.compile(r'<[^>]+>')
        self.special_char_pattern = re.compile(r'[^a-zA-Z0-9\s\-\.]')
    
    def clean(self, text: str) -> str:
        """
        Clean text with configured options.
        
        Args:
            text: Input text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Decode HTML entities
        text = html.unescape(text)
        
        # Remove HTML tags
        if self.remove_html:
            text = self.html_pattern.sub(' ', text)
        
        # Preserve important patterns before cleaning
        placeholders = {}
        
        if self.preserve_cve_ids:
            cve_ids = self.cve_pattern.findall(text)
            for i, cve_id in enumerate(cve_ids):
                placeholder = f"__CVE_{i}__"
                placeholders[placeholder] = cve_id
                text = text.replace(cve_id, placeholder)
        
        if self.preserve_version_numbers:
            versions = self.version_pattern.findall(text)
            for i, version in enumerate(versions):
                placeholder = f"__VER_{i}__"
                placeholders[placeholder] = version
                text = text.replace(version, placeholder)
        
        # Remove URLs
        if self.remove_urls:
            text = self.url_pattern.sub(' ', text)
        
        # Remove special characters
        if self.remove_special_chars:
            text = self.special_char_pattern.sub(' ', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Restore preserved patterns
        for placeholder, original in placeholders.items():
            text = text.replace(placeholder, original)
        
        # Apply lowercase
        if self.lowercase and not (self.preserve_cve_ids or self.preserve_version_numbers):
            text = text.lower()
        
        return text.strip()
    
    def clean_batch(self, texts: List[str]) -> List[str]:
        """
        Clean multiple texts.
        
        Args:
            texts: List of texts to clean
            
        Returns:
            List of cleaned texts
        """
        return [self.clean(text) for text in texts]
    
    def extract_cve_ids(self, text: str) -> List[str]:
        """
        Extract all CVE IDs from text.
        
        Args:
            text: Input text
            
        Returns:
            List of CVE IDs found
        """
        return self.cve_pattern.findall(text)
    
    def extract_versions(self, text: str) -> List[str]:
        """
        Extract version numbers from text.
        
        Args:
            text: Input text
            
        Returns:
            List of version numbers
        """
        return self.version_pattern.findall(text)
    
    @staticmethod
    def remove_duplicates(texts: List[str]) -> List[str]:
        """Remove duplicate texts while preserving order."""
        seen = set()
        result = []
        for text in texts:
            if text not in seen:
                seen.add(text)
                result.append(text)
        return result


# Example usage
if __name__ == "__main__":
    cleaner = TextCleaner()
    
    sample_text = """
    <p>CVE-2024-1234 affects Apache Tomcat versions 9.0.0 to 9.0.70. 
    See https://example.com/advisory for details.</p>
    """
    
    cleaned = cleaner.clean(sample_text)
    print("Original:", sample_text)
    print("Cleaned:", cleaned)
    
    cve_ids = cleaner.extract_cve_ids(sample_text)
    print("CVE IDs found:", cve_ids)
    
    versions = cleaner.extract_versions(sample_text)
    print("Versions found:", versions)
