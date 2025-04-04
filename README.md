# Brock University Events MCP Server

This MCP server connects to the Brock University events RSS feed and provides AI assistants with access to campus events.

## Features

- Fetch and parse the Brock University events RSS feed
- Search for events by keyword
- Get upcoming events for a specified number of days
- Filter events by date or date range
- Filter events by time of day (morning, afternoon, evening)
- Browse event categories
- Filter events by category
- Get specialized views (this week, next week, weekend events)
- Get detailed information for specific events

## Installation Guide

### Prerequisites
- Python 3.10 or higher installed on your computer
- Basic familiarity with command line operations

### Step-by-Step Installation

1. **Get the code**
   - Download this repository or the individual server file

2. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server**:
   ```bash
   python brock_events_server.py
   ```
   
   The server is running successfully when there is no error output. Keep this terminal window open while using the server with Claude.

## Connecting to Claude for Desktop

### Setting up Claude Desktop

1. **Install Claude for Desktop** if you haven't already:
   - Download from [claude.ai/download](https://claude.ai/download)
   - Follow the installation instructions for your operating system

2. **Open the Claude Desktop configuration file**:
   - On Mac: 
     - Click on the Claude menu at the top of your screen
     - Select "Settings..."
     - Click on "Developer" in the left sidebar
     - Click "Edit Config"
   - On Windows:
     - Open File Explorer
     - Navigate to `%APPDATA%\Claude\`
     - Create or edit the file `claude_desktop_config.json`

3. **Add the server configuration**:
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

   Important: Replace `/REPLACE/WITH/FULL/PATH/TO/brock_events_server.py` with the actual full path to where you saved the server file on your computer.

   For example:
   - Mac: `/Users/yourusername/Downloads/mcp-rssfeed/brock_events_server.py`
   - Windows: `C:\\Users\\yourusername\\Downloads\\mcp-rssfeed\\brock_events_server.py`

4. **Save the configuration file** and **restart Claude for Desktop**

5. **Verify connection**: When you open Claude for Desktop, you should see a hammer icon in the bottom right of the chat interface, indicating available tools.

## Available Tools

The server exposes the following tools:

- **get_upcoming_events(days)**: Get upcoming events for the specified number of days
- **search_events(query)**: Search for events matching the query
- **get_events_by_date(date)**: Get events on a specific date (format: YYYY-MM-DD)
- **get_events_by_date_range(start_date, end_date)**: Get events between two dates
- **get_events_by_time_of_day(date, time_range)**: Get events for a specific time of day
- **get_event_categories()**: List all available event categories with organized grouping
- **get_events_by_category(category)**: Get events in a specific category with fuzzy matching
- **get_event_details(query)**: Get detailed information about a specific event by title or ID
- **get_events_this_week()**: Get all events occurring this week (Monday-Sunday)
- **get_events_next_week()**: Get all events occurring next week (Monday-Sunday)
- **get_weekend_events(date)**: Get events for the upcoming or specified weekend

## Example Queries

Here are some example queries you can ask Claude:

- "What events are happening at Brock University this week?"
- "Are there any music events at Brock University?"
- "What's happening on campus next Tuesday?"
- "Show me all the academic events at Brock"
- "What categories of events are available at Brock University?"
- "Tell me more about the Blackout Gala event"
- "When and where is the next workshop happening?"
- "Are there any social events this weekend?"
- "Show me events with free food"
- "What club meetings are happening this week?"
- "What events are happening between March 15 and March 20?"
- "Show me evening events on Friday"
- "What's happening next week at Brock?"

## Troubleshooting

If you encounter issues, try these steps:

### Server Won't Start
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

### Claude Not Connecting to Server
1. **Configuration file**: Double-check your `claude_desktop_config.json` file
   - Ensure there are no syntax errors (missing commas, brackets, etc.)
   - Verify the path to the server file is correct and absolute

2. **Server running**: Make sure your server is still running in the terminal

3. **Claude logs**: Check Claude's logs for errors
   - On Mac: `~/Library/Logs/Claude/mcp*.log`
   - On Windows: `%APPDATA%\Claude\logs\mcp*.log`

4. **Restart Claude**: Sometimes a complete restart of Claude for Desktop resolves connection issues

### RSS Feed Issues
If the server starts but tools aren't working, the RSS feed might be unavailable or its format might have changed. Try accessing [https://events.brocku.ca/events/rss/](https://events.brocku.ca/events/rss/) in your browser to check if it's accessible.

## Contributing

Contributions are welcome! Feel free to submit pull requests or open issues if you have suggestions for improvements.

## License

This project is licensed under the MIT License.