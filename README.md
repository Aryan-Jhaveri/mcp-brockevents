# 🎓 Brock University Events MCP Server

<div align="center">
  
  ![Brock University](https://upload.wikimedia.org/wikipedia/commons/thumb/0/01/Brock_University_Arthur_Schmon_Tower_Aug_2008_3.JPG/500px-Brock_University_Arthur_Schmon_Tower_Aug_2008_3.JPG)

  *Your own assistant to help you network and be involved!*
  
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

## 🛠️ Installation Guide

Follow these steps to get the Brock University Events MCP Server running on your computer:

### Prerequisites

* **Python 3.10 or higher:** Make sure you have a compatible version of Python installed.
* **Basic Command Line Familiarity:** You should be comfortable opening a terminal or command prompt and running basic commands.

### Step-by-Step Installation

1.  **Get the code:**
    * **Using Git:** If you have Git installed, open your terminal and run:
        ```bash
        git clone https://github.com/Aryan-Jhaveri/mcp-brockevents
        cd mcp-brockevents
        ```
    * **Downloading the ZIP:** Alternatively, you can download the project as a ZIP file from the GitHub page and extract it to a folder on your computer. Then, open your terminal and navigate to that folder using the `cd` command.

2.  **Install dependencies:**
    * With your terminal in the project directory (`mcp-brockevents`), run the following command to install all required Python packages:
        ```bash
        pip install -r requirements.txt
        ```
        
### Setting up Claude Desktop

1.  **Install Claude for Desktop:** If you haven't already, download and install the Claude for Desktop application from [claude.ai/download](https://claude.ai/download). Follow the on-screen instructions.

2.  **Open the configuration file:**
    * **On Mac:** Open the Claude Desktop app, click on the Claude menu at the top of your screen, select "Settings...", click on "Developer" in the left sidebar, and then click "Edit Config".
    * **On Windows:** Open File Explorer, navigate to `%APPDATA%\Claude\`, and locate or create the file named `claude_desktop_config.json`.

3.  **Add the server configuration:**
    * Copy and paste the following JSON structure into your `claude_desktop_config.json` file.
    * **Crucially, replace `/REPLACE/WITH/FULL/PATH/TO/brock_events_server.py` with the actual, full path to the `brock_events_server.py` file on your computer.**

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
    * **Example Paths:**
        * **Mac:** `/Users/yourusername/Downloads/mcp-brockevents/brock_events_server.py`
        * **Windows:** `C:\\Users\\yourusername\\Downloads\\mcp-brockevents\\brock_events_server.py`

4.  **Finalize setup:**
    * Save the `claude_desktop_config.json` file.
    * Restart Claude for Desktop.
    * **Verify connection:** After restarting, look for a small hammer icon (🔨) in the bottom right corner of the Claude chat interface. This icon indicates that MCP tools are available and the server is connected.

Now your AI assistant should be able to access and use the tools provided by the Brock University Events MCP Server!

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

## 🔧 Customization Guide

<details open>
<summary><b>📡 Changing the RSS Feed Source</b></summary>

You can configure this server to use event feeds from other universities:

### Step 1: Locate the RSS Feed URL

1. Open `brock_events_server.py` in any text editor
2. Find line 14 where the RSS feed URL is defined:
   ```python
   RSS_FEED_URL = "https://experiencebu.brocku.ca/events.rss"
   ```

### Step 2: Replace with Your Preferred Feed

Replace the URL with another university's event feed:

| University | RSS/XML Feed URL |
|------------|------------------|
| Brock University | https://experiencebu.brocku.ca/events.rss |
| University of Guelph | https://gryphlife.uoguelph.ca/Events.rss |
| Western University | http://westernadvance.ca/calendar/western.xml |

### Step 3: Adapt the Parsing Logic (Advanced)

⚠️ **Important Compatibility Note**: 

The server is specifically designed for Brock University's RSS feed structure. Different universities format their event data with unique:
- Tag naming conventions
- Date formats
- Category systems
- Event property names

If you change the RSS feed URL, you may need to modify the event parsing functions in the code to match the structure of your selected feed. The primary parsing logic is in the `fetch_rss_feed()` and related functions.

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

<details open>
<summary><b>📊 Schedule Optimization</b></summary>

Users can share an image of their personal schedule and ask "What events fit within my schedule for the month, can you find and filter them for me?" Claude will analyze available time slots and recommend compatible events.
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
  
  [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)]()
  [![Issues](https://img.shields.io/github/issues/yourusername/mcp-brockevents.svg)](https://github.com/Aryan-Jhaveri/mcp-brockevents/issues)
  
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
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
  
</div>
