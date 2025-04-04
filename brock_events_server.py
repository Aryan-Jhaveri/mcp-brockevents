import asyncio
import httpx
import feedparser
import datetime
import re
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

def parse_date(date_str: str, convert_to_local: bool = True) -> datetime.datetime:
    """Parse date string into datetime object and convert to local time.
    
    Args:
        date_str: The date string to parse
        convert_to_local: If True, convert GMT/UTC to local time (or EST if local TZ can't be determined)
    """
    try:
        dt = parser.parse(date_str)
        
        if convert_to_local and dt.tzinfo is not None:
            # Try to get local timezone
            try:
                import pytz
                from datetime import timezone
                import time
                
                # Try to get local timezone
                local_tz = None
                try:
                    # Get local timezone using system time
                    local_tz_name = time.tzname[0]
                    local_tz = pytz.timezone(local_tz_name)
                except (ImportError, AttributeError, pytz.exceptions.UnknownTimeZoneError):
                    # If we can't get the local timezone, use Eastern Time (US) as default
                    local_tz = pytz.timezone('America/New_York')  # Eastern Time
                
                # Convert UTC time to local time
                if dt.tzinfo == timezone.utc or str(dt.tzinfo) == 'GMT':
                    dt = dt.astimezone(local_tz)
            except ImportError:
                # If pytz is not available, do a manual offset for EST (-5h from GMT)
                if str(dt.tzinfo) == 'GMT':
                    dt = dt - datetime.timedelta(hours=5)  # EST is GMT-5
            
            # Make naive for comparison operations
            dt = dt.replace(tzinfo=None)
        elif dt.tzinfo is not None:
            # If not converting but has timezone, make naive
            dt = dt.replace(tzinfo=None)
            
        return dt
    except Exception as e:
        # Fallback to current time if parsing fails
        return datetime.datetime.now().replace(tzinfo=None)

def extract_clean_description(description: str) -> str:
    """Extract and clean description text from HTML content."""
    if not description:
        return "No description available"
    
    # Check if content is wrapped in CDATA
    cdata_match = re.search(r'<!\[CDATA\[(.*?)\]\]>', description, re.DOTALL)
    if cdata_match:
        description = cdata_match.group(1)
    
    # Try to extract the p-description section with cleaner text
    desc_match = re.search(r'<div class="p-description description">(.*?)</div>', description, re.DOTALL)
    if desc_match:
        # Extract text and remove HTML tags
        clean_desc = re.sub(r'<.*?>', ' ', desc_match.group(1))
    else:
        # If no match, just remove all HTML tags as a fallback
        clean_desc = re.sub(r'<.*?>', ' ', description)
    
    # Clean up excessive whitespace
    return re.sub(r'\s+', ' ', clean_desc).strip()

def extract_hosts(entry: Dict) -> List[str]:
    """Extract host information from an event entry."""
    hosts = []
    if 'host' in entry:
        if isinstance(entry['host'], list):
            hosts = entry['host']
        else:
            hosts = [entry['host']]
    # Also check author field as backup for host information
    elif 'author' in entry:
        # Author field may contain email and name in format: email@example.com (Name)
        author = entry.get('author', '')
        match = re.search(r'\((.*?)\)', author)
        if match:
            hosts = [match.group(1)]
        else:
            # Just use the full author field if no pattern match
            hosts = [author]
    return hosts

def extract_categories(entry: Dict) -> List[str]:
    """Extract category information from an event entry."""
    categories = []
    # Check for regular categories
    if 'category' in entry:
        if isinstance(entry['category'], list):
            for cat in entry['category']:
                # Handle CDATA wrapped categories
                if isinstance(cat, str):
                    cdata_match = re.search(r'<!\[CDATA\[(.*?)\]\]>', cat, re.DOTALL)
                    if cdata_match:
                        categories.append(cdata_match.group(1))
                    else:
                        categories.append(cat)
                else:
                    categories.append(str(cat))
        else:
            # Handle single category
            cat = entry['category']
            cdata_match = re.search(r'<!\[CDATA\[(.*?)\]\]>', cat, re.DOTALL)
            if cdata_match:
                categories.append(cdata_match.group(1))
            else:
                categories.append(cat)
    
    # Check for tags (alternate way categories might be stored)
    if 'tags' in entry and hasattr(entry, 'tags'):
        for tag in entry.tags:
            if hasattr(tag, 'term') and tag.term:
                categories.append(tag.term)
    
    return categories

def extract_times_from_html(description: str) -> tuple:
    """Extract start and end times from HTML description.
    
    Returns:
        Tuple of (start_datetime, end_datetime) or (None, None) if not found
    """
    if not description:
        return None, None
    
    # Look for datetime attributes in time tags
    start_match = re.search(r'<time class="dt-start dtstart" datetime="([^"]+)"', description)
    end_match = re.search(r'<time class="dt-end dtend" datetime="([^"]+)"', description)
    
    start_datetime = None
    end_datetime = None
    
    if start_match:
        try:
            start_datetime = parser.parse(start_match.group(1))
        except:
            pass
            
    if end_match:
        try:
            end_datetime = parser.parse(end_match.group(1))
        except:
            pass
    
    return start_datetime, end_datetime

def format_event_date(entry: Dict) -> str:
    """Format the date information from an event entry with local time."""
    description = entry.get('description', '')
    
    # Try to extract times from HTML description first
    start_datetime, end_datetime = extract_times_from_html(description)
    
    # If HTML extraction didn't work, use namespace events:start and events:end
    if not start_datetime:
        start_date_str = entry.get('start', '')
        if start_date_str:
            start_datetime = parser.parse(start_date_str)
    
    if not end_datetime:
        end_date_str = entry.get('end', '')
        if end_date_str:
            end_datetime = parser.parse(end_date_str)
    
    # Try to determine local timezone name for display
    tz_name = "EDT"  # Default to Eastern Daylight Time since the events are in EDT
    try:
        import time
        import pytz
        from datetime import timezone
        
        # Try to get local timezone name
        try:
            local_tz_name = time.tzname[0]
            tz = pytz.timezone(local_tz_name)
            tz_name = tz.localize(datetime.datetime.now()).strftime("%Z")
        except:
            # Keep EDT as default
            pass
    except:
        pass
    
    # If no start time was found, use published date
    if not start_datetime:
        date_str = entry.get('published', '')
        date_obj = parse_date(date_str, convert_to_local=True)
        return f"{date_obj.strftime('%A, %B %d, %Y at %I:%M %p')} {tz_name}"
    else:
        # Convert to local time if needed
        if start_datetime.tzinfo is not None:
            start_date_obj = parse_date(str(start_datetime), convert_to_local=True)
        else:
            start_date_obj = start_datetime
            
        if end_datetime:
            if end_datetime.tzinfo is not None:
                end_date_obj = parse_date(str(end_datetime), convert_to_local=True)
            else:
                end_date_obj = end_datetime
        else:
            end_date_obj = None
        
        if end_date_obj:
            # Check if start and end are on the same day
            if start_date_obj.date() == end_date_obj.date():
                # Format with start and end time on same day
                return f"{start_date_obj.strftime('%A, %B %d, %Y from %I:%M %p')} to {end_date_obj.strftime('%I:%M %p')} {tz_name}"
            else:
                # Format with full date and time for both start and end
                return f"{start_date_obj.strftime('%A, %B %d, %Y at %I:%M %p')} to {end_date_obj.strftime('%A, %B %d, %Y at %I:%M %p')} {tz_name}"
        else:
            # Format with just start time
            return f"{start_date_obj.strftime('%A, %B %d, %Y at %I:%M %p')} {tz_name}"

def extract_location_from_html(description: str) -> str:
    """Extract location from HTML description."""
    if not description:
        return "Location not specified"
    
    # Look for location tag
    location_match = re.search(r'<span class="p-location location">([^<]+)</span>', description)
    
    if location_match:
        return location_match.group(1).strip()
    
    return "Location not specified"

def format_event(entry: Dict) -> str:
    """Format an event entry into a readable string."""
    title = entry.get('title', 'Untitled Event')
    
    # Format date information
    formatted_date = format_event_date(entry)
    
    # Extract location - first try HTML description, then fall back to namespace
    description = entry.get('description', '')
    location = extract_location_from_html(description)
    
    # If location not found in HTML, check events:location namespace
    if location == "Location not specified":
        location = entry.get('location', 'Location not specified')
    
    # Extract link
    link = entry.get('link', '')
    
    # Extract and clean description
    clean_desc = extract_clean_description(description)
    
    # Get host and category information
    hosts = extract_hosts(entry)
    categories = extract_categories(entry)
    
    # Format the event information
    event_info = f"""
Event: {title}
Date: {formatted_date}
Location: {location}
"""

    if hosts:
        event_info += f"Hosted by: {', '.join(hosts)}\n"
    
    if categories:
        event_info += f"Categories: {', '.join(categories)}\n"
    
    event_info += f"""
Description: {clean_desc[:300]}{"..." if len(clean_desc) > 300 else ""}

Link: {link}
"""
    return event_info

def filter_events_by_category(entries: List[Dict], category: str) -> List[Dict]:
    """Filter events by a specific category and return unique events."""
    category_events = []
    category_lower = category.lower()
    
    for entry in entries:
        # Check for tags
        if 'tags' in entry and hasattr(entry, 'tags'):
            for tag in entry.tags:
                if hasattr(tag, 'term') and tag.term and category_lower in tag.term.lower():
                    category_events.append(entry)
                    break
        
        # Check for category field which may be list or string
        if 'category' in entry:
            found = False
            if isinstance(entry['category'], list):
                for cat in entry['category']:
                    if isinstance(cat, str) and category_lower in cat.lower():
                        category_events.append(entry)
                        found = True
                        break
            elif isinstance(entry['category'], str) and category_lower in entry['category'].lower():
                category_events.append(entry)
                found = True
            
            if found:
                continue
        
        # Check in description for related terms as fallback
        if 'description' in entry and isinstance(entry['description'], str):
            if category_lower in entry['description'].lower():
                category_events.append(entry)
    
    # Remove duplicates (since we might have added the same event multiple times)
    unique_events = []
    seen_links = set()
    for event in category_events:
        if event.get('link') not in seen_links:
            unique_events.append(event)
            seen_links.add(event.get('link'))
    
    return unique_events

def suggest_similar_categories(entries: List[Dict], category: str) -> str:
    """Suggest similar categories based on available categories in the feed."""
    # Extract all available categories
    suggested_categories = []
    for entry in entries:
        # Get categories from our helper function
        entry_categories = extract_categories(entry)
        for cat in entry_categories:
            if cat:
                suggested_categories.append(cat)
    
    suggested_categories = list(set(suggested_categories))
    suggestion_text = ""
    
    if suggested_categories:
        # Find similar categories
        import difflib
        matches = difflib.get_close_matches(category, suggested_categories, n=3, cutoff=0.3)
        if matches:
            suggestion_text = f"\n\nYou might want to try these similar categories: {', '.join(matches)}"
    
    return suggestion_text

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
        
        # Calculate the date range - ensure naive datetime
        now = datetime.datetime.now().replace(tzinfo=None)
        end_date = now + datetime.timedelta(days=days)
        
        # Filter events by date
        upcoming_events = []
        for entry in feed.entries:
            # First check for event start time
            start_date_str = entry.get('start', '')
            if start_date_str:
                event_date = parse_date(start_date_str)
            else:
                # Fall back to published date
                date_str = entry.get('published', '')
                if not date_str:
                    continue
                event_date = parse_date(date_str)
            
            # Check if the event is within the specified range
            if now <= event_date <= end_date:
                upcoming_events.append(entry)
        
        if not upcoming_events:
            return f"No events found in the next {days} days."
        
        # Sort events by date
        upcoming_events.sort(key=lambda x: parse_date(x.get('start', x.get('published', ''))))
        
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
            description = entry.get('description', '').lower()
            
            if query in title or query in summary or query in description:
                matching_events.append(entry)
        
        if not matching_events:
            return f"No events found matching '{query}'."
        
        # Format the events
        events_text = [format_event(event) for event in matching_events]
        
        return f"Events at Brock University matching '{query}':\n\n" + "\n".join(events_text)
    
    except Exception as e:
        return f"Error searching events: {str(e)}"

@mcp.tool()
async def get_event_details(query: str) -> str:
    """Get detailed information about a specific event by name or ID.
    
    Args:
        query: Event name or ID to search for
    """
    try:
        feed = await fetch_rss_feed()
        
        if not feed or not feed.entries:
            return "No events found in the RSS feed."
        
        # Search for events matching the query
        matching_events = []
        query_lower = query.lower()
        
        for entry in feed.entries:
            # Check event title
            title = entry.get('title', '').lower()
            if query_lower in title:
                matching_events.append(entry)
                continue
            
            # Check event ID/GUID if available
            guid = entry.get('guid', '').lower()
            if query_lower in guid:
                matching_events.append(entry)
                continue
            
            # Check in description as fallback
            if 'description' in entry and isinstance(entry['description'], str):
                if query_lower in entry['description'].lower():
                    matching_events.append(entry)
        
        if not matching_events:
            return f"No events found matching '{query}'. Try searching with a different term."
        
        # If we found multiple matches, return the most detailed one or the first one
        best_match = None
        best_match_score = -1
        
        for event in matching_events:
            # Calculate a match score based on how closely it matches the query
            title = event.get('title', '').lower()
            
            # Exact match gets highest score
            if title == query_lower:
                best_match_score = float('inf')
                best_match = event
                break
            
            # Calculate score based on various factors
            score = 0
            
            # Title starts with query
            if title.startswith(query_lower):
                score += 10
            
            # Query appears in title (already checked above)
            score += 5
            
            # Has description
            if 'description' in event and event['description']:
                score += 3
            
            # Has location
            if 'location' in event and event['location']:
                score += 2
            
            # Has start/end times
            if 'start' in event and event['start']:
                score += 2
            
            # Update best match if score is higher
            if score > best_match_score:
                best_match_score = score
                best_match = event
        
        if best_match:
            # Format detailed event information
            event = best_match
            title = event.get('title', 'Untitled Event')
            link = event.get('link', '')
            
            # Get the description for time and location extraction
            description = event.get('description', '')
            
            # Extract start and end times from HTML first
            start_datetime, end_datetime = extract_times_from_html(description)
            
            # If not found in HTML, fall back to namespace times
            if not start_datetime:
                start_time = event.get('start', '')
                if start_time:
                    start_datetime = parser.parse(start_time)
            
            if not end_datetime:
                end_time = event.get('end', '')
                if end_time:
                    end_datetime = parser.parse(end_time)
            
            # Try to determine timezone name for display
            tz_name = "EDT"  # Default to EDT since Brock University is in Eastern Time
            try:
                import time
                import pytz
                
                try:
                    local_tz_name = time.tzname[0]
                    tz = pytz.timezone(local_tz_name)
                    tz_name = tz.localize(datetime.datetime.now()).strftime("%Z")
                except:
                    pass  # Keep EDT as default
            except:
                pass
            
            # Format the time string
            if start_datetime and end_datetime:
                # Convert to local time if needed
                if start_datetime.tzinfo is not None:
                    start_obj = parse_date(str(start_datetime), convert_to_local=True)
                else:
                    start_obj = start_datetime
                    
                if end_datetime.tzinfo is not None:
                    end_obj = parse_date(str(end_datetime), convert_to_local=True)
                else:
                    end_obj = end_datetime
                
                # Check if start and end are on the same day
                if start_obj.date() == end_obj.date():
                    time_str = f"From {start_obj.strftime('%A, %B %d, %Y at %I:%M %p')} to {end_obj.strftime('%I:%M %p')} {tz_name}"
                else:
                    time_str = f"From {start_obj.strftime('%A, %B %d, %Y at %I:%M %p')} to {end_obj.strftime('%A, %B %d, %Y at %I:%M %p')} {tz_name}"
            elif start_datetime:
                if start_datetime.tzinfo is not None:
                    start_obj = parse_date(str(start_datetime), convert_to_local=True)
                else:
                    start_obj = start_datetime
                time_str = f"{start_obj.strftime('%A, %B %d, %Y at %I:%M %p')} {tz_name}"
            else:
                # If no times found, try published date
                date_str = event.get('published', '')
                if date_str:
                    date_obj = parse_date(date_str, convert_to_local=True)
                    time_str = f"{date_obj.strftime('%A, %B %d, %Y at %I:%M %p')} {tz_name}"
                else:
                    time_str = "Date and time not specified"
            
            # Extract location from HTML first, then fall back to namespace
            location = extract_location_from_html(description)
            if location == "Location not specified":
                location = event.get('location', 'Location not specified')
            
            # Use helper functions to extract event information
            hosts = extract_hosts(event)
            categories = extract_categories(event)
            
            # Extract full description
            description = event.get('description', '')
            clean_desc = extract_clean_description(description)
            
            # Format detailed event information
            result = f"""
Detailed information for: {title}

WHEN: {time_str}

WHERE: {location}
"""
            
            if hosts:
                result += f"\nHOSTED BY: {', '.join(hosts)}\n"
            
            if categories:
                result += f"\nCATEGORIES: {', '.join(categories)}\n"
            
            result += f"""
DESCRIPTION:
{clean_desc}

LINK: {link}
"""
            
            return result
        else:
            return f"No events found matching '{query}'. Try searching with a different term."
    
    except Exception as e:
        return f"Error retrieving event details: {str(e)}"

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
            # Support more flexible date formats
            if len(date) <= 10 and '-' in date:
                target_date = datetime.datetime.strptime(date, '%Y-%m-%d')
            else:
                target_date = parser.parse(date)
                
            # Ensure naive datetime
            if target_date.tzinfo is not None:
                target_date = target_date.replace(tzinfo=None)
        except ValueError:
            return f"Invalid date format: {date}. Please use YYYY-MM-DD format or a natural language date like 'April 10' or 'next Monday'."
        
        # Get the date range for the entire day
        start_date = target_date.replace(hour=0, minute=0, second=0)
        end_date = target_date.replace(hour=23, minute=59, second=59)
        
        # Filter events by date
        day_events = []
        for entry in feed.entries:
            # Try start field first (from events namespace)
            date_str = entry.get('start', '')
            if not date_str:
                # Fall back to published date
                date_str = entry.get('published', '')
                
            if not date_str:
                continue
                
            event_date = parse_date(date_str)
            
            # Check if the event is on the specified date
            if start_date <= event_date <= end_date:
                day_events.append(entry)
        
        if not day_events:
            formatted_date = start_date.strftime('%A, %B %d, %Y')
            return f"No events found on {formatted_date}."
        
        # Sort events by time
        day_events.sort(key=lambda x: parse_date(x.get('start', x.get('published', ''))))
        
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
        
        # Extract categories from events using our helper function
        categories = set()
        for entry in feed.entries:
            entry_categories = extract_categories(entry)
            for category in entry_categories:
                if category:
                    categories.add(category)
        
        if not categories:
            return "No categories found in the events."
        
        # Format the categories
        sorted_categories = sorted(list(categories))
        
        # Group categories by type if possible
        academic_categories = [c for c in sorted_categories if any(term in c.lower() for term in ['academic', 'education', 'lecture', 'workshop', 'thoughtful', 'learning'])]
        social_categories = [c for c in sorted_categories if any(term in c.lower() for term in ['social', 'party', 'networking', 'festival'])]
        arts_categories = [c for c in sorted_categories if any(term in c.lower() for term in ['art', 'music', 'performance', 'exhibition'])]
        sports_categories = [c for c in sorted_categories if any(term in c.lower() for term in ['sport', 'athletic', 'fitness', 'game'])]
        
        # Add remaining categories to other
        other_categories = [c for c in sorted_categories if c not in academic_categories + social_categories + arts_categories + sports_categories]
        
        result = "Available event categories at Brock University:\n\n"
        
        if academic_categories:
            result += "Academic & Learning:\n" + "\n".join(f"- {c}" for c in academic_categories) + "\n\n"
        
        if social_categories:
            result += "Social & Community:\n" + "\n".join(f"- {c}" for c in social_categories) + "\n\n"
        
        if arts_categories:
            result += "Arts & Culture:\n" + "\n".join(f"- {c}" for c in arts_categories) + "\n\n"
        
        if sports_categories:
            result += "Sports & Recreation:\n" + "\n".join(f"- {c}" for c in sports_categories) + "\n\n"
        
        if other_categories:
            result += "Other Categories:\n" + "\n".join(f"- {c}" for c in other_categories)
        
        return result
    
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
        
        # Filter events by category using helper function
        unique_events = filter_events_by_category(feed.entries, category)
        
        if not unique_events:
            suggestion_text = suggest_similar_categories(feed.entries, category)
            return f"No events found in category '{category}'.{suggestion_text}\n\nUse the get_event_categories tool to see all available categories."
        
        # Format the events
        events_text = [format_event(event) for event in unique_events]
        
        return f"Events at Brock University in category '{category}':\n\n" + "\n".join(events_text)
    
    except Exception as e:
        return f"Error retrieving events by category: {str(e)}"

@mcp.tool()
async def get_events_by_date_range(start_date: str, end_date: str) -> str:
    """Get events at Brock University within a specific date range.
    
    Args:
        start_date: Start date in format YYYY-MM-DD or natural language like 'April 10'
        end_date: End date in format YYYY-MM-DD or natural language like 'April 15'
    """
    try:
        feed = await fetch_rss_feed()
        
        if not feed or not feed.entries:
            return "No events found in the RSS feed."
        
        # Parse the dates
        try:
            # Parse start date (support flexible formats)
            if len(start_date) <= 10 and '-' in start_date:
                start_dt = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            else:
                start_dt = parser.parse(start_date)
            
            # Parse end date (support flexible formats)
            if len(end_date) <= 10 and '-' in end_date:
                end_dt = datetime.datetime.strptime(end_date, '%Y-%m-%d')
            else:
                end_dt = parser.parse(end_date)
            
            # Ensure the datetimes are naive (no timezone info)
            if start_dt.tzinfo is not None:
                start_dt = start_dt.replace(tzinfo=None)
            if end_dt.tzinfo is not None:
                end_dt = end_dt.replace(tzinfo=None)
            
            # Set start to beginning of day and end to end of day
            range_start = start_dt.replace(hour=0, minute=0, second=0)
            range_end = end_dt.replace(hour=23, minute=59, second=59)
            
        except ValueError as e:
            return f"Invalid date format: {str(e)}. Please use YYYY-MM-DD format or natural language like 'April 10'."
        
        # Filter events by date range
        range_events = []
        for entry in feed.entries:
            # Try start field first (from events namespace)
            date_str = entry.get('start', '')
            if not date_str:
                # Fall back to published date
                date_str = entry.get('published', '')
                
            if not date_str:
                continue
                
            event_date = parse_date(date_str)
            
            # Check if the event is within the specified range
            if range_start <= event_date <= range_end:
                range_events.append(entry)
        
        if not range_events:
            formatted_start = range_start.strftime('%A, %B %d, %Y')
            formatted_end = range_end.strftime('%A, %B %d, %Y')
            return f"No events found between {formatted_start} and {formatted_end}."
        
        # Sort events by date
        range_events.sort(key=lambda x: parse_date(x.get('start', x.get('published', ''))))
        
        # Format the events
        events_text = [format_event(event) for event in range_events]
        
        formatted_start = range_start.strftime('%A, %B %d, %Y')
        formatted_end = range_end.strftime('%A, %B %d, %Y')
        return f"Events at Brock University between {formatted_start} and {formatted_end}:\n\n" + "\n".join(events_text)
    
    except Exception as e:
        return f"Error retrieving events by date range: {str(e)}"

@mcp.tool()
async def get_events_by_time_of_day(date: str = "", time_range: str = "morning") -> str:
    """Get events at Brock University for a specific time of day.
    
    Args:
        date: Optional date in format YYYY-MM-DD or natural language (defaults to today)
        time_range: Time of day - one of 'morning', 'afternoon', 'evening', or specific hours like '2pm-5pm'
    """
    try:
        feed = await fetch_rss_feed()
        
        if not feed or not feed.entries:
            return "No events found in the RSS feed."
        
        # Parse the target date
        try:
            if date:
                # Support flexible date formats
                if len(date) <= 10 and '-' in date:
                    target_date = datetime.datetime.strptime(date, '%Y-%m-%d')
                else:
                    target_date = parser.parse(date)
                    
                # Ensure naive datetime
                if target_date.tzinfo is not None:
                    target_date = target_date.replace(tzinfo=None)
            else:
                # Default to today
                target_date = datetime.datetime.now().replace(tzinfo=None)
                
            # Set to beginning of day
            target_date = target_date.replace(hour=0, minute=0, second=0)
            
        except ValueError:
            return f"Invalid date format: {date}. Please use YYYY-MM-DD format or a natural language date."
        
        # Determine time range hours
        if time_range.lower() == "morning":
            start_hour = 5
            end_hour = 11
            range_name = "morning (5 AM - 12 PM)"
        elif time_range.lower() == "afternoon":
            start_hour = 12
            end_hour = 16
            range_name = "afternoon (12 PM - 5 PM)"
        elif time_range.lower() == "evening":
            start_hour = 17
            end_hour = 23
            range_name = "evening (5 PM - 12 AM)"
        elif "-" in time_range:
            # Parse a specific time range like "2pm-5pm"
            try:
                time_parts = time_range.split("-")
                start_time = parser.parse(time_parts[0])
                end_time = parser.parse(time_parts[1])
                
                # Ensure naive datetime
                if start_time.tzinfo is not None:
                    start_time = start_time.replace(tzinfo=None)
                if end_time.tzinfo is not None:
                    end_time = end_time.replace(tzinfo=None)
                    
                start_hour = start_time.hour
                end_hour = end_time.hour
                range_name = f"{start_time.strftime('%-I %p')} - {end_time.strftime('%-I %p')}"
            except:
                return f"Invalid time range format: {time_range}. Use 'morning', 'afternoon', 'evening', or a specific range like '2pm-5pm'."
        else:
            return f"Invalid time range: {time_range}. Use 'morning', 'afternoon', 'evening', or a specific range like '2pm-5pm'."
        
        # Set the full date range
        start_date = target_date.replace(hour=start_hour, minute=0, second=0)
        end_date = target_date.replace(hour=end_hour, minute=59, second=59)
        
        # Filter events by time range
        filtered_events = []
        for entry in feed.entries:
            # Try start field first (from events namespace)
            date_str = entry.get('start', '')
            if not date_str:
                # Fall back to published date
                date_str = entry.get('published', '')
                
            if not date_str:
                continue
                
            event_date = parse_date(date_str)
            
            # First check if it's on the right day
            if event_date.date() != target_date.date():
                continue
            
            # Then check if it's in the requested time range
            event_hour = event_date.hour
            if start_hour <= event_hour <= end_hour:
                filtered_events.append(entry)
        
        if not filtered_events:
            formatted_date = target_date.strftime('%A, %B %d, %Y')
            return f"No events found on {formatted_date} during the {range_name}."
        
        # Sort events by time
        filtered_events.sort(key=lambda x: parse_date(x.get('start', x.get('published', ''))))
        
        # Format the events
        events_text = [format_event(event) for event in filtered_events]
        
        formatted_date = target_date.strftime('%A, %B %d, %Y')
        return f"Events at Brock University on {formatted_date} during the {range_name}:\n\n" + "\n".join(events_text)
    
    except Exception as e:
        return f"Error retrieving events by time of day: {str(e)}"

@mcp.tool()
async def get_events_this_week() -> str:
    """Get all events at Brock University occurring this week (Monday-Sunday)."""
    try:
        # Calculate the date range for this week
        today = datetime.datetime.now().replace(tzinfo=None)
        start_of_week = today - datetime.timedelta(days=today.weekday())  # Monday
        end_of_week = start_of_week + datetime.timedelta(days=6)  # Sunday
        
        # Format dates for the query
        start_date = start_of_week.strftime('%Y-%m-%d')
        end_date = end_of_week.strftime('%Y-%m-%d')
        
        # Use the date range function
        return await get_events_by_date_range(start_date, end_date)
    
    except Exception as e:
        return f"Error retrieving events for this week: {str(e)}"

@mcp.tool()
async def get_events_next_week() -> str:
    """Get all events at Brock University occurring next week (Monday-Sunday)."""
    try:
        # Calculate the date range for next week
        today = datetime.datetime.now().replace(tzinfo=None)
        start_of_this_week = today - datetime.timedelta(days=today.weekday())  # Monday of this week
        start_of_next_week = start_of_this_week + datetime.timedelta(days=7)  # Monday of next week
        end_of_next_week = start_of_next_week + datetime.timedelta(days=6)  # Sunday of next week
        
        # Format dates for the query
        start_date = start_of_next_week.strftime('%Y-%m-%d')
        end_date = end_of_next_week.strftime('%Y-%m-%d')
        
        # Use the date range function
        return await get_events_by_date_range(start_date, end_date)
    
    except Exception as e:
        return f"Error retrieving events for next week: {str(e)}"

@mcp.tool()
async def get_weekend_events(date: str = "") -> str:
    """Get events at Brock University occurring on the weekend.
    
    Args:
        date: Optional date in format YYYY-MM-DD or natural language (defaults to upcoming weekend)
    """
    try:
        # Parse the target date
        if date:
            try:
                if len(date) <= 10 and '-' in date:
                    target_date = datetime.datetime.strptime(date, '%Y-%m-%d')
                else:
                    target_date = parser.parse(date)
                    
                # Ensure naive datetime
                if target_date.tzinfo is not None:
                    target_date = target_date.replace(tzinfo=None)
            except ValueError:
                return f"Invalid date format: {date}. Please use YYYY-MM-DD format or a natural language date."
        else:
            # Default to today
            target_date = datetime.datetime.now().replace(tzinfo=None)
        
        # Find the surrounding weekend
        weekday = target_date.weekday()
        
        if weekday >= 5:  # If target date is already a weekend (5=Saturday, 6=Sunday)
            # Calculate the current weekend
            days_from_saturday = weekday - 5
            saturday = target_date - datetime.timedelta(days=days_from_saturday)
            sunday = saturday + datetime.timedelta(days=1)
        else:
            # Calculate the upcoming weekend
            days_to_saturday = 5 - weekday
            saturday = target_date + datetime.timedelta(days=days_to_saturday)
            sunday = saturday + datetime.timedelta(days=1)
        
        # Format dates for the query
        start_date = saturday.strftime('%Y-%m-%d')
        end_date = sunday.strftime('%Y-%m-%d')
        
        # Use the date range function
        result = await get_events_by_date_range(start_date, end_date)
        
        # Replace the title to specify weekend
        result = result.replace("between", "for the weekend of")
        return result
    
    except Exception as e:
        return f"Error retrieving weekend events: {str(e)}"

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')