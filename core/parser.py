import re

# ==========================================
#  REGEX PATTERNS
# ==========================================
PATTERNS = [
    {
        'lang': 'python',
        # Example: File "src/main.py", line 42, in <module>
        'regex': re.compile(r'File "(?P<path>.*?)", line (?P<line>\d+)')
    },
    {
        'lang': 'node',
        # Example: at Object.<anonymous> (/app/server.js:10:5)
        'regex': re.compile(r'\((?P<path>/.*?):(?P<line>\d+):\d+\)')
    },
    {
        'lang': 'php',
        # Example 1: PHP Fatal error: ... in /var/www/html/index.php on line 14
        # Example 2: ... in /app/config.php:52
        'regex': re.compile(r'in\s+(?P<path>.*\.php)(?:\s+on\s+line\s+|:)(?P<line>\d+)')
    },
    {
        'lang': 'ruby',
        # Example: app/models/user.rb:45:in `save'
        'regex': re.compile(r'(?P<path>.*\.rb):(?P<line>\d+):in')
    },
    {
        'lang': 'java',
        # Example: at com.example.Main.main(Main.java:14)
        'regex': re.compile(r'\((?P<path>.*?\.java):(?P<line>\d+)\)')
    },
    {
        'lang': 'rust',
        # Example: thread 'main' panicked at 'index out of bounds', src/main.rs:4:5
        'regex': re.compile(r'(?:at|-->)\s+(?P<path>.*?):(?P<line>\d+)(?::\d+)?')
    },
    {
        'lang': 'go',
        # Example: /usr/local/go/src/runtime/panic.go:884 +0x212
        'regex': re.compile(r'\s+(?P<path>.*?\.go):(?P<line>\d+)')
    },
    {
        'lang': 'cpp',
        # Example: main.cpp:15:10: error: expected ';'
        'regex': re.compile(r'(?P<path>.*?\.(?:c|cpp|h|hpp)):(?P<line>\d+):')
    }
]

def parse_log_line(log_line):
    """
    Iterates through all known language patterns to find a file path and line number.
    """
    for pattern in PATTERNS:
        match = pattern['regex'].search(log_line)
        if match:
            return {
                'filepath': match.group('path').strip(),
                'lineno': int(match.group('line')),
                'type': pattern['lang']
            }
    
    return None
