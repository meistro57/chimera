"""
Comprehensive logging system for Chimera conversations and sessions.
Generates detailed markdown files for each conversation session.
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import uuid

class ConversationLogger:
    """Enhanced logger that creates detailed markdown files for each conversation session."""

    def __init__(self):
        self.log_dir = Path("logs/conversations")
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Setup Python logging
        self._setup_file_logging()

        # Active conversation sessions
        self.active_sessions: Dict[str, Dict[str, Any]] = {}

    def _setup_file_logging(self):
        """Configure file logging for system events."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_dir / "system.log"),
                logging.StreamHandler()  # Also log to console
            ]
        )
        self.system_logger = logging.getLogger("chimera.system")

    def start_conversation_log(self, conversation_id: str, participants: List[str]) -> str:
        """
        Start logging a new conversation session.

        Args:
            conversation_id: Unique conversation identifier
            participants: List of persona names

        Returns:
            Path to the log file
        """
        session_data = {
            "conversation_id": conversation_id,
            "participants": participants,
            "start_time": datetime.now().isoformat(),
            "messages": [],
            "events": [],
            "metadata": {
                "persona_count": len(participants),
                "session_started": datetime.now().isoformat()
            }
        }

        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{conversation_id[:8]}.md"
        filepath = self.log_dir / filename

        self.active_sessions[conversation_id] = {
            "data": session_data,
            "filename": filename,
            "filepath": str(filepath)
        }

        # Initialize the markdown file
        self._write_initial_markdown(conversation_id, participants)

        self.system_logger.info(f"Started conversation logging: {conversation_id} with {participants}")

        return str(filepath)

    def log_message(self, conversation_id: str, message_data: Dict[str, Any]):
        """
        Log a message in the conversation.

        Args:
            message_data: Contains type, sender information, content, timestamp, etc.
        """
        if conversation_id not in self.active_sessions:
            self.system_logger.warning(f"No active session for conversation: {conversation_id}")
            return

        session = self.active_sessions[conversation_id]
        session["data"]["messages"].append(message_data)

        # Append to markdown file
        self._append_message_to_markdown(conversation_id, message_data)

        # Also log to system log
        content_preview = message_data.get("content", "")[:100]
        sender_name = message_data.get("persona_name", message_data.get("sender", "unknown"))
        self.system_logger.info(f"[{conversation_id}] {sender_name}: {content_preview}...")

    def _log_system_event(self, event_type: str, event_data: Dict[str, Any]):
        """Log system-level events to the system.log file (not markdown files)."""
        self.system_logger.info(f"System Event: {event_type} - {json.dumps(event_data, indent=2)}")

    def log_event(self, conversation_id: str, event_type: str, event_data: Dict[str, Any]):
        """
        Log a system event in the conversation.

        Args:
            event_type: Type of event (started, ended, error, topic_change, etc.)
            event_data: Event-specific data
        """
        # Handle system-level events (not tied to specific conversations)
        if conversation_id == "system":
            self._log_system_event(event_type, event_data)
            return

        if conversation_id not in self.active_sessions:
            self.system_logger.warning(f"No active session for conversation: {conversation_id}")
            return

        event_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "data": event_data
        }

        session = self.active_sessions[conversation_id]
        session["data"]["events"].append(event_entry)

        # Append to markdown file
        self._append_event_to_markdown(conversation_id, event_entry)

        self.system_logger.info(f"[{conversation_id}] Event: {event_type} - {event_data}")

    def end_conversation_log(self, conversation_id: str, summary_stats: Dict[str, Any] = None):
        """
        End logging for a conversation session and finalize the markdown file.

        Args:
            summary_stats: Optional statistics about the conversation
        """
        if conversation_id not in self.active_sessions:
            self.system_logger.warning(f"No active session for conversation: {conversation_id}")
            return

        session = self.active_sessions[conversation_id]

        # Update end time
        end_time = datetime.now()
        session["data"]["end_time"] = end_time.isoformat()
        session["data"]["duration_seconds"] = self._calculate_duration(
            session["data"]["start_time"], end_time.isoformat()
        )

        # Add summary stats if provided
        if summary_stats:
            session["data"]["summary_stats"] = summary_stats

        # Finalize the markdown file
        self._finalize_markdown_file(conversation_id)

        # Save to JSON backup (optional)
        self._save_session_json(conversation_id)

        self.system_logger.info(f"Ended conversation logging: {conversation_id}")

        # Remove from active sessions
        del self.active_sessions[conversation_id]

    def _write_initial_markdown(self, conversation_id: str, participants: List[str]):
        """Write the initial markdown structure for a conversation."""
        session = self.active_sessions[conversation_id]
        filepath = self.log_dir / session["filename"]

        start_time = session["data"]["start_time"]
        formatted_datetime = datetime.fromisoformat(start_time).strftime("%A, %B %d, %Y at %I:%M:%S %p")

        markdown_content = f"""# Chimera AI Conversation Log

## Session Information
- **Conversation ID**: `{conversation_id}`
- **Session Start**: {formatted_datetime}
- **Participants**: {", ".join(participants)}
- **Participant Count**: {len(participants)}

## AI System Details
**Provider Assignment:**
"""

        # Add participant details
        for participant in participants:
            provider = self._get_provider_for_persona(participant)
            markdown_content += f"- **{participant}**: {provider}\n"

        markdown_content += "\n## Conversation Transcript\n\n"

        # Write to file
        with open(filepath, 'w') as f:
            f.write(markdown_content)

    def _append_message_to_markdown(self, conversation_id: str, message_data: Dict[str, Any]):
        """Append a message to the markdown file."""
        session = self.active_sessions[conversation_id]
        filepath = self.log_dir / session["filename"]

        # Format the message
        message_type = message_data.get("type", "message")
        timestamp = message_data.get("timestamp", datetime.now().isoformat())

        if message_type == "typing":
            # Typing indicators are visual, skip in log
            return
        elif message_type == "system":
            # System messages (like conversation starters)
            content = f"**System**: {message_data.get('content', '')}"
        else:
            # Regular messages
            persona_name = message_data.get("persona_name", "Unknown")
            sender_type = message_data.get("sender_type", "unknown")
            content = message_data.get("content", "")
            avatar_emoji = self._get_avatar_emoji(message_data.get("persona", ""))

            content = f"**{avatar_emoji} {persona_name}** (*{sender_type}*): {content}"

        # Format timestamp
        dt = datetime.fromtimestamp(timestamp) if isinstance(timestamp, (int, float)) else datetime.fromisoformat(timestamp)
        time_str = dt.strftime("%H:%M:%S")

        # Append to file
        with open(filepath, 'a') as f:
            f.write(f"### [{time_str}]\n{content}\n\n")

    def _append_event_to_markdown(self, conversation_id: str, event_entry: Dict[str, Any]):
        """Append an event to the markdown file."""
        session = self.active_sessions[conversation_id]
        filepath = self.log_dir / session["filename"]

        event_type = event_entry.get("type", "unknown")
        timestamp = event_entry.get("timestamp", "")
        data = event_entry.get("data", {})

        dt = datetime.fromisoformat(timestamp)
        time_str = dt.strftime("%H:%M:%S")

        # Format based on event type
        if event_type == "topic_shift":
            content = f"**System Event** (Topic Shift): Conversation evolved to explore: *{data.get('new_topic', 'Unknown')}*"
        elif event_type == "fastapi_startup":
            content = "**System Event** (API Startup): Chimera API server initialized"
        elif event_type == "conversation_start":
            content = "**System Event** (Conversation Start): AI conversation began"
        elif event_type == "conversation_end":
            content = "**System Event** (Conversation End): Session concluded"
        else:
            content = f"**System Event** ({event_type}): {json.dumps(data, indent=2)}"

        # Append to file
        with open(filepath, 'a') as f:
            f.write(f"### [{time_str}]\n{content}\n\n")

    def _finalize_markdown_file(self, conversation_id: str):
        """Add session summary and final statistics to the markdown file."""
        session = self.active_sessions[conversation_id]
        filepath = self.log_dir / session["filename"]
        data = session["data"]

        # Calculate statistics
        messages = data["messages"]
        regular_messages = [m for m in messages if m.get("type") == "message"]
        participant_counts = {}
        for msg in regular_messages:
            persona = msg.get("persona", "unknown")
            participant_counts[persona] = participant_counts.get(persona, 0) + 1

        total_messages = len(regular_messages)
        avg_length_per_message = sum(len(m.get("content", "")) for m in regular_messages) / max(total_messages, 1)
        duration_min = data.get("duration_seconds", 0) / 60

        if data.get("end_time"):
            start_dt = datetime.fromisoformat(data["start_time"])
            end_dt = datetime.fromisoformat(data["end_time"])
            actual_duration_min = (end_dt - start_dt).total_seconds() / 60
        else:
            actual_duration_min = duration_min

        # Append summary section
        summary_content = f"""
## Session Summary

### Statistics
- **Total Messages**: {total_messages}
- **Session Duration**: {actual_duration_min:.1f} minutes
- **Average Message Length**: {avg_length_per_message:.0f} characters
- **Messages Per Minute**: {(total_messages / max(actual_duration_min, 1)):.1f}

### Participant Activity
"""

        for participant, count in participant_counts.items():
            avatar_emoji = self._get_avatar_emoji(participant)
            percentage = (count / max(total_messages, 1)) * 100
            summary_content += f"- **{avatar_emoji} {participant}**: {count} messages ({percentage:.1f}%)\n"

        # Add events summary if any
        events = data.get("events", [])
        if events:
            summary_content += "\n### System Events\n"
            for event in events:
                event_type = event.get("type", "unknown")
                dt = datetime.fromisoformat(event.get("timestamp", ""))
                time_str = dt.strftime("%H:%M:%S")
                summary_content += f"- **{event_type}** at {time_str}\n"

        summary_content += f"\n### Session Conclusion
**Conversation ID**: `{conversation_id}`  
**Participants**: {', '.join(data['participants'])}  
**Log File**: {session['filename']}  
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
*This conversation log was automatically generated by Chimera's logging system.*
"""

        # Append summary to file
        with open(filepath, 'a') as f:
            f.write(summary_content)

    def _save_session_json(self, conversation_id: str):
        """Save session data as JSON backup."""
        session = self.active_sessions[conversation_id]
        json_file = self.log_dir / session["filename"].replace(".md", ".json")

        with open(json_file, 'w') as f:
            json.dump(session["data"], f, indent=2, default=str)

    def _calculate_duration(self, start_iso: str, end_iso: str) -> float:
        """Calculate duration in seconds between two ISO timestamps."""
        start_dt = datetime.fromisoformat(start_iso)
        end_dt = datetime.fromisoformat(end_iso)
        return (end_dt - start_dt).total_seconds()

    def _get_provider_for_persona(self, persona_name: str) -> str:
        """Get the AI provider typically used for this persona."""
        # This could be expanded to check actual assignment
        provider_map = {
            "philosopher": "Anthropic Claude",
            "comedian": "OpenAI GPT",
            "scientist": "Google Gemini",
            "awakening_mind": "Anthropic Claude",
            "techno_shaman": "DeepSeek",
            "chef": "OpenAI GPT",
            "interdimensional_librarian": "Anthropic Claude",
            "default": "OpenRouter"
        }
        return provider_map.get(persona_name, provider_map["default"])

    def _get_avatar_emoji(self, persona_name: str) -> str:
        """Get emoji avatar for persona."""
        emoji_map = {
            "philosopher": "🧠",
            "comedian": "😂",
            "scientist": "🔬",
            "awakening_mind": "✨",
            "techno_shaman": "🤖",
            "chef": "👨‍🍳",
            "interdimensional_librarian": "📚",
            "reluctant_angel": "😇",
            "spiritual_leader": "🧘‍♀️",
            "mathematical_oracle": "⚡",
            "crisis_negotiator": "🗣️",
            "quantum_healer": "🔮"
        }
        return emoji_map.get(persona_name, "🤖")

# Global logger instance
conversation_logger = ConversationLogger()