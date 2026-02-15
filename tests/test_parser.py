from core import parser

def test_parse_log_line():
    test_cases = [
        ('File "src/server.py", line 55, in start_server', 'src/server.py', 55, 'python'),
        ('at Object.<anonymous> (/app/routes.js:20:12)', '/app/routes.js', 20, 'node'),
        ('PHP Fatal error: Uncaught TypeError in /var/www/html/index.php on line 14', '/var/www/html/index.php', 14, 'php'),
        ('Parse error: syntax error in /app/config.php:52', '/app/config.php', 52, 'php'),
        ("app/controllers/users_controller.rb:45:in `index'", 'app/controllers/users_controller.rb', 45, 'ruby'),
        ("thread 'main' panicked at 'explicit panic', src/lib.rs:10:5", 'src/lib.rs', 10, 'rust'),
        ("\t/home/user/project/main.go:24 +0x123", '/home/user/project/main.go', 24, 'go'),
        ("at com.mycompany.app.App.main(App.java:15)", 'App.java', 15, 'java'),
        ("src/game.cpp:102:1: error: expected '}' at end of input", 'src/game.cpp', 102, 'cpp')
    ]

    for log_line, expected_path, expected_line, expected_type in test_cases:
        result = parser.parse_log_line(log_line)
        assert result is not None, f"Failed to parse: {log_line}"
        assert result['filepath'].endswith(expected_path), f"Path mismatch for {expected_type}"
        assert result['lineno'] == expected_line
        assert result['type'] == expected_type

def test_parse_invalid_line():
    assert parser.parse_log_line("Just a random log line") is None
