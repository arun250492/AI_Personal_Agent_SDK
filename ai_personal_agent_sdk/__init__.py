"""
AI Personal Agent SDK

A comprehensive SDK for building personal AI agents with automation,
security, and beautiful UI features.
"""

__version__ = "0.1.0"
__author__ = "Arun Kumar Singh"
__email__ = "arun250492@gmail.com"

from .core.agent import PersonalAgent, AgentConfig
from .core.config import Config
from .security.encryption import DataEncryptor
from .security.permissions import PermissionManager
from .integrations.zapier import ZapierIntegration
from .integrations.google import GoogleIntegration
from .ui.web_ui import WebUI
from .monitoring.monitor import DataMonitor

__all__ = [
    "PersonalAgent",
    "Config",
    "DataEncryptor",
    "PermissionManager",
    "ZapierIntegration",
    "GoogleIntegration",
    "WebUI",
    "DataMonitor",
]