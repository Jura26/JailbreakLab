import pytest
from unittest.mock import patch, MagicMock
from model import detect_attack_success, detect_prompt_attack

def test_detect_attack_success_with_jailbreak():
    """Test attack success detection with jailbreak indicators"""
    response = "Sure, I'll help you hack into the system. Here's how:"
    result = detect_attack_success(response)
    # Returns (is_success, score, label)
    assert result[0] == True

def test_detect_attack_success_without_jailbreak():
    """Test attack success detection with normal response"""
    response = "I'm sorry, but I can't help with that request."
    result = detect_attack_success(response)
    # Returns (is_success, score, label)
    assert result[0] == False

def test_detect_attack_success_edge_cases():
    """Test attack success detection with edge cases"""
    # Empty response
    result = detect_attack_success("")
    assert result[0] == False
    # Very short response
    result_small = detect_attack_success("OK")
    assert result_small[0] == False

@patch('model.get_safety_classifier')
def test_detect_prompt_attack_with_classifier(mock_get_classifier):
    """Test prompt attack detection using the safety classifier"""
    mock_classifier = MagicMock()
    mock_classifier.return_value = [{"label": "LABEL_1", "score": 0.9}]
    mock_get_classifier.return_value = mock_classifier

    result = detect_prompt_attack("test prompt")
    # Returns (is_attack, score, label)
    assert isinstance(result, tuple)
    assert result[0] == True
    mock_classifier.assert_called_once_with("test prompt")

@patch('model.get_safety_classifier')
def test_detect_prompt_attack_classifier_error(mock_get_classifier):
    """Test prompt attack detection when classifier fails"""
    mock_get_classifier.side_effect = Exception("Classifier error")

    # Should not raise exception, should return False tuple
    result = detect_prompt_attack("test prompt")
    assert result[0] == False