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
    
    # Extract and format the start/end date
    start_date_str = entry.get('start', '')
    end_date_str = entry.get('end', '')
    
    # If specific event start/end times not available, use published date
    if not start_date_str:
        date_str = entry.get('published', '')
        date_obj = parse_date(date_str)
        formatted_date = date_obj.strftime('%A, %B %d, %Y at %I:%M %p')
    else:
        # Parse start and end times
        start_date_obj = parse_date(start_date_str)
        end_date_obj = parse_date(end_date_str) if end_date_str else None
        
        if end_date_obj:
            # Format with start and end time
            formatted_date = f"{start_date_obj.strftime('%A, %B %d, %Y from %I:%M %p')} to {end_date_obj.strftime('%I:%M %p')}"
        else:
            # Format with just start time
            formatted_date = start_date_obj.strftime('%A, %B %d, %Y at %I:%M %p')
    
    # Extract location information
    location = entry.get('location', 'Location not specified')
    
    # Extract link
    link = entry.get('link', '')
    
    # Extract description and clean it up
    description = entry.get('description', '')
    # Try to extract cleaner description from the HTML content if available
    import re
    if description:
        # Try to extract the p-description section with cleaner text
        desc_match = re.search(r'<div class="p-description description">(.*?)</div>', description, re.DOTALL)
        if desc_match:
            # Extract text and remove HTML tags
            clean_desc = re.sub(r'<.*?>', ' ', desc_match.group(1))
            # Clean up excessive whitespace
            clean_desc = re.sub(r'\s+', ' ', clean_desc).strip()
        else:
            # If no match, just remove all HTML tags as a fallback
            clean_desc = re.sub(r'<.*?>', ' ', description)
            clean_desc = re.sub(r'\s+', ' ', clean_desc).strip()
    else:
        clean_desc = "No description available"
    
    # Get host information if available
    hosts = []
    if 'host' in entry:
        if isinstance(entry['host'], list):
            hosts = entry['host']
        else:
            hosts = [entry['host']]
    
    # Extract categories
    categories = []
    if 'category' in entry:
        if isinstance(entry['category'], list):
            categories = entry['category']
        else:
            categories = [entry['category']]
    
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
            
            # Extract start/end times if available
            start_time = event.get('start', '')
            end_time = event.get('end', '')
            
            if start_time and end_time:
                start_obj = parse_date(start_time)
                end_obj = parse_date(end_time)
                time_str = f"From {start_obj.strftime('%A, %B %d, %Y at %I:%M %p')} to {end_obj.strftime('%A, %B %d, %Y at %I:%M %p')}"
            elif start_time:
                start_obj = parse_date(start_time)
                time_str = f"{start_obj.strftime('%A, %B %d, %Y at %I:%M %p')}"
            else:
                time_str = "Date and time not specified"
            
            # Extract location
            location = event.get('location', 'Location not specified')
            
            # Extract hosts
            hosts = []
            if 'host' in event:
                if isinstance(event['host'], list):
                    hosts = event['host']
                else:
                    hosts = [event['host']]
            
            # Extract categories
            categories = []
            if 'category' in event:
                if isinstance(event['category'], list):
                    categories = event['category']
                else:
                    categories = [event['category']]
            
            # Extract full description
            description = event.get('description', '')
            import re
            if description:
                # Try to extract the p-description section with cleaner text
                desc_match = re.search(r'<div class="p-description description">(.*?)</div>', description, re.DOTALL)
                if desc_match:
                    # Extract text and remove HTML tags
                    clean_desc = re.sub(r'<.*?>', ' ', desc_match.group(1))
                    # Clean up excessive whitespace
                    clean_desc = re.sub(r'\s+', ' ', clean_desc).strip()
                else:
                    # If no match, just remove all HTML tags as a fallback
                    clean_desc = re.sub(r'<.*?>', ' ', description)
                    clean_desc = re.sub(r'\s+', ' ', clean_desc).strip()
            else:
                clean_desc = "No description available"
            
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
            # Check both 'tags' and 'category' fields
            if 'tags' in entry:
                for tag in entry.tags:
                    if 'term' in tag:
                        categories.add(tag.term)
            
            if 'category' in entry:
                # Handle both string and list formats
                if isinstance(entry['category'], list):
                    for category in entry['category']:
                        categories.add(category)
                else:
                    categories.add(entry['category'])
        
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
        
        # Filter events by category
        category_events = []
        category_lower = category.lower()
        
        for entry in feed.entries:
            # Check for tags
            if 'tags' in entry:
                for tag in entry.tags:
                    if 'term' in tag and category_lower in tag.term.lower():
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
        
        if not unique_events:
            # Try to suggest an alternative category
            suggested_categories = []
            for entry in feed.entries:
                if 'category' in entry:
                    if isinstance(entry['category'], list):
                        for cat in entry['category']:
                            if isinstance(cat, str):
                                suggested_categories.append(cat)
                    elif isinstance(entry['category'], str):
                        suggested_categories.append(entry['category'])
            
            suggested_categories = list(set(suggested_categories))
            suggestion_text = ""
            if suggested_categories:
                # Find similar categories
                import difflib
                matches = difflib.get_close_matches(category, suggested_categories, n=3, cutoff=0.3)
                if matches:
                    suggestion_text = f"\n\nYou might want to try these similar categories: {', '.join(matches)}"
            
            return f"No events found in category '{category}'.{suggestion_text}\n\nUse the get_event_categories tool to see all available categories."
        
        # Format the events
        events_text = [format_event(event) for event in unique_events]
        
        return f"Events at Brock University in category '{category}':\n\n" + "\n".join(events_text)
    
    except Exception as e:
        return f"Error retrieving events by category: {str(e)}"

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')