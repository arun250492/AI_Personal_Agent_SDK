"""
Web UI for the Personal Agent
"""

import os
import threading
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json


class WebUI:
    """
    Web-based user interface for the Personal Agent
    """

    def __init__(self, agent, port: int = 8080):
        self.agent = agent
        self.port = port
        self.app = Flask(__name__,
                        template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
                        static_folder=os.path.join(os.path.dirname(__file__), 'static'))
        CORS(self.app)
        self._setup_routes()
        self.server_thread = None

    def _setup_routes(self):
        """Setup Flask routes"""

        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/api/dashboard')
        def dashboard():
            """Get dashboard data"""
            meetings = self.agent.get_meetings()
            daily_plan = self.agent.get_daily_plan()
            alarms = self.agent.agent_data.get('alarms', [])

            return jsonify({
                'meetings': meetings[:5],  # Next 5 meetings
                'daily_plan': daily_plan,
                'alarms': alarms,
                'permissions': len(self.agent.permission_manager.get_active_permissions())
            })

        @self.app.route('/api/meetings')
        def get_meetings():
            return jsonify({'meetings': self.agent.get_meetings()})

        @self.app.route('/api/alarms', methods=['GET', 'POST'])
        def alarms():
            if request.method == 'POST':
                data = request.json
                self.agent.add_alarm(data['time'], data['message'])
                return jsonify({'status': 'success'})
            else:
                return jsonify({'alarms': self.agent.agent_data.get('alarms', [])})

        @self.app.route('/api/permissions')
        def permissions():
            active = self.agent.permission_manager.get_active_permissions()
            pending = self.agent.permission_manager.get_pending_permissions()
            return jsonify({
                'active': [{'action': p.action, 'resource': p.resource,
                           'expires_at': p.expires_at} for p in active],
                'pending': [{'action': p.action, 'resource': p.resource,
                            'granted_at': p.granted_at} for p in pending]
            })

        @self.app.route('/api/automations', methods=['POST'])
        def automations():
            data = request.json
            result = self.agent.execute_automation(data['type'], data)
            return jsonify(result)

        @self.app.route('/api/chat', methods=['POST'])
        def chat():
            """AI chat interface"""
            data = request.json
            user_message = data.get('message', '')

            # Use OpenAI for chat
            try:
                response = self.agent.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a helpful personal assistant. Keep responses concise."},
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=500
                )
                ai_response = response.choices[0].message.content
                return jsonify({'response': ai_response})
            except Exception as e:
                return jsonify({'error': str(e)})

    def start(self):
        """Start the web server in a background thread"""
        def run_server():
            self.app.run(host='0.0.0.0', port=self.port, debug=False)

        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        print(f"Web UI started on http://localhost:{self.port}")

    def stop(self):
        """Stop the web server"""
        if self.server_thread:
            # Flask doesn't have a direct way to stop, but since it's daemon thread, it will stop with main process
            pass