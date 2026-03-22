"""
24/7 Data monitoring and alerting system
"""

import time
import threading
import psutil
import logging
from typing import Callable, Dict, Any
from datetime import datetime, timedelta


class DataMonitor:
    """
    Monitors system and data continuously
    """

    def __init__(self, interval_seconds: int = 60):
        self.interval = interval_seconds
        self.monitoring = False
        self.monitor_thread = None
        self.logger = logging.getLogger(__name__)
        self.alerts = []
        self.agent = None

    def start_monitoring(self, agent):
        """Start the monitoring system"""
        self.agent = agent
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("Data monitoring started")

    def stop_monitoring(self):
        """Stop the monitoring system"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("Data monitoring stopped")

    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                self._check_system_health()
                self._check_data_integrity()
                self._check_security_status()
                self._check_upcoming_events()
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")

            time.sleep(self.interval)

    def _check_system_health(self):
        """Check system resource usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            # Alert if system resources are critically low
            if cpu_percent > 90:
                self._add_alert("High CPU usage", f"CPU at {cpu_percent}%", "warning")

            if memory.percent > 90:
                self._add_alert("High memory usage", f"Memory at {memory.percent}%", "warning")

            if disk.percent > 95:
                self._add_alert("Low disk space", f"Disk at {disk.percent}%", "critical")

        except Exception as e:
            self.logger.error(f"System health check failed: {e}")

    def _check_data_integrity(self):
        """Check data integrity and backup status"""
        try:
            # Check if data file exists and is readable
            import os
            data_path = os.path.join(self.agent.data_path, "agent_data.enc")
            if not os.path.exists(data_path):
                self._add_alert("Data file missing", "Agent data file not found", "critical")
                return

            # Try to read and decrypt data
            with open(data_path, "rb") as f:
                encrypted_data = f.read()

            decrypted_data = self.agent.encryptor.decrypt(encrypted_data)
            data = self.agent.encryptor.decrypt(encrypted_data)  # Test decryption

            # Check data structure
            import json
            json.loads(data.decode())

        except Exception as e:
            self._add_alert("Data corruption", f"Data integrity check failed: {e}", "critical")

    def _check_security_status(self):
        """Check security status and permissions"""
        try:
            # Check for expired permissions
            expired_perms = []
            current_time = time.time()

            for perm_id, perm in self.agent.permission_manager.permissions.items():
                if current_time >= perm.expires_at:
                    expired_perms.append(perm_id)

            for perm_id in expired_perms:
                del self.agent.permission_manager.permissions[perm_id]
                self._add_alert("Permission expired", f"Permission {perm_id} has expired", "info")

            # Check for pending permissions that need attention
            pending_count = len(self.agent.permission_manager.pending_permissions)
            if pending_count > 0:
                self._add_alert("Pending permissions", f"{pending_count} permissions awaiting approval", "info")

        except Exception as e:
            self.logger.error(f"Security check failed: {e}")

    def _check_upcoming_events(self):
        """Check for upcoming important events"""
        try:
            if self.agent.google:
                upcoming = self.agent.google.get_upcoming_events(minutes=60)
                for event in upcoming:
                    event_time = datetime.fromisoformat(event['start'].replace('Z', '+00:00'))
                    now = datetime.now(event_time.tzinfo)
                    time_diff = (event_time - now).total_seconds() / 60  # minutes

                    if 10 <= time_diff <= 15:  # 10-15 minutes before
                        if event['id'] not in self.agent.agent_data.get('reminded_events', []):
                            self.agent._send_notification(
                                "Upcoming Event",
                                f"Event '{event['summary']}' starts in {int(time_diff)} minutes"
                            )
                            self.agent.agent_data.setdefault('reminded_events', []).append(event['id'])
                            self.agent._save_data()

        except Exception as e:
            self.logger.error(f"Event check failed: {e}")

    def _add_alert(self, title: str, message: str, severity: str):
        """Add an alert to the system"""
        alert = {
            'id': f"alert_{int(time.time())}",
            'title': title,
            'message': message,
            'severity': severity,
            'timestamp': datetime.now().isoformat()
        }

        self.alerts.append(alert)

        # Keep only last 100 alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]

        # Log alert
        if severity == 'critical':
            self.logger.critical(f"{title}: {message}")
        elif severity == 'warning':
            self.logger.warning(f"{title}: {message}")
        else:
            self.logger.info(f"{title}: {message}")

        # Send notification for critical alerts
        if severity == 'critical':
            if self.agent:
                self.agent._send_notification(f"Critical Alert: {title}", message)

    def get_alerts(self, severity: str = None, limit: int = 50) -> list:
        """Get alerts, optionally filtered by severity"""
        alerts = self.alerts
        if severity:
            alerts = [a for a in alerts if a['severity'] == severity]

        return alerts[-limit:]

    def clear_alerts(self, alert_ids: list = None):
        """Clear alerts"""
        if alert_ids:
            self.alerts = [a for a in self.alerts if a['id'] not in alert_ids]
        else:
            self.alerts = []