"""
dLNk Telegram Bot - Integration Command Handlers
=================================================
Command handlers for AI Bridge and Security integration features.

Author: dLNk Team (AI-10 Integration)
Version: 1.0.0
"""

import logging
from datetime import datetime
from typing import TYPE_CHECKING

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

if TYPE_CHECKING:
    from ..bot import DLNkBot

logger = logging.getLogger(__name__)


def register_integration_handlers(router: Router, bot: "DLNkBot"):
    """
    Register integration-related command handlers.
    
    Args:
        router: aiogram Router instance
        bot: DLNkBot instance
    """
    
    @router.message(Command("bridge"))
    async def cmd_bridge_status(message: Message):
        """Handle /bridge command - Show AI Bridge status"""
        try:
            from integrations import get_ai_bridge_integration
            
            integration = get_ai_bridge_integration(bot_instance=bot)
            status = await integration.get_status()
            
            if status:
                response = integration.format_status_message(status)
            else:
                response = (
                    "❌ <b>AI Bridge Status</b>\n\n"
                    "Cannot connect to AI Bridge.\n"
                    "The service may be offline or unreachable."
                )
            
            await message.answer(response)
            logger.info(f"Bridge status requested by {message.from_user.id}")
            
        except ImportError:
            await message.answer(
                "⚠️ <b>Integration Not Available</b>\n\n"
                "AI Bridge integration module is not installed."
            )
        except Exception as e:
            logger.error(f"Error getting bridge status: {e}")
            await message.answer(f"❌ Error: {str(e)}")
    
    @router.message(Command("health"))
    async def cmd_health_check(message: Message):
        """Handle /health command - Perform health check"""
        try:
            from integrations import get_ai_bridge_integration
            
            await message.answer("🔍 Performing health check...")
            
            integration = get_ai_bridge_integration(bot_instance=bot)
            health = await integration.health_check()
            
            response = integration.format_health_message(health)
            await message.answer(response)
            
            logger.info(f"Health check performed by {message.from_user.id}")
            
        except ImportError:
            await message.answer(
                "⚠️ <b>Integration Not Available</b>\n\n"
                "AI Bridge integration module is not installed."
            )
        except Exception as e:
            logger.error(f"Error performing health check: {e}")
            await message.answer(f"❌ Error: {str(e)}")
    
    @router.message(Command("providers"))
    async def cmd_providers(message: Message):
        """Handle /providers command - List AI providers"""
        try:
            from integrations import get_ai_bridge_integration
            
            integration = get_ai_bridge_integration(bot_instance=bot)
            providers = await integration.get_providers()
            
            if providers:
                lines = ["🤖 <b>AI Providers</b>\n"]
                
                for provider in providers:
                    name = provider.get('name', 'Unknown')
                    available = provider.get('available', False)
                    icon = "🟢" if available else "🔴"
                    status = "Available" if available else "Unavailable"
                    
                    lines.append(f"{icon} <b>{name}</b>: {status}")
                    
                    if provider.get('model'):
                        lines.append(f"   Model: <code>{provider['model']}</code>")
                    if provider.get('latency'):
                        lines.append(f"   Latency: {provider['latency']}ms")
                
                response = "\n".join(lines)
            else:
                response = (
                    "🤖 <b>AI Providers</b>\n\n"
                    "No providers available or cannot connect to AI Bridge."
                )
            
            await message.answer(response)
            
        except ImportError:
            await message.answer(
                "⚠️ <b>Integration Not Available</b>\n\n"
                "AI Bridge integration module is not installed."
            )
        except Exception as e:
            logger.error(f"Error getting providers: {e}")
            await message.answer(f"❌ Error: {str(e)}")
    
    @router.message(Command("token"))
    async def cmd_token_status(message: Message):
        """Handle /token command - Show token status"""
        try:
            from integrations import get_ai_bridge_integration
            
            integration = get_ai_bridge_integration(bot_instance=bot)
            token_status = await integration.get_token_status()
            
            valid = token_status.get('valid', False)
            icon = "🔑" if valid else "🔒"
            status = "Valid" if valid else "Invalid/Expired"
            
            response = f"""
{icon} <b>Token Status</b>

<b>Status:</b> {status}
"""
            
            if token_status.get('expires_at'):
                response += f"<b>Expires:</b> {token_status['expires_at']}\n"
            
            if token_status.get('refresh_at'):
                response += f"<b>Next Refresh:</b> {token_status['refresh_at']}\n"
            
            if token_status.get('error'):
                response += f"\n⚠️ <b>Error:</b> {token_status['error']}"
            
            await message.answer(response)
            
        except ImportError:
            await message.answer(
                "⚠️ <b>Integration Not Available</b>\n\n"
                "AI Bridge integration module is not installed."
            )
        except Exception as e:
            logger.error(f"Error getting token status: {e}")
            await message.answer(f"❌ Error: {str(e)}")
    
    @router.message(Command("refresh_token"))
    async def cmd_refresh_token(message: Message):
        """Handle /refresh_token command - Request token refresh"""
        try:
            from integrations import get_ai_bridge_integration
            
            await message.answer("🔄 Requesting token refresh...")
            
            integration = get_ai_bridge_integration(bot_instance=bot)
            success = await integration.refresh_token()
            
            if success:
                response = "✅ Token refresh requested successfully."
            else:
                response = "❌ Failed to refresh token. Check AI Bridge logs."
            
            await message.answer(response)
            logger.info(f"Token refresh requested by {message.from_user.id}: {success}")
            
        except ImportError:
            await message.answer(
                "⚠️ <b>Integration Not Available</b>\n\n"
                "AI Bridge integration module is not installed."
            )
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            await message.answer(f"❌ Error: {str(e)}")
    
    @router.message(Command("security"))
    async def cmd_security_status(message: Message):
        """Handle /security command - Show security status"""
        try:
            from integrations import get_security_integration
            
            integration = get_security_integration(bot_instance=bot)
            stats = integration.get_stats()
            recent_events = integration.get_recent_events(limit=5)
            
            response = f"""
🛡️ <b>Security Status</b>

<b>Events Received:</b> {stats.get('events_received', 0)}
<b>Events Forwarded:</b> {stats.get('events_forwarded', 0)}
<b>Events Failed:</b> {stats.get('events_failed', 0)}

<b>By Type:</b>
"""
            
            by_type = stats.get('by_type', {})
            if by_type:
                for event_type, count in by_type.items():
                    response += f"  • {event_type}: {count}\n"
            else:
                response += "  No events recorded\n"
            
            response += "\n<b>By Severity:</b>\n"
            by_severity = stats.get('by_severity', {})
            severity_names = {1: "Low", 2: "Medium", 3: "High", 4: "Critical"}
            if by_severity:
                for sev, count in sorted(by_severity.items()):
                    response += f"  • {severity_names.get(sev, sev)}: {count}\n"
            else:
                response += "  No events recorded\n"
            
            if recent_events:
                response += "\n<b>Recent Events:</b>\n"
                for event in recent_events[:5]:
                    title = event.get('title', 'Unknown')
                    timestamp = event.get('timestamp', '')[:19]
                    response += f"  • [{timestamp}] {title}\n"
            
            await message.answer(response)
            
        except ImportError:
            await message.answer(
                "⚠️ <b>Integration Not Available</b>\n\n"
                "Security integration module is not installed."
            )
        except Exception as e:
            logger.error(f"Error getting security status: {e}")
            await message.answer(f"❌ Error: {str(e)}")
    
    @router.message(Command("monitor"))
    async def cmd_monitor(message: Message):
        """Handle /monitor command - Toggle monitoring"""
        args = message.text.split()[1:] if len(message.text.split()) > 1 else []
        
        try:
            from integrations import get_ai_bridge_integration
            
            integration = get_ai_bridge_integration(bot_instance=bot)
            
            if not args or args[0].lower() == "status":
                # Show status
                stats = integration.get_integration_stats()
                monitoring = stats.get('monitoring_active', False)
                
                response = f"""
📡 <b>Monitoring Status</b>

<b>Active:</b> {"Yes" if monitoring else "No"}
<b>Checks Performed:</b> {stats.get('checks_performed', 0)}
<b>Alerts Sent:</b> {stats.get('alerts_sent', 0)}
<b>Last Check:</b> {stats.get('last_check', 'Never')}

<b>Commands:</b>
• /monitor start - Start monitoring
• /monitor stop - Stop monitoring
• /monitor status - Show this status
"""
                await message.answer(response)
                
            elif args[0].lower() == "start":
                interval = int(args[1]) if len(args) > 1 and args[1].isdigit() else 60
                await integration.start_monitoring(interval_seconds=interval)
                await message.answer(
                    f"✅ Monitoring started (interval: {interval}s)"
                )
                logger.info(f"Monitoring started by {message.from_user.id}")
                
            elif args[0].lower() == "stop":
                await integration.stop_monitoring()
                await message.answer("✅ Monitoring stopped")
                logger.info(f"Monitoring stopped by {message.from_user.id}")
                
            else:
                await message.answer(
                    "❌ <b>Usage:</b> /monitor [start|stop|status]\n\n"
                    "<b>Examples:</b>\n"
                    "<code>/monitor start</code>\n"
                    "<code>/monitor start 120</code> (interval in seconds)\n"
                    "<code>/monitor stop</code>"
                )
                
        except ImportError:
            await message.answer(
                "⚠️ <b>Integration Not Available</b>\n\n"
                "AI Bridge integration module is not installed."
            )
        except Exception as e:
            logger.error(f"Error with monitoring: {e}")
            await message.answer(f"❌ Error: {str(e)}")
    
    @router.message(Command("integration"))
    async def cmd_integration_help(message: Message):
        """Handle /integration command - Show integration help"""
        help_text = """
🔗 <b>Integration Commands</b>

<b>AI Bridge:</b>
/bridge - Show AI Bridge status
/health - Perform health check
/providers - List AI providers
/token - Show token status
/refresh_token - Request token refresh
/monitor [start|stop|status] - Toggle monitoring

<b>Security:</b>
/security - Show security status

<b>Usage Examples:</b>
<code>/bridge</code> - Get current AI Bridge status
<code>/health</code> - Check system health
<code>/monitor start 120</code> - Start monitoring every 2 minutes
"""
        await message.answer(help_text)
