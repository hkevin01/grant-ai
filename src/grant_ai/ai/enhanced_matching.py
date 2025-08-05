"""
Enhanced ML-based Grant Matching

Provides intelligent grant matching algorithms using advanced ML techniques.
"""

from pathlib import Path
from typing import Dict, List, Tuple

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from grant_ai.models.grant import Grant
from grant_ai.models.organization import OrganizationProfile


class EnhancedGrantMatcher:
    """Advanced ML-based grant matching system."""

    def __init__(self, model_dir: str = "data/models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=10000,
            ngram_range=(1, 2)
        )
        self.success_model_path = self.model_dir / "success_model.joblib"
        self._load_or_create_success_model()

    def _load_or_create_success_model(self):
        """Load existing success prediction model or create new one."""
        if self.success_model_path.exists():
            self.success_model = joblib.load(self.success_model_path)
        else:
            from sklearn.ensemble import GradientBoostingClassifier
            self.success_model = GradientBoostingClassifier()

    def train_success_model(
        self,
        successful_grants: List[Grant],
        unsuccessful_grants: List[Grant]
    ) -> None:
        """Train the grant success prediction model."""
        # Combine grant texts
        all_grants = successful_grants + unsuccessful_grants
        grant_texts = [
            f"{g.title} {g.description} {' '.join(g.focus_areas)}"
            for g in all_grants
        ]

        # Create feature vectors
        X = self.vectorizer.fit_transform(grant_texts)
        y = [1] * len(successful_grants) + [0] * len(unsuccessful_grants)

        # Train model
        self.success_model.fit(X, y)

        # Save model
        joblib.dump(self.success_model, self.success_model_path)

    def predict_success_probability(
        self,
        grant: Grant,
        org: OrganizationProfile
    ) -> Tuple[float, Dict[str, float]]:
        """Predict probability of success for a grant application."""
        # Create feature vector
        grant_text = (
            f"{grant.title} {grant.description} "
            f"{' '.join(grant.focus_areas)}"
        )
        org_text = (
            f"{org.name} {org.description} "
            f"{' '.join(org.focus_areas)}"
        )
        combined_text = f"{grant_text} {org_text}"

        X = self.vectorizer.transform([combined_text])

        # Get base probability
        base_prob = self.success_model.predict_proba(X)[0][1]

        # Calculate additional factors
        org_focus_match = len(
            set(grant.focus_areas) & set(org.focus_areas)
        ) / max(len(grant.focus_areas), 1)

        amount_fit = 1.0
        if grant.amount_typical and org.typical_grant_size:
            amount_diff = abs(
                grant.amount_typical - org.typical_grant_size
            )
            amount_fit = 1 / (1 + amount_diff / org.typical_grant_size)

        # Combine factors
        final_prob = 0.6 * base_prob + 0.25 * org_focus_match + 0.15 * amount_fit

        return final_prob, {
            'base_probability': base_prob,
            'focus_area_match': org_focus_match,
            'amount_fit': amount_fit,
            'final_probability': final_prob
        }

    def find_matching_grants(
        self,
        org: OrganizationProfile,
        available_grants: List[Grant],
        min_similarity: float = 0.3
    ) -> List[Tuple[Grant, float, Dict]]:
        """Find matching grants for an organization using ML."""
        if not available_grants:
            return []

        # Create organization profile vector
        org_text = (
            f"{org.name} {org.description} "
            f"{' '.join(org.focus_areas)}"
        )

        # Create grant vectors
        grant_texts = [
            f"{g.title} {g.description} {' '.join(g.focus_areas)}"
            for g in available_grants
        ]

        # Calculate similarities
        all_texts = [org_text] + grant_texts
        tfidf_matrix = self.vectorizer.fit_transform(all_texts)

        similarities = cosine_similarity(
            tfidf_matrix[0:1], tfidf_matrix[1:]
        )[0]

        # Get success predictions
        matches = []
        for i, (grant, similarity) in enumerate(
            zip(available_grants, similarities)
        ):
            if similarity >= min_similarity:
                success_prob, factors = self.predict_success_probability(
                    grant, org
                )
                matches.append((grant, similarity, {
                    'similarity': similarity,
                    'success_probability': success_prob,
                    **factors
                }))

        # Sort by combined score
        return sorted(
            matches,
            key=lambda x: (x[1] + x[2]['success_probability']) / 2,
            reverse=True
        )
            key=lambda x: (x[1] + x[2]['success_probability']) / 2,
            reverse=True
        )
