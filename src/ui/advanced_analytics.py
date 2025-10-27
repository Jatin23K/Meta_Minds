# =========================================================
# advanced_analytics.py: Advanced Analytics Dashboard System
# =========================================================
# Implements comprehensive analytics dashboard with advanced visualizations
# for Meta Minds question quality and performance analysis

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import json
import logging
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Analytics components
from smart_validator import QuestionQualityMetrics, SMARTCriteria
from smart_question_generator import DatasetContext, QuestionType
from ml_learning_system import QuestionFeedback, LearningPattern, AdvancedMLLearningSystem
from performance_optimizer import PerformanceMetrics, get_performance_report

@dataclass
class AnalyticsInsight:
    """Structured insight from analytics."""
    insight_id: str
    category: str  # 'performance', 'quality', 'trends', 'recommendations'
    title: str
    description: str
    value: Any
    trend: str  # 'improving', 'declining', 'stable'
    confidence: float  # 0-1
    recommendations: List[str]
    supporting_data: Dict[str, Any]

class AdvancedAnalyticsDashboard:
    """Comprehensive analytics dashboard for Meta Minds."""
    
    def __init__(self):
        self.insights: List[AnalyticsInsight] = []
        self.charts: Dict[str, go.Figure] = {}
        self.raw_data: Dict[str, Any] = {}
        
        # Color schemes for visualizations
        self.color_schemes = {
            'quality': ['#10b981', '#f59e0b', '#ef4444'],  # Green, Yellow, Red
            'smart': ['#3b82f6', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b'],  # Blue spectrum
            'performance': ['#6366f1', '#8b5cf6', '#d946ef'],  # Purple spectrum
            'categorical': px.colors.qualitative.Set3
        }
    
    def analyze_question_quality_trends(self, quality_reports: Dict[str, Any], 
                                      time_period: str = "all") -> Dict[str, go.Figure]:
        """Analyze and visualize question quality trends."""
        charts = {}
        
        # Overall quality distribution
        all_scores = []
        dataset_names = []
        
        for dataset_name, report in quality_reports.items():
            if 'summary' in report and 'average_score' in report['summary']:
                all_scores.append(report['summary']['average_score'])
                dataset_names.append(dataset_name)
        
        if all_scores:
            # Quality distribution histogram
            fig_hist = px.histogram(
                x=all_scores,
                title="Question Quality Score Distribution",
                labels={'x': 'Quality Score', 'y': 'Count'},
                color_discrete_sequence=[self.color_schemes['quality'][0]]
            )
            fig_hist.add_vline(x=np.mean(all_scores), line_dash="dash", 
                              annotation_text=f"Average: {np.mean(all_scores):.2f}")
            charts['quality_distribution'] = fig_hist
            
            # Quality by dataset bar chart
            fig_bar = px.bar(
                x=dataset_names,
                y=all_scores,
                title="Quality Scores by Dataset",
                labels={'x': 'Dataset', 'y': 'Average Quality Score'},
                color=all_scores,
                color_continuous_scale='RdYlGn'
            )
            fig_bar.add_hline(y=0.8, line_dash="dash", 
                             annotation_text="Excellent Threshold (0.8)")
            charts['quality_by_dataset'] = fig_bar
        
        # SMART criteria radar chart
        charts['smart_criteria_radar'] = self._create_smart_radar_chart(quality_reports)
        
        # Quality trends over time (simulated data for demo)
        charts['quality_trends'] = self._create_quality_trends_chart()
        
        return charts
    
    def _create_smart_radar_chart(self, quality_reports: Dict[str, Any]) -> go.Figure:
        """Create radar chart for SMART criteria analysis."""
        criteria_names = ['Specific', 'Measurable', 'Action-Oriented', 'Relevant', 'Time-Bound']
        
        # Aggregate SMART scores across all datasets
        criteria_scores = {criterion: [] for criterion in criteria_names}
        
        for dataset_name, report in quality_reports.items():
            if 'coverage_analysis' in report:
                coverage = report['coverage_analysis']
                for i, criterion in enumerate(['specific', 'measurable', 'action_oriented', 'relevant', 'time_bound']):
                    if criterion in coverage:
                        criteria_scores[criteria_names[i]].append(coverage[criterion].get('coverage_percentage', 0))
        
        # Calculate averages
        avg_scores = [np.mean(scores) if scores else 50 for scores in criteria_scores.values()]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=avg_scores,
            theta=criteria_names,
            fill='toself',
            name='SMART Coverage',
            line_color=self.color_schemes['smart'][0]
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    ticksuffix="%"
                )
            ),
            title="SMART Criteria Coverage Analysis",
            showlegend=False
        )
        
        return fig
    
    def _create_quality_trends_chart(self) -> go.Figure:
        """Create quality trends over time chart."""
        # Simulated time series data
        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        
        # Simulate improving trend with some noise
        base_trend = np.linspace(0.6, 0.85, 30)
        noise = np.random.normal(0, 0.05, 30)
        quality_scores = np.clip(base_trend + noise, 0, 1)
        
        fig = go.Figure()
        
        # Add main trend line
        fig.add_trace(go.Scatter(
            x=dates,
            y=quality_scores,
            mode='lines+markers',
            name='Quality Score',
            line=dict(color=self.color_schemes['quality'][0], width=3),
            marker=dict(size=6)
        ))
        
        # Add trend line
        z = np.polyfit(range(len(quality_scores)), quality_scores, 1)
        p = np.poly1d(z)
        trend_line = p(range(len(quality_scores)))
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=trend_line,
            mode='lines',
            name='Trend',
            line=dict(color=self.color_schemes['quality'][1], width=2, dash='dash')
        ))
        
        # Add threshold lines
        fig.add_hline(y=0.8, line_dash="dot", line_color="green", 
                     annotation_text="Excellent (0.8)")
        fig.add_hline(y=0.6, line_dash="dot", line_color="orange", 
                     annotation_text="Good (0.6)")
        
        fig.update_layout(
            title="Question Quality Trends Over Time",
            xaxis_title="Date",
            yaxis_title="Average Quality Score",
            yaxis=dict(range=[0, 1]),
            hovermode='x unified'
        )
        
        return fig
    
    def analyze_question_diversity(self, questions: List[str]) -> Dict[str, go.Figure]:
        """Analyze and visualize question diversity."""
        charts = {}
        
        if not questions:
            return charts
        
        # Question type analysis
        question_types = self._categorize_questions(questions)
        
        # Question type pie chart
        fig_pie = px.pie(
            values=list(question_types.values()),
            names=list(question_types.keys()),
            title="Question Type Distribution",
            color_discrete_sequence=self.color_schemes['categorical']
        )
        charts['question_types'] = fig_pie
        
        # Question length distribution
        lengths = [len(q.split()) for q in questions]
        fig_length = px.histogram(
            x=lengths,
            title="Question Length Distribution (Words)",
            labels={'x': 'Number of Words', 'y': 'Count'},
            color_discrete_sequence=[self.color_schemes['smart'][0]]
        )
        fig_length.add_vline(x=np.mean(lengths), line_dash="dash",
                            annotation_text=f"Average: {np.mean(lengths):.1f} words")
        charts['question_length'] = fig_length
        
        # Question complexity heatmap
        charts['complexity_heatmap'] = self._create_complexity_heatmap(questions)
        
        return charts
    
    def _categorize_questions(self, questions: List[str]) -> Dict[str, int]:
        """Categorize questions by type."""
        categories = {
            'Trend Analysis': 0,
            'Relationship Discovery': 0,
            'Performance Metrics': 0,
            'Comparative Analysis': 0,
            'Anomaly Detection': 0,
            'Forecasting': 0,
            'Other': 0
        }
        
        keywords = {
            'Trend Analysis': ['trend', 'over time', 'change', 'growth', 'decline', 'evolution'],
            'Relationship Discovery': ['relationship', 'correlation', 'impact', 'influence', 'affect'],
            'Performance Metrics': ['performance', 'metric', 'kpi', 'measure', 'indicator'],
            'Comparative Analysis': ['compare', 'difference', 'versus', 'between', 'contrast'],
            'Anomaly Detection': ['anomaly', 'outlier', 'unusual', 'exception', 'abnormal'],
            'Forecasting': ['predict', 'forecast', 'future', 'projection', 'estimate']
        }
        
        for question in questions:
            question_lower = question.lower()
            categorized = False
            
            for category, kwords in keywords.items():
                if any(keyword in question_lower for keyword in kwords):
                    categories[category] += 1
                    categorized = True
                    break
            
            if not categorized:
                categories['Other'] += 1
        
        return categories
    
    def _create_complexity_heatmap(self, questions: List[str]) -> go.Figure:
        """Create complexity analysis heatmap."""
        # Analyze different complexity dimensions
        complexity_metrics = []
        
        for i, question in enumerate(questions[:20]):  # Limit to first 20 for visualization
            metrics = {
                'Question': f"Q{i+1}",
                'Length': len(question.split()),
                'Specificity': question.count(',') + question.count(';'),
                'Analytical Terms': sum(1 for term in ['analyze', 'examine', 'evaluate', 'assess'] 
                                     if term in question.lower()),
                'Time References': sum(1 for term in ['time', 'period', 'trend', 'historical'] 
                                     if term in question.lower())
            }
            complexity_metrics.append(metrics)
        
        df = pd.DataFrame(complexity_metrics)
        
        # Normalize for heatmap
        numeric_cols = ['Length', 'Specificity', 'Analytical Terms', 'Time References']
        for col in numeric_cols:
            df[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min()) if df[col].max() > df[col].min() else 0
        
        fig = px.imshow(
            df[numeric_cols].T,
            x=df['Question'],
            y=numeric_cols,
            title="Question Complexity Analysis",
            color_continuous_scale='Viridis',
            aspect='auto'
        )
        
        return fig
    
    def analyze_performance_metrics(self, performance_data: Dict[str, Any]) -> Dict[str, go.Figure]:
        """Analyze and visualize performance metrics."""
        charts = {}
        
        # Cache performance
        cache_stats = performance_data.get('cache_stats', {})
        if cache_stats:
            charts['cache_performance'] = self._create_cache_performance_chart(cache_stats)
        
        # Operation performance
        performance_summary = performance_data.get('performance_summary', {})
        if performance_summary:
            charts['operation_performance'] = self._create_operation_performance_chart(performance_summary)
        
        # System resource utilization
        charts['resource_utilization'] = self._create_resource_utilization_chart()
        
        return charts
    
    def _create_cache_performance_chart(self, cache_stats: Dict[str, Any]) -> go.Figure:
        """Create cache performance visualization."""
        metrics = ['Hit Rate', 'Total Requests', 'Cache Size', 'Memory Usage (MB)']
        values = [
            cache_stats.get('hit_rate', 0) * 100,
            cache_stats.get('total_requests', 0),
            cache_stats.get('entries', 0),
            cache_stats.get('total_size_bytes', 0) / (1024 * 1024)
        ]
        
        # Normalize values for radar chart
        max_values = [100, 1000, 100, 50]  # Representative max values
        normalized_values = [min(v / max_v * 100, 100) for v, max_v in zip(values, max_values)]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=normalized_values,
            theta=metrics,
            fill='toself',
            name='Cache Performance',
            line_color=self.color_schemes['performance'][0]
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            title="Cache Performance Metrics",
            showlegend=False
        )
        
        return fig
    
    def _create_operation_performance_chart(self, performance_summary: Dict[str, Any]) -> go.Figure:
        """Create operation performance chart."""
        operations = list(performance_summary.keys())
        avg_durations = [perf['avg_duration'] for perf in performance_summary.values()]
        counts = [perf['count'] for perf in performance_summary.values()]
        
        # Create subplot with secondary y-axis
        fig = make_subplots(
            specs=[[{"secondary_y": True}]],
            subplot_titles=["Operation Performance Analysis"]
        )
        
        # Add bar chart for average duration
        fig.add_trace(
            go.Bar(
                x=operations,
                y=avg_durations,
                name="Avg Duration (s)",
                marker_color=self.color_schemes['performance'][0]
            ),
            secondary_y=False
        )
        
        # Add line chart for operation count
        fig.add_trace(
            go.Scatter(
                x=operations,
                y=counts,
                mode='lines+markers',
                name="Operation Count",
                line=dict(color=self.color_schemes['performance'][1], width=3),
                marker=dict(size=8)
            ),
            secondary_y=True
        )
        
        # Update axes labels
        fig.update_xaxes(title_text="Operations")
        fig.update_yaxes(title_text="Average Duration (seconds)", secondary_y=False)
        fig.update_yaxes(title_text="Operation Count", secondary_y=True)
        
        fig.update_layout(title_text="Operation Performance Metrics")
        
        return fig
    
    def _create_resource_utilization_chart(self) -> go.Figure:
        """Create system resource utilization chart."""
        # Simulated resource data over time
        time_points = pd.date_range(start='2024-01-01 00:00:00', periods=24, freq='H')
        
        cpu_usage = np.random.normal(45, 10, 24)  # Simulate CPU usage
        memory_usage = np.random.normal(60, 8, 24)  # Simulate memory usage
        cache_hit_rate = np.random.normal(85, 5, 24)  # Simulate cache hit rate
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=time_points,
            y=cpu_usage,
            mode='lines+markers',
            name='CPU Usage (%)',
            line=dict(color=self.color_schemes['performance'][0])
        ))
        
        fig.add_trace(go.Scatter(
            x=time_points,
            y=memory_usage,
            mode='lines+markers',
            name='Memory Usage (%)',
            line=dict(color=self.color_schemes['performance'][1])
        ))
        
        fig.add_trace(go.Scatter(
            x=time_points,
            y=cache_hit_rate,
            mode='lines+markers',
            name='Cache Hit Rate (%)',
            line=dict(color=self.color_schemes['performance'][2])
        ))
        
        fig.update_layout(
            title="System Resource Utilization (24h)",
            xaxis_title="Time",
            yaxis_title="Percentage (%)",
            yaxis=dict(range=[0, 100]),
            hovermode='x unified'
        )
        
        return fig
    
    def generate_insights(self, quality_reports: Dict[str, Any], 
                         performance_data: Dict[str, Any],
                         questions: List[str]) -> List[AnalyticsInsight]:
        """Generate actionable insights from analytics data."""
        insights = []
        
        # Quality insights
        if quality_reports:
            insights.extend(self._generate_quality_insights(quality_reports))
        
        # Performance insights
        if performance_data:
            insights.extend(self._generate_performance_insights(performance_data))
        
        # Diversity insights
        if questions:
            insights.extend(self._generate_diversity_insights(questions))
        
        return insights
    
    def _generate_quality_insights(self, quality_reports: Dict[str, Any]) -> List[AnalyticsInsight]:
        """Generate insights about question quality."""
        insights = []
        
        # Calculate overall metrics
        all_scores = []
        high_quality_count = 0
        total_questions = 0
        
        for report in quality_reports.values():
            if 'summary' in report:
                summary = report['summary']
                all_scores.append(summary.get('average_score', 0))
                high_quality_count += summary.get('high_quality_count', 0)
                total_questions += summary.get('total_questions', 0)
        
        if all_scores:
            avg_quality = np.mean(all_scores)
            
            # Overall quality insight
            if avg_quality >= 0.8:
                trend = "excellent"
                recommendations = ["Maintain current quality standards", "Share best practices across datasets"]
            elif avg_quality >= 0.7:
                trend = "good"
                recommendations = ["Focus on improving SMART compliance", "Enhance specificity in questions"]
            else:
                trend = "needs_improvement"
                recommendations = ["Review question generation process", "Increase focus on measurable outcomes"]
            
            insights.append(AnalyticsInsight(
                insight_id="overall_quality",
                category="quality",
                title="Overall Question Quality",
                description=f"Average quality score across all datasets is {avg_quality:.2f}",
                value=avg_quality,
                trend=trend,
                confidence=0.9,
                recommendations=recommendations,
                supporting_data={"total_datasets": len(all_scores), "score_range": [min(all_scores), max(all_scores)]}
            ))
            
            # High quality rate insight
            high_quality_rate = high_quality_count / total_questions if total_questions > 0 else 0
            
            insights.append(AnalyticsInsight(
                insight_id="high_quality_rate",
                category="quality",
                title="High-Quality Question Rate",
                description=f"{high_quality_rate:.1%} of questions meet high-quality standards",
                value=high_quality_rate,
                trend="improving" if high_quality_rate > 0.7 else "stable",
                confidence=0.85,
                recommendations=["Target 80%+ high-quality rate", "Focus on underperforming datasets"],
                supporting_data={"high_quality_count": high_quality_count, "total_questions": total_questions}
            ))
        
        return insights
    
    def _generate_performance_insights(self, performance_data: Dict[str, Any]) -> List[AnalyticsInsight]:
        """Generate insights about system performance."""
        insights = []
        
        cache_stats = performance_data.get('cache_stats', {})
        if cache_stats:
            hit_rate = cache_stats.get('hit_rate', 0)
            
            if hit_rate >= 0.8:
                trend = "excellent"
                recommendations = ["Cache strategy is working well", "Monitor for cache size optimization"]
            elif hit_rate >= 0.6:
                trend = "good"
                recommendations = ["Consider increasing cache TTL", "Analyze cache miss patterns"]
            else:
                trend = "needs_improvement"
                recommendations = ["Review caching strategy", "Increase cache size", "Optimize cache keys"]
            
            insights.append(AnalyticsInsight(
                insight_id="cache_performance",
                category="performance",
                title="Cache Hit Rate",
                description=f"Current cache hit rate is {hit_rate:.1%}",
                value=hit_rate,
                trend=trend,
                confidence=0.9,
                recommendations=recommendations,
                supporting_data=cache_stats
            ))
        
        return insights
    
    def _generate_diversity_insights(self, questions: List[str]) -> List[AnalyticsInsight]:
        """Generate insights about question diversity."""
        insights = []
        
        if not questions:
            return insights
        
        # Analyze question diversity
        question_types = self._categorize_questions(questions)
        total_questions = sum(question_types.values())
        
        # Calculate diversity score (entropy-based)
        diversity_score = 0
        for count in question_types.values():
            if count > 0:
                p = count / total_questions
                diversity_score -= p * np.log2(p)
        
        max_diversity = np.log2(len(question_types))
        normalized_diversity = diversity_score / max_diversity if max_diversity > 0 else 0
        
        if normalized_diversity >= 0.8:
            trend = "excellent"
            recommendations = ["Maintain diverse question portfolio", "Continue balanced approach"]
        elif normalized_diversity >= 0.6:
            trend = "good"
            recommendations = ["Slightly increase diversity", "Focus on underrepresented categories"]
        else:
            trend = "needs_improvement"
            recommendations = ["Increase question type diversity", "Balance question categories", "Explore new analytical angles"]
        
        insights.append(AnalyticsInsight(
            insight_id="question_diversity",
            category="diversity",
            title="Question Type Diversity",
            description=f"Question diversity score is {normalized_diversity:.2f} (0-1 scale)",
            value=normalized_diversity,
            trend=trend,
            confidence=0.8,
            recommendations=recommendations,
            supporting_data={"question_types": question_types, "total_questions": total_questions}
        ))
        
        return insights
    
    def create_executive_summary(self, insights: List[AnalyticsInsight]) -> Dict[str, Any]:
        """Create executive summary of analytics findings."""
        summary = {
            "overall_health": "good",
            "key_metrics": {},
            "top_insights": [],
            "priority_actions": [],
            "performance_indicators": {}
        }
        
        # Calculate overall health score
        health_scores = []
        for insight in insights:
            if insight.trend == "excellent":
                health_scores.append(1.0)
            elif insight.trend == "good":
                health_scores.append(0.7)
            elif insight.trend == "stable":
                health_scores.append(0.5)
            else:
                health_scores.append(0.3)
        
        if health_scores:
            avg_health = np.mean(health_scores)
            if avg_health >= 0.8:
                summary["overall_health"] = "excellent"
            elif avg_health >= 0.6:
                summary["overall_health"] = "good"
            else:
                summary["overall_health"] = "needs_attention"
        
        # Extract key metrics
        for insight in insights:
            if insight.category in ["quality", "performance"]:
                summary["key_metrics"][insight.title] = {
                    "value": insight.value,
                    "trend": insight.trend,
                    "confidence": insight.confidence
                }
        
        # Top insights (highest confidence, needs improvement)
        priority_insights = sorted(
            [i for i in insights if i.trend in ["needs_improvement", "excellent"]],
            key=lambda x: x.confidence,
            reverse=True
        )[:3]
        
        summary["top_insights"] = [
            {
                "title": insight.title,
                "description": insight.description,
                "trend": insight.trend
            }
            for insight in priority_insights
        ]
        
        # Priority actions
        all_recommendations = []
        for insight in insights:
            if insight.trend == "needs_improvement":
                all_recommendations.extend(insight.recommendations)
        
        summary["priority_actions"] = list(set(all_recommendations))[:5]
        
        return summary
    
    def export_analytics_report(self, quality_reports: Dict[str, Any],
                               performance_data: Dict[str, Any],
                               questions: List[str]) -> Dict[str, Any]:
        """Export comprehensive analytics report."""
        # Generate all analytics
        quality_charts = self.analyze_question_quality_trends(quality_reports)
        diversity_charts = self.analyze_question_diversity(questions)
        performance_charts = self.analyze_performance_metrics(performance_data)
        insights = self.generate_insights(quality_reports, performance_data, questions)
        executive_summary = self.create_executive_summary(insights)
        
        # Combine all results
        report = {
            "timestamp": datetime.now().isoformat(),
            "executive_summary": executive_summary,
            "insights": [asdict(insight) for insight in insights],
            "charts": {
                "quality": {name: fig.to_json() for name, fig in quality_charts.items()},
                "diversity": {name: fig.to_json() for name, fig in diversity_charts.items()},
                "performance": {name: fig.to_json() for name, fig in performance_charts.items()}
            },
            "raw_data": {
                "quality_reports": quality_reports,
                "performance_data": performance_data,
                "question_count": len(questions)
            }
        }
        
        return report

# Global analytics dashboard instance
analytics_dashboard = AdvancedAnalyticsDashboard()

def generate_comprehensive_analytics(quality_reports: Dict[str, Any],
                                   performance_data: Optional[Dict[str, Any]] = None,
                                   questions: Optional[List[str]] = None) -> Dict[str, Any]:
    """Generate comprehensive analytics report."""
    
    # Use defaults if not provided
    performance_data = performance_data or get_performance_report()
    questions = questions or []
    
    # Generate analytics
    return analytics_dashboard.export_analytics_report(
        quality_reports, performance_data, questions
    )

def create_quality_dashboard_charts(quality_reports: Dict[str, Any]) -> Dict[str, go.Figure]:
    """Create dashboard charts for quality analysis."""
    return analytics_dashboard.analyze_question_quality_trends(quality_reports)

def create_performance_dashboard_charts(performance_data: Dict[str, Any]) -> Dict[str, go.Figure]:
    """Create dashboard charts for performance analysis."""
    return analytics_dashboard.analyze_performance_metrics(performance_data)

def get_actionable_insights(quality_reports: Dict[str, Any],
                          performance_data: Dict[str, Any],
                          questions: List[str]) -> List[AnalyticsInsight]:
    """Get actionable insights from analytics data."""
    return analytics_dashboard.generate_insights(quality_reports, performance_data, questions)
