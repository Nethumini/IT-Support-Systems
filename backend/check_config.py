#!/usr/bin/env python3
"""
Configuration checker - verify that all required settings are present.
Run this to diagnose why the bot might be offline.
"""
import sys
from pathlib import Path
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import get_settings

def check_config():
    """Check all critical configuration settings."""
    print("=" * 80)
    print("🔍 AutoOps AI Configuration Check")
    print("=" * 80)
    
    settings = get_settings()
    
    checks = {
        "LLM Provider": {
            "value": settings.llm_provider,
            "expected": ["openai", "gemini"],
            "critical": True
        },
        "Google API Key": {
            "value": "***" + settings.google_api_key[-10:] if settings.google_api_key else "NOT SET",
            "critical": True,
            "check": bool(settings.google_api_key)
        },
        "Gemini Model": {
            "value": settings.gemini_model,
            "critical": True,
            "check": bool(settings.gemini_model)
        },
        "Database URL": {
            "value": settings.database_url,
            "critical": True,
            "check": bool(settings.database_url)
        },
        "Secret Key": {
            "value": "***" + settings.secret_key[-5:] if settings.secret_key else "NOT SET",
            "critical": False
        },
        "Allowed Origins": {
            "value": f"{len(settings.get_allowed_origins_list())} origins configured",
            "critical": False
        }
    }
    
    all_good = True
    
    for name, config in checks.items():
        is_critical = config.get("critical", False)
        status = "✅"
        
        if "check" in config:
            if not config["check"]:
                status = "❌" if is_critical else "⚠️ "
                all_good = False if is_critical else all_good
        elif "expected" in config:
            if config["value"] not in config["expected"]:
                status = "❌" if is_critical else "⚠️ "
                all_good = False if is_critical else all_good
        
        priority = "[CRITICAL]" if is_critical else "[optional]"
        print(f"{status} {name:<25} {priority:<12} {config['value']}")
    
    print("=" * 80)
    
    if not all_good:
        print("\n❌ Configuration issues found!")
        print("\n📝 Fix: Update your .env file with missing values")
        print("   Location: backend/.env")
        print("\n🔗 Get Google API Key from: https://makersuite.google.com/app/apikey")
        return False
    else:
        print("\n✅ All critical configuration settings are present!")
        print("\n🚀 Bot should be online")
        return True

if __name__ == "__main__":
    success = check_config()
    sys.exit(0 if success else 1)
