import os
import sys
import yaml
import logging
from dotenv import load_dotenv

# Import our custom modules
from core import monitor, parser, analyzer, notifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 1. Load Environment Variables (Security First)
load_dotenv()

import re
import os
import yaml

def load_config(path="config.yaml"):
    """
    Loads the YAML config and interpolates environment variables.
    Syntax: ${VAR_NAME} will be replaced by the value of os.getenv('VAR_NAME')
    """
    if not os.path.exists(path):
        logger.error(f"Config file not found at {path}")
        sys.exit(1)
    
    with open(path, "r") as f:
        content = f.read()

    # REGEX MAGIC: Find all occurrences of ${VAR_NAME}
    pattern = re.compile(r'\$\{(\w+)\}')
    
    def replace_env(match):
        env_var = match.group(1)
        # Get the value from .env or system, return empty string if missing
        value = os.getenv(env_var)
        if value is None:
            logger.warning(f"Config variable ${{{env_var}}} not set in environment.")
            return "" 
        return value

    # Replace variables in the raw text BEFORE parsing YAML
    updated_content = pattern.sub(replace_env, content)
    
    try:
        return yaml.safe_load(updated_content)
    except yaml.YAMLError as e:
        logger.error(f"Error parsing config file: {e}")
        sys.exit(1)

def handle_new_log(entry, config):
    """
    Handles potentially multi-line log entries.
    Scans for the best file/line match to provide context to the AI.
    """
    logger.debug(f"Received log entry: {entry[:50]}...")
    trigger_levels = config['monitoring'].get('trigger_levels', [])
    lines = entry.strip().split('\n')
    
    # 1. Determine if this entry should trigger analysis
    is_error_level = any(level in entry.upper() for level in trigger_levels)
    
    # 2. Look for the best file path match (scanning bottom-up is usually better for traces)
    best_match = None
    ignored_keywords = ['site-packages', 'dist-packages', 'node_modules', '/usr/lib', 'lib/python']
    
    for line in reversed(lines):
        parsed = parser.parse_log_line(line)
        if parsed:
            filepath = parsed['filepath']
            # If it's not a library file, it's our best candidate
            if not any(kw in filepath for kw in ignored_keywords):
                best_match = parsed
                break
            # Store library matches as a fallback if nothing else is found
            if not best_match:
                best_match = parsed

    if not (is_error_level or best_match):
        return

    if best_match:
        logger.info(f"Trace detected: {best_match['filepath']} (Line {best_match['lineno']})")
    elif is_error_level:
        logger.info(f"Trigger Detected: {lines[0][:100]}...")

    # 3. Analyze & Notify
    ai_suggestion = analyzer.analyze_error(entry, best_match, config)
    
    if ai_suggestion:
        notifier.send_slack_alert(entry, ai_suggestion, config)
        notifier.send_email_alert(entry, ai_suggestion, config)

def main():
    logger.info("STARTING LOG ANALYZER")

    # 1. Load Config
    config = load_config()
    
    # 2. Validation
    log_path = config['monitoring']['log_file']
    logger.info(f"Target Log: {log_path}")
    logger.info(f"Triggers: {config['monitoring']['trigger_levels']}")
    
    # 3. Define the Callback
    # We create a wrapper function that passes 'config' to our handler
    def on_new_line(line):
        handle_new_log(line, config)

    # 4. Start Monitoring
    # This blocks the script and keeps it running forever
    monitor.start_monitoring(config, on_new_line)

if __name__ == "__main__":
    main()