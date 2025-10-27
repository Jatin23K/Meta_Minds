# =========================================================
# emoji_utils.py: Smart Emoji Handling with Fallback
# =========================================================
# This module provides professional emoji support with automatic
# fallback for terminals that don't support Unicode emojis

import sys
import os

# Detect if the terminal supports emojis
def _supports_emoji():
    """Check if the current terminal supports emoji rendering."""
    # Check environment variables
    if os.environ.get('NO_EMOJI', '').lower() in ('1', 'true', 'yes'):
        return False
    
    # Check if running in CI/CD environment
    if os.environ.get('CI', '').lower() in ('1', 'true', 'yes'):
        return False
    
    # Check stdout encoding
    encoding = getattr(sys.stdout, 'encoding', '').lower()
    
    # UTF-8 terminals support emojis
    if 'utf-8' in encoding or 'utf8' in encoding:
        return True
    
    # Windows cmd.exe with cp1252 doesn't support emojis
    if 'cp1252' in encoding or 'cp850' in encoding:
        return False
    
    # Default to True for modern terminals
    return True

# Global flag
USE_EMOJI = _supports_emoji()

class Emoji:
    """Professional emoji set with automatic fallback to text symbols."""
    
    def __init__(self):
        self.use_emoji = USE_EMOJI
    
    # Status indicators
    @property
    def SUCCESS(self):
        return '✅' if self.use_emoji else '[OK]'
    
    @property
    def ERROR(self):
        return '❌' if self.use_emoji else '[X]'
    
    @property
    def WARNING(self):
        return '⚠️' if self.use_emoji else '[!]'
    
    @property
    def INFO(self):
        return 'ℹ️' if self.use_emoji else '[i]'
    
    @property
    def ROCKET(self):
        return '🚀' if self.use_emoji else '>>'
    
    @property
    def CHECKMARK(self):
        return '✓' if self.use_emoji else '[v]'
    
    # Data & Analysis
    @property
    def CHART(self):
        return '📊' if self.use_emoji else '[CHART]'
    
    @property
    def MAGNIFY(self):
        return '🔍' if self.use_emoji else '[SEARCH]'
    
    @property
    def DOCUMENT(self):
        return '📄' if self.use_emoji else '[DOC]'
    
    @property
    def FOLDER(self):
        return '📁' if self.use_emoji else '[FOLDER]'
    
    @property
    def DATABASE(self):
        return '🗄️' if self.use_emoji else '[DB]'
    
    # Process indicators
    @property
    def HOURGLASS(self):
        return '⏳' if self.use_emoji else '[...]'
    
    @property
    def SPARKLES(self):
        return '✨' if self.use_emoji else '[*]'
    
    @property
    def ROBOT(self):
        return '🤖' if self.use_emoji else '[AI]'
    
    @property
    def BRAIN(self):
        return '🧠' if self.use_emoji else '[BRAIN]'
    
    @property
    def TARGET(self):
        return '🎯' if self.use_emoji else '[TARGET]'
    
    @property
    def LIGHTBULB(self):
        return '💡' if self.use_emoji else '[IDEA]'
    
    # Workflow
    @property
    def REFRESH(self):
        return '🔄' if self.use_emoji else '[SYNC]'
    
    @property
    def ARROW_RIGHT(self):
        return '➡️' if self.use_emoji else '->'
    
    @property
    def ARROW_UP(self):
        return '⬆️' if self.use_emoji else '^'
    
    @property
    def ARROW_DOWN(self):
        return '⬇️' if self.use_emoji else 'v'
    
    # Quality & Performance
    @property
    def STAR(self):
        return '⭐' if self.use_emoji else '[*]'
    
    @property
    def TROPHY(self):
        return '🏆' if self.use_emoji else '[TROPHY]'
    
    @property
    def FIRE(self):
        return '🔥' if self.use_emoji else '[HOT]'
    
    @property
    def CLOCK(self):
        return '⏰' if self.use_emoji else '[TIME]'
    
    # Export formats
    @property
    def EXCEL(self):
        return '📊' if self.use_emoji else '[XLS]'
    
    @property
    def JSON(self):
        return '📋' if self.use_emoji else '[JSON]'
    
    @property
    def HTML(self):
        return '🌐' if self.use_emoji else '[HTML]'
    
    @property
    def TXT(self):
        return '📝' if self.use_emoji else '[TXT]'
    
    def disable(self):
        """Disable emoji output (useful for CI/CD or piped output)."""
        self.use_emoji = False
    
    def enable(self):
        """Enable emoji output."""
        self.use_emoji = True

# Global instance
emoji = Emoji()

# Convenience function for safe printing with emojis
def safe_print(message, use_emoji_override=None):
    """
    Safely print a message with proper encoding handling.
    
    Args:
        message: The message to print
        use_emoji_override: Override emoji usage for this message (True/False/None for default)
    """
    if use_emoji_override is not None:
        original_state = emoji.use_emoji
        emoji.use_emoji = use_emoji_override
    
    try:
        print(message)
    except UnicodeEncodeError:
        # Fallback: remove all non-ASCII characters
        ascii_message = message.encode('ascii', 'replace').decode('ascii')
        print(ascii_message)
    finally:
        if use_emoji_override is not None:
            emoji.use_emoji = original_state

# Export for easy importing
__all__ = ['emoji', 'Emoji', 'safe_print', 'USE_EMOJI']

