# =========================================================
# advanced_ml_models.py: Advanced ML Models for Question Generation
# =========================================================
# Deep learning models for enhanced question generation and data understanding
# Includes transformer models, neural networks, and specialized ML pipelines

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import pandas as pd
from transformers import (
    AutoTokenizer, AutoModel, AutoModelForSequenceClassification,
    T5ForConditionalGeneration, T5Tokenizer,
    GPT2LMHeadModel, GPT2Tokenizer,
    pipeline
)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import tensorflow as tf
from sentence_transformers import SentenceTransformer
import joblib
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import json
from pathlib import Path

@dataclass
class MLModelConfig:
    """Configuration for ML models."""
    model_name: str
    model_type: str  # 'transformer', 'neural_net', 'classical'
    checkpoint_path: Optional[str] = None
    device: str = 'auto'
    max_length: int = 512
    batch_size: int = 16
    learning_rate: float = 2e-5
    num_epochs: int = 3

class QuestionGenerationDataset(Dataset):
    """PyTorch dataset for question generation training."""
    
    def __init__(self, contexts: List[str], questions: List[str], tokenizer, max_length: int = 512):
        self.contexts = contexts
        self.questions = questions
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.contexts)
    
    def __getitem__(self, idx):
        context = str(self.contexts[idx])
        question = str(self.questions[idx])
        
        # Tokenize input and target
        inputs = self.tokenizer(
            context,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        targets = self.tokenizer(
            question,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': inputs['input_ids'].squeeze(),
            'attention_mask': inputs['attention_mask'].squeeze(),
            'labels': targets['input_ids'].squeeze()
        }

class TransformerQuestionGenerator(nn.Module):
    """Advanced transformer model for question generation."""
    
    def __init__(self, model_name: str = "t5-base"):
        super().__init__()
        self.model_name = model_name
        self.tokenizer = T5Tokenizer.from_pretrained(model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(model_name)
        
        # Add special tokens for data analysis
        special_tokens = [
            "<data>", "</data>", "<column>", "</column>",
            "<context>", "</context>", "<smart>", "</smart>"
        ]
        self.tokenizer.add_tokens(special_tokens)
        self.model.resize_token_embeddings(len(self.tokenizer))
    
    def forward(self, input_ids, attention_mask, labels=None):
        return self.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels
        )
    
    def generate_questions(self, context: str, num_questions: int = 5,
                          temperature: float = 0.8) -> List[str]:
        """Generate questions for given context."""
        
        # Prepare input
        input_text = f"<context>{context}</context> Generate {num_questions} SMART questions:"
        inputs = self.tokenizer(
            input_text,
            return_tensors="pt",
            max_length=512,
            truncation=True
        )
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                inputs.input_ids,
                attention_mask=inputs.attention_mask,
                max_length=200,
                num_return_sequences=num_questions,
                temperature=temperature,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        questions = []
        for output in outputs:
            question = self.tokenizer.decode(output, skip_special_tokens=True)
            questions.append(question.strip())
        
        return questions

class NeuralQuestionClassifier(nn.Module):
    """Neural network for question quality classification."""
    
    def __init__(self, input_dim: int = 768, hidden_dim: int = 256, num_classes: int = 5):
        super().__init__()
        
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim // 2, num_classes)
        )
        
        self.softmax = nn.Softmax(dim=1)
    
    def forward(self, x):
        logits = self.encoder(x)
        return self.softmax(logits)

class DataUnderstandingModel:
    """Advanced ML model for data understanding and pattern recognition."""
    
    def __init__(self):
        self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
        self.topic_model = None
        self.clustering_model = None
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
        # Quality prediction model
        self.quality_model = pipeline(
            "text-classification",
            model="microsoft/DialoGPT-medium",
            return_all_scores=True
        )
    
    def analyze_dataset_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze patterns in dataset using ML techniques."""
        
        patterns = {
            'column_relationships': self._analyze_column_relationships(df),
            'data_distribution': self._analyze_data_distribution(df),
            'semantic_groups': self._identify_semantic_groups(df),
            'anomaly_patterns': self._detect_anomaly_patterns(df),
            'temporal_patterns': self._analyze_temporal_patterns(df)
        }
        
        return patterns
    
    def _analyze_column_relationships(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze relationships between columns using correlation and MI."""
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return {'correlation_matrix': {}, 'strong_correlations': []}
        
        # Correlation analysis
        corr_matrix = df[numeric_cols].corr()
        
        # Find strong correlations
        strong_correlations = []
        for i, col1 in enumerate(numeric_cols):
            for j, col2 in enumerate(numeric_cols):
                if i < j and abs(corr_matrix.iloc[i, j]) > 0.7:
                    strong_correlations.append({
                        'column1': col1,
                        'column2': col2,
                        'correlation': corr_matrix.iloc[i, j],
                        'relationship_type': 'positive' if corr_matrix.iloc[i, j] > 0 else 'negative'
                    })
        
        return {
            'correlation_matrix': corr_matrix.to_dict(),
            'strong_correlations': strong_correlations
        }
    
    def _analyze_data_distribution(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze data distribution patterns."""
        
        distribution_info = {}
        
        for column in df.columns:
            if df[column].dtype in ['int64', 'float64']:
                # Numeric distribution
                distribution_info[column] = {
                    'type': 'numeric',
                    'mean': float(df[column].mean()),
                    'std': float(df[column].std()),
                    'skewness': float(df[column].skew()),
                    'kurtosis': float(df[column].kurtosis()),
                    'outlier_count': len(df[column][np.abs(df[column] - df[column].mean()) > 2 * df[column].std()])
                }
            else:
                # Categorical distribution
                value_counts = df[column].value_counts()
                distribution_info[column] = {
                    'type': 'categorical',
                    'unique_count': df[column].nunique(),
                    'most_common': value_counts.head(5).to_dict(),
                    'entropy': float(-np.sum(value_counts / len(df) * np.log2(value_counts / len(df) + 1e-10)))
                }
        
        return distribution_info
    
    def _identify_semantic_groups(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Identify semantic groups of columns using embeddings."""
        
        # Create column descriptions
        column_descriptions = []
        for col in df.columns:
            sample_values = df[col].dropna().astype(str).head(5).tolist()
            description = f"Column {col}: {', '.join(sample_values)}"
            column_descriptions.append(description)
        
        # Generate embeddings
        embeddings = self.sentence_transformer.encode(column_descriptions)
        
        # Cluster columns
        n_clusters = min(5, len(df.columns) // 2) if len(df.columns) > 3 else 2
        if len(df.columns) > 1:
            clustering = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = clustering.fit_predict(embeddings)
            
            # Group columns by cluster
            semantic_groups = {}
            for i, col in enumerate(df.columns):
                cluster_id = f"group_{cluster_labels[i]}"
                if cluster_id not in semantic_groups:
                    semantic_groups[cluster_id] = []
                semantic_groups[cluster_id].append(col)
        else:
            semantic_groups = {"group_0": list(df.columns)}
        
        return semantic_groups
    
    def _detect_anomaly_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect anomaly patterns in the data."""
        
        anomalies = {}
        
        for column in df.columns:
            if df[column].dtype in ['int64', 'float64']:
                # Statistical anomalies
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
                
                anomalies[column] = {
                    'outlier_count': len(outliers),
                    'outlier_percentage': len(outliers) / len(df) * 100,
                    'bounds': {'lower': float(lower_bound), 'upper': float(upper_bound)}
                }
            else:
                # Categorical anomalies (rare values)
                value_counts = df[column].value_counts()
                rare_threshold = len(df) * 0.01  # Less than 1% of data
                
                rare_values = value_counts[value_counts < rare_threshold]
                
                anomalies[column] = {
                    'rare_value_count': len(rare_values),
                    'rare_values': rare_values.to_dict()
                }
        
        return anomalies
    
    def _analyze_temporal_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze temporal patterns if datetime columns exist."""
        
        temporal_patterns = {}
        
        # Try to identify datetime columns
        datetime_cols = []
        for col in df.columns:
            if df[col].dtype == 'datetime64[ns]' or 'date' in col.lower() or 'time' in col.lower():
                try:
                    pd.to_datetime(df[col])
                    datetime_cols.append(col)
                except:
                    pass
        
        for col in datetime_cols:
            try:
                dt_series = pd.to_datetime(df[col])
                
                temporal_patterns[col] = {
                    'date_range': {
                        'start': dt_series.min().isoformat(),
                        'end': dt_series.max().isoformat()
                    },
                    'frequency_analysis': self._analyze_date_frequency(dt_series),
                    'seasonal_patterns': self._detect_seasonal_patterns(dt_series)
                }
            except Exception as e:
                temporal_patterns[col] = {'error': str(e)}
        
        return temporal_patterns
    
    def _analyze_date_frequency(self, dt_series: pd.Series) -> Dict[str, Any]:
        """Analyze frequency patterns in datetime series."""
        
        # Group by different time units
        daily_counts = dt_series.dt.date.value_counts()
        monthly_counts = dt_series.dt.to_period('M').value_counts()
        
        return {
            'daily_avg': float(daily_counts.mean()),
            'monthly_avg': float(monthly_counts.mean()),
            'most_active_day': str(daily_counts.index[0]) if len(daily_counts) > 0 else None,
            'most_active_month': str(monthly_counts.index[0]) if len(monthly_counts) > 0 else None
        }
    
    def _detect_seasonal_patterns(self, dt_series: pd.Series) -> Dict[str, Any]:
        """Detect seasonal patterns in datetime series."""
        
        # Simple seasonal analysis
        month_counts = dt_series.dt.month.value_counts().sort_index()
        weekday_counts = dt_series.dt.dayofweek.value_counts().sort_index()
        
        return {
            'monthly_distribution': month_counts.to_dict(),
            'weekday_distribution': weekday_counts.to_dict(),
            'peak_month': int(month_counts.idxmax()) if len(month_counts) > 0 else None,
            'peak_weekday': int(weekday_counts.idxmax()) if len(weekday_counts) > 0 else None
        }

class AdvancedMLQuestionGenerator:
    """Advanced ML-powered question generator using multiple models."""
    
    def __init__(self, model_config: MLModelConfig):
        self.config = model_config
        self.device = self._setup_device()
        
        # Initialize models
        self.transformer_generator = TransformerQuestionGenerator(model_config.model_name)
        self.quality_classifier = NeuralQuestionClassifier()
        self.data_understanding = DataUnderstandingModel()
        
        # Load pre-trained weights if available
        self._load_models()
        
        self.logger = logging.getLogger("AdvancedMLQuestionGenerator")
    
    def _setup_device(self) -> torch.device:
        """Setup computation device."""
        if self.config.device == 'auto':
            return torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        return torch.device(self.config.device)
    
    def _load_models(self):
        """Load pre-trained model weights."""
        if self.config.checkpoint_path and Path(self.config.checkpoint_path).exists():
            try:
                checkpoint = torch.load(self.config.checkpoint_path, map_location=self.device)
                
                if 'transformer_generator' in checkpoint:
                    self.transformer_generator.load_state_dict(checkpoint['transformer_generator'])
                
                if 'quality_classifier' in checkpoint:
                    self.quality_classifier.load_state_dict(checkpoint['quality_classifier'])
                
                self.logger.info(f"Loaded models from {self.config.checkpoint_path}")
            except Exception as e:
                self.logger.warning(f"Failed to load models: {e}")
    
    def generate_enhanced_questions(self, dataset_name: str, df: pd.DataFrame,
                                  context: Dict[str, Any],
                                  num_questions: int = 20) -> List[Dict[str, Any]]:
        """Generate enhanced questions using advanced ML models."""
        
        # Step 1: Analyze dataset with ML models
        self.logger.info("Analyzing dataset patterns with ML models...")
        dataset_patterns = self.data_understanding.analyze_dataset_patterns(df)
        
        # Step 2: Create enriched context
        enriched_context = self._create_enriched_context(df, context, dataset_patterns)
        
        # Step 3: Generate questions using transformer
        self.logger.info("Generating questions with transformer model...")
        questions = self._generate_questions_with_transformer(
            dataset_name, df, enriched_context, num_questions
        )
        
        # Step 4: Classify and score questions
        self.logger.info("Scoring questions with neural classifier...")
        scored_questions = self._score_questions_with_ml(questions, enriched_context)
        
        # Step 5: Apply pattern-based improvements
        enhanced_questions = self._enhance_questions_with_patterns(
            scored_questions, dataset_patterns
        )
        
        # Step 6: Final ranking and selection
        final_questions = self._rank_and_select_questions(
            enhanced_questions, num_questions
        )
        
        return final_questions
    
    def _create_enriched_context(self, df: pd.DataFrame, context: Dict[str, Any],
                               patterns: Dict[str, Any]) -> str:
        """Create enriched context for question generation."""
        
        # Base context
        context_parts = [
            f"Dataset: {len(df)} rows, {len(df.columns)} columns",
            f"Subject Area: {context.get('subject_area', 'general')}",
            f"Target Audience: {context.get('target_audience', 'analysts')}"
        ]
        
        # Add pattern insights
        if patterns.get('column_relationships', {}).get('strong_correlations'):
            correlations = patterns['column_relationships']['strong_correlations']
            context_parts.append(f"Strong correlations found: {len(correlations)} relationships")
        
        if patterns.get('semantic_groups'):
            groups = patterns['semantic_groups']
            context_parts.append(f"Column groups identified: {len(groups)} semantic clusters")
        
        if patterns.get('temporal_patterns'):
            temp_cols = list(patterns['temporal_patterns'].keys())
            if temp_cols:
                context_parts.append(f"Temporal data: {len(temp_cols)} time-based columns")
        
        # Add data quality insights
        anomaly_info = patterns.get('anomaly_patterns', {})
        outlier_cols = [col for col, info in anomaly_info.items() 
                       if isinstance(info, dict) and info.get('outlier_count', 0) > 0]
        if outlier_cols:
            context_parts.append(f"Data quality: {len(outlier_cols)} columns with outliers")
        
        return " | ".join(context_parts)
    
    def _generate_questions_with_transformer(self, dataset_name: str, df: pd.DataFrame,
                                           context: str, num_questions: int) -> List[str]:
        """Generate questions using transformer model."""
        
        # Create detailed prompt for transformer
        column_info = []
        for col in df.columns[:10]:  # Limit to first 10 columns
            dtype = str(df[col].dtype)
            sample_values = df[col].dropna().astype(str).head(3).tolist()
            column_info.append(f"{col} ({dtype}): {', '.join(sample_values)}")
        
        prompt = f"""
        <data>
        Dataset: {dataset_name}
        Context: {context}
        Columns: {' | '.join(column_info)}
        </data>
        
        Generate {num_questions} SMART analytical questions for this dataset:
        """
        
        # Use transformer to generate questions
        questions = self.transformer_generator.generate_questions(
            prompt, num_questions, temperature=0.8
        )
        
        return questions
    
    def _score_questions_with_ml(self, questions: List[str],
                                context: str) -> List[Dict[str, Any]]:
        """Score questions using ML models."""
        
        scored_questions = []
        
        for question in questions:
            # Generate embeddings for question and context
            question_embedding = self.data_understanding.sentence_transformer.encode([question])
            context_embedding = self.data_understanding.sentence_transformer.encode([context])
            
            # Calculate relevance score using cosine similarity
            relevance_score = float(cosine_similarity(question_embedding, context_embedding)[0][0])
            
            # Calculate complexity score based on question length and structure
            complexity_score = self._calculate_complexity_score(question)
            
            # Calculate specificity score
            specificity_score = self._calculate_specificity_score(question)
            
            # Overall ML score (weighted combination)
            ml_score = (
                0.4 * relevance_score +
                0.3 * complexity_score +
                0.3 * specificity_score
            )
            
            scored_questions.append({
                'question': question,
                'ml_score': ml_score,
                'relevance_score': relevance_score,
                'complexity_score': complexity_score,
                'specificity_score': specificity_score,
                'ml_generated': True
            })
        
        return scored_questions
    
    def _calculate_complexity_score(self, question: str) -> float:
        """Calculate complexity score for a question."""
        
        # Factors that increase complexity
        complexity_factors = [
            len(question.split()) > 10,  # Length
            '?' in question,  # Question structure
            any(word in question.lower() for word in ['compare', 'analyze', 'relationship', 'pattern', 'trend']),
            any(word in question.lower() for word in ['statistical', 'correlation', 'distribution', 'variance']),
            question.count(',') > 1,  # Multi-part questions
        ]
        
        complexity_score = sum(complexity_factors) / len(complexity_factors)
        return complexity_score
    
    def _calculate_specificity_score(self, question: str) -> float:
        """Calculate specificity score for a question."""
        
        # Factors that increase specificity
        specificity_factors = [
            any(word in question.lower() for word in ['specific', 'particular', 'exactly', 'precisely']),
            question.count('%') > 0 or question.count('$') > 0,  # Specific metrics
            any(word in question.lower() for word in ['top', 'bottom', 'highest', 'lowest', 'maximum', 'minimum']),
            any(word in question.lower() for word in ['average', 'median', 'mean', 'standard deviation']),
            len([word for word in question.split() if word.isupper()]) > 0,  # Proper nouns/acronyms
        ]
        
        specificity_score = sum(specificity_factors) / len(specificity_factors)
        return specificity_score
    
    def _enhance_questions_with_patterns(self, scored_questions: List[Dict[str, Any]],
                                       patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Enhance questions based on discovered patterns."""
        
        enhanced_questions = scored_questions.copy()
        
        # Add pattern-specific questions
        if patterns.get('column_relationships', {}).get('strong_correlations'):
            correlations = patterns['column_relationships']['strong_correlations']
            for corr in correlations[:3]:  # Top 3 correlations
                pattern_question = {
                    'question': f"What explains the {corr['relationship_type']} correlation between {corr['column1']} and {corr['column2']}?",
                    'ml_score': 0.85,
                    'pattern_based': True,
                    'pattern_type': 'correlation',
                    'pattern_strength': abs(corr['correlation'])
                }
                enhanced_questions.append(pattern_question)
        
        # Add temporal pattern questions
        if patterns.get('temporal_patterns'):
            for col, temp_info in patterns['temporal_patterns'].items():
                if 'date_range' in temp_info:
                    pattern_question = {
                        'question': f"What trends can be observed in the data over the time period from {temp_info['date_range']['start'][:10]} to {temp_info['date_range']['end'][:10]}?",
                        'ml_score': 0.80,
                        'pattern_based': True,
                        'pattern_type': 'temporal',
                        'temporal_column': col
                    }
                    enhanced_questions.append(pattern_question)
        
        # Add anomaly pattern questions
        anomalies = patterns.get('anomaly_patterns', {})
        high_outlier_cols = [col for col, info in anomalies.items() 
                           if isinstance(info, dict) and info.get('outlier_percentage', 0) > 5]
        
        for col in high_outlier_cols[:2]:  # Top 2 outlier columns
            pattern_question = {
                'question': f"What factors might explain the outliers in {col}? Are these data errors or genuine extreme values?",
                'ml_score': 0.75,
                'pattern_based': True,
                'pattern_type': 'anomaly',
                'outlier_column': col
            }
            enhanced_questions.append(pattern_question)
        
        return enhanced_questions
    
    def _rank_and_select_questions(self, questions: List[Dict[str, Any]],
                                 num_questions: int) -> List[Dict[str, Any]]:
        """Rank and select the best questions."""
        
        # Sort by ML score
        questions.sort(key=lambda x: x.get('ml_score', 0), reverse=True)
        
        # Ensure diversity by avoiding too similar questions
        selected_questions = []
        question_embeddings = []
        
        for question_data in questions:
            if len(selected_questions) >= num_questions:
                break
            
            question_text = question_data['question']
            question_embedding = self.data_understanding.sentence_transformer.encode([question_text])
            
            # Check similarity with already selected questions
            is_similar = False
            for existing_embedding in question_embeddings:
                similarity = cosine_similarity(question_embedding, existing_embedding)[0][0]
                if similarity > 0.8:  # Too similar
                    is_similar = True
                    break
            
            if not is_similar:
                selected_questions.append(question_data)
                question_embeddings.append(question_embedding)
        
        return selected_questions
    
    def train_models(self, training_data: List[Dict[str, Any]]):
        """Train the ML models with custom data."""
        
        # Prepare training data
        contexts = [item['context'] for item in training_data]
        questions = [item['question'] for item in training_data]
        quality_scores = [item.get('quality_score', 0.5) for item in training_data]
        
        # Train transformer generator
        self._train_transformer_generator(contexts, questions)
        
        # Train quality classifier
        self._train_quality_classifier(questions, quality_scores)
        
        self.logger.info("Model training completed")
    
    def _train_transformer_generator(self, contexts: List[str], questions: List[str]):
        """Train the transformer question generator."""
        
        dataset = QuestionGenerationDataset(
            contexts, questions, 
            self.transformer_generator.tokenizer,
            self.config.max_length
        )
        
        dataloader = DataLoader(
            dataset, 
            batch_size=self.config.batch_size,
            shuffle=True
        )
        
        optimizer = optim.AdamW(
            self.transformer_generator.parameters(),
            lr=self.config.learning_rate
        )
        
        self.transformer_generator.train()
        
        for epoch in range(self.config.num_epochs):
            total_loss = 0
            
            for batch in dataloader:
                optimizer.zero_grad()
                
                outputs = self.transformer_generator(
                    input_ids=batch['input_ids'].to(self.device),
                    attention_mask=batch['attention_mask'].to(self.device),
                    labels=batch['labels'].to(self.device)
                )
                
                loss = outputs.loss
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            
            avg_loss = total_loss / len(dataloader)
            self.logger.info(f"Epoch {epoch+1}/{self.config.num_epochs}, Loss: {avg_loss:.4f}")
    
    def _train_quality_classifier(self, questions: List[str], quality_scores: List[float]):
        """Train the quality classifier."""
        
        # Generate embeddings for questions
        question_embeddings = self.data_understanding.sentence_transformer.encode(questions)
        
        # Convert quality scores to classes (0-4)
        quality_classes = [min(int(score * 5), 4) for score in quality_scores]
        
        # Create dataset and dataloader
        X = torch.FloatTensor(question_embeddings)
        y = torch.LongTensor(quality_classes)
        
        dataset = torch.utils.data.TensorDataset(X, y)
        dataloader = DataLoader(dataset, batch_size=self.config.batch_size, shuffle=True)
        
        optimizer = optim.Adam(self.quality_classifier.parameters(), lr=self.config.learning_rate)
        criterion = nn.CrossEntropyLoss()
        
        self.quality_classifier.train()
        
        for epoch in range(self.config.num_epochs):
            total_loss = 0
            
            for batch_x, batch_y in dataloader:
                optimizer.zero_grad()
                
                outputs = self.quality_classifier(batch_x.to(self.device))
                loss = criterion(outputs, batch_y.to(self.device))
                
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            
            avg_loss = total_loss / len(dataloader)
            self.logger.info(f"Quality Classifier Epoch {epoch+1}/{self.config.num_epochs}, Loss: {avg_loss:.4f}")
    
    def save_models(self, checkpoint_path: str):
        """Save trained models."""
        
        checkpoint = {
            'transformer_generator': self.transformer_generator.state_dict(),
            'quality_classifier': self.quality_classifier.state_dict(),
            'config': self.config
        }
        
        torch.save(checkpoint, checkpoint_path)
        self.logger.info(f"Models saved to {checkpoint_path}")

# Configuration for different model setups
DEFAULT_CONFIG = MLModelConfig(
    model_name="t5-small",
    model_type="transformer",
    device="auto",
    max_length=512,
    batch_size=8,
    learning_rate=2e-5,
    num_epochs=3
)

ADVANCED_CONFIG = MLModelConfig(
    model_name="t5-base",
    model_type="transformer",
    device="auto",
    max_length=768,
    batch_size=16,
    learning_rate=1e-5,
    num_epochs=5
)

def create_advanced_ml_generator(config: MLModelConfig = None) -> AdvancedMLQuestionGenerator:
    """Create an advanced ML question generator."""
    if config is None:
        config = DEFAULT_CONFIG
    
    return AdvancedMLQuestionGenerator(config)
