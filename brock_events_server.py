import asyncio
import httpx
import feedparser
import datetime
from typing import Dict, List, Optional, Any
from dateutil import parser
from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("BrockU Events Assistant")

# Constants
RSS_FEED_URL = "https://experiencebu.brocku.ca/events.rss"
USER_AGENT = "brocku-events-assistant/1.0"

# Cache the feed data to avoid excessive requests
last_fetch_time = None
cached_feed = None
CACHE_DURATION = 300  # seconds (5 minutes)

async def fetch_rss_feed():
    """Fetch the RSS feed from Brock University with caching."""
    global last_fetch_time, cached_feed
    
    current_time = datetime.datetime.now().timestamp()
    
    # Use cached data if it's still fresh
    if last_fetch_time and current_time - last_fetch_time < CACHE_DURATION and cached_feed:
        return cached_feed
    
    # Fetch new data
    async with httpx.AsyncClient() as client:
        try:
            headers = {
                "User-Agent": USER_AGENT
            }
            response = await client.get(RSS_FEED_URL, headers=headers, timeout=30.0)
            response.raise_for_status()
            
            # Parse the RSS feed
            feed_content = response.text
            feed = feedparser.parse(feed_content)
            
            # Update cache
            last_fetch_time = current_time
            cached_feed = feed
            
            return feed
        except Exception as e:
            if cached_feed:
                # Return cached data if available, even if it's stale
                return cached_feed
            raise Exception(f"Failed to fetch RSS feed: {str(e)}")

def parse_date(date_str: str) -> datetime.datetime:
    """Parse date string into datetime object."""
    try:
        return parser.parse(date_str)
    except:
        return datetime.datetime.now()  # Fallback to current time if parsing fails

def format_event(entry: Dict) -> str:
    """Format an event entry into a readable string."""
    title = entry.get('title', 'Untitled Event')
    
    # Extract and format the date
    date_str = entry.get('published', '')
    date_obj = parse_date(date_str)
    formatted_date = date_obj.strftime('%A, %B %d, %Y at %I:%M %p')
    
    # Extract location from summary if available
    summary = entry.get('summary', '')
    
    # Extract link
    link = entry.get('link', '')
    
    # Format the event information
    event_info = f"""
Event: {title}
Date: {formatted_date}
Details: {summary}
Link: {link}
"""
    return event_info

@mcp.tool()
async def get_upcoming_events(days: int = 7) -> str:
    """Get upcoming events at Brock University.
    
    Args:
        days: Number of days to look ahead (default: 7)
    """
    try:
        feed = await fetch_rss_feed()
        
        if not feed or not feed.entries:
            return "No events found in the RSS feed."
        
        # Calculate the date range
        now = datetime.datetime.now()
        end_date = now + datetime.timedelta(days=days)
        
        # Filter events by date
        upcoming_events = []
        for entry in feed.entries:
            date_str = entry.get('published', '')
            if not date_str:
                continue
                
            event_date = parse_date(date_str)
            
            # Check if the event is within the specified range
            if now <= event_date <= end_date:
                upcoming_events.append(entry)
        
        if not upcoming_events:
            return f"No events found in the next {days} days."
        
        # Format the events
        events_text = [format_event(event) for event in upcoming_events]
        
        return f"Upcoming events at Brock University for the next {days} days:\n\n" + "\n".join(events_text)
    
    except Exception as e:
        return f"Error retrieving upcoming events: {str(e)}"

@mcp.tool()
async def search_events(query: str) -> str:
    """Search for events at Brock University based on a keyword query.
    
    Args:
        query: Search term to find in event titles or descriptions
    """
    try:
        feed = await fetch_rss_feed()
        
        if not feed or not feed.entries:
            return "No events found in the RSS feed."
        
        # Filter events by search query
        matching_events = []
        query = query.lower()
        
        for entry in feed.entries:
            title = entry.get('title', '').lower()
            summary = entry.get('summary', '').lower()
            
            if query in title or query in summary:
                matching_events.append(entry)
        
        if not matching_events:
            return f"No events found matching '{query}'."
        
        # Format the events
        events_text = [format_event(event) for event in matching_events]
        
        return f"Events at Brock University matching '{query}':\n\n" + "\n".join(events_text)
    
    except Exception as e:
        return f"Error searching events: {str(e)}"

@mcp.tool()
async def get_events_by_date(date: str) -> str:
    """Get events at Brock University for a specific date.
    
    Args:
        date: Date in format YYYY-MM-DD
    """
    try:
        feed = await fetch_rss_feed()
        
        if not feed or not feed.entries:
            return "No events found in the RSS feed."
        
        # Parse the target date
        try:
            target_date = datetime.datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return f"Invalid date format: {date}. Please use YYYY-MM-DD format."
        
        # Get the date range for the entire day
        start_date = target_date.replace(hour=0, minute=0, second=0)
        end_date = target_date.replace(hour=23, minute=59, second=59)
        
        # Filter events by date
        day_events = []
        for entry in feed.entries:
            date_str = entry.get('published', '')
            if not date_str:
                continue
                
            event_date = parse_date(date_str)
            
            # Check if the event is on the specified date
            if start_date <= event_date <= end_date:
                day_events.append(entry)
        
        if not day_events:
            return f"No events found on {date}."
        
        # Format the events
        events_text = [format_event(event) for event in day_events]
        
        formatted_date = start_date.strftime('%A, %B %d, %Y')
        return f"Events at Brock University on {formatted_date}:\n\n" + "\n".join(events_text)
    
    except Exception as e:
        return f"Error retrieving events by date: {str(e)}"

@mcp.tool()
async def get_event_categories() -> str:
    """Get available event categories at Brock University."""
    try:
        feed = await fetch_rss_feed()
        
        if not feed or not feed.entries:
            return "No events found in the RSS feed."
        
        # Extract categories from events
        categories = set()
        for entry in feed.entries:
            if 'tags' in entry:
                for tag in entry.tags:
                    if 'term' in tag:
                        categories.add(tag.term)
        
        if not categories:
            return "No categories found in the events."
        
        # Format the categories
        sorted_categories = sorted(list(categories))
        return "Available event categories at Brock University:\n\n" + "\n".join(sorted_categories)
    
    except Exception as e:
        return f"Error retrieving event categories: {str(e)}"

@mcp.tool()
async def get_events_by_category(category: str) -> str:
    """Get events at Brock University for a specific category.
    
    Args:
        category: Event category to filter by
    """
    try:
        feed = await fetch_rss_feed()
        
        if not feed or not feed.entries:
            return "No events found in the RSS feed."
        
        # Filter events by category
        category_events = []
        category = category.lower()
        
        for entry in feed.entries:
            if 'tags' in entry:
                for tag in entry.tags:
                    if 'term' in tag and tag.term.lower() == category:
                        category_events.append(entry)
                        break
        
        if not category_events:
            return f"No events found in category '{category}'."
        
        # Format the events
        events_text = [format_event(event) for event in category_events]
        
        return f"Events at Brock University in category '{category}':\n\n" + "\n".join(events_text)
    
    except Exception as e:
        return f"Error retrieving events by category: {str(e)}"

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')