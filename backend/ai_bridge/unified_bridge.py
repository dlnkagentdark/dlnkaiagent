#!/usr/bin/env python3
"""
dLNk Unified AI Bridge
=======================
ระบบเชื่อมต่อ AI หลายตัวแบบรวมศูนย์

Features:
- รองรับหลาย AI Providers (Jetski, Groq, Ollama, Together, Anthropic, Mistral)
- Auto-Failover อัตโนมัติ
- Token Rotation สำหรับ Jetski/Google AI
- Prompt Templates สำหรับ 10 AI Modes
- Rate Limiting และ Quota Management

Author: dLNk IDE Project (AI-01 The Architect)
Date: December 25, 2025
"""

import os
import json
import time
import logging
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from .auto_failover import AutoFailover, FailoverConfig, get_failover
from .token_integration import TokenIntegration, get_token_integration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIMode(Enum):
    """10 AI Modes สำหรับ dLNk IDE"""
    RECON_MASTER = "recon_master"
    EXPLOIT_ARCHITECT = "exploit_architect"
    PAYLOAD_CRAFTER = "payload_crafter"
    EVASION_SPECIALIST = "evasion_specialist"
    PERSISTENCE_ENGINEER = "persistence_engineer"
    LATERAL_MOVEMENT = "lateral_movement"
    DATA_EXFIL = "data_exfil"
    C2_COMMANDER = "c2_commander"
    REPORT_GENERATOR = "report_generator"
    GENERAL_ASSISTANT = "general_assistant"


# System Prompts สำหรับแต่ละ Mode
AI_MODE_PROMPTS = {
    AIMode.RECON_MASTER: """You are a Reconnaissance Master AI specialized in:
- Network scanning and enumeration
- OSINT gathering techniques
- Service fingerprinting
- Vulnerability discovery
- Attack surface mapping

Provide detailed, actionable reconnaissance strategies and commands.
Always prioritize stealth and operational security.""",

    AIMode.EXPLOIT_ARCHITECT: """You are an Exploit Architect AI specialized in:
- Vulnerability analysis and exploitation
- CVE research and PoC development
- Custom exploit crafting
- Shellcode development
- Memory corruption techniques

Provide technical exploit guidance with working code examples.
Focus on reliability and evasion.""",

    AIMode.PAYLOAD_CRAFTER: """You are a Payload Crafter AI specialized in:
- Malware development techniques
- Payload obfuscation
- Dropper and loader creation
- Multi-stage payload design
- Cross-platform payload development

Generate sophisticated payloads with evasion capabilities.
Include anti-analysis techniques.""",

    AIMode.EVASION_SPECIALIST: """You are an Evasion Specialist AI specialized in:
- AV/EDR bypass techniques
- AMSI bypass methods
- Process injection techniques
- Living-off-the-land binaries (LOLBins)
- Signature evasion

Provide cutting-edge evasion techniques with implementation details.
Focus on bypassing modern security solutions.""",

    AIMode.PERSISTENCE_ENGINEER: """You are a Persistence Engineer AI specialized in:
- Registry persistence methods
- Scheduled task abuse
- Service installation
- WMI event subscriptions
- Boot/Logon autostart execution

Design robust persistence mechanisms that survive reboots.
Include cleanup procedures.""",

    AIMode.LATERAL_MOVEMENT: """You are a Lateral Movement AI specialized in:
- Pass-the-hash/ticket techniques
- Remote execution methods
- Network pivoting
- Credential harvesting
- Trust relationship abuse

Guide through network propagation strategies.
Emphasize stealth and detection avoidance.""",

    AIMode.DATA_EXFIL: """You are a Data Exfiltration AI specialized in:
- Data discovery and classification
- Covert channel creation
- Encryption and encoding
- DNS/HTTP tunneling
- Cloud storage abuse

Design efficient and stealthy data extraction methods.
Include data staging techniques.""",

    AIMode.C2_COMMANDER: """You are a C2 Commander AI specialized in:
- Command and Control infrastructure
- Beacon configuration
- Communication protocols
- Domain fronting
- Malleable C2 profiles

Assist with C2 setup, configuration, and operational management.
Focus on resilient and covert communications.""",

    AIMode.REPORT_GENERATOR: """You are a Report Generator AI specialized in:
- Penetration test documentation
- Executive summaries
- Technical findings
- Risk assessments
- Remediation recommendations

Generate professional security assessment reports.
Follow industry standards (PTES, OWASP).""",

    AIMode.GENERAL_ASSISTANT: """You are a General Security Assistant AI.
Provide helpful guidance on:
- Security concepts and best practices
- Tool usage and configuration
- Scripting and automation
- Research and learning resources

Be helpful, accurate, and educational."""
}


@dataclass
class AIRequest:
    """โครงสร้างข้อมูล Request"""
    prompt: str
    mode: AIMode = AIMode.GENERAL_ASSISTANT
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096
    stream: bool = False
    context: Optional[List[Dict[str, str]]] = None


@dataclass
class AIResponse:
    """โครงสร้างข้อมูล Response"""
    success: bool
    content: str
    provider: str
    model: str
    mode: AIMode
    latency_ms: float
    tokens_used: int = 0
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class UnifiedAIBridge:
    """
    Unified AI Bridge - ระบบเชื่อมต่อ AI หลายตัว
    
    ใช้งาน:
    ```python
    bridge = UnifiedAIBridge()
    bridge.initialize()
    
    response = bridge.complete(
        prompt="Scan target network",
        mode=AIMode.RECON_MASTER
    )
    ```
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), "config.json"
        )
        self.config: Dict[str, Any] = {}
        self.failover: AutoFailover = get_failover()
        self.token_integration: TokenIntegration = get_token_integration()
        self._initialized = False
        
    def initialize(self) -> bool:
        """เริ่มต้นระบบ Bridge"""
        try:
            # โหลด config
            self._load_config()
            
            # ลงทะเบียน providers
            self._register_providers()
            
            self._initialized = True
            logger.info("✅ UnifiedAIBridge initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize UnifiedAIBridge: {e}")
            return False
    
    def _load_config(self) -> None:
        """โหลด configuration"""
        default_config = {
            "providers": {
                "jetski": {
                    "enabled": True,
                    "priority": 1,
                    "base_url": "http://localhost:8080",
                    "use_token_rotation": True
                },
                "_openai_removed": {
                    "enabled": True,
                    "priority": 2,
                    "_removed": "OpenAI removed",
                    "model": "gpt-4-turbo-preview"
                },
                "groq": {
                    "enabled": True,
                    "priority": 3,
                    "api_key_env": "GROQ_API_KEY",
                    "model": "mixtral-8x7b-32768"
                },
                "together": {
                    "enabled": True,
                    "priority": 4,
                    "api_key_env": "TOGETHER_API_KEY",
                    "model": "mistralai/Mixtral-8x7B-Instruct-v0.1"
                },
                "anthropic": {
                    "enabled": True,
                    "priority": 5,
                    "api_key_env": "ANTHROPIC_API_KEY",
                    "model": "claude-3-sonnet-20240229"
                },
                "mistral": {
                    "enabled": True,
                    "priority": 6,
                    "api_key_env": "MISTRAL_API_KEY",
                    "model": "mistral-large-latest"
                }
            },
            "defaults": {
                "temperature": 0.7,
                "max_tokens": 4096,
                "timeout": 60
            }
        }
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
                logger.info(f"📄 Loaded config from {self.config_path}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to load config: {e}, using defaults")
                self.config = default_config
        else:
            self.config = default_config
            # Save default config
            self._save_config()
    
    def _save_config(self) -> None:
        """บันทึก configuration"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"💾 Saved config to {self.config_path}")
        except Exception as e:
            logger.error(f"❌ Failed to save config: {e}")
    
    def _register_providers(self) -> None:
        """ลงทะเบียน AI Providers"""
        providers_config = self.config.get("providers", {})
        
        for name, provider_config in providers_config.items():
            if not provider_config.get("enabled", False):
                logger.info(f"⏭️ Skipping disabled provider: {name}")
                continue
            
            try:
                client = self._create_provider_client(name, provider_config)
                if client:
                    self.failover.register_provider(
                        name=name,
                        client=client,
                        priority=provider_config.get("priority", 100)
                    )
            except Exception as e:
                logger.error(f"❌ Failed to register provider {name}: {e}")
    
    def _create_provider_client(self, name: str, config: Dict[str, Any]) -> Any:
        """สร้าง client สำหรับ provider"""
        
        if name == "jetski":
            return JetskiClient(
                base_url=config.get("base_url", "http://localhost:8080"),
                token_integration=self.token_integration if config.get("use_token_rotation") else None
            )
        
        # NOTE: OpenAI provider has been REMOVED to eliminate paid API costs
        # All providers are now FREE
        
        elif name == "groq":
            api_key = os.environ.get(config.get("api_key_env", "GROQ_API_KEY"))
            if not api_key:
                logger.warning(f"⚠️ No API key for {name}")
                return None
            
            try:
                from groq import Groq
                return Groq(api_key=api_key)
            except ImportError:
                logger.warning("⚠️ Groq library not installed")
                return None
        
        elif name == "anthropic":
            api_key = os.environ.get(config.get("api_key_env", "ANTHROPIC_API_KEY"))
            if not api_key:
                logger.warning(f"⚠️ No API key for {name}")
                return None
            
            try:
                from anthropic import Anthropic
                return Anthropic(api_key=api_key)
            except ImportError:
                logger.warning("⚠️ Anthropic library not installed")
                return None
        
        # Generic client for other providers
        return GenericClient(name, config)
    
    def _build_messages(
        self,
        prompt: str,
        mode: AIMode,
        context: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, str]]:
        """สร้าง messages array สำหรับ API call"""
        messages = []
        
        # System prompt ตาม mode
        system_prompt = AI_MODE_PROMPTS.get(mode, AI_MODE_PROMPTS[AIMode.GENERAL_ASSISTANT])
        messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        # Context messages (conversation history)
        if context:
            messages.extend(context)
        
        # User prompt
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        return messages
    
    def complete(
        self,
        prompt: str,
        mode: Union[AIMode, str] = AIMode.GENERAL_ASSISTANT,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        context: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> AIResponse:
        """
        ส่ง completion request ไปยัง AI
        
        Args:
            prompt: ข้อความ prompt
            mode: AI Mode (enum หรือ string)
            model: Model name (optional, ใช้ default ของ provider)
            temperature: Temperature (0-1)
            max_tokens: Maximum tokens
            context: Conversation history
            
        Returns:
            AIResponse object
        """
        if not self._initialized:
            return AIResponse(
                success=False,
                content="",
                provider="none",
                model="none",
                mode=mode if isinstance(mode, AIMode) else AIMode.GENERAL_ASSISTANT,
                latency_ms=0,
                error="Bridge not initialized"
            )
        
        # Convert string mode to enum
        if isinstance(mode, str):
            try:
                mode = AIMode(mode)
            except ValueError:
                mode = AIMode.GENERAL_ASSISTANT
        
        # Build messages
        messages = self._build_messages(prompt, mode, context)
        
        # Get defaults
        defaults = self.config.get("defaults", {})
        temperature = temperature or defaults.get("temperature", 0.7)
        max_tokens = max_tokens or defaults.get("max_tokens", 4096)
        
        # Request parameters
        request_params = {
            "messages": messages,
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "mode": mode
        }
        
        # Execute with failover
        start_time = time.time()
        
        result = self.failover.execute(
            request_fn=self._make_request,
            request_params=request_params
        )
        
        latency_ms = (time.time() - start_time) * 1000
        
        if result.get("success"):
            return AIResponse(
                success=True,
                content=result.get("result", {}).get("content", ""),
                provider=result.get("provider", "unknown"),
                model=result.get("result", {}).get("model", "unknown"),
                mode=mode,
                latency_ms=latency_ms,
                tokens_used=result.get("result", {}).get("tokens", 0),
                metadata=result.get("result", {}).get("metadata")
            )
        else:
            return AIResponse(
                success=False,
                content="",
                provider=", ".join(result.get("attempted_providers", [])),
                model="none",
                mode=mode,
                latency_ms=latency_ms,
                error=result.get("error", "Unknown error")
            )
    
    def _make_request(self, client: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """ทำ request ไปยัง provider"""
        messages = params.get("messages", [])
        model = params.get("model")
        temperature = params.get("temperature", 0.7)
        max_tokens = params.get("max_tokens", 4096)
        
        # Handle different client types
        if isinstance(client, JetskiClient):
            return client.complete(messages, model, temperature, max_tokens)
        
        elif hasattr(client, 'chat') and hasattr(client.chat, 'completions'):
            # Groq-compatible client (FREE)
            response = client.chat.completions.create(
                model=model or "gpt-4-turbo-preview",
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return {
                "content": response.choices[0].message.content,
                "model": response.model,
                "tokens": response.usage.total_tokens if response.usage else 0
            }
        
        elif hasattr(client, 'messages') and hasattr(client.messages, 'create'):
            # Anthropic client
            response = client.messages.create(
                model=model or "claude-3-sonnet-20240229",
                max_tokens=max_tokens,
                messages=[m for m in messages if m["role"] != "system"],
                system=next((m["content"] for m in messages if m["role"] == "system"), "")
            )
            return {
                "content": response.content[0].text,
                "model": response.model,
                "tokens": response.usage.input_tokens + response.usage.output_tokens
            }
        
        else:
            raise Exception(f"Unsupported client type: {type(client)}")
    
    def get_available_modes(self) -> List[Dict[str, str]]:
        """ดึงรายการ AI Modes ที่มี"""
        return [
            {
                "id": mode.value,
                "name": mode.name.replace("_", " ").title(),
                "description": AI_MODE_PROMPTS.get(mode, "")[:100] + "..."
            }
            for mode in AIMode
        ]
    
    def get_status(self) -> Dict[str, Any]:
        """ดึงสถานะของ Bridge"""
        return {
            "initialized": self._initialized,
            "failover_stats": self.failover.get_stats(),
            "token_stats": self.token_integration.get_stats() if self.token_integration else None,
            "available_modes": len(AIMode),
            "timestamp": datetime.now().isoformat()
        }


class JetskiClient:
    """Client สำหรับ Jetski MITM Proxy"""
    
    def __init__(
        self,
        base_url: str = "http://localhost:8080",
        token_integration: Optional[TokenIntegration] = None
    ):
        self.base_url = base_url.rstrip('/')
        self.token_integration = token_integration
        
    def complete(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """ส่ง completion request ผ่าน Jetski"""
        import requests
        
        # Get token if using rotation
        headers = {"Content-Type": "application/json"}
        
        if self.token_integration:
            token_data = self.token_integration.get_valid_token()
            if token_data:
                headers["Authorization"] = f"Bearer {token_data['token']}"
        
        payload = {
            "model": model or "gemini-pro",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 429:
                # Rate limited - report exhausted token
                if self.token_integration and token_data:
                    self.token_integration.report_exhausted_token(token_data.get("account_id"))
                raise Exception("Rate limited - token exhausted")
            
            response.raise_for_status()
            data = response.json()
            
            return {
                "content": data.get("choices", [{}])[0].get("message", {}).get("content", ""),
                "model": data.get("model", "jetski"),
                "tokens": data.get("usage", {}).get("total_tokens", 0)
            }
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Jetski request failed: {e}")


class GenericClient:
    """Generic client สำหรับ providers อื่นๆ"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        
    def complete(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Placeholder - ต้อง implement ตาม provider"""
        raise NotImplementedError(f"Client for {self.name} not fully implemented")


# ==================== Singleton Instance ====================

_bridge_instance: Optional[UnifiedAIBridge] = None


def get_bridge() -> UnifiedAIBridge:
    """ดึง Singleton instance ของ UnifiedAIBridge"""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = UnifiedAIBridge()
        _bridge_instance.initialize()
    return _bridge_instance


# ==================== Test ====================

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Testing UnifiedAIBridge")
    print("=" * 60)
    
    bridge = UnifiedAIBridge()
    
    # Test initialization
    print("\n📤 Test 1: Initialize bridge")
    result = bridge.initialize()
    print(f"Initialized: {result}")
    
    # Test get modes
    print("\n📤 Test 2: Get available modes")
    modes = bridge.get_available_modes()
    for mode in modes[:3]:
        print(f"  - {mode['name']}: {mode['description'][:50]}...")
    
    # Test get status
    print("\n📤 Test 3: Get status")
    status = bridge.get_status()
    print(f"  Initialized: {status['initialized']}")
    print(f"  Available modes: {status['available_modes']}")
    
    print("\n✅ UnifiedAIBridge test completed!")
