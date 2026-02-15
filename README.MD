# 🔍 AI Log Analyzer

**AI Log Analyzer** is a lightweight, real-time log monitoring tool that uses Artificial Intelligence to detect errors, analyze stack traces, and suggest code fixes instantly. It supports notifications via **Slack** and **Email**.

> 🚀 **Features**
> - **Real-time Monitoring:** Watches log files as they change.
> - **Smart Parsing:** Automatically detects file paths and line numbers for Python, Node.js, PHP, Ruby, Go, Rust, Java, and C++.
> - **AI Analysis:** Uses LLMs (via `litellm`) to explain errors and suggest specific code fixes.
> - **Context Aware:** Can read the local source code around the error (securely) to provide context-aware solutions.
> - **Multi-Channel Alerts:** Sends notifications to Slack and Email.

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/log-analyzer.git
   cd log-analyzer
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Environment Variables:**
   Copy the example environment file and add your keys.
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your API keys (e.g., OpenAI, Anthropic) and notification credentials.

## ⚙️ Configuration

The application is configured via `config.yaml`. You can customize monitoring triggers, AI models, and notification channels.

### 1. Monitoring Settings
Define where your log file is and what keywords trigger an alert.
```yaml
monitoring:
  log_file: "./app.log"       # Path to the log file you want to watch
  poll_interval: 0.5          # Aggregation delay (seconds) for multi-line logs
  trigger_levels:             # Keywords that trigger analysis
    - "ERROR"
    - "CRITICAL"
```

### 2. AI Settings
Configure the AI provider. This project uses `litellm`, so it supports OpenAI, Claude, Gemini, Ollama, and more.
```yaml
ai_analysis:
  enabled: true
  enable_code_context: true   # specific lines of code will be sent to AI for better context
  project_root: "."           # Root of the source code being monitored
  model: "ollama/deepseek-r1:1.5b" # or "gpt-4o", "claude-3-opus", etc.
```

### 3. Notifications
Enable or disable alerts for specific channels.
```yaml
notifications:
  slack:
    enabled: true
    webhook_url: "${SLACK_WEBHOOK_URL}"
  
  email:
    enabled: true
    recipients: ["user@example.com"]
```

## 🚀 Usage

Start the analyzer by running:

```bash
python main.py
```

The tool will now "tail" the configured log file. It uses a short buffering window (default 0.5s) to aggregate related log lines—such as multi-line stack traces—into a single entry. When it detects an entry containing an error keyword (e.g., `ERROR`), it will:
1. Parse the entry to find the most relevant source file.
2. Read the surrounding code context.
3. Send the data to the AI model.
4. Dispatch an alert with the AI's explanation and suggested fix.

```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
