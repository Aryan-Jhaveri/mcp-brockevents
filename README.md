# 🎓 Brock University Events MCP Server

<div align="center">
  
  ![Brock University](https://upload.wikimedia.org/wikipedia/en/thumb/3/3f/Brock_University_logo.svg/320px-Brock_University_logo.svg.png)

  *Never miss a campus event again!*
  
  [![Model Context Protocol](https://img.shields.io/badge/MCP-Compatible-blue)](https://modelcontextprotocol.io)
  [![Claude](https://img.shields.io/badge/Claude-Desktop-purple)](https://claude.ai/download)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  
</div>

## 📋 Overview

This MCP server connects to the Brock University events RSS feed and provides AI assistants with access to campus events. It allows students and faculty to easily discover relevant events, filter by date or category, and get comprehensive event details.

## ✨ Features

- 🔄 **Real-time data**: Fetch and parse the Brock University events RSS feed
- 🔍 **Search capabilities**: Find events by keyword
- 📅 **Timeline views**: Get upcoming events for a specified number of days
- 📆 **Date filtering**: Filter events by date or date range
- ⏰ **Time filtering**: Find events by time of day (morning, afternoon, evening)
- 🏷️ **Categories**: Browse event categories and filter events accordingly
- 📊 **Special views**: Get customized lists (this week, next week, weekend events)
- 📝 **Detailed info**: Access comprehensive details for specific events

## 🛠️ Installation Guide

### Prerequisites
- 🐍 Python 3.10 or higher installed on your computer
- 💻 Basic familiarity with command line operations

### Step-by-Step Installation

<details open>
<summary><b>1️⃣ Get the code</b></summary>

```bash
# Clone with Git
git clone https://github.com/yourusername/mcp-rssfeed.git
cd mcp-rssfeed

# Or download the ZIP and extract it
```
</details>

<details open>
<summary><b>2️⃣ Install dependencies</b></summary>

```bash
# Install all required packages
pip install -r requirements.txt
```
</details>

<details open>
<summary><b>3️⃣ Launch the server</b></summary>

```bash
# Start the MCP server
python brock_events_server.py
```

> 💡 The server is running successfully when there is no error output. Keep this terminal window open while using the server with Claude.
</details>

## 🔄 Connecting to Claude for Desktop

### Setting up Claude Desktop

<details open>
<summary><b>1️⃣ Install Claude for Desktop</b></summary>

- Download from [claude.ai/download](https://claude.ai/download)
- Follow the installation instructions for your operating system
</details>

<details open>
<summary><b>2️⃣ Open the configuration file</b></summary>

**Mac users**:
1. Click on the Claude menu at the top of your screen
2. Select "Settings..."
3. Click on "Developer" in the left sidebar
4. Click "Edit Config"

**Windows users**:
1. Open File Explorer
2. Navigate to `%APPDATA%\Claude\`
3. Create or edit the file `claude_desktop_config.json`
</details>

<details open>
<summary><b>3️⃣ Add the server configuration</b></summary>

Copy and paste the following JSON into the configuration file:

```json
{
  "mcpServers": {
    "brocku-events": {
      "command": "python",
      "args": [
        "/REPLACE/WITH/FULL/PATH/TO/brock_events_server.py"
      ]
    }
  }
}
```

> ⚠️ **Important**: Replace `/REPLACE/WITH/FULL/PATH/TO/brock_events_server.py` with the actual full path to the server file on your computer.

Examples:
- **Mac**: `/Users/yourusername/Downloads/mcp-rssfeed/brock_events_server.py`
- **Windows**: `C:\\Users\\yourusername\\Downloads\\mcp-rssfeed\\brock_events_server.py`
</details>

<details open>
<summary><b>4️⃣ Finalize setup</b></summary>

1. Save the configuration file
2. Restart Claude for Desktop
3. **Verify connection**: Look for the 🔨 hammer icon in the bottom right of the chat interface, indicating available tools
</details>

## 🧰 Available Tools

<div align="center">
  <table>
    <tr>
      <th>Tool</th>
      <th>Description</th>
    </tr>
    <tr>
      <td><code>get_upcoming_events(days)</code></td>
      <td>Get events for the specified number of days ahead</td>
    </tr>
    <tr>
      <td><code>search_events(query)</code></td>
      <td>Search for events matching the keyword query</td>
    </tr>
    <tr>
      <td><code>get_events_by_date(date)</code></td>
      <td>Get events on a specific date (format: YYYY-MM-DD)</td>
    </tr>
    <tr>
      <td><code>get_events_by_date_range(start_date, end_date)</code></td>
      <td>Get events between two specified dates</td>
    </tr>
    <tr>
      <td><code>get_events_by_time_of_day(date, time_range)</code></td>
      <td>Filter events by time of day (morning/afternoon/evening)</td>
    </tr>
    <tr>
      <td><code>get_event_categories()</code></td>
      <td>List all available event categories with organized grouping</td>
    </tr>
    <tr>
      <td><code>get_events_by_category(category)</code></td>
      <td>Get events in a specific category with fuzzy matching</td>
    </tr>
    <tr>
      <td><code>get_event_details(query)</code></td>
      <td>Get detailed information about a specific event</td>
    </tr>
    <tr>
      <td><code>get_events_this_week()</code></td>
      <td>Get all events occurring this week (Monday-Sunday)</td>
    </tr>
    <tr>
      <td><code>get_events_next_week()</code></td>
      <td>Get all events occurring next week (Monday-Sunday)</td>
    </tr>
    <tr>
      <td><code>get_weekend_events(date)</code></td>
      <td>Get events for the upcoming or specified weekend</td>
    </tr>
  </table>
</div>

## 💬 Example Queries

<details open>
<summary><b>Basic Queries</b></summary>

- 📅 "What events are happening at Brock University this week?"
- 🎵 "Are there any music events at Brock University?"
- 📝 "What's happening on campus next Tuesday?"
- 🎓 "Show me all the academic events at Brock"
- 📋 "What categories of events are available at Brock University?"
- 🔍 "Tell me more about the Blackout Gala event"
- 🏢 "When and where is the next workshop happening?"
- 👥 "Are there any social events this weekend?"
- 🍔 "Show me events with free food"
- 🤝 "What club meetings are happening this week?"
- 📆 "What events are happening between March 15 and March 20?"
- 🌙 "Show me evening events on Friday"
- 📊 "What's happening next week at Brock?"
</details>

## 🚀 Advanced Use Cases

Students can quickly chat and find events based on their interests:

<details open>
<summary><b>🔎 Professional Development</b></summary>

Users can upload their resume to find and filter professional networking events, and have Claude create elevator pitches about them. Perfect for preparing a game plan for networking events!
</details>

<details open>
<summary><b>📱 Calendar Integration</b></summary>

Claude can filter events and create .ics files of selected events for users to add to their iCal or sync across their other calendars. [Learn how to import .ics files to Google Calendar](https://support.google.com/calendar/answer/37118?hl=en&co=GENIE.Platform%3DDesktop)
</details>

## ⚠️ Troubleshooting

<details>
<summary><b>🛑 Server Won't Start</b></summary>

1. **Check Python version**: Make sure you have Python 3.10+ installed
   ```bash
   python --version
   ```

2. **Dependency issues**: Try reinstalling dependencies one by one
   ```bash
   pip install mcp[cli]
   pip install httpx feedparser python-dateutil pytz
   ```

3. **Permission errors**: Make sure you have permission to run the script
</details>

<details>
<summary><b>🔌 Claude Not Connecting to Server</b></summary>

1. **Configuration file**: Double-check your `claude_desktop_config.json` file
   - Ensure there are no syntax errors (missing commas, brackets, etc.)
   - Verify the path to the server file is correct and absolute

2. **Server running**: Make sure your server is still running in the terminal

3. **Claude logs**: Check Claude's logs for errors
   - On Mac: `~/Library/Logs/Claude/mcp*.log`
   - On Windows: `%APPDATA%\Claude\logs\mcp*.log`

4. **Restart Claude**: Sometimes a complete restart of Claude for Desktop resolves connection issues
</details>

<details>
<summary><b>📡 RSS Feed Issues</b></summary>

If the server starts but tools aren't working, the RSS feed might be unavailable or its format might have changed. 

Try accessing [https://events.brocku.ca/events/rss/](https://events.brocku.ca/events.rss/) in your browser to check if it's accessible.
</details>

## 👥 Contributing

<div align="center">
  
  [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)
  [![Issues](https://img.shields.io/github/issues/yourusername/mcp-rssfeed.svg)](https://github.com/Aryan-Jhaveri/mcp-brockevents/issues)
  
</div>

Contributions are welcome! Feel free to submit pull requests or open issues if you have suggestions for improvements.

### Developer Resources

<div align="center">
  <table>
    <tr>
      <td align="center">
        <a href="https://modelcontextprotocol.io/tutorials/building-mcp-with-llms">
          <img src="https://mintlify.s3.us-west-1.amazonaws.com/mcp/images/claude-desktop-mcp-plug-icon.svg" width="80" alt="MCP with LLMs"><br>
          <b>Building MCP with LLMs</b>
        </a>
      </td>
      <td align="center">
        <a href="https://modelcontextprotocol.io/docs/concepts/architecture">
          <img src="https://mintlify.s3.us-west-1.amazonaws.com/mcp/images/claude-desktop-mcp-hammer-icon.svg" width="80" alt="MCP Docs"><br>
          <b>MCP Documentation</b>
        </a>
      </td>
    </tr>
  </table>
</div>

## 📄 License

<div align="center">
  
  This project is licensed under the [MIT License](LICENSE).
  
  Copyright © 2024
  
</div>
