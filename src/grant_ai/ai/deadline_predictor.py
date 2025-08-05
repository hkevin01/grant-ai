"""
Grant Deadline Prediction Model.

This module implements machine learning models to predict grant application
deadlines based on historical data and grant patterns.
"""

import json
import logging
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

from grant_ai.models.grant import Grant


class GrantDeadlinePredictionModel:
    """Machine learning model for predicting grant deadlines."""

    def __init__(self, model_dir: str = "data/models"):
        """Initialize the deadline prediction model."""
        self.logger = logging.getLogger(__name__)

        # Model directory setup
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)

        # Model files
        self.model_file = self.model_dir / "deadline_predictor.pkl"
        self.encoder_file = self.model_dir / "label_encoders.pkl"
        self.scaler_file = self.model_dir / "feature_scaler.pkl"
        self.feature_importance_file = (
            self.model_dir / "feature_importance.json"
        )

        # Initialize models and preprocessing
        self.model = None
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.feature_columns = []
        self.is_trained = False

        # Load existing model if available
        self._load_model()

        # Grant type patterns
        self.grant_type_patterns = {
            'research': {
                'keywords': ['research', 'study', 'investigation', 'analysis'],
                'typical_duration': 365,  # days
                'application_window': 60
            },
            'education': {
                'keywords': [
                    'education', 'training', 'workshop', 'curriculum'
                ],
                'typical_duration': 180,
                'application_window': 45
            },
            'community': {
                'keywords': ['community', 'outreach', 'service', 'program'],
                'typical_duration': 90,
                'application_window': 30
            },
            'technology': {
                'keywords': ['technology', 'innovation', 'development', 'AI'],
                'typical_duration': 270,
                'application_window': 45
            },
            'arts': {
                'keywords': ['arts', 'creative', 'cultural', 'music'],
                'typical_duration': 120,
                'application_window': 30
            }
        }

        self.logger.info("Grant deadline prediction model initialized")

    def predict_deadline(
        self,
        grant: Grant,
        confidence_threshold: float = 0.7
    ) -> Dict[str, any]:
        """
        Predict application deadline for a grant.

        Returns prediction with confidence score and reasoning.
        """
        try:
            if not self.is_trained:
                # Use heuristic-based prediction
                return self._heuristic_prediction(grant)

            # Prepare features for ML prediction
            features = self._extract_features(grant)
            if not features:
                return self._heuristic_prediction(grant)

            # Make prediction
            feature_array = np.array([features])
            predicted_days = self.model.predict(feature_array)[0]

            # Calculate confidence
            confidence = self._calculate_prediction_confidence(
                grant, features, predicted_days
            )

            # Calculate predicted deadline
            if grant.posting_date:
                predicted_deadline = grant.posting_date + timedelta(
                    days=int(predicted_days)
                )
            else:
                predicted_deadline = datetime.now() + timedelta(
                    days=int(predicted_days)
                )

            result = {
                'predicted_deadline': predicted_deadline,
                'days_from_posting': int(predicted_days),
                'confidence': confidence,
                'method': 'machine_learning',
                'reasoning': self._generate_prediction_reasoning(
                    grant, predicted_days, confidence
                )
            }

            # Fallback to heuristic if confidence is too low
            if confidence < confidence_threshold:
                heuristic_result = self._heuristic_prediction(grant)
                result['fallback_prediction'] = heuristic_result
                result['recommendation'] = (
                    'Low confidence ML prediction - consider heuristic result'
                )

            return result

        except Exception as e:
            self.logger.error(
                "Error in deadline prediction: %s", str(e)
            )
            return self._heuristic_prediction(grant)

    def train_model(
        self,
        training_grants: List[Grant],
        validation_split: float = 0.2
    ) -> Dict[str, float]:
        """Train the deadline prediction model on historical data."""
        try:
            self.logger.info(
                "Training deadline prediction model with %d grants",
                len(training_grants)
            )

            # Prepare training data
            features_list = []
            targets = []

            for grant in training_grants:
                if (grant.posting_date and grant.application_deadline):
                    features = self._extract_features(grant)
                    if features:
                        days_to_deadline = (
                            grant.application_deadline - grant.posting_date
                        ).days

                        if 1 <= days_to_deadline <= 730:  # 1 day to 2 years
                            features_list.append(features)
                            targets.append(days_to_deadline)

            if len(features_list) < 10:
                self.logger.warning(
                    "Insufficient training data (%d samples)",
                    len(features_list)
                )
                return {'error': 'insufficient_data'}

            # Convert to numpy arrays
            X = np.array(features_list)
            y = np.array(targets)

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=validation_split, random_state=42
            )

            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)

            # Train ensemble model
            self.model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )

            self.model.fit(X_train_scaled, y_train)

            # Evaluate model
            train_pred = self.model.predict(X_train_scaled)
            test_pred = self.model.predict(X_test_scaled)

            metrics = {
                'train_mae': mean_absolute_error(y_train, train_pred),
                'test_mae': mean_absolute_error(y_test, test_pred),
                'train_rmse': np.sqrt(mean_squared_error(y_train, train_pred)),
                'test_rmse': np.sqrt(mean_squared_error(y_test, test_pred)),
                'training_samples': len(X_train),
                'test_samples': len(X_test)
            }

            self.is_trained = True

            # Save model and metrics
            self._save_model()
            self._save_feature_importance()

            self.logger.info(
                "Model training completed. Test MAE: %.2f days",
                metrics['test_mae']
            )

            return metrics

        except Exception as e:
            self.logger.error("Error training model: %s", str(e))
            return {'error': str(e)}

    def _extract_features(self, grant: Grant) -> Optional[List[float]]:
        """Extract numerical features from a grant for ML prediction."""
        try:
            features = []

            # Grant type (categorical -> numerical)
            grant_type = self._classify_grant_type(grant)
            grant_type_encoded = self._encode_categorical(
                'grant_type', grant_type
            )
            features.append(grant_type_encoded)

            # Amount features
            if grant.amount_min and grant.amount_max:
                features.extend([
                    np.log1p(grant.amount_min),  # Log transform
                    np.log1p(grant.amount_max),
                    grant.amount_max - grant.amount_min  # Range
                ])
            elif grant.amount_typical:
                features.extend([
                    np.log1p(grant.amount_typical),
                    np.log1p(grant.amount_typical),
                    0  # No range
                ])
            else:
                features.extend([0, 0, 0])

            # Text-based features
            title_length = len(grant.title) if grant.title else 0
            desc_length = len(grant.description) if grant.description else 0

            features.extend([
                title_length,
                desc_length,
                len(grant.eligibility_criteria) if grant.eligibility_criteria else 0
            ])

            # Source features
            source_encoded = self._encode_categorical('source', grant.source)
            features.append(source_encoded)

            # Temporal features (if posting date available)
            if grant.posting_date:
                posting_date = grant.posting_date
                features.extend([
                    posting_date.month,
                    posting_date.weekday(),
                    posting_date.day
                ])
            else:
                now = datetime.now()
                features.extend([now.month, now.weekday(), now.day])

            # Complexity indicators
            complexity_score = self._calculate_complexity_score(grant)
            features.append(complexity_score)

            return features

        except Exception as e:
            self.logger.warning(
                "Error extracting features for grant %s: %s",
                grant.title, str(e)
            )
            return None

    def _classify_grant_type(self, grant: Grant) -> str:
        """Classify grant into predefined types based on content."""
        text = f"{grant.title} {grant.description}".lower()

        scores = {}
        for grant_type, patterns in self.grant_type_patterns.items():
            score = sum(
                1 for keyword in patterns['keywords']
                if keyword in text
            )
            scores[grant_type] = score

        if scores:
            return max(scores, key=scores.get)
        return 'other'

    def _calculate_complexity_score(self, grant: Grant) -> float:
        """Calculate a complexity score based on grant characteristics."""
        score = 0.0

        # Requirements complexity
        if grant.eligibility_criteria:
            score += len(grant.eligibility_criteria) * 0.1

        # Amount complexity
        if grant.amount_min and grant.amount_max:
            if grant.amount_max > 1000000:  # $1M+
                score += 0.5
            elif grant.amount_max > 100000:  # $100K+
                score += 0.3

        # Text complexity (readability proxy)
        if grant.description:
            sentences = grant.description.count('.') + 1
            words = len(grant.description.split())
            if words > 0:
                avg_sentence_length = words / sentences
                if avg_sentence_length > 20:
                    score += 0.2

        return min(score, 1.0)

    def _encode_categorical(self, column: str, value: str) -> float:
        """Encode categorical values to numerical."""
        if column not in self.label_encoders:
            self.label_encoders[column] = LabelEncoder()
            # Fit with common values
            if column == 'grant_type':
                common_values = list(self.grant_type_patterns.keys()) + ['other']
            elif column == 'source':
                common_values = ['nasa', 'esa', 'nsf', 'doe', 'grants_gov', 'other']
            else:
                common_values = [value]

            self.label_encoders[column].fit(common_values)

        try:
            return float(self.label_encoders[column].transform([value])[0])
        except ValueError:
            # Unknown value - return encoded 'other' or default
            if 'other' in self.label_encoders[column].classes_:
                return float(
                    self.label_encoders[column].transform(['other'])[0]
                )
            return 0.0

    def _heuristic_prediction(self, grant: Grant) -> Dict[str, any]:
        """Fallback heuristic-based deadline prediction."""
        try:
            # Classify grant type
            grant_type = self._classify_grant_type(grant)
            patterns = self.grant_type_patterns.get(
                grant_type, self.grant_type_patterns['community']
            )

            # Base prediction on grant type
            base_days = patterns['application_window']

            # Adjust based on amount
            if grant.amount_max and grant.amount_max > 500000:
                base_days += 30  # Larger grants typically have longer windows
            elif grant.amount_max and grant.amount_max > 100000:
                base_days += 15

            # Adjust based on complexity
            complexity = self._calculate_complexity_score(grant)
            if complexity > 0.5:
                base_days += 15

            # Seasonal adjustments
            current_month = datetime.now().month
            if current_month in [11, 12]:  # End of year
                base_days -= 7
            elif current_month in [6, 7, 8]:  # Summer
                base_days += 7

            # Calculate predicted deadline
            if grant.posting_date:
                predicted_deadline = grant.posting_date + timedelta(
                    days=base_days
                )
            else:
                predicted_deadline = datetime.now() + timedelta(
                    days=base_days
                )

            return {
                'predicted_deadline': predicted_deadline,
                'days_from_posting': base_days,
                'confidence': 0.6,  # Moderate confidence for heuristics
                'method': 'heuristic',
                'grant_type': grant_type,
                'reasoning': f"Based on {grant_type} grant patterns and complexity"
            }

        except Exception as e:
            self.logger.error(
                "Error in heuristic prediction: %s", str(e)
            )
            # Ultimate fallback
            return {
                'predicted_deadline': datetime.now() + timedelta(days=30),
                'days_from_posting': 30,
                'confidence': 0.3,
                'method': 'default_fallback',
                'reasoning': 'Default 30-day prediction due to error'
            }

    def _calculate_prediction_confidence(
        self,
        grant: Grant,
        features: List[float],
        predicted_days: float
    ) -> float:
        """Calculate confidence score for ML prediction."""
        confidence = 0.8  # Base confidence

        # Reduce confidence if features are incomplete
        if 0 in features[:3]:  # Missing amount features
            confidence -= 0.2

        if not grant.posting_date:
            confidence -= 0.1

        # Check if prediction is reasonable
        if predicted_days < 1 or predicted_days > 365:
            confidence -= 0.3

        # Increase confidence if grant matches known patterns
        grant_type = self._classify_grant_type(grant)
        if grant_type in self.grant_type_patterns:
            typical_window = self.grant_type_patterns[grant_type]['application_window']
            if abs(predicted_days - typical_window) < 15:
                confidence += 0.1

        return max(0.1, min(1.0, confidence))

    def _generate_prediction_reasoning(
        self,
        grant: Grant,
        predicted_days: float,
        confidence: float
    ) -> str:
        """Generate human-readable reasoning for the prediction."""
        grant_type = self._classify_grant_type(grant)

        reasons = [
            f"Classified as {grant_type} grant type"
        ]

        if grant.amount_max:
            if grant.amount_max > 500000:
                reasons.append("Large funding amount suggests longer application window")
            elif grant.amount_max < 50000:
                reasons.append("Smaller funding amount suggests shorter application window")

        complexity = self._calculate_complexity_score(grant)
        if complexity > 0.5:
            reasons.append("High complexity requirements may extend deadline")

        if confidence < 0.6:
            reasons.append("Lower confidence due to limited data")

        return "; ".join(reasons)

    def _save_model(self) -> None:
        """Save trained model and preprocessing objects."""
        try:
            if self.model:
                with open(self.model_file, 'wb') as f:
                    pickle.dump(self.model, f)

            if self.label_encoders:
                with open(self.encoder_file, 'wb') as f:
                    pickle.dump(self.label_encoders, f)

            with open(self.scaler_file, 'wb') as f:
                pickle.dump(self.scaler, f)

            self.logger.info("Model saved successfully")

        except Exception as e:
            self.logger.error("Error saving model: %s", str(e))

    def _load_model(self) -> None:
        """Load trained model and preprocessing objects."""
        try:
            if self.model_file.exists():
                with open(self.model_file, 'rb') as f:
                    self.model = pickle.load(f)
                self.is_trained = True

            if self.encoder_file.exists():
                with open(self.encoder_file, 'rb') as f:
                    self.label_encoders = pickle.load(f)

            if self.scaler_file.exists():
                with open(self.scaler_file, 'rb') as f:
                    self.scaler = pickle.load(f)

            if self.is_trained:
                self.logger.info("Pre-trained model loaded successfully")

        except Exception as e:
            self.logger.warning("Error loading model: %s", str(e))
            self.is_trained = False

    def _save_feature_importance(self) -> None:
        """Save feature importance analysis."""
        try:
            if (self.model and hasattr(self.model, 'feature_importances_')):
                feature_names = [
                    'grant_type', 'amount_min_log', 'amount_max_log',
                    'amount_range', 'title_length', 'desc_length',
                    'eligibility_count', 'source', 'month', 'weekday',
                    'day', 'complexity_score'
                ]

                importance_dict = dict(
                    zip(feature_names, self.model.feature_importances_)
                )

                with open(self.feature_importance_file, 'w') as f:
                    json.dump(importance_dict, f, indent=2)

                self.logger.info("Feature importance saved")

        except Exception as e:
            self.logger.warning(
                "Error saving feature importance: %s", str(e)
            )

    def get_model_info(self) -> Dict[str, any]:
        """Get information about the current model."""
        return {
            'is_trained': self.is_trained,
            'model_type': type(self.model).__name__ if self.model else None,
            'feature_count': len(self.feature_columns),
            'model_file_exists': self.model_file.exists(),
            'grant_type_patterns': list(self.grant_type_patterns.keys())
        }
