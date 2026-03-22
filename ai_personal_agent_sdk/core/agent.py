"""
Core Personal Agent implementation
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from openai import OpenAI
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from ..security.encryption import DataEncryptor
from ..security.permissions import PermissionManager
from ..integrations.zapier import ZapierIntegration
from ..integrations.google import GoogleIntegration
from ..monitoring.monitor import DataMonitor
from ..ui.web_ui import WebUI


@dataclass
class AgentConfig:
    openai_api_key: str
    zapier_api_key: Optional[str] = None
    google_credentials_path: Optional[str] = None
    encryption_key: Optional[str] = None
    data_storage_path: str = "./agent_data"
    ui_port: int = 8080
    monitoring_interval: int = 60  # seconds


class PersonalAgent:
    """
    Main Personal Agent class that orchestrates all functionality
    """

    def __init__(self, config: AgentConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.encryptor = DataEncryptor(config.encryption_key or os.urandom(32))
        self.permission_manager = PermissionManager()
        self.monitor = DataMonitor(self.config.monitoring_interval)

        # Initialize integrations
        self.openai_client = OpenAI(api_key=config.openai_api_key)
        self.zapier = ZapierIntegration(config.zapier_api_key) if config.zapier_api_key else None
        self.google = GoogleIntegration(config.google_credentials_path) if config.google_credentials_path else None

        # Initialize UI
        self.ui = WebUI(self, port=config.ui_port)

        # Scheduler for automated tasks
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

        # Data storage
        os.makedirs(config.data_storage_path, exist_ok=True)
        self.data_path = config.data_storage_path

        # Load existing data
        self._load_data()

    def _load_data(self):
        """Load encrypted data from storage"""
        try:
            data_file = os.path.join(self.data_path, "agent_data.enc")
            if os.path.exists(data_file):
                with open(data_file, "rb") as f:
                    encrypted_data = f.read()
                decrypted_data = self.encryptor.decrypt(encrypted_data)
                self.agent_data = json.loads(decrypted_data.decode())
            else:
                self.agent_data = {
                    "meetings": [],
                    "tasks": [],
                    "alarms": [],
                    "permissions": {},
                    "preferences": {}
                }
        except Exception as e:
            self.logger.error(f"Failed to load data: {e}")
            self.agent_data = {"meetings": [], "tasks": [], "alarms": [], "permissions": {}, "preferences": {}}

    def _save_data(self):
        """Save data encrypted to storage"""
        try:
            data_json = json.dumps(self.agent_data)
            encrypted_data = self.encryptor.encrypt(data_json.encode())
            data_file = os.path.join(self.data_path, "agent_data.enc")
            with open(data_file, "wb") as f:
                f.write(encrypted_data)
        except Exception as e:
            self.logger.error(f"Failed to save data: {e}")

    def start(self):
        """Start the personal agent"""
        self.logger.info("Starting Personal Agent...")

        # Start monitoring
        self.monitor.start_monitoring(self)

        # Start UI
        self.ui.start()

        # Schedule daily planning
        self.scheduler.add_job(
            self._daily_planning,
            CronTrigger(hour=6, minute=0),  # 6 AM daily
            id="daily_planning"
        )

        # Schedule meeting checks
        self.scheduler.add_job(
            self._check_upcoming_meetings,
            CronTrigger(minute="*/15"),  # Every 15 minutes
            id="meeting_checks"
        )

        self.logger.info("Personal Agent started successfully")

    def stop(self):
        """Stop the personal agent"""
        self.logger.info("Stopping Personal Agent...")
        self.scheduler.shutdown()
        self.monitor.stop_monitoring()
        self.ui.stop()
        self._save_data()
        self.logger.info("Personal Agent stopped")

    def _daily_planning(self):
        """Perform daily planning using AI"""
        try:
            # Get today's schedule from Google Calendar
            if self.google:
                today_events = self.google.get_today_events()
            else:
                today_events = []

            # Get pending tasks
            pending_tasks = [t for t in self.agent_data["tasks"] if not t.get("completed", False)]

            # Use AI to plan the day
            prompt = f"""
            Based on the following information, create a daily plan:

            Today's events: {json.dumps(today_events, indent=2)}
            Pending tasks: {json.dumps(pending_tasks, indent=2)}

            Please provide a structured daily plan with:
            1. Morning routine
            2. Work blocks
            3. Breaks and meals
            4. Evening activities
            5. Any adjustments needed
            """

            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000
            )

            plan = response.choices[0].message.content
            self.agent_data["daily_plan"] = {
                "date": datetime.now().date().isoformat(),
                "plan": plan
            }
            self._save_data()

            # Notify user
            self._send_notification("Daily Plan Ready", "Your AI assistant has prepared your daily plan")

        except Exception as e:
            self.logger.error(f"Daily planning failed: {e}")

    def _check_upcoming_meetings(self):
        """Check for upcoming meetings and send reminders"""
        try:
            if not self.google:
                return

            upcoming = self.google.get_upcoming_events(minutes=30)
            for event in upcoming:
                if event["id"] not in self.agent_data.get("notified_meetings", []):
                    self._send_notification(
                        "Upcoming Meeting",
                        f"You have a meeting: {event['summary']} at {event['start']}"
                    )
                    self.agent_data.setdefault("notified_meetings", []).append(event["id"])
                    self._save_data()

        except Exception as e:
            self.logger.error(f"Meeting check failed: {e}")

    def _send_notification(self, title: str, message: str):
        """Send notification to user"""
        # Use plyer for desktop notifications
        try:
            from plyer import notification
            notification.notify(
                title=title,
                message=message,
                app_name="AI Personal Agent"
            )
        except ImportError:
            self.logger.warning("plyer not available for notifications")

    def request_permission(self, action: str, resource: str, duration_minutes: int = 60) -> bool:
        """Request permission for an action"""
        return self.permission_manager.request_permission(action, resource, duration_minutes)

    def execute_automation(self, automation_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute automation via Zapier"""
        if not self.zapier:
            return {"error": "Zapier integration not configured"}

        if not self.request_permission("automation", automation_type):
            return {"error": "Permission denied"}

        return self.zapier.execute_automation(automation_type, params)

    def get_meetings(self) -> List[Dict]:
        """Get upcoming meetings"""
        if self.google:
            return self.google.get_upcoming_events()
        return []

    def add_alarm(self, time: str, message: str):
        """Add an alarm"""
        alarm = {
            "id": f"alarm_{len(self.agent_data['alarms'])}",
            "time": time,
            "message": message,
            "active": True
        }
        self.agent_data["alarms"].append(alarm)
        self._save_data()

        # Schedule the alarm
        hour, minute = map(int, time.split(":"))
        self.scheduler.add_job(
            lambda: self._send_notification("Alarm", message),
            CronTrigger(hour=hour, minute=minute),
            id=alarm["id"]
        )

    def get_daily_plan(self) -> Optional[str]:
        """Get today's daily plan"""
        plan_data = self.agent_data.get("daily_plan", {})
        if plan_data.get("date") == datetime.now().date().isoformat():
            return plan_data.get("plan")
        return None