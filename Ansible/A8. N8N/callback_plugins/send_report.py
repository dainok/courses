from __future__ import absolute_import, division, print_function
__metaclass__ = type

import json
import requests
from ansible.plugins.callback import CallbackBase

DOCUMENTATION = """
callback: send_report
type: notification
short_description: Sends final playbook report via HTTP POST
description:
  - Sends a JSON report to a webhook at the end of the playbook run.
options:
  webhook_url:
    description: URL to send the report to
    required: true
    env:
      - name: ANSIBLE_REPORT_WEBHOOK
    ini:
      - section: course
        key: webhook_url
"""

class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = "notification"
    CALLBACK_NAME = "send_report"
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self):
        super(CallbackModule, self).__init__()
        self.results = {}
        self.webhook_url = None

    def set_options(self, task_keys=None, var_options=None, direct=None):
        super(CallbackModule, self).set_options(task_keys, var_options, direct)
        self.webhook_url = self.get_option("webhook_url")

    def v2_runner_on_ok(self, result):
        self._store(result, "ok")

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self._store(result, "failed")

    def v2_runner_on_skipped(self, result):
        self._store(result, "skipped")

    def v2_runner_on_unreachable(self, result):
        self._store(result, "unreachable")

    def _store(self, result, state):
        host = result._host.get_name()
        task = result.task_name

        if host not in self.results:
            self.results[host] = []

        self.results[host].append({
            "task": task,
            "state": state,
            "stdout": result._result.get("stdout"),
            "stderr": result._result.get("stderr"),
            "msg": result._result.get("msg"),
            "changed": result._result.get("changed", False),
            "result": result._result
        })

    def v2_playbook_on_stats(self, stats):
        summary = {
            host: stats.summarize(host)
            for host in stats.processed
        }

        payload = {
            "summary": summary,
            "results": self.results,
        }

        try:
            requests.post(self.webhook_url, json=payload, timeout=3)
        except Exception as e:
            self._display.warning("Impossibile inviare il report: %s" % str(e))
