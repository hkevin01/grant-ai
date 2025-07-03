"""
AI Assistant service for intelligent grant matching and form filling.
Uses free, locally-runnable AI models for privacy and cost-effectiveness.
"""
import logging
import re
from typing import Dict, List, Optional, Tuple

from grant_ai.models import OrganizationProfile
from grant_ai.models.grant import Grant


class AIAssistant:
    """AI-powered assistant for grant research and application assistance."""
    
    def __init__(self):
        """Initialize the AI assistant with required models."""
        self.logger = logging.getLogger(__name__)
        self._similarity_model = None
        self._nlp_model = None
        self._initialized = False
        
        try:
            self._initialize_models()
            self._initialized = True
        except Exception as e:
            self.logger.warning(f"AI models not available: {e}")
            self._initialized = False
    
    def _initialize_models(self):
        """Initialize AI models if available."""
        try:
            # Initialize sentence transformers for semantic similarity
            from sentence_transformers import SentenceTransformer
            self._similarity_model = SentenceTransformer(
                'all-MiniLM-L6-v2',
                device='cpu'  # Use CPU for compatibility
            )
            self.logger.info("Loaded sentence similarity model")
        except ImportError:
            self.logger.warning("sentence-transformers not available")
        except Exception as e:
            self.logger.warning(f"Failed to load similarity model: {e}")
        
        try:
            # Initialize spaCy for NLP tasks
            import spacy
            try:
                self._nlp_model = spacy.load("en_core_web_sm")
                self.logger.info("Loaded spaCy NLP model")
            except OSError:
                self.logger.warning("spaCy model 'en_core_web_sm' not found")
        except ImportError:
            self.logger.warning("spaCy not available")
    
    def is_available(self) -> bool:
        """Check if AI assistant is properly initialized."""
        return self._initialized and (
            self._similarity_model is not None or self._nlp_model is not None
        )
    
    def rank_grants_by_relevance(
        self,
        grants: List[Grant],
        organization: OrganizationProfile,
        limit: int = 20
    ) -> List[Tuple[Grant, float]]:
        """
        Rank grants by relevance to organization using AI similarity.
        
        Args:
            grants: List of grants to rank
            organization: Organization profile
            limit: Maximum number of grants to return
            
        Returns:
            List of (grant, relevance_score) tuples, sorted by relevance
        """
        if not self.is_available() or not grants:
            return [(grant, 0.5) for grant in grants[:limit]]
        
        try:
            # Create organization description for comparison
            org_description = self._create_organization_description(organization)
            
            scored_grants = []
            for grant in grants:
                score = self._calculate_grant_relevance(grant, org_description)
                scored_grants.append((grant, score))
            
            # Sort by relevance score (descending)
            scored_grants.sort(key=lambda x: x[1], reverse=True)
            
            return scored_grants[:limit]
            
        except Exception as e:
            self.logger.error(f"Error ranking grants: {e}")
            return [(grant, 0.5) for grant in grants[:limit]]
    
    def _create_organization_description(self, org: OrganizationProfile) -> str:
        """Create a comprehensive description of the organization."""
        description_parts = []
        
        if org.organization_name:
            description_parts.append(f"Organization: {org.organization_name}")
        
        if org.organization_type:
            description_parts.append(f"Type: {org.organization_type}")
        
        if org.mission_statement:
            description_parts.append(f"Mission: {org.mission_statement}")
        
        if org.target_beneficiaries:
            description_parts.append(f"Beneficiaries: {org.target_beneficiaries}")
        
        if org.funding_priorities:
            description_parts.append(f"Priorities: {org.funding_priorities}")
        
        if org.current_programs:
            description_parts.append(f"Programs: {org.current_programs}")
        
        if org.geographic_scope:
            description_parts.append(f"Geographic scope: {org.geographic_scope}")
        
        return " ".join(description_parts)
    
    def _calculate_grant_relevance(
        self,
        grant: Grant,
        org_description: str
    ) -> float:
        """Calculate relevance score between grant and organization."""
        try:
            # Create grant description
            grant_description = f"{grant.title} {grant.description or ''}"
            grant_description += f" {grant.funder_name or ''}"
            
            if hasattr(grant, 'focus_areas') and grant.focus_areas:
                grant_description += f" {' '.join(grant.focus_areas)}"
            
            # Use sentence similarity if available
            if self._similarity_model:
                return self._calculate_semantic_similarity(
                    org_description,
                    grant_description
                )
            
            # Fallback to keyword matching
            return self._calculate_keyword_similarity(
                org_description,
                grant_description
            )
            
        except Exception as e:
            self.logger.warning(f"Error calculating relevance: {e}")
            return 0.5
    
    def _calculate_semantic_similarity(
        self,
        text1: str,
        text2: str
    ) -> float:
        """Calculate semantic similarity using sentence transformers."""
        try:
            from sentence_transformers import util

            # Encode texts
            embedding1 = self._similarity_model.encode(text1)
            embedding2 = self._similarity_model.encode(text2)
            
            # Calculate cosine similarity
            similarity = util.cos_sim(embedding1, embedding2)
            return float(similarity[0][0])
            
        except Exception as e:
            self.logger.warning(f"Semantic similarity calculation failed: {e}")
            return self._calculate_keyword_similarity(text1, text2)
    
    def _calculate_keyword_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity based on keyword overlap."""
        try:
            # Extract keywords using NLP if available
            if self._nlp_model:
                keywords1 = self._extract_keywords_nlp(text1)
                keywords2 = self._extract_keywords_nlp(text2)
            else:
                keywords1 = self._extract_keywords_simple(text1)
                keywords2 = self._extract_keywords_simple(text2)
            
            # Calculate Jaccard similarity
            intersection = len(keywords1.intersection(keywords2))
            union = len(keywords1.union(keywords2))
            
            if union == 0:
                return 0.0
            
            return intersection / union
            
        except Exception as e:
            self.logger.warning(f"Keyword similarity calculation failed: {e}")
            return 0.3
    
    def _extract_keywords_nlp(self, text: str) -> set:
        """Extract keywords using spaCy NLP."""
        try:
            doc = self._nlp_model(text.lower())
            keywords = set()
            
            for token in doc:
                # Include important words (nouns, adjectives, proper nouns)
                if (token.pos_ in ['NOUN', 'PROPN', 'ADJ'] and
                    len(token.text) > 2 and
                    not token.is_stop and
                    not token.is_punct):
                    keywords.add(token.lemma_)
            
            # Include named entities
            for ent in doc.ents:
                if ent.label_ in ['ORG', 'PERSON', 'GPE', 'MONEY']:
                    keywords.add(ent.text.lower())
            
            return keywords
            
        except Exception as e:
            self.logger.warning(f"NLP keyword extraction failed: {e}")
            return self._extract_keywords_simple(text)
    
    def _extract_keywords_simple(self, text: str) -> set:
        """Simple keyword extraction using regex."""
        # Remove punctuation and split into words
        words = re.findall(r'\b\w{3,}\b', text.lower())
        
        # Common stop words to filter out
        stop_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all',
            'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day',
            'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new',
            'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did',
            'man', 'end', 'few', 'men', 'run', 'say', 'she', 'too',
            'use', 'her', 'big', 'got', 'let', 'put', 'say', 'try',
            'ask', 'own', 'and', 'any', 'may', 'say', 'she', 'use'
        }
        
        return {word for word in words if word not in stop_words}
    
    def suggest_search_terms(self, organization: OrganizationProfile) -> List[str]:
        """Suggest search terms based on organization profile."""
        terms = []
        
        try:
            # Add organization type and focus areas
            if organization.organization_type:
                terms.append(organization.organization_type.lower())
            
            # Extract key terms from mission statement
            if organization.mission_statement:
                if self._nlp_model:
                    keywords = self._extract_keywords_nlp(
                        organization.mission_statement
                    )
                    terms.extend(list(keywords)[:5])
                else:
                    keywords = self._extract_keywords_simple(
                        organization.mission_statement
                    )
                    terms.extend(list(keywords)[:5])
            
            # Add funding priorities
            if organization.funding_priorities:
                priorities = organization.funding_priorities.split(',')
                terms.extend([p.strip().lower() for p in priorities[:3]])
            
            # Add target beneficiaries
            if organization.target_beneficiaries:
                beneficiaries = organization.target_beneficiaries.split(',')
                terms.extend([b.strip().lower() for b in beneficiaries[:3]])
            
            # Remove duplicates and limit
            unique_terms = list(dict.fromkeys(terms))
            return unique_terms[:10]
            
        except Exception as e:
            self.logger.error(f"Error suggesting search terms: {e}")
            return ['nonprofit', 'community', 'education', 'social services']
    
    def auto_fill_suggestions(
        self,
        field_name: str,
        organization: OrganizationProfile,
        context: Optional[str] = None
    ) -> List[str]:
        """
        Suggest auto-fill values for form fields.
        
        Args:
            field_name: Name or label of the form field
            organization: Organization profile
            context: Additional context about the form/field
            
        Returns:
            List of suggested values
        """
        try:
            field_lower = field_name.lower()
            suggestions = []
            
            # Organization name fields
            if any(term in field_lower for term in [
                'organization', 'org', 'company', 'entity', 'institution'
            ]):
                if organization.organization_name:
                    suggestions.append(organization.organization_name)
            
            # Mission/purpose fields
            elif any(term in field_lower for term in [
                'mission', 'purpose', 'objective', 'goal', 'vision'
            ]):
                if organization.mission_statement:
                    suggestions.append(organization.mission_statement)
            
            # Type/category fields
            elif any(term in field_lower for term in [
                'type', 'category', 'classification', 'sector'
            ]):
                if organization.organization_type:
                    suggestions.append(organization.organization_type)
            
            # Beneficiary fields
            elif any(term in field_lower for term in [
                'beneficiary', 'served', 'target', 'population', 'audience'
            ]):
                if organization.target_beneficiaries:
                    suggestions.append(organization.target_beneficiaries)
            
            # Geographic fields
            elif any(term in field_lower for term in [
                'location', 'address', 'geographic', 'region', 'area'
            ]):
                if organization.geographic_scope:
                    suggestions.append(organization.geographic_scope)
                if hasattr(organization, 'address') and organization.address:
                    suggestions.append(organization.address)
            
            # Contact fields
            elif any(term in field_lower for term in [
                'contact', 'email', 'phone', 'website'
            ]):
                if hasattr(organization, 'contact_email') and organization.contact_email:
                    suggestions.append(organization.contact_email)
                if hasattr(organization, 'website') and organization.website:
                    suggestions.append(organization.website)
            
            # Program/service fields
            elif any(term in field_lower for term in [
                'program', 'service', 'activity', 'project', 'initiative'
            ]):
                if organization.current_programs:
                    suggestions.append(organization.current_programs)
            
            return suggestions[:3]  # Limit to top 3 suggestions
            
        except Exception as e:
            self.logger.error(f"Error generating auto-fill suggestions: {e}")
            return []
    
    def extract_grant_requirements(self, grant: Grant) -> Dict[str, any]:
        """
        Extract and structure grant requirements using NLP.
        
        Args:
            grant: Grant object to analyze
            
        Returns:
            Dictionary with structured requirements
        """
        try:
            text = f"{grant.title} {grant.description or ''}"
            
            requirements = {
                'eligibility': [],
                'funding_range': None,
                'deadlines': [],
                'required_documents': [],
                'focus_areas': [],
                'geographic_restrictions': []
            }
            
            if self._nlp_model:
                doc = self._nlp_model(text)
                
                # Extract organizations mentioned
                for ent in doc.ents:
                    if ent.label_ == 'ORG':
                        requirements['eligibility'].append(ent.text)
                    elif ent.label_ == 'MONEY':
                        requirements['funding_range'] = ent.text
                    elif ent.label_ == 'DATE':
                        requirements['deadlines'].append(ent.text)
                    elif ent.label_ == 'GPE':  # Geographic entities
                        requirements['geographic_restrictions'].append(ent.text)
            
            # Extract using keyword patterns
            requirements.update(self._extract_requirements_patterns(text))
            
            return requirements
            
        except Exception as e:
            self.logger.error(f"Error extracting grant requirements: {e}")
            return {}
    
    def _extract_requirements_patterns(self, text: str) -> Dict[str, any]:
        """Extract requirements using regex patterns."""
        requirements = {
            'eligibility': [],
            'required_documents': [],
            'focus_areas': []
        }
        
        try:
            text_lower = text.lower()
            
            # Common eligibility patterns
            eligibility_patterns = [
                r'(nonprofit|non-profit)\s+(organizations?|entities?)',
                r'501\(c\)\(3\)\s+organizations?',
                r'charitable\s+organizations?',
                r'community\s+organizations?',
                r'educational\s+institutions?',
                r'universities?',
                r'schools?',
                r'faith-based\s+organizations?'
            ]
            
            for pattern in eligibility_patterns:
                matches = re.findall(pattern, text_lower)
                if matches:
                    requirements['eligibility'].extend(matches)
            
            # Document requirements
            doc_patterns = [
                r'(proposal|application|letter\s+of\s+intent)',
                r'(budget|financial\s+statement)',
                r'(tax\s+exempt|501c3)\s+(letter|determination)',
                r'(references|recommendations)',
                r'(timeline|work\s+plan)',
                r'(evaluation\s+plan|metrics)'
            ]
            
            for pattern in doc_patterns:
                matches = re.findall(pattern, text_lower)
                if matches:
                    requirements['required_documents'].extend(matches)
            
            # Focus areas
            focus_patterns = [
                r'(education|educational)',
                r'(health|healthcare|medical)',
                r'(housing|affordable\s+housing)',
                r'(arts|culture|cultural)',
                r'(environment|environmental)',
                r'(youth|children)',
                r'(seniors|elderly)',
                r'(community\s+development)',
                r'(social\s+services)',
                r'(technology|STEM)'
            ]
            
            for pattern in focus_patterns:
                matches = re.findall(pattern, text_lower)
                if matches:
                    requirements['focus_areas'].extend(matches)
            
        except Exception as e:
            self.logger.warning(f"Pattern extraction failed: {e}")
        
        return requirements
    
    def get_status(self) -> Dict[str, any]:
        """Get status information about the AI assistant."""
        return {
            'initialized': self._initialized,
            'similarity_model_available': self._similarity_model is not None,
            'nlp_model_available': self._nlp_model is not None,
            'features_available': {
                'semantic_similarity': self._similarity_model is not None,
                'keyword_extraction': True,
                'auto_fill_suggestions': True,
                'requirement_extraction': True
            }
        }
