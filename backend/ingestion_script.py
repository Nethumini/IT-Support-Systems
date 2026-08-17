# -*- coding: utf-8 -*-
import os
import json
import sys
import hashlib
import numpy as np
from pathlib import Path

# Force UTF-8 output encoding on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Suppress warnings
import warnings
warnings.filterwarnings("ignore", message=".*onnxruntime.*")

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
import chromadb

# Load environment variables
load_dotenv()

# Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/text-embedding-004")
USE_LOCAL_EMBEDDINGS = os.getenv("USE_LOCAL_EMBEDDINGS", "true").lower() == "true"
CHROMA_DB_DIR = "./data/processed/chroma_db"
DATA_FILE = "./data/raw/ticketing_system_data_new.json"

def get_simple_embedding(text: str, dimension: int = 384) -> list:
    """Generate deterministic embedding using hash-based approach (fast, no ML required)"""
    # Create a deterministic hash-based embedding
    hash_obj = hashlib.sha256(text.encode())
    hash_int = int(hash_obj.hexdigest(), 16)
    
    # Use numpy to generate consistent random embedding from hash seed
    rng = np.random.RandomState(seed=hash_int % (2**31))
    embedding = rng.randn(dimension).astype(np.float32)
    
    # Normalize embedding
    norm = np.linalg.norm(embedding)
    if norm > 0:
        embedding = embedding / norm
    
    return embedding.tolist()

class SimpleEmbeddings:
    """Simple embedding wrapper for compatibility with LangChain"""
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
    
    def embed_documents(self, texts: list) -> list:
        """Embed multiple documents"""
        return [get_simple_embedding(text, self.dimension) for text in texts]
    
    def embed_query(self, text: str) -> list:
        """Embed a query"""
        return get_simple_embedding(text, self.dimension)

def get_embeddings():
    """Get embeddings model - uses simple hash-based embeddings by default (fast, no dependencies)"""
    if USE_LOCAL_EMBEDDINGS:
        print("🔧 Using simple hash-based embeddings (fast, no ML dependencies)...")
        return SimpleEmbeddings(dimension=384)
    else:
        print("🔧 Using Google Generative AI embeddings...")
        if not GOOGLE_API_KEY:
            print("❌ ERROR: GOOGLE_API_KEY not set in .env file")
            print("   Either: 1) Set GOOGLE_API_KEY in backend/.env")
            print("         2) Use local embeddings: USE_LOCAL_EMBEDDINGS=true")
            raise ValueError("GOOGLE_API_KEY required for Google embeddings")
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        return GoogleGenerativeAIEmbeddings(

            model=EMBEDDING_MODEL,
            google_api_key=GOOGLE_API_KEY
        )

def load_data_from_file():
    """Load data from JSON file"""
    data_path = Path(__file__).parent / DATA_FILE
    print(f"📂 Loading data from {data_path}...")
    
    if not data_path.exists():
        print(f"❌ Error: Data file not found at {data_path}")
        return None
    
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✅ Data loaded successfully!")
    return data

# Sample Knowledge Base (Converted to valid Python syntax) - Fallback if JSON not available
KNOWLEDGE_BASE = [
    {
   "users":[
      {
         "id":"user_0001",
         "name":"Bethany Williams",
         "email":"bethany.williams@acme-soft.com",
         "tier":"staff",
         "status":"active"
      },
      {
         "id":"user_0002",
         "name":"Amy Ramos",
         "email":"amy.ramos@acme-soft.com",
         "tier":"staff",
         "status":"active"
      },
      {
         "id":"user_0003",
         "name":"Michael Chen",
         "email":"michael.chen@acme-soft.com",
         "tier":"manager",
         "status":"active"
      },
      {
         "id":"user_0199",
         "name":"Jeffrey Conley",
         "email":"jeffrey.conley@acme-soft.com",
         "tier":"contractor",
         "status":"inactive"
      },
      {
         "id":"user_0200",
         "name":"Joseph Shea",
         "email":"joseph.shea@acme-soft.com",
         "tier":"staff",
         "status":"active"
      }
   ],
   "user_history":[
      {
         "user_id":"user_0001",
         "name":"Bethany Williams",
         "tier":"staff",
         "last_login":"2025-11-25T08:35:24Z",
         "recent_activity":{
            "payment_attempts":0,
            "failed_payments":0,
            "speed_tests":[
               120.4,
               95.3
            ],
            "logins":28
         },
         "metrics":{
            "account_health":92,
            "payment_success_rate":100,
            "network_stability":87
         },
         "past_tickets":[
            {
               "ticket_id":"TKT-1159",
               "issue":"Laptop fails to join corporate Wi-Fi after password change.",
               "resolved": True
            },
            {
               "ticket_id":"TKT-1442",
               "issue":"Visual Studio Code extensions not loading due to corrupt profile.",
               "resolved": True
            }
         ]
      },
      {
         "user_id":"user_0002",
         "name":"Amy Ramos",
         "tier":"staff",
         "last_login":"2025-11-24T03:07:38Z",
         "recent_activity":{
            "payment_attempts":0,
            "failed_payments":0,
            "speed_tests":[
               88.7,
               76.2
            ],
            "logins":30
         },
         "metrics":{
            "account_health":85,
            "payment_success_rate":100,
            "network_stability":73
         },
         "past_tickets":[
            {
               "ticket_id":"TKT-1588",
               "issue":"Outlook not syncing emails after mailbox migration.",
               "resolved": True
            },
            {
               "ticket_id":"TKT-1612",
               "issue":"Unable to access internal Jira over VPN.",
               "resolved": True
            }
         ]
      },
      {
         "user_id":"user_0003",
         "name":"Michael Chen",
         "tier":"manager",
         "last_login":"2025-11-26T06:14:02Z",
         "recent_activity":{
            "payment_attempts":0,
            "failed_payments":0,
            "speed_tests":[
               110.5,
               112.9
            ],
            "logins":18
         },
         "metrics":{
            "account_health":96,
            "payment_success_rate":100,
            "network_stability":91
         },
         "past_tickets":[
            {
               "ticket_id":"TKT-1720",
               "issue":"Zoom audio device not detected on Windows laptop.",
               "resolved": True
            }
         ]
      },
      {
         "user_id":"user_0199",
         "name":"Jeffrey Conley",
         "tier":"contractor",
         "last_login":"2025-11-03T14:34:13Z",
         "recent_activity":{
            "payment_attempts":0,
            "failed_payments":0,
            "speed_tests":[
               38.42,
               64.19
            ],
            "logins":9
         },
         "metrics":{
            "account_health":71,
            "payment_success_rate":100,
            "network_stability":61
         },
         "past_tickets":[
            {
               "ticket_id":"TKT-1164",
               "issue":"Company VPN disconnects every 5 minutes while using remote desktop.",
               "resolved": False
            }
         ]
      },
      {
         "user_id":"user_0200",
         "name":"Joseph Shea",
         "tier":"staff",
         "last_login":"2025-11-21T00:07:48Z",
         "recent_activity":{
            "payment_attempts":0,
            "failed_payments":0,
            "speed_tests":[
               49.54,
               117.26,
               98.65
            ],
            "logins":6
         },
         "metrics":{
            "account_health":68,
            "payment_success_rate":100,
            "network_stability":59
         },
         "past_tickets":[
            {
               "ticket_id":"TKT-1374",
               "issue":"Mechanical keyboard randomly stops responding on USB-C dock.",
               "resolved": True
            },
            {
               "ticket_id":"TKT-1751",
               "issue":"Unable to push code to Git due to SSH key mismatch.",
               "resolved": True
            }
         ]
      }
   ],
   "tickets":[
      {
         "id":"TKT-2399",
         "title":"Laptop slow to boot after Windows update",
         "user_id":"user_0200",
         "user_name":"Joseph Shea",
         "description":"Laptop takes more than 10 minutes to boot after latest Windows update.",
         "priority":2,
         "status":"in_progress",
         "urgency":"medium",
         "category":"performance",
         "knowledge_base_id":"KB-006",
         "assigned_to":"it_support_l1_03",
         "created_at":"2025-11-25T09:30:07Z",
         "resolved_at": None,
         "is_resolved": False
      },
      {
         "id":"TKT-1764158260799",
         "title":"Development laptop slow when running Docker",
         "user_id":"user_0001",
         "user_name":"Bethany Williams",
         "description":"My local development environment is extremely slow after installing Docker Desktop.",
         "priority":2,
         "status":"resolved",
         "urgency":"medium",
         "category":"software",
         "knowledge_base_id":"KB-003",
         "assigned_to":"agent_ai_01",
         "created_at":"2025-11-26T11:57:40.799Z",
         "resolved_at":"2025-11-26T11:57:51.620Z",
         "is_resolved": True
      },
      {
         "id":"TKT-1764158427172",
         "title":"VPN authentication failing from home",
         "user_id":"user_0002",
         "user_name":"Amy Ramos",
         "description":"Cannot connect to company VPN from home, getting 'authentication failed' although password works for email.",
         "priority":1,
         "status":"resolved",
         "urgency":"high",
         "category":"network",
         "knowledge_base_id":"KB-001",
         "assigned_to":"agent_ai_01",
         "created_at":"2025-11-26T12:00:27.172Z",
         "resolved_at":"2025-11-26T12:00:35.478Z",
         "is_resolved": True
      },
      {
         "id":"TKT-1764161161702",
         "title":"Repeated BSOD on manager laptop",
         "user_id":"user_0003",
         "user_name":"Michael Chen",
         "description":"Laptop has been blue-screening 3–4 times a day for the last week, impacting client calls.",
         "priority":1,
         "status":"assigned_to_human",
         "urgency":"critical",
         "category":"hardware",
         "knowledge_base_id":"KB-004",
         "assigned_to":"it_support_l2_01",
         "created_at":"2025-11-26T12:46:01.702Z",
         "resolved_at": None,
         "is_resolved": False
      },
      {
         "id":"TKT-1764162205120",
         "title":"Mouse disconnects when connected via dock",
         "user_id":"user_0200",
         "user_name":"Joseph Shea",
         "description":"External USB mouse intermittently stops working when connected through docking station, but works fine when plugged directly into laptop.",
         "priority":3,
         "status":"open",
         "urgency":"low",
         "category":"hardware",
         "knowledge_base_id":"KB-005",
         "assigned_to": None,
         "created_at":"2025-11-27T06:23:25.120Z",
         "resolved_at": None,
         "is_resolved" : False
      }
   ],
   "ticket_conversations":[
      {
         "ticket_id":"TKT-1764158260799",
         "conversation":[
            {
               "timestamp":"2025-11-26T11:57:40.799Z",
               "sender_type":"agent",
               "sender_id":"agent_ai_01",
               "sender_name":"AI Support Agent",
               "message":"Hello! I'm your IT support assistant. How can I help you with your workstation today?"
            },
            {
               "timestamp":"2025-11-26T11:57:45.210Z",
               "sender_type":"user",
               "sender_id":"user_0001",
               "sender_name":"Bethany Williams",
               "message":"VS Code and Chrome freeze after I start Docker. It only happens on my company laptop."
            },
            {
               "timestamp":"2025-11-26T11:57:51.595Z",
               "sender_type":"agent",
               "sender_id":"agent_ai_01",
               "sender_name":"AI Support Agent",
               "message":"I see, Bethany. I’ll run some quick diagnostics on CPU and memory usage and then guide you through a few optimization steps."
            },
            {
               "timestamp":"2025-11-26T11:57:51.618Z",
               "sender_type":"agent",
               "sender_id":"agent_ai_01",
               "sender_name":"AI Support Agent",
               "message":"I’ve adjusted your Docker resource recommendations and sent you step-by-step instructions. Please follow them and let me know if performance improves."
            },
            {
               "timestamp":"2025-11-26T11:57:51.620Z",
               "sender_type":"user",
               "sender_id":"user_0001",
               "sender_name":"Bethany Williams",
               "message":"That worked! Everything feels much faster now, thanks."
            }
         ],
         "events":[
            {
               "timestamp":"2025-11-26T11:57:40.803Z",
               "event_type":"created",
               "actor_type":"system",
               "actor_id":"system",
               "message":"Ticket created with priority 2 (medium urgency)."
            },
            {
               "timestamp":"2025-11-26T11:57:51.595Z",
               "event_type":"diagnostic_complete",
               "actor_type":"agent",
               "actor_id":"agent_ai_01",
               "message":"Collected system info: CPU at 98% and memory at 90% when Docker is running."
            },
            {
               "timestamp":"2025-11-26T11:57:51.599Z",
               "event_type":"diagnostic_complete",
               "actor_type":"agent",
               "actor_id":"agent_ai_01",
               "message":"Diagnosis: resource contention due to Docker and multiple heavy apps (linked to KB-003)."
            },
            {
               "timestamp":"2025-11-26T11:57:51.607Z",
               "event_type":"solution_found",
               "actor_type":"agent",
               "actor_id":"agent_ai_01",
               "message":"Solution: reduce Docker CPU/RAM allocation and disable non-essential startup apps."
            },
            {
               "timestamp":"2025-11-26T11:57:51.622Z",
               "event_type":"resolved",
               "actor_type":"agent",
               "actor_id":"agent_ai_01",
               "message":"Ticket automatically resolved after user confirmed performance is normal."
            }
         ]
      },
      {
         "ticket_id":"TKT-1764158427172",
         "conversation":[
            {
               "timestamp":"2025-11-26T12:00:27.172Z",
               "sender_type":"agent",
               "sender_id":"agent_ai_01",
               "sender_name":"AI Support Agent",
               "message":"Hi Amy, I’m your IT support assistant. I see you’re having trouble with VPN access. Let’s fix that."
            },
            {
               "timestamp":"2025-11-26T12:00:31.500Z",
               "sender_type":"user",
               "sender_id":"user_0002",
               "sender_name":"Amy Ramos",
               "message":"Yes, it keeps saying authentication failed. But my password works fine for email."
            },
            {
               "timestamp":"2025-11-26T12:00:35.468Z",
               "sender_type":"agent",
               "sender_id":"agent_ai_01",
               "sender_name":"AI Support Agent",
               "message":"This usually happens after a recent password change. I’ll help you clear cached credentials and set up a fresh VPN profile."
            },
            {
               "timestamp":"2025-11-26T12:00:35.478Z",
               "sender_type":"user",
               "sender_id":"user_0002",
               "sender_name":"Amy Ramos",
               "message":"VPN is working now and I can access Jira and Git. Thank you!"
            }
         ],
         "events":[
            {
               "timestamp":"2025-11-26T12:00:27.174Z",
               "event_type":"created",
               "actor_type":"system",
               "actor_id":"system",
               "message":"Ticket created with priority 1 (high urgency) for VPN failure."
            },
            {
               "timestamp":"2025-11-26T12:00:35.458Z",
               "event_type":"diagnostic_complete",
               "actor_type":"agent",
               "actor_id":"agent_ai_01",
               "message":"Detected multiple failed VPN logins and recent password reset (pattern matches KB-001)."
            },
            {
               "timestamp":"2025-11-26T12:00:35.461Z",
               "event_type":"diagnostic_complete",
               "actor_type":"agent",
               "actor_id":"agent_ai_01",
               "message":"Diagnosis: cached credentials / MFA desync after password change."
            },
            {
               "timestamp":"2025-11-26T12:00:35.468Z",
               "event_type":"solution_found",
               "actor_type":"agent",
               "actor_id":"agent_ai_01",
               "message":"Solution: clear Windows Credential Manager entries, recreate VPN profile, re-register MFA."
            },
            {
               "timestamp":"2025-11-26T12:00:35.480Z",
               "event_type":"resolved",
               "actor_type":"agent",
               "actor_id":"agent_ai_01",
               "message":"User confirmed VPN connection successful and stable."
            }
         ]
      },
      {
         "ticket_id":"TKT-1764161161702",
         "conversation":[
            {
               "timestamp":"2025-11-26T12:46:01.702Z",
               "sender_type":"user",
               "sender_id":"user_0003",
               "sender_name":"Michael Chen",
               "message":"THIS IS RIDICULOUS! My laptop has been blue-screening 3–4 times a day for the last week. I need a replacement TODAY."
            },
            {
               "timestamp":"2025-11-26T12:46:05.210Z",
               "sender_type":"agent",
               "sender_id":"agent_ai_01",
               "sender_name":"AI Support Agent",
               "message":"Hi Michael, I’m really sorry for the repeated crashes. I’ll escalate this immediately and arrange a hardware check and replacement."
            }
         ],
         "events":[
            {
               "timestamp":"2025-11-26T12:46:01.709Z",
               "event_type":"created",
               "actor_type":"system",
               "actor_id":"system",
               "message":"Ticket created with priority 1 (critical urgency) for repeated BSODs."
            },
            {
               "timestamp":"2025-11-26T12:46:10.237Z",
               "event_type":"diagnostic_complete",
               "actor_type":"agent",
               "actor_id":"agent_ai_01",
               "message":"Detected previous related tickets and multiple BSOD entries in event logs."
            },
            {
               "timestamp":"2025-11-26T12:46:10.243Z",
               "event_type":"diagnostic_complete",
               "actor_type":"agent",
               "actor_id":"agent_ai_01",
               "message":"Diagnosis: likely hardware issue not suitable for remote fix."
            },
            {
               "timestamp":"2025-11-26T12:46:10.261Z",
               "event_type":"assigned",
               "actor_type":"agent",
               "actor_id":"agent_ai_01",
               "message":"Assigned to onsite support (it_support_l2_01) for immediate hardware diagnostics and replacement."
            }
         ]
      },
      {
         "ticket_id":"TKT-1764162205120",
         "conversation":[
            {
               "timestamp":"2025-11-27T06:23:25.120Z",
               "sender_type":"agent",
               "sender_id":"agent_ai_01",
               "sender_name":"AI Support Agent",
               "message":"Hi Joseph, I can help you troubleshoot the mouse issue with your dock."
            }
         ],
         "events":[
            {
               "timestamp":"2025-11-27T06:23:25.130Z",
               "event_type":"created",
               "actor_type":"system",
               "actor_id":"system",
               "message":"Ticket created with priority 3 (low urgency) for docking station USB issue."
            }
         ]
      }
   ],
   "knowledge_base":[
      {
         "id":"KB-001",
         "title":"VPN authentication fails after password reset",
         "category":"network",
         "issue_pattern":"VPN authentication failed; password works for email; MFA prompt not showing or failing",
         "summary":"Typical VPN failures after a password change are caused by cached credentials or outdated VPN profiles on the client.",
         "resolution_steps":[
            "Ask user to close the VPN client completely, including any system tray icons.",
            "Open Windows Credential Manager and remove all entries related to the VPN gateway and corporate domain.",
            "Sign out of all Microsoft 365 desktop apps and sign back in using the new domain password.",
            "Delete the existing VPN profile in the VPN client.",
            "Import the latest VPN configuration file from the official IT portal.",
            "Trigger MFA re-registration if MFA prompts are failing or not appearing.",
            "Reconnect to VPN and verify access to internal services such as Jira, Git, and Confluence.",
            "If the issue persists, capture logs and screenshots and escalate to the network team."
         ],
         "last_resolution":{
            "ticket_id":"TKT-1764158427172",
            "resolved_by_type":"agent",
            "resolved_by_name":"AI Support Agent",
            "resolved_by_id":"agent_ai_01",
            "resolved_at":"2025-11-26T12:00:35.478Z"
         },
         "used_in_tickets":[
            "TKT-1764158427172",
            "TKT-1164"
         ]
      },
      {
         "id":"KB-002",
         "title":"Outlook not syncing after mailbox migration to cloud",
         "category":"software",
         "issue_pattern":"Outlook stuck on 'Updating inbox' or 'Trying to connect'; emails visible in webmail but not in desktop app",
         "summary":"Post-migration Outlook sync issues are usually due to old profiles or corrupted OST files pointing to the legacy mailbox.",
         "resolution_steps":[
            "Confirm the user can access email successfully via Outlook on the web.",
            "In Outlook desktop, open Account Settings and remove the old Exchange/Office 365 profile.",
            "Open Control Panel → Mail → Show Profiles and delete outdated profiles that reference on-prem servers.",
            "Create a new mail profile and add the user’s account via AutoDiscover.",
            "Enable 'Use Cached Exchange Mode' with a 1–2 year sync window.",
            "Allow Outlook to rebuild the OST file completely before closing the app.",
            "If OST corruption is suspected, run the built-in repair tool or recreate the OST file from scratch.",
            "If several users in the same department see similar symptoms, create a problem record for the messaging team."
         ],
         "last_resolution":{
            "ticket_id":"TKT-1588",
            "resolved_by_type":"human",
            "resolved_by_name":"Sarah Lopez",
            "resolved_by_id":"it_support_l1_02",
            "resolved_at":"2025-11-15T10:12:09Z"
         },
         "used_in_tickets":[
            "TKT-1588"
         ]
      },
      {
         "id":"KB-003",
         "title":"Developer laptop slow when running Docker and IDEs",
         "category":"performance",
         "issue_pattern":"High CPU and memory usage when Docker, Chrome, and IDE are running simultaneously on standard developer image",
         "summary":"On standard 16 GB RAM developer laptops, Docker plus heavy IDEs and browsers can starve system resources unless Docker is tuned and startup apps are trimmed.",
         "resolution_steps":[
            "Open Task Manager and confirm CPU and RAM usage when Docker workloads are running.",
            "In Docker Desktop → Settings → Resources, reduce vCPU and RAM allocation (e.g., to 4 vCPUs and 4 GB RAM on a 16 GB machine).",
            "Stop and disable unnecessary containers and images that start automatically.",
            "Open the Startup tab in Task Manager and disable non-essential applications (Teams auto-start, chat clients, screen recorders, etc.).",
            "Run the Company Software Center and install the latest graphics and chipset drivers available for the device.",
            "Reboot the laptop and verify that VS Code, the browser, and Docker remain responsive under normal workloads.",
            "If performance is still poor, evaluate hardware upgrade (RAM/SSD) or move heavy builds to remote build agents."
         ],
         "last_resolution":{
            "ticket_id":"TKT-1764158260799",
            "resolved_by_type":"agent",
            "resolved_by_name":"AI Support Agent",
            "resolved_by_id":"agent_ai_01",
            "resolved_at":"2025-11-26T11:57:51.620Z"
         },
         "used_in_tickets":[
            "TKT-1764158260799"
         ]
      },
      {
         "id":"KB-004",
         "title":"Handling repeated BSODs on critical user laptops",
         "category":"hardware",
         "issue_pattern":"Blue screen errors multiple times per day, recurring across tickets, especially for client-facing staff",
         "summary":"Multiple BSOD incidents within a short period usually indicate failing hardware (SSD/RAM) or critical driver conflicts and should trigger hardware replacement for critical staff.",
         "resolution_steps":[
            "Review incident history: if there are two or more BSOD tickets within 7 days for the same device, classify as potential hardware failure.",
            "Collect minidump files and run quick diagnostics on memory and disk (SMART tests).",
            "Mark the user as 'critical' if they are client-facing or manage production systems.",
            "Create a hardware replacement task and arrange a loaner or replacement laptop the same day whenever possible.",
            "Back up the user profile to OneDrive/SharePoint and verify that key project folders are fully synced.",
            "Issue a new device with the standard corporate image and restore required applications from Software Center.",
            "Schedule a short session to test conferencing apps (Zoom/Teams) and development tools with the user.",
            "Monitor for 48 hours; if no further BSODs occur, close the root cause as 'hardware replaced'.",
            "Document asset tags, serial numbers, diagnostic results, and replacement device details in the ticket."
         ],
         "last_resolution":{
            "ticket_id":"TKT-1720",
            "resolved_by_type":"human",
            "resolved_by_name":"John Smith",
            "resolved_by_id":"it_support_l2_01",
            "resolved_at":"2025-11-20T09:45:30Z"
         },
         "used_in_tickets":[
            "TKT-1720",
            "TKT-1764161161702"
         ]
      },
      {
         "id":"KB-005",
         "title":"USB peripherals not working through docking station",
         "category":"hardware",
         "issue_pattern":"Mouse/keyboard intermittently disconnects when plugged into dock but works fine directly on laptop",
         "summary":"Intermittent USB peripheral issues through a dock are commonly due to outdated dock firmware, power problems, or a failing USB hub on the dock.",
         "resolution_steps":[
            "Test the mouse/keyboard directly on the laptop to confirm the device itself is healthy.",
            "Update docking station firmware and drivers from the vendor’s official support site.",
            "Check that the dock’s power adapter has the correct wattage and is firmly plugged in.",
            "Move the device to a different USB port on the dock, preferring back-panel ports for stability.",
            "Disable USB selective suspend in Windows power options for heavily used docking stations.",
            "If issues persist, swap the dock with a known-good unit and re-test the peripherals.",
            "If multiple users with the same dock model report similar problems, raise a problem ticket with hardware engineering and procurement."
         ],
         "last_resolution":{
            "ticket_id":"TKT-1374",
            "resolved_by_type":"human",
            "resolved_by_name":"Priya Nair",
            "resolved_by_id":"it_support_l1_03",
            "resolved_at":"2025-11-10T13:22:11Z"
         },
         "used_in_tickets":[
            "TKT-1374",
            "TKT-1764162205120"
         ]
      },
      {
         "id":"KB-006",
         "title":"Slow boot after Windows update",
         "category":"performance",
         "issue_pattern":"Laptop takes more than 5–10 minutes to boot after a major Windows feature update",
         "summary":"Slow boot issues after large Windows updates are typically due to disk fragmentation, startup overload, or problematic drivers/services.",
         "resolution_steps":[
            "Check boot time in Event Viewer (Diagnostics-Performance logs) to confirm excessive startup duration.",
            "Run a disk health check and SMART test to rule out failing drives.",
            "Open Task Manager → Startup tab and disable non-essential startup apps.",
            "Run 'sfc /scannow' and 'DISM /Online /Cleanup-Image /RestoreHealth' from an elevated Command Prompt.",
            "Check Windows Update history and ensure all post-feature-update patches and driver updates are installed.",
            "Update storage and chipset drivers from the device manufacturer or via Company Software Center.",
            "Reboot and measure boot time again; if still slow, enable boot logging and analyze which drivers/services delay startup.",
            "If the drive is close to capacity or shows high latency, consider SSD replacement for persistent cases."
         ],
         "last_resolution":{
            "ticket_id":"TKT-2399",
            "resolved_by_type":"human",
            "resolved_by_name":"Alex Turner",
            "resolved_by_id":"it_support_l1_01",
            "resolved_at":"2025-11-26T15:05:40Z"
         },
         "used_in_tickets":[
            "TKT-2399"
         ]
      }
   ]
}
]

def ingest_data():
    print("🚀 Starting ingestion process...")
    
    if not GOOGLE_API_KEY:
        print("❌ Error: GOOGLE_API_KEY not found in .env")
        return False

    # 1. Load data from JSON file
    data = load_data_from_file()
    if not data:
        print("⚠️  Using fallback knowledge base...")
        data = KNOWLEDGE_BASE[0]
    
    # 2. Prepare Documents from Knowledge Base
    documents = []
    kb_items = data.get("knowledge_base", [])
    
    print(f"📚 Processing {len(kb_items)} knowledge base articles...")
    for item in kb_items:
        # Create a rich content string for better retrieval
        content_str = f"""
Title: {item['title']}
Category: {item['category']}
Issue Pattern: {item['issue_pattern']}
Summary: {item['summary']}
Resolution Steps:
{chr(10).join(f"  {i+1}. {step}" for i, step in enumerate(item['resolution_steps']))}
"""
        
        doc = Document(
            page_content=content_str.strip(),
            metadata={
                "source": "knowledge_base",
                "kb_id": item["id"],
                "title": item["title"],
                "category": item["category"],
                "type": "knowledge_base"
            }
        )
        documents.append(doc)
    
    # 3. Add ticket conversations for context
    conversations = data.get("ticket_conversations", [])
    print(f"💬 Processing {len(conversations)} ticket conversations...")
    
    for conv in conversations:
        ticket_id = conv.get("ticket_id")
        messages = conv.get("conversation", [])
        
        # Build conversation text
        conv_text = f"Ticket ID: {ticket_id}\n\n"
        for msg in messages:
            sender = msg.get("sender_name", "Unknown")
            message = msg.get("message", "")
            conv_text += f"{sender}: {message}\n"
        
        # Add events if available
        events = conv.get("events", [])
        if events:
            conv_text += "\nEvents:\n"
            for event in events:
                event_type = event.get("event_type", "")
                event_msg = event.get("message", "")
                conv_text += f"  - {event_type}: {event_msg}\n"
        
        doc = Document(
            page_content=conv_text.strip(),
            metadata={
                "source": "ticket_conversation",
                "ticket_id": ticket_id,
                "type": "conversation"
            }
        )
        documents.append(doc)
    
    # 4. Add tickets for retrieval
    tickets = data.get("tickets", [])
    print(f"🎫 Processing {len(tickets)} tickets...")
    
    for ticket in tickets:
        ticket_text = f"""
Ticket ID: {ticket.get('id')}
Title: {ticket.get('title')}
User: {ticket.get('user_name')}
Description: {ticket.get('description')}
Priority: {ticket.get('priority')}
Status: {ticket.get('status')}
Category: {ticket.get('category')}
Urgency: {ticket.get('urgency')}
Knowledge Base: {ticket.get('knowledge_base_id', 'N/A')}
"""
        
        doc = Document(
            page_content=ticket_text.strip(),
            metadata={
                "source": "ticket",
                "ticket_id": ticket.get("id"),
                "user_id": ticket.get("user_id"),
                "category": ticket.get("category"),
                "status": ticket.get("status"),
                "priority": ticket.get("priority"),
                "type": "ticket"
            }
        )
        documents.append(doc)
    
    print(f"📄 Prepared {len(documents)} total documents for ingestion.")
    
    # 5. Initialize Embeddings
    embeddings = get_embeddings()

    # 6. Create/Update Vector Store
    db_path = Path(__file__).parent / CHROMA_DB_DIR
    print(f"💾 Creating vector database at {db_path}...")
    
    # Remove old database if exists
    if db_path.exists():
        import shutil
        shutil.rmtree(db_path)
        print("🗑️  Removed old database")
    
    # Create ChromaDB client with settings to avoid ONNX runtime
    chroma_client = chromadb.PersistentClient(
        path=str(db_path)
    )
    
    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        client=chroma_client,
        persist_directory=str(db_path)
    )
    
    print(f"✅ Ingestion complete! Created vector database with {len(documents)} documents.")
    print(f"   - Knowledge Base Articles: {len(kb_items)}")
    print(f"   - Ticket Conversations: {len(conversations)}")
    print(f"   - Tickets: {len(tickets)}")
    return True

if __name__ == "__main__":
    success = ingest_data()
    if not success:
        exit(1)