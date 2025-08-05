"""
Advanced Grant Relevance Scoring using NLP and Machine Learning.

This module implements sophisticated grant-organization matching using:
- Natural Language Processing for semantic similarity
- Sentiment analysis for grant language assessment
- Keyword weighting and TF-IDF scoring
- Machine learning-based compatibility scoring
"""

import logging
from datetime import datetime
from typing import Dict, List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from textblob import TextBlob

from grant_ai.models.grant import Grant
from grant_ai.models.organization import OrganizationProfile


class GrantRelevanceScorer:
    """Advanced grant relevance scoring using NLP and machine learning."""

    def __init__(self):
        """Initialize the scorer with pre-trained models and configurations."""
        self.logger = logging.getLogger(__name__)

        # TF-IDF vectorizer for semantic similarity
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True,
            min_df=1,
            max_df=0.95
        )

        # Domain-specific keyword weights
        self.keyword_weights = {
            # High priority keywords (3x weight)
            'education': 3.0,
            'youth': 3.0,
            'nonprofit': 3.0,
            'community': 3.0,
            'arts': 3.0,
            'music': 3.0,
            'robotics': 3.0,
            'STEM': 3.0,
            'housing': 3.0,
            'development': 3.0,

            # Medium priority keywords (2x weight)
            'program': 2.0,
            'training': 2.0,
            'support': 2.0,
            'services': 2.0,
            'outreach': 2.0,
            'engagement': 2.0,
            'innovation': 2.0,
            'technology': 2.0,
            'research': 2.0,
            'scholarship': 2.0,

            # Standard keywords (1x weight)
            'project': 1.0,
            'initiative': 1.0,
            'collaboration': 1.0,
            'partnership': 1.0,
            'impact': 1.0,
            'sustainable': 1.0,
            'inclusive': 1.0,
            'accessible': 1.0
        }

        # Negative sentiment indicators
        self.negative_indicators = [
            'limited', 'restricted', 'exclusive', 'competitive',
            'difficult', 'complex', 'expensive', 'challenging',
            'stringent', 'rigorous', 'demanding'
        ]

        # Positive sentiment indicators
        self.positive_indicators = [
            'innovative', 'collaborative', 'supportive', 'inclusive',
            'accessible', 'flexible', 'comprehensive', 'sustainable',
            'impactful', 'transformative', 'empowering', 'creative'
        ]

    def calculate_relevance_score(
        self,
        grant: Grant,
        organization: OrganizationProfile
    ) -> Dict[str, float]:
        """
        Calculate comprehensive relevance score between grant and organization.

        Returns a dictionary with detailed scoring breakdown.
        """
        try:
            # Prepare text data
            grant_text = self._prepare_grant_text(grant)
            org_text = self._prepare_organization_text(organization)

            if not grant_text or not org_text:
                self.logger.warning(
                    "Insufficient text data for relevance scoring"
                )
                return self._default_score()

            # Calculate component scores
            semantic_score = self._calculate_semantic_similarity(
                grant_text, org_text
            )
            keyword_score = self._calculate_keyword_score(
                grant_text, organization
            )
            sentiment_score = self._calculate_sentiment_compatibility(
                grant_text, org_text
            )
            temporal_score = self._calculate_temporal_relevance(grant)
            eligibility_score = self._calculate_eligibility_match(
                grant, organization
            )

            # Weighted combination
            final_score = (
                semantic_score * 0.30 +      # 30% semantic similarity
                keyword_score * 0.25 +       # 25% keyword matching
                sentiment_score * 0.15 +     # 15% sentiment compatibility
                temporal_score * 0.15 +      # 15% timing relevance
                eligibility_score * 0.15     # 15% eligibility match
            )

            score_breakdown = {
                'final_score': min(final_score, 1.0),
                'semantic_similarity': semantic_score,
                'keyword_matching': keyword_score,
                'sentiment_compatibility': sentiment_score,
                'temporal_relevance': temporal_score,
                'eligibility_match': eligibility_score,
                'confidence': self._calculate_confidence(
                    grant_text, org_text
                )
            }

            self.logger.debug(
                "Relevance score calculated: %.3f for grant %s",
                final_score, grant.title
            )

            return score_breakdown

        except Exception as e:
            self.logger.error(
                "Error calculating relevance score: %s", str(e)
            )
            return self._default_score()

    def _prepare_grant_text(self, grant: Grant) -> str:
        """Prepare grant text for analysis."""
        text_parts = []

        if grant.title:
            text_parts.append(grant.title)
        if grant.description:
            text_parts.append(grant.description)
        if grant.summary:
            text_parts.append(grant.summary)
        if grant.eligibility_criteria:
            text_parts.append(' '.join(grant.eligibility_criteria))
        if grant.focus_areas:
            text_parts.append(' '.join(grant.focus_areas))

        return ' '.join(text_parts).strip()

    def _prepare_organization_text(self, organization: OrganizationProfile) -> str:
        """Prepare organization text for analysis."""
        text_parts = []

        if organization.name:
            text_parts.append(organization.name)
        if organization.description:
            text_parts.append(organization.description)
        if organization.mission_statement:
            text_parts.append(organization.mission_statement)
        if organization.target_demographics:
            text_parts.append(' '.join(organization.target_demographics))
        if organization.focus_areas:
            focus_text = ' '.join([
                str(area).replace('_', ' ').lower()
                for area in organization.focus_areas
            ])
            text_parts.append(focus_text)

        return ' '.join(text_parts).strip()

    def _calculate_semantic_similarity(
        self, grant_text: str, org_text: str
    ) -> float:
        """Calculate semantic similarity using TF-IDF and cosine similarity."""
        try:
            # Fit vectorizer on combined text
            combined_text = [grant_text, org_text]
            tfidf_matrix = self.vectorizer.fit_transform(combined_text)

            # Calculate cosine similarity
            similarity_matrix = cosine_similarity(tfidf_matrix)
            similarity_score = similarity_matrix[0, 1]

            return max(0.0, min(1.0, similarity_score))

        except Exception as e:
            self.logger.warning(
                "Error in semantic similarity calculation: %s", str(e)
            )
            return 0.0

    def _calculate_keyword_score(
        self, grant_text: str, organization: OrganizationProfile
    ) -> float:
        """Calculate keyword-based relevance score with weighting."""
        grant_text_lower = grant_text.lower()
        total_score = 0.0
        max_possible_score = 0.0

        # Organization-specific keywords
        org_keywords = organization.get_focus_keywords()
        if hasattr(organization, 'key_programs'):
            org_keywords.extend(organization.key_programs)
        if organization.target_demographics:
            org_keywords.extend(organization.target_demographics)

        # Score each keyword
        for keyword in org_keywords:
            keyword_lower = keyword.lower()
            weight = self.keyword_weights.get(keyword_lower, 1.0)
            max_possible_score += weight

            # Check for exact matches and partial matches
            if keyword_lower in grant_text_lower:
                total_score += weight
            elif any(
                word in grant_text_lower
                for word in keyword_lower.split()
            ):
                total_score += weight * 0.5

        # Add weighted keyword scoring
        for keyword, weight in self.keyword_weights.items():
            if keyword in grant_text_lower:
                # Boost score for high-priority domain keywords
                if weight >= 3.0:
                    total_score += weight * 0.5
                elif weight >= 2.0:
                    total_score += weight * 0.3
                else:
                    total_score += weight * 0.1

        if max_possible_score > 0:
            return min(1.0, total_score / max_possible_score)
        return 0.0

    def _calculate_sentiment_compatibility(
        self, grant_text: str, org_text: str
    ) -> float:
        """Analyze sentiment compatibility between grant and organization."""
        try:
            # Analyze sentiment of both texts
            grant_blob = TextBlob(grant_text)
            org_blob = TextBlob(org_text)

            grant_sentiment = grant_blob.sentiment.polarity
            org_sentiment = org_blob.sentiment.polarity

            # Check for negative indicators in grant text
            grant_text_lower = grant_text.lower()
            negative_count = sum(
                1 for indicator in self.negative_indicators
                if indicator in grant_text_lower
            )

            # Check for positive indicators
            positive_count = sum(
                1 for indicator in self.positive_indicators
                if indicator in grant_text_lower
            )

            # Calculate compatibility score
            sentiment_diff = abs(grant_sentiment - org_sentiment)
            sentiment_compatibility = 1.0 - (sentiment_diff / 2.0)

            # Adjust for positive/negative indicators
            if positive_count > negative_count:
                sentiment_compatibility += 0.1
            elif negative_count > positive_count:
                sentiment_compatibility -= 0.1

            return max(0.0, min(1.0, sentiment_compatibility))

        except Exception as e:
            self.logger.warning(
                "Error in sentiment analysis: %s", str(e)
            )
            return 0.5  # Neutral score

    def _calculate_temporal_relevance(self, grant: Grant) -> float:
        """Calculate temporal relevance based on deadlines and timing."""
        try:
            now = datetime.now()
            score = 0.5  # Default score

            # Application deadline relevance
            if grant.application_deadline:
                days_until_deadline = (grant.application_deadline - now).days

                if days_until_deadline < 0:
                    score = 0.0  # Deadline passed
                elif days_until_deadline <= 7:
                    score = 0.3  # Very urgent
                elif days_until_deadline <= 30:
                    score = 0.7  # Urgent
                elif days_until_deadline <= 60:
                    score = 1.0  # Optimal timing
                elif days_until_deadline <= 180:
                    score = 0.8  # Good timing
                else:
                    score = 0.6  # Far future

            # Grant status consideration
            if hasattr(grant, 'status'):
                if grant.status == 'open':
                    score *= 1.0
                elif grant.status == 'upcoming':
                    score *= 0.8
                elif grant.status == 'closed':
                    score = 0.0

            return score

        except Exception as e:
            self.logger.warning(
                "Error in temporal relevance calculation: %s", str(e)
            )
            return 0.5

    def _calculate_eligibility_match(
        self, grant: Grant, organization: OrganizationProfile
    ) -> float:
        """Calculate eligibility matching score."""
        score = 0.0

        # Organization type eligibility
        if hasattr(grant, 'eligibility_types'):
            if 'nonprofit' in [et.lower() for et in grant.eligibility_types]:
                score += 0.3

        # Geographic eligibility
        if hasattr(grant, 'geographic_scope') and organization.location:
            if (grant.geographic_scope == 'national' or
                organization.location.lower() in
                grant.geographic_scope.lower()):
                score += 0.3

        # Funding amount compatibility
        if grant.amount_min and grant.amount_max:
            org_min, org_max = organization.preferred_grant_size
            if not (grant.amount_max < org_min or grant.amount_min > org_max):
                score += 0.4
        elif hasattr(grant, 'amount_typical'):
            org_min, org_max = organization.preferred_grant_size
            if org_min <= grant.amount_typical <= org_max:
                score += 0.4

        return min(1.0, score)

    def _calculate_confidence(self, grant_text: str, org_text: str) -> float:
        """Calculate confidence level in the scoring."""
        # Length-based confidence
        text_length_score = min(1.0, (len(grant_text) + len(org_text)) / 1000)

        # Keyword richness
        grant_words = set(grant_text.lower().split())
        org_words = set(org_text.lower().split())

        domain_keywords_found = sum(
            1 for keyword in self.keyword_weights.keys()
            if keyword in grant_words or keyword in org_words
        )

        keyword_confidence = min(1.0, domain_keywords_found / 10)

        # Combined confidence
        confidence = (text_length_score * 0.6 + keyword_confidence * 0.4)
        return confidence

    def _default_score(self) -> Dict[str, float]:
        """Return default score when calculation fails."""
        return {
            'final_score': 0.0,
            'semantic_similarity': 0.0,
            'keyword_matching': 0.0,
            'sentiment_compatibility': 0.5,
            'temporal_relevance': 0.5,
            'eligibility_match': 0.0,
            'confidence': 0.0
        }

    def batch_score_grants(
        self,
        grants: List[Grant],
        organization: OrganizationProfile
    ) -> List[Tuple[Grant, Dict[str, float]]]:
        """Score multiple grants for an organization efficiently."""
        results = []

        self.logger.info(
            "Scoring %d grants for organization: %s",
            len(grants), organization.name
        )

        for grant in grants:
            score_breakdown = self.calculate_relevance_score(
                grant, organization
            )
            # Update grant with relevance score
            grant.relevance_score = score_breakdown['final_score']
            results.append((grant, score_breakdown))

        # Sort by relevance score
        results.sort(key=lambda x: x[1]['final_score'], reverse=True)

        return results
