"""
Named Entity Recognition (NER) using spaCy

Extract entities from CVE descriptions:
- Organizations (vendors)
- Products
- Versions
- Locations
- Technical terms
"""

import spacy
from typing import List, Dict, Any, Optional
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class NERExtractor:
    """
    Extract named entities from CVE descriptions using spaCy.
    """
    
    def __init__(
        self,
        model_name: str = "en_core_web_sm",
        batch_size: int = 100,
        n_process: int = 1
    ):
        """
        Initialize NER extractor with spaCy model.
        
        Args:
            model_name: spaCy model to use (en_core_web_sm, en_core_web_lg, etc.)
            batch_size: Number of texts to process in batch
            n_process: Number of processes for parallel processing
        """
        self.model_name = model_name
        self.batch_size = batch_size
        self.n_process = n_process
        
        try:
            self.nlp = spacy.load(model_name)
            logger.info(f"Loaded spaCy model: {model_name}")
        except OSError:
            logger.error(f"Model '{model_name}' not found. Downloading...")
            from spacy.cli import download
            download(model_name)
            self.nlp = spacy.load(model_name)
        
        # Add custom entity ruler for CVE-specific patterns
        self._add_custom_patterns()
    
    def _add_custom_patterns(self):
        """Add custom entity recognition patterns for security terms."""
        if "entity_ruler" not in self.nlp.pipe_names:
            ruler = self.nlp.add_pipe("entity_ruler", before="ner")
        else:
            ruler = self.nlp.get_pipe("entity_ruler")
        
        # Define patterns for common security products/vendors
        patterns = [
            # Software products
            {"label": "PRODUCT", "pattern": "Apache Tomcat"},
            {"label": "PRODUCT", "pattern": "Apache HTTP Server"},
            {"label": "PRODUCT", "pattern": "Microsoft Windows"},
            {"label": "PRODUCT", "pattern": "Windows Server"},
            {"label": "PRODUCT", "pattern": "Linux Kernel"},
            {"label": "PRODUCT", "pattern": "Google Chrome"},
            {"label": "PRODUCT", "pattern": "Mozilla Firefox"},
            {"label": "PRODUCT", "pattern": "Oracle Database"},
            {"label": "PRODUCT", "pattern": "MySQL"},
            {"label": "PRODUCT", "pattern": "PostgreSQL"},
            
            # Vulnerability types
            {"label": "VULN_TYPE", "pattern": "buffer overflow"},
            {"label": "VULN_TYPE", "pattern": "SQL injection"},
            {"label": "VULN_TYPE", "pattern": "cross-site scripting"},
            {"label": "VULN_TYPE", "pattern": "XSS"},
            {"label": "VULN_TYPE", "pattern": "remote code execution"},
            {"label": "VULN_TYPE", "pattern": "RCE"},
            {"label": "VULN_TYPE", "pattern": "privilege escalation"},
            {"label": "VULN_TYPE", "pattern": "denial of service"},
            {"label": "VULN_TYPE", "pattern": "DoS"},
        ]
        
        ruler.add_patterns(patterns)
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities from text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary mapping entity labels to lists of entity texts
        """
        doc = self.nlp(text)
        
        entities = defaultdict(list)
        
        for ent in doc.ents:
            entities[ent.label_].append(ent.text)
        
        # Remove duplicates while preserving order
        for label in entities:
            seen = set()
            unique = []
            for item in entities[label]:
                if item not in seen:
                    seen.add(item)
                    unique.append(item)
            entities[label] = unique
        
        return dict(entities)
    
    def extract_entities_batch(self, texts: List[str]) -> List[Dict[str, List[str]]]:
        """
        Extract entities from multiple texts efficiently.
        
        Args:
            texts: List of texts to process
            
        Returns:
            List of entity dictionaries
        """
        results = []
        
        for doc in self.nlp.pipe(texts, batch_size=self.batch_size, n_process=self.n_process):
            entities = defaultdict(list)
            for ent in doc.ents:
                entities[ent.label_].append(ent.text)
            results.append(dict(entities))
        
        return results
    
    def extract_products(self, text: str) -> List[str]:
        """
        Extract software products mentioned in text.
        
        Args:
            text: Input text
            
        Returns:
            List of product names
        """
        entities = self.extract_entities(text)
        products = entities.get("PRODUCT", [])
        
        # Also check ORG entities that might be product names
        orgs = entities.get("ORG", [])
        
        # Combine and deduplicate
        all_products = list(set(products + orgs))
        return all_products
    
    def extract_vendors(self, text: str) -> List[str]:
        """
        Extract vendor/organization names from text.
        
        Args:
            text: Input text
            
        Returns:
            List of vendor names
        """
        entities = self.extract_entities(text)
        return entities.get("ORG", [])
    
    def extract_vulnerability_types(self, text: str) -> List[str]:
        """
        Extract vulnerability type mentions.
        
        Args:
            text: Input text
            
        Returns:
            List of vulnerability types
        """
        entities = self.extract_entities(text)
        return entities.get("VULN_TYPE", [])
    
    def get_entity_summary(self, text: str) -> Dict[str, Any]:
        """
        Get comprehensive entity summary from text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with all extracted information
        """
        entities = self.extract_entities(text)
        
        return {
            "organizations": entities.get("ORG", []),
            "products": entities.get("PRODUCT", []),
            "persons": entities.get("PERSON", []),
            "locations": entities.get("GPE", []),
            "dates": entities.get("DATE", []),
            "versions": entities.get("CARDINAL", []),  # Often captures version numbers
            "vulnerability_types": entities.get("VULN_TYPE", []),
            "all_entities": entities
        }
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Comprehensive text analysis including tokens, POS tags, and entities.
        
        Args:
            text: Input text
            
        Returns:
            Analysis results
        """
        doc = self.nlp(text)
        
        return {
            "tokens": [token.text for token in doc],
            "lemmas": [token.lemma_ for token in doc],
            "pos_tags": [(token.text, token.pos_) for token in doc],
            "entities": self.get_entity_summary(text),
            "noun_chunks": [chunk.text for chunk in doc.noun_chunks],
            "sentence_count": len(list(doc.sents))
        }


# Example usage
if __name__ == "__main__":
    # Initialize extractor
    extractor = NERExtractor(model_name="en_core_web_sm")
    
    # Sample CVE description
    sample_text = """
    CVE-2024-1234 affects Apache Tomcat versions 9.0.0 to 9.0.70. 
    This vulnerability allows remote attackers to execute arbitrary code 
    through SQL injection in the authentication module. 
    The issue was discovered by researchers at Microsoft Security Response Center.
    """
    
    # Extract entities
    print("=" * 60)
    print("Entity Extraction Example")
    print("=" * 60)
    
    entities = extractor.extract_entities(sample_text)
    print("\nAll Entities:")
    for label, items in entities.items():
        print(f"  {label}: {items}")
    
    print("\nProducts:", extractor.extract_products(sample_text))
    print("Vendors:", extractor.extract_vendors(sample_text))
    print("Vulnerability Types:", extractor.extract_vulnerability_types(sample_text))
    
    print("\nEntity Summary:")
    summary = extractor.get_entity_summary(sample_text)
    for key, value in summary.items():
        if value:
            print(f"  {key}: {value}")
