# AI Personal Agent SDK

A comprehensive, secure AI-powered personal assistant SDK that provides 24/7 automation, intelligent planning, and beautiful web interface for managing your digital life.

## Features

### 🤖 AI-Powered Automation
- **Intelligent Planning**: Daily schedule optimization using OpenAI GPT-4
- **Smart Reminders**: Context-aware notifications for meetings and tasks
- **Conversational AI**: Natural language chat interface for assistance

### 🔒 Enterprise-Grade Security
- **End-to-End Encryption**: All data encrypted with AES-256
- **Permission-Based Access**: Granular control over data access with time-limited permissions
- **Hacker Protection**: Continuous monitoring and security alerts
- **Local Data Storage**: No data sent to external servers without explicit permission

### 🔗 Seamless Integrations
- **Google Services**: Gmail, Google Calendar integration
- **Zapier Automation**: Connect with 5000+ apps and services
- **Social Media**: Automated posting and monitoring
- **Email Management**: Intelligent email processing and responses

### 🎨 Beautiful Web UI
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Dashboard**: Live updates of meetings, tasks, and alerts
- **Interactive Chat**: AI assistant with natural conversation
- **Permission Management**: Visual approval system for data access

### 📱 24/7 Monitoring
- **Continuous Operation**: Background monitoring of all data sources
- **System Health**: Resource usage and performance monitoring
- **Security Alerts**: Instant notifications for security events
- **Data Integrity**: Automatic corruption detection and repair

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web UI        │    │   Core Agent    │    │   Integrations  │
│   (Flask)       │◄──►│   (Scheduler)   │◄──►│   (Google,      │
│                 │    │                 │    │    Zapier)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Security      │    │   Monitoring    │    │   Data Storage  │
│   (Encryption,  │    │   (24/7 Health  │    │   (Encrypted    │
│    Permissions) │    │    Checks)      │    │    Local)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Core Components

1. **PersonalAgent**: Main orchestrator class
2. **Security Layer**: Encryption and permission management
3. **Integration Layer**: External service connections
4. **Monitoring System**: Continuous health and security checks
5. **Web UI**: User interface and API endpoints

## Installation

### Prerequisites

- Python 3.8+
- OpenAI API key
- Google Cloud Project (for Google integrations)
- Zapier API key (optional, for advanced automations)

### Install from Source

```bash
git clone https://github.com/yourusername/ai-personal-agent-sdk.git
cd ai-personal-agent-sdk
pip install -e .
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Environment Setup

Create a `.env` file in your project directory:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional - for Google integrations
GOOGLE_CREDENTIALS_PATH=path/to/google/credentials.json

# Optional - for Zapier automations
ZAPIER_API_KEY=your_zapier_api_key_here

# Optional - custom settings
DATA_STORAGE_PATH=./my_agent_data
UI_PORT=8080
MONITORING_INTERVAL=60
```

### 2. Google Setup (Optional)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Gmail API and Google Calendar API
4. Create credentials (OAuth 2.0 Client ID)
5. Download the credentials JSON file
6. Set the path in your `.env` file

### 3. Basic Usage

```python
from ai_personal_agent_sdk import PersonalAgent, Config

# Load configuration
config = Config()

# Create agent
agent_config = Config.AgentConfig(
    openai_api_key=config.openai_api_key,
    zapier_api_key=config.zapier_api_key,
    google_credentials_path=config.google_credentials_path
)

# Start the agent
agent = PersonalAgent(agent_config)
agent.start()

# The web UI will be available at http://localhost:8080
```

### 4. Using the Web Interface

1. Open your browser and go to `http://localhost:8080`
2. View your dashboard with meetings, daily plan, and active permissions
3. Chat with the AI assistant
4. Set alarms and manage automations
5. Approve or deny permission requests

## API Reference

### PersonalAgent Class

#### Initialization
```python
agent = PersonalAgent(config: AgentConfig)
```

#### Methods
- `start()`: Start the agent and all services
- `stop()`: Stop the agent and save data
- `request_permission(action, resource, duration_minutes)`: Request permission for an action
- `execute_automation(type, params)`: Execute automation via Zapier
- `get_meetings()`: Get upcoming meetings
- `add_alarm(time, message)`: Add a new alarm
- `get_daily_plan()`: Get today's AI-generated plan

### Security Features

#### Data Encryption
All sensitive data is automatically encrypted using AES-256 encryption:

```python
from ai_personal_agent_sdk.security import DataEncryptor

encryptor = DataEncryptor(key)
encrypted = encryptor.encrypt(b"sensitive data")
decrypted = encryptor.decrypt(encrypted)
```

#### Permission Management
```python
from ai_personal_agent_sdk.security import PermissionManager

pm = PermissionManager()
approved = pm.request_permission("read_email", "gmail", 60)  # 60 minutes
```

### Integrations

#### Google Services
```python
from ai_personal_agent_sdk.integrations import GoogleIntegration

google = GoogleIntegration("path/to/credentials.json")
emails = google.get_recent_emails()
events = google.get_today_events()
```

#### Zapier Automations
```python
from ai_personal_agent_sdk.integrations import ZapierIntegration

zapier = ZapierIntegration("your_api_key")
result = zapier.execute_automation("email_reply", {"message": "Hello!"})
```

## Security Best Practices

### Data Protection
- All data is stored locally and encrypted
- No data is sent to external servers without explicit permission
- Encryption keys are managed securely

### Permission System
- All sensitive operations require explicit permission
- Permissions are time-limited and auto-expire
- Users can revoke permissions at any time

### Network Security
- All API calls use HTTPS
- Credentials are stored encrypted
- No sensitive data in logs

### Monitoring & Alerts
- Continuous security monitoring
- Instant alerts for suspicious activity
- Regular data integrity checks

## Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `ZAPIER_API_KEY` | Zapier API key | Optional |
| `GOOGLE_CREDENTIALS_PATH` | Path to Google credentials | Optional |
| `DATA_STORAGE_PATH` | Data storage directory | `./agent_data` |
| `UI_PORT` | Web UI port | `8080` |
| `MONITORING_INTERVAL` | Monitoring check interval (seconds) | `60` |

## Troubleshooting

### Common Issues

1. **OpenAI API Key Issues**
   - Ensure your API key is valid and has sufficient credits
   - Check the key format (should start with `sk-`)

2. **Google Integration Problems**
   - Verify credentials JSON file path
   - Ensure APIs are enabled in Google Cloud Console
   - Check OAuth consent screen configuration

3. **Permission Denied Errors**
   - Check if the required permissions are granted
   - Verify permission expiration times
   - Look for pending permission requests in the UI

4. **Web UI Not Loading**
   - Check if port 8080 is available
   - Verify Flask is installed correctly
   - Check browser console for JavaScript errors

### Logs and Debugging

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check the logs for detailed error information and system status.

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
git clone https://github.com/yourusername/ai-personal-agent-sdk.git
cd ai-personal-agent-sdk
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest tests/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/ai-personal-agent-sdk/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/ai-personal-agent-sdk/discussions)

## Roadmap

- [ ] Mobile app companion
- [ ] Voice interface integration
- [ ] Advanced AI models support
- [ ] Multi-user support
- [ ] Plugin system for custom integrations
- [ ] Advanced analytics and insights

---

**Important Security Notice**: This SDK is designed with privacy and security as top priorities. All data processing happens locally on your device. No personal data is transmitted to external servers without your explicit permission and approval.