# Brock University Events MCP Server

An MCP (Model Context Protocol) server that fetches and provides information about events at Brock University via the ExperienceBU RSS feed.

## Overview

This server connects to the Brock University events RSS feed, parses the events, and provides tools to search, filter, and retrieve event information. It's designed to be used with Claude or other MCP-compatible clients to create an AI assistant for university events.

## Features

- Fetches and parses the ExperienceBU RSS feed
- Caches event information to improve performance
- Provides tools to search events by various criteria (keyword, category, date, location)
- Offers resources to view upcoming events
- Includes prompt templates for common event-related queries

## Installation

### Prerequisites

- Python 3.7+
- pip or uv package manager

### Installation Steps

1. Clone this repository
2. Install dependencies:

```bash
# Using uv (recommended)
uv pip install "mcp[cli]" httpx

# Or using pip
pip install "mcp[cli]" httpx
```

## Usage

### Running with MCP CLI

The easiest way to run the server is with the MCP CLI:

```bash
# Using uv
uv run mcp dev brock_events_server.py

# Using pip
mcp dev brock_events_server.py
```

### Installing in Claude Desktop

To use this server with Claude Desktop:

```bash
# Using uv
uv run mcp install brock_events_server.py --name "Brock Events"

# Using pip
mcp install brock_events_server.py --name "Brock Events"
```

### Direct Execution

You can also run the server directly:

```bash
python brock_events_server.py
```

## Available Tools

The server provides the following tools:

1. `search_events` - Search for events with filtering options
2. `get_event_details` - Get detailed information about a specific event
3. `get_events_by_day` - Get all events occurring on a specific day
4. `list_categories` - List all event categories
5. `list_locations` - List all event locations

## Resources

- `events://upcoming` - Returns a list of upcoming events

## Prompt Templates

1. `find_events_prompt` - Create a prompt to find events based on interests and date range
2. `plan_my_day_prompt` - Create a prompt to help plan a day's schedule based on available events

## Example Conversations

### Finding Events About a Topic

**User**: "What events related to learning are happening this month?"

**Claude** can:
1. Use the `search_events` tool with the query "learning" and appropriate date filters
2. Format the results into a natural response
3. Suggest specific events that match the user's interests

### Planning a Day on Campus

**User**: "I'll be on campus next Tuesday. What events should I check out?"

**Claude** can:
1. Use the `get_events_by_day` tool with the date of next Tuesday
2. Present the events in chronological order
3. Suggest a schedule based on location and timing

## Customization

You can customize this server by:

1. Modifying the `RSS_URL` constant to point to a different RSS feed
2. Adjusting the `CACHE_DURATION` to change how often events are refreshed
3. Adding new tools, resources, or prompts as needed

## Troubleshooting

If you encounter issues:

1. Check that the RSS feed URL is accessible
2. Make sure all dependencies are installed
3. Verify that your Python version is compatible
4. Check the MCP Inspector logs for any error messages

## License

This project is provided under the MIT License.
