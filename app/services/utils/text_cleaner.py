"""
Text cleaning utilities for post-OCR processing
"""
import re
from typing import List, Dict, Tuple
from app.core.exceptions import CodeCleaningException


class TextCleaner:
    """Clean and enhance OCR-extracted text"""
    
    # Common OCR character substitutions
    CHAR_SUBSTITUTIONS = {
        # Numbers often misread as letters
        'O': '0', 'l': '1', 'I': '1', 'S': '5', 'B': '8',
        # Letters often misread as numbers/symbols
        '0': 'O', '1': 'l', '5': 'S', '8': 'B',
        # Common symbol misreads
        '|': 'l', '¡': '!', '¿': '?', '«': '<', '»': '>',
        # Quotes and brackets
        '"': '"', '"': '"', ''': "'", ''': "'",
        '（': '(', '）': ')', '［': '[', '］': ']', '｛': '{', '｝': '}',
    }
    
    # Programming language keywords for context
    PROGRAMMING_KEYWORDS = {
        'python': ['def', 'class', 'import', 'from', 'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'return'],
        'javascript': ['function', 'var', 'let', 'const', 'if', 'else', 'for', 'while', 'return', 'class'],
        'java': ['public', 'private', 'class', 'interface', 'if', 'else', 'for', 'while', 'return', 'import'],
        'cpp': ['#include', 'int', 'void', 'class', 'if', 'else', 'for', 'while', 'return', 'namespace'],
        'csharp': ['using', 'namespace', 'class', 'public', 'private', 'if', 'else', 'for', 'while', 'return'],
    }
    
    @staticmethod
    def remove_extra_whitespace(text: str) -> str:
        """Remove excessive whitespace while preserving code structure"""
        try:
            # Replace multiple spaces with single space, but preserve indentation
            lines = text.split('\n')
            cleaned_lines = []
            
            for line in lines:
                # Preserve leading whitespace (indentation)
                leading_whitespace = len(line) - len(line.lstrip())
                content = line.strip()
                
                if content:  # Only process non-empty lines
                    # Replace multiple spaces in content with single space
                    content = re.sub(r' +', ' ', content)
                    # Reconstruct line with original indentation
                    cleaned_line = ' ' * leading_whitespace + content
                    cleaned_lines.append(cleaned_line)
                else:
                    cleaned_lines.append('')  # Preserve empty lines
            
            return '\n'.join(cleaned_lines)
        except Exception as e:
            raise CodeCleaningException(f"Failed to remove extra whitespace: {str(e)}")
    
    @staticmethod
    def fix_common_ocr_errors(text: str) -> str:
        """Fix common OCR character recognition errors"""
        try:
            # Apply character substitutions in programming context
            result = text
            
            # Fix common programming-specific errors
            programming_fixes = {
                # Common bracket/parentheses errors
                r'\(\s*\)': '()',
                r'\[\s*\]': '[]',
                r'\{\s*\}': '{}',
                # Fix spacing around operators
                r'(\w)\s*=\s*(\w)': r'\1 = \2',
                r'(\w)\s*\+\s*(\w)': r'\1 + \2',
                r'(\w)\s*-\s*(\w)': r'\1 - \2',
                r'(\w)\s*\*\s*(\w)': r'\1 * \2',
                r'(\w)\s*/\s*(\w)': r'\1 / \2',
                # Fix common keyword errors
                r'\bdet\b': 'def',  # 'det' often misread as 'def'
                r'\bpnnt\b': 'print',  # 'pnnt' often misread as 'print'
                r'\bretum\b': 'return',  # 'retum' often misread as 'return'
                r'\bimpon\b': 'import',  # 'impon' often misread as 'import'
            }
            
            for pattern, replacement in programming_fixes.items():
                result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
            
            return result
        except Exception as e:
            raise CodeCleaningException(f"Failed to fix OCR errors: {str(e)}")
    
    @staticmethod
    def detect_programming_language(text: str) -> Tuple[str, float]:
        """
        Detect programming language from text content
        
        Returns:
            Tuple of (language, confidence_score)
        """
        try:
            text_lower = text.lower()
            language_scores = {}
            
            for lang, keywords in TextCleaner.PROGRAMMING_KEYWORDS.items():
                score = 0
                for keyword in keywords:
                    # Count keyword occurrences
                    count = len(re.findall(r'\b' + re.escape(keyword) + r'\b', text_lower))
                    score += count
                
                # Normalize by number of keywords
                language_scores[lang] = score / len(keywords) if keywords else 0
            
            # Find language with highest score
            if language_scores:
                best_lang = max(language_scores, key=language_scores.get)
                confidence = min(language_scores[best_lang], 1.0)  # Cap at 1.0
                return best_lang, confidence
            
            return "unknown", 0.0
        except Exception as e:
            return "unknown", 0.0
    
    @staticmethod
    def fix_indentation(text: str, language_hint: str = None) -> str:
        """Fix and normalize indentation based on programming language"""
        try:
            lines = text.split('\n')
            if not lines:
                return text
            
            # Detect indentation pattern
            indentations = []
            for line in lines:
                if line.strip():  # Only consider non-empty lines
                    leading_spaces = len(line) - len(line.lstrip())
                    if leading_spaces > 0:
                        indentations.append(leading_spaces)
            
            if not indentations:
                return text  # No indentation to fix
            
            # Find common indentation unit (GCD of all indentations)
            from math import gcd
            indent_unit = indentations[0]
            for indent in indentations[1:]:
                indent_unit = gcd(indent_unit, indent)
            
            # Normalize indentation to 4 spaces (common standard)
            if indent_unit > 0:
                normalized_lines = []
                for line in lines:
                    if line.strip():
                        leading_spaces = len(line) - len(line.lstrip())
                        indent_level = leading_spaces // indent_unit
                        normalized_line = '    ' * indent_level + line.lstrip()
                        normalized_lines.append(normalized_line)
                    else:
                        normalized_lines.append('')
                
                return '\n'.join(normalized_lines)
            
            return text
        except Exception as e:
            raise CodeCleaningException(f"Failed to fix indentation: {str(e)}")
    
    @staticmethod
    def remove_non_code_text(text: str) -> str:
        """Remove non-code text like headers, footers, page numbers"""
        try:
            lines = text.split('\n')
            code_lines = []
            
            for line in lines:
                line_stripped = line.strip()
                
                # Skip likely non-code lines
                if (
                    not line_stripped or  # Empty lines are kept
                    len(line_stripped) < 2 or  # Very short lines likely noise
                    re.match(r'^Page \d+', line_stripped) or  # Page numbers
                    re.match(r'^\d+$', line_stripped) or  # Standalone numbers
                    re.match(r'^[A-Z\s]+$', line_stripped) and len(line_stripped) > 10  # All caps headers
                ):
                    if not line_stripped:  # Keep empty lines for structure
                        code_lines.append('')
                    continue
                
                code_lines.append(line)
            
            return '\n'.join(code_lines)
        except Exception as e:
            raise CodeCleaningException(f"Failed to remove non-code text: {str(e)}")
    
    @classmethod
    def clean_extracted_text(cls, raw_text: str, language_hint: str = None) -> Dict[str, any]:
        """
        Complete text cleaning pipeline
        
        Args:
            raw_text: Raw OCR extracted text
            language_hint: Optional programming language hint
            
        Returns:
            Dictionary with cleaned text and metadata
        """
        try:
            # Step 1: Remove non-code text
            text = cls.remove_non_code_text(raw_text)
            
            # Step 2: Fix common OCR errors
            text = cls.fix_common_ocr_errors(text)
            
            # Step 3: Remove extra whitespace
            text = cls.remove_extra_whitespace(text)
            
            # Step 4: Fix indentation
            text = cls.fix_indentation(text, language_hint)
            
            # Step 5: Detect programming language
            detected_lang, lang_confidence = cls.detect_programming_language(text)
            
            return {
                'cleaned_text': text,
                'detected_language': detected_lang,
                'language_confidence': lang_confidence,
                'original_length': len(raw_text),
                'cleaned_length': len(text),
                'reduction_ratio': 1 - (len(text) / len(raw_text)) if raw_text else 0
            }
        except Exception as e:
            raise CodeCleaningException(f"Text cleaning pipeline failed: {str(e)}")