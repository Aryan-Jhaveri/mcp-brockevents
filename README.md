# Brock University Events MCP Server

This MCP server connects to the Brock University events RSS feed and provides AI assistants with access to campus events.

## Features

- Fetch and parse the Brock University events RSS feed
- Search for events by keyword
- Get upcoming events for a specified number of days
- Filter events by date
- Browse event categories
- Filter events by category

## Installation

1. Clone this repository or download the server file

2. Install the required dependencies:

```bash
pip install "mcp[cli]" httpx feedparser python-dateutil
```

3. Run the server:

```bash
python brocku_events_server.py
```

## Using with Claude for Desktop

To use this server with Claude for Desktop:

1. Make sure you have Claude for Desktop installed

2. Open your Claude for Desktop configuration at:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

3. Add the following configuration:

```json
{
  "mcpServers": {
    "brocku-events": {
      "command": "python",
      "args": [
        "/absolute/path/to/brocku_events_server.py"
      ]
    }
  }
}
```

Replace `/absolute/path/to/brocku_events_server.py` with the actual path to the server file.

4. Restart Claude for Desktop

## Available Tools

The server exposes the following tools:

- **get_upcoming_events(days)**: Get upcoming events for the specified number of days
- **search_events(query)**: Search for events matching the query
- **get_events_by_date(date)**: Get events on a specific date (format: YYYY-MM-DD)
- **get_event_categories()**: List all available event categories with organized grouping
- **get_events_by_category(category)**: Get events in a specific category with fuzzy matching
- **get_event_details(query)**: Get detailed information about a specific event by title or ID

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

## Troubleshooting

If you encounter any issues:

1. Check that the RSS feed URL is still valid
2. Ensure you have all the required dependencies installed
3. Verify that your Claude for Desktop configuration is correct
4. Check Claude for Desktop logs for any error messages

## Contributing

Contributions are welcome! Feel free to submit pull requests or open issues if you have suggestions for improvements.

## License

This project is licensed under the MIT License.