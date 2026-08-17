"""
Static data endpoints - Quick actions and error codes.
Serves data from JSON files in the backend/data directory.
"""
import json
import os
from pathlib import Path
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

router = APIRouter()

# Get the data directory path (backend/data)
# From backend/app/api/endpoints/static_data.py -> backend/data
# Go up 4 levels: endpoints -> api -> app -> backend, then add data
BASE_DIR = Path(__file__).parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data"

# Cache for loaded data
_quick_actions_cache = None
_error_codes_cache = None


def _load_json_file(filename: str) -> Dict[str, Any]:
    """Load and parse a JSON file from the data directory."""
    file_path = DATA_DIR / filename
    if not file_path.exists():
        raise HTTPException(
            status_code=500,
            detail=f"Data file not found: {filename}"
        )
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Invalid JSON in {filename}: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error loading {filename}: {str(e)}"
        )


@router.get("/quick-actions")
async def get_quick_actions():
    """
    Get all quick actions data.
    Returns actions list and categories configuration.
    """
    global _quick_actions_cache
    if _quick_actions_cache is None:
        _quick_actions_cache = _load_json_file("quick_actions.json")
    return _quick_actions_cache


@router.get("/error-codes")
async def get_error_codes():
    """
    Get all error codes data.
    Returns error codes organized by platform (windows, mac, linux).
    """
    global _error_codes_cache
    if _error_codes_cache is None:
        _error_codes_cache = _load_json_file("error_codes.json")
    return _error_codes_cache


@router.get("/error-codes/{platform}")
async def get_error_codes_by_platform(platform: str):
    """
    Get error codes for a specific platform.
    
    Args:
        platform: One of 'windows', 'mac', or 'linux'
    
    Returns:
        List of error codes for the specified platform
    """
    if platform not in ['windows', 'mac', 'linux']:
        raise HTTPException(
            status_code=400,
            detail="Platform must be one of: windows, mac, linux"
        )
    
    global _error_codes_cache
    if _error_codes_cache is None:
        _error_codes_cache = _load_json_file("error_codes.json")
    
    if platform not in _error_codes_cache:
        raise HTTPException(
            status_code=404,
            detail=f"No error codes found for platform: {platform}"
        )
    
    return {
        "platform": platform,
        "error_codes": _error_codes_cache[platform]
    }


@router.post("/static-data/reload")
async def reload_static_data():
    """
    Reload static data from JSON files.
    Useful for development when data files are updated.
    """
    global _quick_actions_cache, _error_codes_cache
    _quick_actions_cache = None
    _error_codes_cache = None
    
    # Force reload by loading the files
    _load_json_file("quick_actions.json")
    _load_json_file("error_codes.json")
    
    return {
        "message": "Static data cache cleared. Data will be reloaded on next request."
    }

