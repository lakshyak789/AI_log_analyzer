import os
import smtplib
import requests
import json
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

def send_slack_alert(log_entry, ai_analysis, service_name, config):
    """
    Sends a formatted message to a Slack channel using a Webhook URL.
    """
    # 1. Check if Slack is enabled
    slack_config = config.get('notifications', {}).get('slack', {})
    if not slack_config.get('enabled'):
        return

    # 2. Get Webhook URL (Securely from Env Var)
    webhook_url = slack_config.get('webhook_url')
    if not webhook_url:
        logger.warning("Slack enabled but Webhook URL not found in environment.")
        return

    # 3. Format the Message (using Slack Block Kit for nice formatting)
    payload = {
        "text": f"🚨 *Crash Detected in {service_name}* 🚨",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"Error in {service_name}",
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Error Detected:*\n`{log_entry.strip()}`"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🤖 AI Suggestion:*\n{ai_analysis}"
                }
            }
        ]
    }

    try:
        response = requests.post(
            webhook_url, 
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 200:
            logger.info("Slack alert sent successfully.")
        else:
            logger.error(f"Failed to send Slack alert: {response.text}")
    except Exception as e:
        logger.error(f"Error sending Slack request: {e}")

def send_email_alert(log_entry, ai_analysis, service_name, config):
    """
    Sends an email using standard SMTP.
    """
    # 1. Check if Email is enabled
    logger.debug("Checking email notification settings...")
    email_config = config.get('notifications', {}).get('email', {})
    if not email_config.get('enabled'):
        logger.debug("Email notifications are disabled in config.")
        return

    # 2. Get Credentials
    smtp_server = email_config.get('smtp_server')
    smtp_port = email_config.get('smtp_port')
    sender_email = email_config.get('sender_email')
    recipients = email_config.get('recipients', [])
    
    
    password = email_config.get('password') 

    if not (smtp_server and password):
        logger.warning("Email enabled but missing configuration or password.")
        return

    # 3. Construct Email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ", ".join(recipients)
    msg['Subject'] = f"🚨 Log Error Detected: {log_entry[:50]}..."

    body = f"""
    <h2>Error Detected in Service: {service_name}</h2>
    <pre style="background-color: #f4f4f4; padding: 10px;">{log_entry}</pre>
    
    <h3>🤖 AI Analysis & Fix</h3>
    <div style="white-space: pre-wrap;">{ai_analysis}</div>
    """
    msg.attach(MIMEText(body, 'html'))

    # 4. Send
    try:
        logger.info(f"Connecting to {smtp_server}:{smtp_port}...")
        
        # IF PORT IS 465 -> Use SMTP_SSL (Implicit SSL)
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        
        # IF PORT IS 587 -> Use SMTP + starttls (Explicit TLS)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls() 

        server.login(sender_email, password)
        server.sendmail(sender_email, recipients, msg.as_string())
        server.quit()
        logger.info(f"Email sent to {len(recipients)} recipients.")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")



def send_discord_alert(log_entry, ai_analysis, service_name, config):
    """Sends a formatted alert to a Discord channel."""
    
    discord_config = config.get('notifications', {}).get('discord', {})
    if not discord_config.get('enabled'):
        return

    
    webhook_url = discord_config.get('webhook_url')

    # Truncated strings as  discord limits embed descriptions to 4096 characters and field values to 1024
    safe_error = log_entry[:1000]
    safe_fix = ai_analysis[:1000]

    payload = {
        "username": "AI Log Analyzer",
        "embeds": [
            {
                "title": f"🚨 Crash Detected in {service_name}",
                "description": f"**Raw Error Trace:**\n```python\n{safe_error}\n```",
                "color": 15158332, 
                "fields": [
                    {
                        "name": "🧠 AI Suggested Fix",
                        "value": f"{safe_fix}"
                    }
                ],
                "footer": {
                    "text": "Powered by RAG Middleware"
                }
            }
        ]
    }

    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        print(f"✅ Discord alert sent for {service_name}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to send Discord alert: {e}")
