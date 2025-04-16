# safecp

`🛡️ safecp` is a lightweight clipboard monitoring service for **macOS** and **Linux** that helps prevent accidental leaks of sensitive information by automatically scrubbing clipboard content using custom patterns. It is a great tool to avoid leaking sensitive information to any LLM out in the wild! 

---

## ✨ Features

- 🔍 Monitors clipboard in real-time
- 🧽 Replaces sensitive data with safe placeholders (e.g., emails, API keys, credit cards)
- ⚙️ User-customizable pattern definitions via a JSON file
- 🖥️ Runs as a background service on macOS and Linux


## 🚀 Installation

Clone the repository and run the install script:

```bash
git clone https://github.com/albertoperdomo2/safecp.git
cd safecp
./install
```

> The install script sets up the service, ensures your default pattern file is placed at `~/.safecp.patterns.json` and provide instructions to on how to start/stop the service.


## 🧠 How It Works

- `safecp` monitors the system clipboard.
- When new content is copied, it scans it against patterns (defined in JSON).
- Any matches (e.g., email addresses, tokens, secrets) are replaced with safe placeholders.
- The cleaned version is then written back to the clipboard, overwriting the original.


## 📂 Patterns File

Pattern definitions live in:

```
~/.safecp.patterns.json
```

A basic version from `patterns/basic.json` is copied there the first time you run the service. You can modify this file to define your own regex-based patterns and replacement templates.

**Example:**

```json
{
  "email": {
    "pattern": "[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+",
    "replacement_template": "[email hidden {counter}]"
  }
}
```


## 🛠️ Requirements

This project is written in **Python 3** and uses:

- `AppKit` for macOS clipboard access
- `Gtk` via `PyGObject` for Linux support

Make sure the following dependencies are installed:

### macOS:

```bash
pip install pyobjc
```

### Linux:

```bash
sudo apt install python3-gi gir1.2-gtk-3.0
pip install PyGObject
```

Copy something sensitive like an email or token. Watch as it gets sanitized instantly 🎉

---

See [LICENSE](LICENSE)
