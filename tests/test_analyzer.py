import os
import pytest
from core import analyzer

def test_analyze_error(tmp_path):
    # Create a dummy config for testing
    test_config = {
        'ai_analysis': {
            'enabled': True,
            'enable_code_context': True,
            'project_root': str(tmp_path),
            'model': 'ollama/deepseek-r1:1.5b', 
            'api_base': 'http://localhost:11434',
            'model_api_key': '' 
        }
    }

    # Create a dummy python file to act as our "broken code"
    dummy_code = """def calculate_total(items):
    total = 0
    for item in items:
        total += item['price']
    return total

# The error happens here because 'items' is None
calculate_total(None)
"""
    test_file = tmp_path / "test_broken.py"
    test_file.write_text(dummy_code)

    # Mock log and parsed data
    mock_log = 'TypeError: \'NoneType\' object is not iterable in calculate_total'
    mock_parsed_data = {'filepath': 'test_broken.py', 'lineno': 3, 'type': 'python'}

    # We mock the completion call to avoid actual API calls during tests
    # Since we can't easily mock the import inside the module without more complex setup,
    # we'll trust the integration or use unittest.mock if required. 
    # For now, let's just ensure it runs without crashing if the server isn't there,
    # or better, mock `completion`.
    
    from unittest.mock import patch
    with patch('core.analyzer.completion') as mock_completion:
        mock_completion.return_value.choices = [type('obj', (object,), {'message': type('obj', (object,), {'content': 'Mock AI Suggestion'})})]
        
        result = analyzer.analyze_error(mock_log, mock_parsed_data, test_config)
        
        assert "Mock AI Suggestion" in result
        mock_completion.assert_called_once()
