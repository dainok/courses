# 📘 **README – Ansible Callback Plugin: send_report**

## 🔍 Overview

`send_report` is a custom **Ansible callback plugin** that automatically sends a **full execution report** to an HTTP endpoint using a POST request.

The plugin collects:

* task status: ok, failed, skipped, unreachable
* stdout / stderr
* changed / msg values
* per-host execution summary

Everything is sent as structured JSON to your webhook.

---

## 📂 Project Structure

```
callback_plugins/
    send_report.py
ansible.cfg
README.md
```

---

## ⚙️ Installation

### 1. Copy the plugin into your project

Place the file here:

```
callback_plugins/send_report.py
```

Or into one of Ansible’s standard callback paths:

* `~/.ansible/plugins/callback/`
* `/usr/share/ansible/plugins/callback/`

---

## 🔧 Configuration

### 1. Enable the plugin in `ansible.cfg`

```ini
[defaults]
callback_plugins = ./callback_plugins
callbacks_enabled = send_report
inventory = inventory.ini
```

### 2. Configure the webhook URL

```ini
[callback_send_report]
webhook_url = https://example.com/report
```

Or via environment variable:

```bash
export ANSIBLE_REPORT_WEBHOOK="https://example.com/report"
```

---

## ▶️ Usage

Run your playbook normally:

```bash
ansible-playbook site.yml
```

A POST request will be sent at the end of the run, containing:

* the host summary
* the result of each task
* stdout/stderr
* full raw Ansible result data

---

## 📤 Example JSON Payload

```json
{
  "summary": {
    "host1": {
      "ok": 5,
      "changed": 2,
      "failed": 0,
      "skipped": 1,
      "unreachable": 0
    }
  },
  "results": {
    "host1": [
      {
        "task": "Install packages",
        "state": "ok",
        "stdout": "Installed successfully",
        "stderr": null,
        "changed": true,
        "msg": null,
        "result": { "changed": true }
      }
    ]
  }
}
```

---

## 🛠 Dependencies

The plugin requires:

```bash
pip install requests
```

---

## 🧪 Verifying Plugin Installation

To confirm that Ansible detects the plugin, run:

```bash
ansible-doc -t callback send_report
```

If the plugin is loaded correctly, Ansible will show its documentation.

If it does **not** appear, check:

* the plugin path
* `callback_plugins` configuration
* `callbacks_enabled` setting

---

## 🚨 Notes

* The playbook does **not** fail if the webhook is unreachable.
* Sensitive data (Vault secrets, passwords) is not logged.
* HTTP POST timeout is set to **3 seconds** to avoid blocking execution.

---

## 🧩 Debugging

To inspect callback loading:

```bash
ansible-playbook site.yml -vvv
```

You should see something like:

```
loaded callback plugin send_report
```
