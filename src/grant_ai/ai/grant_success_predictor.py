"""
Predictive Grant Success Scoring using Machine Learning

This module implements ML models to predict grant application success
based on organization profile, grant history, and application quality metrics.
"""

import json
import logging
import pickle
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler

from grant_ai.ai.grant_relevance_scorer import GrantRelevanceScorer
from grant_ai.models.grant import Grant
from grant_ai.models.organization import OrganizationProfile


@dataclass
class SuccessPrediction:
    """Container for grant success prediction results."""
    grant_id: str
    organization_id: str
    success_probability: float
    confidence_score: float
    key_factors: List[str]
    recommendation: str
    risk_level: str  # 'Low', 'Medium', 'High'
    predicted_outcome: str  # 'Success', 'Failure', 'Uncertain'

    def to_dict(self) -> Dict:
        """Convert to dictionary format."""
        return {
            'grant_id': self.grant_id,
            'organization_id': self.organization_id,
            'success_probability': self.success_probability,
            'confidence_score': self.confidence_score,
            'key_factors': self.key_factors,
            'recommendation': self.recommendation,
            'risk_level': self.risk_level,
            'predicted_outcome': self.predicted_outcome
        }


class GrantSuccessPredictor:
    """ML-based grant success prediction system."""

    def __init__(self, model_dir: str = "data/models"):
        """Initialize the predictor with model directory."""
        self.logger = logging.getLogger(__name__)
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)

        # Initialize models
        self.classifier = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.text_vectorizer = TfidfVectorizer(
            max_features=500,
            stop_words='english',
            ngram_range=(1, 2)
        )

        # Label encoders for categorical features
        self.label_encoders = {}

        # Feature importance tracking
        self.feature_names = []
        self.feature_importance = {}

        # Grant relevance scorer for compatibility analysis
        self.relevance_scorer = GrantRelevanceScorer()

        # Model performance metrics
        self.model_performance = {}

        self.logger.info("Grant Success Predictor initialized")

    def extract_features(
        self,
        grant: Grant,
        organization: OrganizationProfile,
        historical_data: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Extract comprehensive features for prediction."""
        try:
            features = {}

            # Basic grant features
            features['grant_amount'] = getattr(grant, 'amount_typical', 0)
            features['grant_duration'] = self._estimate_grant_duration(grant)
            features['application_complexity'] = self._assess_complexity(grant)

            # Organization features
            features['org_age'] = self._calculate_org_age(organization)
            features['org_experience'] = len(getattr(organization, 'past_grants', []))
            features['org_focus_alignment'] = self._calculate_focus_alignment(
                grant, organization
            )

            # Historical success features
            if historical_data:
                hist_features = self._extract_historical_features(
                    organization, historical_data
                )
                features.update(hist_features)
            else:
                # Default values if no history
                features.update({
                    'historical_success_rate': 0.5,
                    'avg_grant_amount_won': 0,
                    'total_grants_applied': 0,
                    'recent_success_trend': 0.5,
                    'funder_relationship_score': 0.5
                })

            # Grant relevance features using existing scorer
            relevance_score = self.relevance_scorer.calculate_relevance_score(
                grant, organization
            )
            features.update({
                'relevance_score': relevance_score['final_score'],
                'semantic_similarity': relevance_score['semantic_similarity'],
                'keyword_matching': relevance_score['keyword_matching'],
                'sentiment_compatibility': relevance_score['sentiment_compatibility']
            })

            # Competitive landscape features
            features.update(self._assess_competition(grant))

            # Temporal features
            features.update(self._extract_temporal_features(grant))

            # Text features from grant description
            grant_text = f"{getattr(grant, 'title', '')} {getattr(grant, 'description', '')}"
            features['grant_text'] = grant_text

            return features

        except Exception as e:
            self.logger.error(f"Error extracting features: {e}")
            return {}

    def _estimate_grant_duration(self, grant: Grant) -> float:
        """Estimate grant duration in months."""
        # Heuristic based on grant amount and type
        amount = getattr(grant, 'amount_typical', 0)
        if amount < 10000:
            return 6.0  # Small grants typically 6 months
        elif amount < 100000:
            return 12.0  # Medium grants typically 1 year
        else:
            return 24.0  # Large grants typically 2+ years

    def _assess_complexity(self, grant: Grant) -> float:
        """Assess application complexity score (0-1)."""
        complexity_score = 0.0

        # Factor in grant amount (higher amount = more complex)
        amount = getattr(grant, 'amount_typical', 0)
        if amount > 100000:
            complexity_score += 0.3
        elif amount > 50000:
            complexity_score += 0.2
        else:
            complexity_score += 0.1

        # Factor in focus areas (more areas = more complex)
        focus_areas = getattr(grant, 'focus_areas', [])
        if len(focus_areas) > 3:
            complexity_score += 0.3
        elif len(focus_areas) > 1:
            complexity_score += 0.2
        else:
            complexity_score += 0.1

        # Factor in requirements complexity
        description = getattr(grant, 'description', '')
        if any(word in description.lower() for word in
               ['evaluation', 'partnership', 'collaboration', 'multi-year']):
            complexity_score += 0.2

        return min(complexity_score, 1.0)

    def _calculate_org_age(self, organization: OrganizationProfile) -> float:
        """Calculate organization age in years."""
        # If established date is available, use it
        if hasattr(organization, 'established_date'):
            try:
                established = datetime.fromisoformat(str(organization.established_date))
                return (datetime.now() - established).days / 365.25
            except:
                pass

        # Estimate based on organization maturity indicators
        experience_indicators = len(getattr(organization, 'past_grants', []))
        if experience_indicators > 10:
            return 10.0  # Mature organization
        elif experience_indicators > 5:
            return 5.0   # Established organization
        else:
            return 2.0   # Newer organization

    def _calculate_focus_alignment(
        self,
        grant: Grant,
        organization: OrganizationProfile
    ) -> float:
        """Calculate alignment between grant and organization focus areas."""
        grant_areas = set(getattr(grant, 'focus_areas', []))
        org_areas = set(getattr(organization, 'focus_areas', []))

        if not grant_areas or not org_areas:
            return 0.5  # Neutral if missing data

        # Calculate Jaccard similarity
        intersection = len(grant_areas & org_areas)
        union = len(grant_areas | org_areas)

        return intersection / union if union > 0 else 0.0

    def _extract_historical_features(
        self,
        organization: OrganizationProfile,
        historical_data: List[Dict]
    ) -> Dict[str, float]:
        """Extract features from historical grant data."""
        org_id = getattr(organization, 'id', getattr(organization, 'name', 'unknown'))

        # Filter data for this organization
        org_applications = [
            app for app in historical_data
            if app.get('organization_id') == org_id
        ]

        if not org_applications:
            return {
                'historical_success_rate': 0.5,
                'avg_grant_amount_won': 0,
                'total_grants_applied': 0,
                'recent_success_trend': 0.5,
                'funder_relationship_score': 0.5
            }

        # Calculate success rate
        successful = [app for app in org_applications
                     if app.get('status') in ['awarded', 'funded', 'approved']]
        success_rate = len(successful) / len(org_applications)

        # Average grant amount won
        amounts_won = [app.get('amount_awarded', 0) for app in successful]
        avg_amount_won = np.mean(amounts_won) if amounts_won else 0

        # Recent success trend (last 2 years)
        recent_cutoff = datetime.now() - timedelta(days=730)
        recent_apps = [
            app for app in org_applications
            if app.get('submission_date') and
            datetime.fromisoformat(str(app['submission_date'])) > recent_cutoff
        ]

        if recent_apps:
            recent_successful = [app for app in recent_apps
                               if app.get('status') in ['awarded', 'funded', 'approved']]
            recent_trend = len(recent_successful) / len(recent_apps)
        else:
            recent_trend = success_rate

        # Funder relationship score
        funder_relationships = {}
        for app in org_applications:
            funder = app.get('funder', 'unknown')
            if funder not in funder_relationships:
                funder_relationships[funder] = {'total': 0, 'successful': 0}
            funder_relationships[funder]['total'] += 1
            if app.get('status') in ['awarded', 'funded', 'approved']:
                funder_relationships[funder]['successful'] += 1

        # Calculate weighted average relationship score
        relationship_scores = []
        for funder_data in funder_relationships.values():
            if funder_data['total'] > 0:
                score = funder_data['successful'] / funder_data['total']
                weight = funder_data['total']  # Weight by number of interactions
                relationship_scores.extend([score] * weight)

        avg_relationship_score = np.mean(relationship_scores) if relationship_scores else 0.5

        return {
            'historical_success_rate': success_rate,
            'avg_grant_amount_won': avg_amount_won,
            'total_grants_applied': len(org_applications),
            'recent_success_trend': recent_trend,
            'funder_relationship_score': avg_relationship_score
        }

    def _assess_competition(self, grant: Grant) -> Dict[str, float]:
        """Assess competitive landscape for the grant."""
        # Heuristic assessment based on grant characteristics
        competition_score = 0.5  # Base competition level

        # Higher amounts typically have more competition
        amount = getattr(grant, 'amount_typical', 0)
        if amount > 500000:
            competition_score = 0.8
        elif amount > 100000:
            competition_score = 0.7
        elif amount < 25000:
            competition_score = 0.3

        # Popular focus areas have more competition
        focus_areas = getattr(grant, 'focus_areas', [])
        competitive_areas = {'education', 'health', 'environment', 'technology'}
        if any(area.lower() in competitive_areas for area in focus_areas):
            competition_score += 0.1

        return {
            'competition_level': min(competition_score, 1.0),
            'market_saturation': competition_score * 0.8  # Related metric
        }

    def _extract_temporal_features(self, grant: Grant) -> Dict[str, float]:
        """Extract temporal features from grant timing."""
        features = {}

        # If deadline information is available
        if hasattr(grant, 'deadline_date'):
            try:
                deadline = datetime.fromisoformat(str(grant.deadline_date))
                days_until_deadline = (deadline - datetime.now()).days
                features['days_until_deadline'] = days_until_deadline
                features['deadline_pressure'] = max(0, (30 - days_until_deadline) / 30)
            except:
                features['days_until_deadline'] = 30  # Default
                features['deadline_pressure'] = 0.5
        else:
            features['days_until_deadline'] = 30
            features['deadline_pressure'] = 0.5

        # Seasonal factors
        current_month = datetime.now().month
        features['application_month'] = current_month
        features['is_year_end'] = 1.0 if current_month in [11, 12] else 0.0
        features['is_fiscal_year_end'] = 1.0 if current_month in [6, 9] else 0.0

        return features

    def prepare_training_data(
        self,
        training_data: List[Dict]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data for the model."""
        try:
            X = []
            y = []

            for record in training_data:
                # Create Grant and Organization objects
                grant_data = record.get('grant', {})
                org_data = record.get('organization', {})
                historical_data = record.get('historical_data', [])

                grant = Grant(**grant_data)
                organization = OrganizationProfile(**org_data)

                # Extract features
                features = self.extract_features(grant, organization, historical_data)

                # Prepare feature vector
                feature_vector = self._vectorize_features(features)
                X.append(feature_vector)

                # Target variable (1 for success, 0 for failure)
                outcome = record.get('outcome', 'failure')
                y.append(1 if outcome in ['awarded', 'funded', 'approved'] else 0)

            self.logger.info(f"Prepared training data: {len(X)} samples")
            return np.array(X), np.array(y)

        except Exception as e:
            self.logger.error(f"Error preparing training data: {e}")
            return np.array([]), np.array([])

    def _vectorize_features(self, features: Dict[str, Any]) -> List[float]:
        """Convert feature dictionary to numerical vector."""
        # Extract numerical features
        numerical_features = [
            features.get('grant_amount', 0),
            features.get('grant_duration', 12),
            features.get('application_complexity', 0.5),
            features.get('org_age', 2),
            features.get('org_experience', 0),
            features.get('org_focus_alignment', 0.5),
            features.get('historical_success_rate', 0.5),
            features.get('avg_grant_amount_won', 0),
            features.get('total_grants_applied', 0),
            features.get('recent_success_trend', 0.5),
            features.get('funder_relationship_score', 0.5),
            features.get('relevance_score', 0.5),
            features.get('semantic_similarity', 0.5),
            features.get('keyword_matching', 0.5),
            features.get('sentiment_compatibility', 0.5),
            features.get('competition_level', 0.5),
            features.get('market_saturation', 0.5),
            features.get('days_until_deadline', 30),
            features.get('deadline_pressure', 0.5),
            features.get('application_month', 6),
            features.get('is_year_end', 0),
            features.get('is_fiscal_year_end', 0)
        ]

        return numerical_features

    def train_model(
        self,
        training_data: List[Dict],
        test_size: float = 0.2,
        save_model: bool = True
    ) -> Dict[str, Any]:
        """Train the success prediction model."""
        try:
            # Prepare data
            X, y = self.prepare_training_data(training_data)

            if len(X) == 0:
                raise ValueError("No training data available")

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42, stratify=y
            )

            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)

            # Train model
            self.classifier.fit(X_train_scaled, y_train)

            # Evaluate model
            train_score = self.classifier.score(X_train_scaled, y_train)
            test_score = self.classifier.score(X_test_scaled, y_test)

            # Cross-validation
            cv_scores = cross_val_score(
                self.classifier, X_train_scaled, y_train, cv=5
            )

            # Predictions for detailed metrics
            y_pred = self.classifier.predict(X_test_scaled)

            # Calculate detailed metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, zero_division=0)
            recall = recall_score(y_test, y_pred, zero_division=0)

            # Feature importance
            feature_importance = dict(zip(
                [f'feature_{i}' for i in range(len(X_train[0]))],
                self.classifier.feature_importances_
            ))

            # Store performance metrics
            self.model_performance = {
                'train_score': train_score,
                'test_score': test_score,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'feature_importance': feature_importance,
                'training_samples': len(X_train),
                'test_samples': len(X_test),
                'trained_at': datetime.now().isoformat()
            }

            # Save model if requested
            if save_model:
                self._save_model()

            self.logger.info(f"Model trained successfully. Test accuracy: {accuracy:.3f}")
            return self.model_performance

        except Exception as e:
            self.logger.error(f"Error training model: {e}")
            return {}

    def predict_success(
        self,
        grant: Grant,
        organization: OrganizationProfile,
        historical_data: Optional[List[Dict]] = None
    ) -> SuccessPrediction:
        """Predict grant application success probability."""
        try:
            # Extract features
            features = self.extract_features(grant, organization, historical_data)
            feature_vector = self._vectorize_features(features)

            # Scale features
            feature_vector_scaled = self.scaler.transform([feature_vector])

            # Make prediction
            success_probability = self.classifier.predict_proba(feature_vector_scaled)[0][1]
            confidence_score = max(success_probability, 1 - success_probability)

            # Determine outcome and risk level
            if success_probability >= 0.7:
                predicted_outcome = "Success"
                risk_level = "Low"
            elif success_probability >= 0.4:
                predicted_outcome = "Uncertain"
                risk_level = "Medium"
            else:
                predicted_outcome = "Failure"
                risk_level = "High"

            # Identify key factors
            key_factors = self._identify_key_factors(features, feature_vector)

            # Generate recommendation
            recommendation = self._generate_recommendation(
                success_probability, features, key_factors
            )

            return SuccessPrediction(
                grant_id=getattr(grant, 'id', 'unknown'),
                organization_id=getattr(organization, 'id', getattr(organization, 'name', 'unknown')),
                success_probability=success_probability,
                confidence_score=confidence_score,
                key_factors=key_factors,
                recommendation=recommendation,
                risk_level=risk_level,
                predicted_outcome=predicted_outcome
            )

        except Exception as e:
            self.logger.error(f"Error predicting success: {e}")
            # Return default prediction
            return SuccessPrediction(
                grant_id='unknown',
                organization_id='unknown',
                success_probability=0.5,
                confidence_score=0.5,
                key_factors=[],
                recommendation="Insufficient data for prediction",
                risk_level="Medium",
                predicted_outcome="Uncertain"
            )

    def _identify_key_factors(
        self,
        features: Dict[str, Any],
        feature_vector: List[float]
    ) -> List[str]:
        """Identify key factors influencing the prediction."""
        factors = []

        # Check relevance score
        relevance_score = features.get('relevance_score', 0)
        if relevance_score > 0.8:
            factors.append("Excellent grant-organization alignment")
        elif relevance_score < 0.3:
            factors.append("Poor grant-organization fit")

        # Check historical performance
        historical_success = features.get('historical_success_rate', 0.5)
        if historical_success > 0.7:
            factors.append("Strong historical success rate")
        elif historical_success < 0.3:
            factors.append("Limited historical success")

        # Check competition level
        competition = features.get('competition_level', 0.5)
        if competition > 0.8:
            factors.append("High competition environment")
        elif competition < 0.3:
            factors.append("Low competition opportunity")

        # Check organization experience
        experience = features.get('org_experience', 0)
        if experience > 10:
            factors.append("Extensive grant experience")
        elif experience < 3:
            factors.append("Limited grant experience")

        # Check deadline pressure
        deadline_pressure = features.get('deadline_pressure', 0.5)
        if deadline_pressure > 0.7:
            factors.append("Tight application deadline")

        return factors[:5]  # Return top 5 factors

    def _generate_recommendation(
        self,
        success_probability: float,
        features: Dict[str, Any],
        key_factors: List[str]
    ) -> str:
        """Generate actionable recommendations."""
        if success_probability >= 0.7:
            return "Strong candidate for application. Proceed with confidence and ensure high-quality submission."
        elif success_probability >= 0.5:
            return "Moderate success probability. Consider strengthening application based on key factors identified."
        elif success_probability >= 0.3:
            return "Lower success probability. Evaluate if resources could be better allocated to other opportunities."
        else:
            return "High risk application. Consider improving organizational capacity before applying."

    def _save_model(self):
        """Save the trained model and components."""
        try:
            model_path = self.model_dir / "success_predictor.pkl"
            scaler_path = self.model_dir / "scaler.pkl"
            performance_path = self.model_dir / "performance.json"

            # Save model
            with open(model_path, 'wb') as f:
                pickle.dump(self.classifier, f)

            # Save scaler
            with open(scaler_path, 'wb') as f:
                pickle.dump(self.scaler, f)

            # Save performance metrics
            with open(performance_path, 'w') as f:
                json.dump(self.model_performance, f, indent=2)

            self.logger.info("Model saved successfully")

        except Exception as e:
            self.logger.error(f"Error saving model: {e}")

    def load_model(self) -> bool:
        """Load a previously trained model."""
        try:
            model_path = self.model_dir / "success_predictor.pkl"
            scaler_path = self.model_dir / "scaler.pkl"
            performance_path = self.model_dir / "performance.json"

            if not all(p.exists() for p in [model_path, scaler_path]):
                self.logger.warning("Model files not found")
                return False

            # Load model
            with open(model_path, 'rb') as f:
                self.classifier = pickle.load(f)

            # Load scaler
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)

            # Load performance metrics
            if performance_path.exists():
                with open(performance_path, 'r') as f:
                    self.model_performance = json.load(f)

            self.logger.info("Model loaded successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error loading model: {e}")
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        return {
            'model_type': 'GradientBoostingClassifier',
            'performance_metrics': self.model_performance,
            'feature_count': len(self._vectorize_features({})),
            'is_trained': hasattr(self.classifier, 'feature_importances_'),
            'model_dir': str(self.model_dir)
        }
