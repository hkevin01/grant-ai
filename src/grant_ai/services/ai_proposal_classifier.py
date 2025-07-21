"""
AI Proposal Classifier
Classifies RFPs and funding calls by domain and AI relevance
Includes robust error handling and logging.
"""
import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple
import logging

from grant_ai.models.grant import Grant
from grant_ai.utils.logger import get_logger

logger = get_logger(__name__)


class GrantDomain(Enum):
    """Grant application domains"""
    EARTH_OBSERVATION = "earth_observation"
    DEEP_SPACE = "deep_space"
    CREWED_MISSIONS = "crewed_missions"
    SPACE_TECHNOLOGY = "space_technology"
    AI_RESEARCH = "ai_research"
    EDUCATION = "education"
    HEALTH_TECHNOLOGY = "health_technology"
    ENERGY = "energy"
    CLIMATE = "climate"
    CYBERSECURITY = "cybersecurity"
    OTHER = "other"


class AIRelevance(Enum):
    """AI relevance levels"""
    HIGH = "high"          # Core AI/ML focus
    MEDIUM = "medium"      # AI component or application
    LOW = "low"           # Minimal AI relevance
    NONE = "none"         # No AI relevance


@dataclass
class ClassificationResult:
    """Result of grant classification"""
    domain: GrantDomain
    ai_relevance: AIRelevance
    confidence_score: float
    matched_keywords: List[str]
    reasoning: str


class AIProposalClassifier:
    """Lightweight classifier for grant proposals and RFPs"""
    
    def __init__(self):
        # Domain classification keywords
        self.domain_keywords = {
            GrantDomain.EARTH_OBSERVATION: [
                'earth observation', 'satellite imagery', 'remote sensing',
                'climate monitoring', 'environmental monitoring',
                'geospatial data', 'earth science', 'landsat', 'modis'
            ],
            GrantDomain.DEEP_SPACE: [
                'deep space', 'planetary science', 'mars', 'jupiter',
                'outer planets', 'asteroid', 'comet', 'exoplanet',
                'interplanetary', 'space exploration'
            ],
            GrantDomain.CREWED_MISSIONS: [
                'crew', 'astronaut', 'human spaceflight', 'space station',
                'life support', 'human factors', 'spacewalk', 'eva',
                'crew safety', 'lunar gateway'
            ],
            GrantDomain.SPACE_TECHNOLOGY: [
                'spacecraft', 'propulsion', 'navigation', 'guidance',
                'spacecraft systems', 'mission design', 'orbital mechanics',
                'space systems engineering'
            ],
            GrantDomain.AI_RESEARCH: [
                'artificial intelligence', 'machine learning',
                'deep learning', 'neural networks', 'computer vision',
                'natural language processing', 'robotics'
            ],
            GrantDomain.EDUCATION: [
                'education', 'learning', 'curriculum', 'teaching',
                'students', 'school', 'university', 'training'
            ],
            GrantDomain.HEALTH_TECHNOLOGY: [
                'health', 'medical', 'healthcare', 'biomedical',
                'clinical', 'patient', 'therapy', 'diagnosis'
            ],
            GrantDomain.ENERGY: [
                'energy', 'power', 'renewable', 'solar', 'wind',
                'nuclear', 'battery', 'grid', 'efficiency'
            ],
            GrantDomain.CLIMATE: [
                'climate', 'carbon', 'greenhouse gas', 'emission',
                'sustainability', 'environmental', 'weather'
            ],
            GrantDomain.CYBERSECURITY: [
                'cybersecurity', 'security', 'encryption', 'privacy',
                'cyber', 'threat', 'vulnerability', 'network security'
            ]
        }
        
        # AI relevance keywords with weights
        self.ai_keywords = {
            # High relevance (core AI/ML)
            'artificial intelligence': 3.0,
            'machine learning': 3.0,
            'deep learning': 3.0,
            'neural networks': 3.0,
            'computer vision': 3.0,
            'natural language processing': 3.0,
            'nlp': 3.0,
            'reinforcement learning': 3.0,
            'ai models': 3.0,
            'ai algorithms': 3.0,
            
            # Medium relevance (AI applications)
            'automation': 2.0,
            'autonomous systems': 2.5,
            'robotics': 2.5,
            'intelligent systems': 2.0,
            'predictive analytics': 2.0,
            'data mining': 2.0,
            'pattern recognition': 2.0,
            'algorithm development': 2.0,
            'smart systems': 2.0,
            
            # Lower relevance (AI-adjacent)
            'data science': 1.5,
            'big data': 1.5,
            'analytics': 1.0,
            'optimization': 1.0,
            'modeling': 1.0,
            'simulation': 1.0,
            'computational': 1.0
        }
        
        # NASA/ESA specific frameworks
        self.framework_keywords = {
            'nasa_responsible_ai': [
                'responsible ai', 'ai ethics', 'ai safety',
                'explainable ai', 'trustworthy ai', 'ai governance'
            ],
            'esa_discovery_themes': [
                'autonomy', 'onboard processing', 'edge computing',
                'space autonomy', 'intelligent spacecraft'
            ]
        }
    
    def classify_grant(self, grant: Grant) -> ClassificationResult:
        """Classify a grant by domain and AI relevance"""
        text_content = f"{grant.title} {grant.description}".lower()
        
        # Classify domain
        domain, domain_confidence, domain_keywords = self._classify_domain(
            text_content
        )
        
        # Classify AI relevance
        ai_relevance, ai_confidence, ai_keywords = self._classify_ai_relevance(
            text_content
        )
        
        # Overall confidence (average of domain and AI confidence)
        overall_confidence = (domain_confidence + ai_confidence) / 2
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            domain, ai_relevance, domain_keywords, ai_keywords
        )
        
        return ClassificationResult(
            domain=domain,
            ai_relevance=ai_relevance,
            confidence_score=overall_confidence,
            matched_keywords=domain_keywords + ai_keywords,
            reasoning=reasoning
        )
    
    def classify_multiple_grants(self, grants: List[Grant]) -> Dict[str, ClassificationResult]:
        """Classify multiple grants"""
        results = {}
        for grant in grants:
            # Use grant title as key, or generate a unique identifier
            key = grant.title[:50] if grant.title else f"grant_{id(grant)}"
            results[key] = self.classify_grant(grant)
        return results
    
    def _classify_domain(self, text: str) -> Tuple[GrantDomain, float, List[str]]:
        """Classify the domain of the grant"""
        domain_scores = {}
        matched_keywords = {}
        
        for domain, keywords in self.domain_keywords.items():
            score = 0
            domain_matches = []
            
            for keyword in keywords:
                if keyword in text:
                    score += 1
                    domain_matches.append(keyword)
            
            if score > 0:
                domain_scores[domain] = score
                matched_keywords[domain] = domain_matches
        
        if not domain_scores:
            return GrantDomain.OTHER, 0.1, []
        
        # Find domain with highest score
        best_domain = max(domain_scores, key=domain_scores.get)
        max_score = domain_scores[best_domain]
        
        # Calculate confidence based on score and keyword count
        total_keywords = len(self.domain_keywords[best_domain])
        confidence = min(max_score / total_keywords, 1.0)
        
        return best_domain, confidence, matched_keywords.get(best_domain, [])
    
    def _classify_ai_relevance(self, text: str) -> Tuple[AIRelevance, float, List[str]]:
        """Classify AI relevance of the grant"""
        ai_score = 0
        matched_keywords = []
        
        for keyword, weight in self.ai_keywords.items():
            if keyword in text:
                ai_score += weight
                matched_keywords.append(keyword)
        
        # Determine AI relevance level based on score
        if ai_score >= 5.0:
            relevance = AIRelevance.HIGH
            confidence = min(ai_score / 10.0, 1.0)
        elif ai_score >= 2.0:
            relevance = AIRelevance.MEDIUM
            confidence = min(ai_score / 5.0, 1.0)
        elif ai_score > 0:
            relevance = AIRelevance.LOW
            confidence = min(ai_score / 2.0, 1.0)
        else:
            relevance = AIRelevance.NONE
            confidence = 0.9  # High confidence in no AI relevance
        
        return relevance, confidence, matched_keywords
    
    def _generate_reasoning(
        self,
        domain: GrantDomain,
        ai_relevance: AIRelevance,
        domain_keywords: List[str],
        ai_keywords: List[str]
    ) -> str:
        """Generate human-readable reasoning for classification"""
        
        reasoning_parts = []
        
        # Domain reasoning
        if domain != GrantDomain.OTHER:
            reasoning_parts.append(
                f"Classified as {domain.value.replace('_', ' ').title()} "
                f"based on keywords: {', '.join(domain_keywords[:3])}"
            )
        else:
            reasoning_parts.append("Could not determine specific domain")
        
        # AI relevance reasoning
        if ai_relevance == AIRelevance.HIGH:
            reasoning_parts.append(
                f"High AI relevance due to core AI terms: "
                f"{', '.join(ai_keywords[:3])}"
            )
        elif ai_relevance == AIRelevance.MEDIUM:
            reasoning_parts.append(
                f"Medium AI relevance with AI applications: "
                f"{', '.join(ai_keywords[:3])}"
            )
        elif ai_relevance == AIRelevance.LOW:
            reasoning_parts.append(
                f"Low AI relevance with minimal AI connection: "
                f"{', '.join(ai_keywords[:2])}"
            )
        else:
            reasoning_parts.append("No significant AI relevance detected")
        
        return ". ".join(reasoning_parts) + "."
    
    def get_classification_summary(
        self,
        results: Dict[str, ClassificationResult]
    ) -> Dict:
        """Get summary statistics for classification results"""
        
        if not results:
            return {
                'total_grants': 0,
                'domain_distribution': {},
                'ai_relevance_distribution': {},
                'high_ai_grants': [],
                'average_confidence': 0
            }
        
        # Domain distribution
        domain_counts = {}
        for result in results.values():
            domain = result.domain.value
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        # AI relevance distribution
        ai_counts = {}
        for result in results.values():
            ai_level = result.ai_relevance.value
            ai_counts[ai_level] = ai_counts.get(ai_level, 0) + 1
        
        # High AI relevance grants
        high_ai_grants = [
            grant_name for grant_name, result in results.items()
            if result.ai_relevance == AIRelevance.HIGH
        ]
        
        # Average confidence
        avg_confidence = sum(
            result.confidence_score for result in results.values()
        ) / len(results)
        
        return {
            'total_grants': len(results),
            'domain_distribution': domain_counts,
            'ai_relevance_distribution': ai_counts,
            'high_ai_grants': high_ai_grants,
            'average_confidence': round(avg_confidence, 3)
        }
    
    def filter_by_nasa_esa_frameworks(self, grants: List[Grant]) -> List[Grant]:
        """Filter grants relevant to NASA/ESA frameworks"""
        relevant_grants = []
        
        for grant in grants:
            text_content = f"{grant.title} {grant.description}".lower()
            
            # Check for NASA Responsible AI framework relevance
            nasa_score = sum(
                1 for keyword in self.framework_keywords['nasa_responsible_ai']
                if keyword in text_content
            )
            
            # Check for ESA Discovery themes relevance
            esa_score = sum(
                1 for keyword in self.framework_keywords['esa_discovery_themes']
                if keyword in text_content
            )
            
            # Include if relevant to either framework
            if nasa_score > 0 or esa_score > 0:
                # Create a copy of the grant with framework info
                relevant_grant = grant.model_copy()
                
                # Store framework relevance in description or a custom way
                framework_info = []
                if nasa_score > 0:
                    framework_info.append('NASA_Responsible_AI')
                if esa_score > 0:
                    framework_info.append('ESA_Discovery_Themes')
                
                # Add framework info to description
                relevant_grant.description += f" [Framework: {', '.join(framework_info)}]"
                
                relevant_grants.append(relevant_grant)
        
        return relevant_grants


# Integration function for existing grant system
def classify_and_filter_grants(grants: List[Grant]) -> Dict:
    """Classify grants by domain and AI relevance, with error handling and logging."""
    summary = {
        "total_grants": len(grants),
        "domain_distribution": {},
        "average_confidence": 0.0,
    }
    high_ai_grants = []
    confidences = []
    try:
        classifier = AIProposalClassifier()
        # Classify all grants
        classification_results = classifier.classify_multiple_grants(grants)
        
        # Filter by NASA/ESA frameworks
        framework_relevant = classifier.filter_by_nasa_esa_frameworks(grants)
        
        for grant in grants:
            result = classifier.classify_grant(grant)
            # ...existing classification logic...
            domain = GrantDomain.OTHER
            ai_relevance = AIRelevance.NONE
            confidence = 0.5
            # Example logic (replace with real):
            if "AI" in grant.title or "machine learning" in grant.description:
                ai_relevance = AIRelevance.HIGH
                confidence = 0.95
                high_ai_grants.append(grant)
                domain = GrantDomain.AI_RESEARCH
            confidences.append(confidence)
            summary["domain_distribution"].setdefault(domain.value, 0)
            summary["domain_distribution"][domain.value] += 1
        summary["average_confidence"] = sum(confidences) / max(1, len(confidences))
        logger.info(f"Classified {len(grants)} grants. High AI relevance: {len(high_ai_grants)}.")
    except Exception as e:
        logger.error(f"Error classifying grants: {e}")
    return {
        "summary": summary,
        "high_ai_grants": high_ai_grants,
    }
