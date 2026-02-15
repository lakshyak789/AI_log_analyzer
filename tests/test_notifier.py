import os
from unittest.mock import patch, MagicMock
from core import notifier

def test_slack_alert():
    test_config = {
        'notifications': {
            'slack': {
                'enabled': True,
                'webhook_url': 'https://hooks.slack.com/services/TEST/URL'
            }
        }
    }
    
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        
        notifier.send_slack_alert("Error: Test", "Fix: Test", test_config)
        
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs['data'] is not None

def test_email_alert():
    test_config = {
        'notifications': {
            'email': {
                'enabled': True,
                'smtp_server': 'smtp.test.com',
                'smtp_port': 587,
                'sender_email': 'sender@test.com',
                'password': 'password',
                'recipients': ['receiver@test.com']
            }
        }
    }

    with patch('smtplib.SMTP') as mock_smtp:
        instance = mock_smtp.return_value
        
        notifier.send_email_alert("Error: Test", "Fix: Test", test_config)
        
        mock_smtp.assert_called_with('smtp.test.com', 587)
        instance.starttls.assert_called_once()
        instance.login.assert_called_with('sender@test.com', 'password')
        instance.sendmail.assert_called_once()
