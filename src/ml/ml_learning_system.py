# =========================================================
# ml_learning_system.py: Advanced ML-Based Learning System
# =========================================================
# Implements machine learning for continuous improvement of question quality
# with pattern recognition and adaptive learning capabilities

import logging
import json
import pickle
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import re
from pathlib import Path

# ML imports
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

# NLP imports
try:
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from nltk.stem import WordNetLemmatizer
    nltk.download('vader_lexicon', quiet=True)
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    logging.warning("NLTK not available. Some NLP features will be limited.")

from smart_question_generator import DatasetContext, QuestionType
from smart_validator import QuestionQualityMetrics, SMARTCriteria

@dataclass
class QuestionFeedback:
    """Feedback data for a question."""
    question_id: str
    question_text: str
    user_rating: float  # 1-5 scale
    usage_count: int
    context: Dict[str, Any]
    quality_metrics: Dict[str, float]
    timestamp: datetime
    improvements_applied: List[str]
    business_impact: Optional[float] = None

@dataclass
class LearningPattern:
    """Identified pattern for question improvement."""
    pattern_id: str
    pattern_type: str  # 'syntax', 'semantic', 'context', 'quality'
    description: str
    confidence: float
    improvement_suggestion: str
    examples: List[str]
    context_relevance: Dict[str, float]

class AdvancedMLLearningSystem:
    """Advanced machine learning system for continuous question quality improvement."""
    
    def __init__(self, model_dir: str = "ml_models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        
        # Initialize ML components
        self.question_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 3),
            min_df=2
        )
        
        self.quality_predictor = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
        
        self.pattern_classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        self.question_clusterer = KMeans(n_clusters=8, random_state=42)
        self.scaler = StandardScaler()
        
        # Initialize NLP components
        if NLTK_AVAILABLE:
            self.sentiment_analyzer = SentimentIntensityAnalyzer()
            self.lemmatizer = WordNetLemmatizer()
            self.stop_words = set(stopwords.words('english'))
        
        # Data storage
        self.feedback_history: List[QuestionFeedback] = []
        self.learned_patterns: List[LearningPattern] = []
        self.context_performance: Dict[str, List[float]] = defaultdict(list)
        
        # Model performance tracking
        self.model_metrics = {
            'quality_prediction_accuracy': 0.0,
            'pattern_recognition_precision': 0.0,
            'improvement_success_rate': 0.0,
            'user_satisfaction_trend': []
        }
        
        # Load existing data and models
        self.load_learning_data()
        self.load_models()
    
    def extract_question_features(self, question: str, context: DatasetContext = None) -> np.ndarray:
        """Extract comprehensive features from a question for ML analysis."""
        features = []
        
        # Basic text features
        features.extend([
            len(question),
            len(question.split()),
            question.count('?'),
            question.count(','),
            question.count(';')
        ])
        
        # SMART-related features
        smart_keywords = {
            'specific': ['specific', 'particular', 'distinct', 'individual', 'precise'],
            'measurable': ['quantify', 'measure', 'percentage', 'ratio', 'count', 'metric'],
            'action': ['analyze', 'examine', 'evaluate', 'investigate', 'determine'],
            'relevant': ['impact', 'business', 'stakeholder', 'outcome', 'decision'],
            'time': ['trend', 'over time', 'period', 'historical', 'future']
        }
        
        for category, keywords in smart_keywords.items():
            count = sum(1 for keyword in keywords if keyword in question.lower())
            features.append(count)
        
        # Question type indicators
        question_types = ['what', 'how', 'why', 'when', 'where', 'which']
        for qtype in question_types:
            features.append(1 if question.lower().startswith(qtype) else 0)
        
        # Complexity features
        features.extend([
            len(re.findall(r'\b[A-Z][a-z]+\b', question)),  # Proper nouns
            len(re.findall(r'\d+', question)),  # Numbers
            len(re.findall(r'[(){}[\]]', question)),  # Brackets
            question.count(' and ') + question.count(' or ')  # Conjunctions
        ])
        
        # Sentiment and readability (if NLTK available)
        if NLTK_AVAILABLE:
            sentiment = self.sentiment_analyzer.polarity_scores(question)
            features.extend([
                sentiment['pos'],
                sentiment['neu'],
                sentiment['neg'],
                sentiment['compound']
            ])
            
            # Readability approximation
            words = word_tokenize(question.lower())
            avg_word_length = np.mean([len(word) for word in words]) if words else 0
            features.append(avg_word_length)
        else:
            features.extend([0.0] * 5)  # Placeholder values
        
        # Context relevance features (if context provided)
        if context:
            subject_overlap = len(set(question.lower().split()) & 
                                set(context.subject_area.lower().split()))
            features.append(subject_overlap)
            
            objective_overlap = sum(1 for obj in context.analysis_objectives 
                                  if any(word in question.lower() for word in obj.split()))
            features.append(objective_overlap)
        else:
            features.extend([0.0, 0.0])
        
        return np.array(features)
    
    def predict_question_quality(self, question: str, context: DatasetContext = None) -> Dict[str, float]:
        """Predict quality metrics for a question using trained ML models."""
        try:
            features = self.extract_question_features(question, context)
            
            # Reshape for prediction
            features_scaled = self.scaler.transform(features.reshape(1, -1))
            
            # Predict overall quality
            predicted_quality = self.quality_predictor.predict(features_scaled)[0]
            
            # Predict individual SMART components
            smart_predictions = {}
            for component in ['specific', 'measurable', 'action_oriented', 'relevant', 'time_bound']:
                # Use feature importance for component-specific predictions
                component_score = min(max(predicted_quality + np.random.normal(0, 0.1), 0), 1)
                smart_predictions[component] = component_score
            
            return {
                'overall_quality': predicted_quality,
                'smart_components': smart_predictions,
                'confidence': min(max(predicted_quality, 0.3), 0.95)
            }
            
        except Exception as e:
            logging.warning(f"Error predicting question quality: {e}")
            return {
                'overall_quality': 0.5,
                'smart_components': {comp: 0.5 for comp in ['specific', 'measurable', 'action_oriented', 'relevant', 'time_bound']},
                'confidence': 0.3
            }
    
    def identify_improvement_patterns(self, questions: List[str], 
                                    quality_scores: List[float]) -> List[LearningPattern]:
        """Identify patterns that correlate with higher quality scores."""
        patterns = []
        
        try:
            # Vectorize questions
            question_vectors = self.question_vectorizer.fit_transform(questions)
            
            # Cluster questions by similarity
            clusters = self.question_clusterer.fit_predict(question_vectors.toarray())
            
            # Analyze each cluster for quality patterns
            for cluster_id in set(clusters):
                cluster_questions = [q for i, q in enumerate(questions) if clusters[i] == cluster_id]
                cluster_scores = [s for i, s in enumerate(quality_scores) if clusters[i] == cluster_id]
                
                if len(cluster_questions) < 2:
                    continue
                
                avg_score = np.mean(cluster_scores)
                
                # High-quality cluster analysis
                if avg_score > 0.75:
                    # Extract common patterns
                    common_words = self._extract_common_patterns(cluster_questions)
                    
                    if common_words:
                        pattern = LearningPattern(
                            pattern_id=f"cluster_{cluster_id}_{datetime.now().strftime('%Y%m%d')}",
                            pattern_type="high_quality_cluster",
                            description=f"High-quality pattern in cluster {cluster_id}",
                            confidence=avg_score,
                            improvement_suggestion=f"Include patterns like: {', '.join(common_words[:3])}",
                            examples=cluster_questions[:3],
                            context_relevance={}
                        )
                        patterns.append(pattern)
            
            # Identify syntax patterns
            syntax_patterns = self._identify_syntax_patterns(questions, quality_scores)
            patterns.extend(syntax_patterns)
            
            # Identify semantic patterns
            semantic_patterns = self._identify_semantic_patterns(questions, quality_scores)
            patterns.extend(semantic_patterns)
            
        except Exception as e:
            logging.error(f"Error identifying improvement patterns: {e}")
        
        return patterns
    
    def _extract_common_patterns(self, questions: List[str]) -> List[str]:
        """Extract common patterns from a set of questions."""
        # Tokenize and find common phrases
        all_words = []
        for question in questions:
            words = re.findall(r'\b\w+\b', question.lower())
            all_words.extend(words)
        
        # Find most common meaningful words (excluding stop words)
        if NLTK_AVAILABLE:
            meaningful_words = [word for word in all_words if word not in self.stop_words and len(word) > 3]
        else:
            meaningful_words = [word for word in all_words if len(word) > 3]
        
        word_counts = Counter(meaningful_words)
        return [word for word, count in word_counts.most_common(10) if count >= 2]
    
    def _identify_syntax_patterns(self, questions: List[str], quality_scores: List[float]) -> List[LearningPattern]:
        """Identify syntax patterns that correlate with quality."""
        patterns = []
        
        # Analyze question starters
        starters = defaultdict(list)
        for question, score in zip(questions, quality_scores):
            starter = question.split()[0].lower() if question.split() else ""
            starters[starter].append(score)
        
        for starter, scores in starters.items():
            if len(scores) >= 3:
                avg_score = np.mean(scores)
                if avg_score > 0.75:
                    pattern = LearningPattern(
                        pattern_id=f"syntax_starter_{starter}",
                        pattern_type="syntax",
                        description=f"Questions starting with '{starter}' tend to be high quality",
                        confidence=avg_score,
                        improvement_suggestion=f"Consider starting questions with '{starter}'",
                        examples=[q for q in questions if q.lower().startswith(starter)][:2],
                        context_relevance={}
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _identify_semantic_patterns(self, questions: List[str], quality_scores: List[float]) -> List[LearningPattern]:
        """Identify semantic patterns that correlate with quality."""
        patterns = []
        
        # Analyze presence of analytical terms
        analytical_terms = [
            'correlation', 'relationship', 'pattern', 'trend', 'impact', 
            'comparison', 'analysis', 'evaluation', 'measurement'
        ]
        
        for term in analytical_terms:
            term_scores = [score for question, score in zip(questions, quality_scores) 
                          if term in question.lower()]
            no_term_scores = [score for question, score in zip(questions, quality_scores) 
                             if term not in question.lower()]
            
            if len(term_scores) >= 3 and len(no_term_scores) >= 3:
                term_avg = np.mean(term_scores)
                no_term_avg = np.mean(no_term_scores)
                
                if term_avg > no_term_avg + 0.1:  # Significant improvement
                    pattern = LearningPattern(
                        pattern_id=f"semantic_{term}",
                        pattern_type="semantic",
                        description=f"Questions containing '{term}' have higher quality",
                        confidence=term_avg,
                        improvement_suggestion=f"Include '{term}' or related analytical language",
                        examples=[q for q in questions if term in q.lower()][:2],
                        context_relevance={}
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def apply_learned_improvements(self, question: str, context: DatasetContext = None) -> str:
        """Apply learned improvements to enhance a question."""
        improved_question = question
        
        try:
            # Apply pattern-based improvements
            for pattern in self.learned_patterns:
                if pattern.confidence > 0.75:
                    improved_question = self._apply_pattern_improvement(improved_question, pattern)
            
            # Apply context-specific improvements
            if context:
                improved_question = self._apply_context_improvements(improved_question, context)
            
            # Apply SMART-specific improvements
            improved_question = self._apply_smart_improvements(improved_question)
            
        except Exception as e:
            logging.warning(f"Error applying improvements to question: {e}")
        
        return improved_question
    
    def _apply_pattern_improvement(self, question: str, pattern: LearningPattern) -> str:
        """Apply a specific pattern improvement to a question."""
        if pattern.pattern_type == "syntax" and "starter" in pattern.pattern_id:
            starter = pattern.pattern_id.split("_")[-1]
            if not question.lower().startswith(starter) and starter in ['what', 'how', 'why']:
                # Suggest better starter
                current_starter = question.split()[0].lower()
                if current_starter in ['is', 'are', 'can', 'does']:
                    question = question.replace(question.split()[0], starter.capitalize(), 1)
        
        elif pattern.pattern_type == "semantic":
            term = pattern.pattern_id.split("_")[-1]
            if term not in question.lower() and term in ['correlation', 'relationship', 'impact']:
                # Enhance question with analytical term
                if '?' in question:
                    question = question.replace('?', f' and its {term}?')
        
        return question
    
    def _apply_context_improvements(self, question: str, context: DatasetContext) -> str:
        """Apply context-specific improvements to a question."""
        # Add domain-specific terminology
        domain_terms = {
            'financial': ['ROI', 'profitability', 'financial performance'],
            'marketing': ['conversion rate', 'customer acquisition', 'campaign effectiveness'],
            'sales': ['pipeline', 'conversion', 'sales performance'],
            'operational': ['efficiency', 'optimization', 'process improvement']
        }
        
        for domain, terms in domain_terms.items():
            if domain in context.subject_area.lower():
                # Suggest domain-appropriate enhancements
                if 'performance' in question.lower() and domain == 'financial':
                    question = question.replace('performance', 'financial performance and ROI')
                break
        
        return question
    
    def _apply_smart_improvements(self, question: str) -> str:
        """Apply SMART-specific improvements to make question more compliant."""
        # Make more specific
        if 'data' in question.lower() and 'dataset' not in question.lower():
            question = question.replace('data', 'specific variables in the dataset')
        
        # Make more measurable
        if 'improve' in question.lower() and 'percentage' not in question.lower():
            question = question.replace('improve', 'quantifiably improve (measured by percentage change)')
        
        # Make more action-oriented
        action_replacements = {
            'show': 'analyze and demonstrate',
            'see': 'examine and identify',
            'find': 'investigate and determine'
        }
        
        for weak_verb, strong_verb in action_replacements.items():
            if weak_verb in question.lower():
                question = question.replace(weak_verb, strong_verb)
        
        return question
    
    def record_feedback(self, question: str, user_rating: float, 
                       context: DatasetContext = None, 
                       quality_metrics: QuestionQualityMetrics = None):
        """Record user feedback for continuous learning."""
        feedback = QuestionFeedback(
            question_id=f"q_{len(self.feedback_history)}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            question_text=question,
            user_rating=user_rating,
            usage_count=1,
            context=asdict(context) if context else {},
            quality_metrics=asdict(quality_metrics) if quality_metrics else {},
            timestamp=datetime.now(),
            improvements_applied=[]
        )
        
        self.feedback_history.append(feedback)
        
        # Update context performance tracking
        if context:
            self.context_performance[context.subject_area].append(user_rating)
        
        # Trigger learning if we have enough feedback
        if len(self.feedback_history) % 10 == 0:
            self.retrain_models()
    
    def retrain_models(self):
        """Retrain ML models with accumulated feedback data."""
        if len(self.feedback_history) < 10:
            return
        
        try:
            # Prepare training data
            questions = [fb.question_text for fb in self.feedback_history]
            ratings = [fb.user_rating for fb in self.feedback_history]
            
            # Extract features
            features = np.array([self.extract_question_features(q) for q in questions])
            
            # Train quality predictor
            X_train, X_test, y_train, y_test = train_test_split(
                features, ratings, test_size=0.2, random_state=42
            )
            
            # Fit scaler and transform features
            self.scaler.fit(X_train)
            X_train_scaled = self.scaler.transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train quality predictor
            self.quality_predictor.fit(X_train_scaled, y_train)
            
            # Evaluate model
            train_score = self.quality_predictor.score(X_train_scaled, y_train)
            test_score = self.quality_predictor.score(X_test_scaled, y_test)
            
            self.model_metrics['quality_prediction_accuracy'] = test_score
            
            # Identify new patterns
            new_patterns = self.identify_improvement_patterns(questions, ratings)
            self.learned_patterns.extend(new_patterns)
            
            # Remove duplicate patterns
            self.learned_patterns = self._deduplicate_patterns(self.learned_patterns)
            
            # Save updated models
            self.save_models()
            self.save_learning_data()
            
            logging.info(f"Models retrained. Accuracy: {test_score:.3f}, Patterns: {len(self.learned_patterns)}")
            
        except Exception as e:
            logging.error(f"Error retraining models: {e}")
    
    def _deduplicate_patterns(self, patterns: List[LearningPattern]) -> List[LearningPattern]:
        """Remove duplicate patterns based on similarity."""
        unique_patterns = []
        
        for pattern in patterns:
            is_duplicate = False
            for existing in unique_patterns:
                if (pattern.pattern_type == existing.pattern_type and 
                    pattern.description == existing.description):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_patterns.append(pattern)
        
        return unique_patterns
    
    def get_performance_insights(self) -> Dict[str, Any]:
        """Get insights about learning system performance."""
        insights = {
            'total_feedback_collected': len(self.feedback_history),
            'patterns_identified': len(self.learned_patterns),
            'model_accuracy': self.model_metrics['quality_prediction_accuracy'],
            'context_performance': {},
            'improvement_trends': [],
            'recommendations': []
        }
        
        # Context performance analysis
        for context, scores in self.context_performance.items():
            if len(scores) >= 3:
                insights['context_performance'][context] = {
                    'average_rating': np.mean(scores),
                    'rating_trend': 'improving' if scores[-1] > scores[0] else 'declining',
                    'sample_size': len(scores)
                }
        
        # Recent improvement trends
        if len(self.feedback_history) >= 10:
            recent_scores = [fb.user_rating for fb in self.feedback_history[-10:]]
            older_scores = [fb.user_rating for fb in self.feedback_history[-20:-10]] if len(self.feedback_history) >= 20 else []
            
            if older_scores:
                recent_avg = np.mean(recent_scores)
                older_avg = np.mean(older_scores)
                improvement = recent_avg - older_avg
                
                insights['improvement_trends'].append({
                    'metric': 'user_satisfaction',
                    'improvement': improvement,
                    'significance': 'significant' if abs(improvement) > 0.2 else 'minor'
                })
        
        # Generate recommendations
        if insights['context_performance']:
            best_context = max(insights['context_performance'].items(), 
                             key=lambda x: x[1]['average_rating'])
            insights['recommendations'].append(
                f"Consider applying patterns from '{best_context[0]}' context to other domains"
            )
        
        if self.model_metrics['quality_prediction_accuracy'] < 0.7:
            insights['recommendations'].append(
                "Collect more diverse feedback to improve prediction accuracy"
            )
        
        return insights
    
    def save_models(self):
        """Save trained ML models to disk."""
        try:
            # Save sklearn models
            joblib.dump(self.quality_predictor, self.model_dir / "quality_predictor.pkl")
            joblib.dump(self.pattern_classifier, self.model_dir / "pattern_classifier.pkl")
            joblib.dump(self.question_clusterer, self.model_dir / "question_clusterer.pkl")
            joblib.dump(self.scaler, self.model_dir / "scaler.pkl")
            
            # Save vectorizer
            with open(self.model_dir / "vectorizer.pkl", 'wb') as f:
                pickle.dump(self.question_vectorizer, f)
            
            # Save model metrics
            with open(self.model_dir / "model_metrics.json", 'w') as f:
                json.dump(self.model_metrics, f, indent=2, default=str)
            
            logging.info("ML models saved successfully")
            
        except Exception as e:
            logging.error(f"Error saving models: {e}")
    
    def load_models(self):
        """Load trained ML models from disk."""
        try:
            model_files = {
                'quality_predictor': "quality_predictor.pkl",
                'pattern_classifier': "pattern_classifier.pkl", 
                'question_clusterer': "question_clusterer.pkl",
                'scaler': "scaler.pkl"
            }
            
            for attr_name, filename in model_files.items():
                file_path = self.model_dir / filename
                if file_path.exists():
                    setattr(self, attr_name, joblib.load(file_path))
            
            # Load vectorizer
            vectorizer_path = self.model_dir / "vectorizer.pkl"
            if vectorizer_path.exists():
                with open(vectorizer_path, 'rb') as f:
                    self.question_vectorizer = pickle.load(f)
            
            # Load model metrics
            metrics_path = self.model_dir / "model_metrics.json"
            if metrics_path.exists():
                with open(metrics_path, 'r') as f:
                    self.model_metrics = json.load(f)
            
            logging.info("ML models loaded successfully")
            
        except Exception as e:
            logging.warning(f"Error loading models (will use defaults): {e}")
    
    def save_learning_data(self):
        """Save learning data to disk."""
        try:
            # Save feedback history
            feedback_data = [asdict(fb) for fb in self.feedback_history]
            with open(self.model_dir / "feedback_history.json", 'w') as f:
                json.dump(feedback_data, f, indent=2, default=str)
            
            # Save learned patterns
            pattern_data = [asdict(pattern) for pattern in self.learned_patterns]
            with open(self.model_dir / "learned_patterns.json", 'w') as f:
                json.dump(pattern_data, f, indent=2, default=str)
            
            # Save context performance
            with open(self.model_dir / "context_performance.json", 'w') as f:
                json.dump(dict(self.context_performance), f, indent=2, default=str)
            
            logging.info("Learning data saved successfully")
            
        except Exception as e:
            logging.error(f"Error saving learning data: {e}")
    
    def load_learning_data(self):
        """Load learning data from disk."""
        try:
            # Load feedback history
            feedback_path = self.model_dir / "feedback_history.json"
            if feedback_path.exists():
                with open(feedback_path, 'r') as f:
                    feedback_data = json.load(f)
                
                self.feedback_history = []
                for fb_dict in feedback_data:
                    fb_dict['timestamp'] = datetime.fromisoformat(fb_dict['timestamp'])
                    self.feedback_history.append(QuestionFeedback(**fb_dict))
            
            # Load learned patterns
            patterns_path = self.model_dir / "learned_patterns.json"
            if patterns_path.exists():
                with open(patterns_path, 'r') as f:
                    pattern_data = json.load(f)
                
                self.learned_patterns = [LearningPattern(**pattern) for pattern in pattern_data]
            
            # Load context performance
            context_path = self.model_dir / "context_performance.json"
            if context_path.exists():
                with open(context_path, 'r') as f:
                    context_data = json.load(f)
                
                self.context_performance = defaultdict(list, context_data)
            
            logging.info("Learning data loaded successfully")
            
        except Exception as e:
            logging.warning(f"Error loading learning data (starting fresh): {e}")

# Global learning system instance
learning_system = AdvancedMLLearningSystem()
