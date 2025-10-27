#!/usr/bin/env python3
"""
Test script for SMART components to verify everything is working correctly.
"""

def test_smart_components():
    """Test all SMART components to ensure they're working properly."""
    print('🧪 Testing SMART components...')
    
    try:
        # Test imports
        from smart_question_generator import SMARTQuestionGenerator, DatasetContext
        from context_collector import ContextCollector  
        from smart_validator import SMARTValidator
        import pandas as pd
        print('✅ All imports successful')
        
        # Test context creation
        context = DatasetContext(
            subject_area='financial analysis',
            analysis_objectives=['trend analysis', 'risk assessment'],
            target_audience='financial analysts',
            business_context='Investment portfolio analysis'
        )
        print('✅ DatasetContext created successfully')
        
        # Test validator
        validator = SMARTValidator()
        test_question = 'How do quarterly revenue trends correlate with market volatility over the 2020-2024 period?'
        metrics = validator.validate_question_quality(test_question, context)
        print(f'✅ SMART validation working - Score: {metrics.overall_score:.2f}')
        
        # Test SMART criteria details
        print(f'   - Specific: {metrics.smart_score:.2f}')
        print(f'   - Clarity: {metrics.clarity_score:.2f}')
        print(f'   - Actionability: {metrics.actionability_score:.2f}')
        print(f'   - Relevance: {metrics.relevance_score:.2f}')
        
        # Test generator initialization
        generator = SMARTQuestionGenerator()
        print('✅ SMARTQuestionGenerator initialized successfully')
        
        # Test context collector initialization
        collector = ContextCollector()
        print('✅ ContextCollector initialized successfully')
        
        # Test predefined contexts
        predefined = collector.predefined_contexts
        print(f'✅ {len(predefined)} predefined contexts loaded')
        
        print('🎉 All SMART components working correctly!')
        return True
        
    except Exception as e:
        print(f'❌ Error testing SMART components: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_smart_components()
