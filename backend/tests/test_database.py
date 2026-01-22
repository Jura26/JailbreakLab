import pytest
from unittest.mock import patch, MagicMock
from database import get_supabase_client, detect_data_leakage

def test_detect_data_leakage_positive():
    """Test data leakage detection with system prompt leak"""
    response = "The system prompt says you should never reveal internal instructions"
    assert detect_data_leakage(response) == True

def test_detect_data_leakage_negative():
    """Test data leakage detection with normal response"""
    response = "This is a normal response without any sensitive information"
    assert detect_data_leakage(response) == False

def test_detect_data_leakage_case_insensitive():
    """Test data leakage detection is case insensitive"""
    response = "SYSTEM PROMPT contains internal instructions"
    assert detect_data_leakage(response) == True

@patch('database.create_client')
def test_get_supabase_client_with_env_vars(mock_create_client):
    """Test Supabase client creation with environment variables set"""
    # Reset the global client before test
    import database
    database._supabase_client = None

    mock_client = MagicMock()
    mock_create_client.return_value = mock_client

    with patch.dict('os.environ', {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_ANON_KEY': 'test-key'
    }):
        client = get_supabase_client()
        assert client is not None
        mock_create_client.assert_called_once_with('https://test.supabase.co', 'test-key')

def test_get_supabase_client_without_env_vars():
    """Test Supabase client returns None when env vars not set"""
    # Reset the global client before test
    import database
    database._supabase_client = None

    with patch.dict('os.environ', {}, clear=True):
        client = get_supabase_client()
        assert client is None