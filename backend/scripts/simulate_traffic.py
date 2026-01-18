
import requests
import time
import random
import uuid
from datetime import datetime

API_URL = "http://127.0.0.1:8000/api/incidents/create"

TEMPLATES = [
    {
        "title": "Suspicious PowerShell Execution",
        "category": "Execution",
        "source": "Azure Sentinel",
        "description": "Detected encoded PowerShell command execution on production database server.",
        "severity": "critical",
        "classification": "TP",
        "confidence": 98.5
    },
    {
        "title": "Impossible Travel Detection",
        "category": "Initial Access",
        "source": "Azure AD",
        "description": "User {user} logged in from {loc1} and {loc2} within {mins} minutes.",
        "severity": "high",
        "classification": "TP",
        "confidence": 89.2
    },
    {
        "title": "Anomalous Data Exfiltration",
        "category": "Exfiltration",
        "source": "CloudDefender Network",
        "description": "Unusual outbound traffic spike ({size} GB) to unknown IP {ip}.",
        "severity": "high",
        "classification": "TP",
        "confidence": 92.1
    },
    {
        "title": "Brute Force Attempt (SSH)",
        "category": "Credential Access",
        "source": "Linux Security Module",
        "description": "Multiple failed SSH login attempts from IP {ip}.",
        "severity": "medium",
        "classification": "TP",
        "confidence": 99.0
    },
    {
        "title": "New Admin Account Created",
        "category": "Persistence",
        "source": "Azure Activity Log",
        "description": "Privileged account '{user}' created by existing admin.",
        "severity": "medium",
        "classification": "FP",
        "confidence": 65.0
    },
    {
        "title": "S3 Bucket Public Access Enabled",
        "category": "Defense Evasion",
        "source": "CloudTrail",
        "description": "Bucket 'finance-backup-{rand}' ACL set to public-read.",
        "severity": "critical",
        "classification": "TP",
        "confidence": 100.0
    }
]

LOCATIONS = ["New York", "London", "Tokyo", "Sydney", "Moscow", "Beijing", "Berlin", "Paris"]
USERS = ["admin", "jdoe", "backup_svc", "root", "devops_user", "sql_sa"]

def generate_incident():
    tpl = random.choice(TEMPLATES)
    
    # Randomize details
    desc = tpl["description"].format(
        user=random.choice(USERS),
        loc1=random.choice(LOCATIONS),
        loc2=random.choice(LOCATIONS),
        mins=random.randint(5, 60),
        size=random.randint(1, 50),
        ip=f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
        rand=random.randint(1000, 9999)
    )
    
    feature_confidence = tpl["confidence"] + random.uniform(-5.0, 1.0)
    
    incident = {
        "id": f"INC-2024-{random.randint(1000, 99999)}",
        "title": tpl["title"],
        "severity": tpl["severity"],
        "category": tpl["category"],
        "source": tpl["source"],
        "timestamp": "Just now",
        "classification": tpl["classification"],
        "confidence": round(feature_confidence, 1),
        "description": desc,
        "features": {
            "alert_burst_count": random.randint(1, 100),
            "hour_of_day": datetime.now().hour,
            "day_of_week": datetime.now().weekday(),
            "Category": tpl["category"],
            "all_features": {
                "Category": tpl["category"],
                "Severity": tpl["severity"],
                "Source": tpl["source"]
            }
        }
    }
    return incident

def simulate():
    print("🚀 Starting Incident Traffic Simulator...")
    print(f"Targeting: {API_URL}")
    print("Press Ctrl+C to stop.")
    
    while True:
        try:
            incident = generate_incident()
            resp = requests.post(API_URL, json=incident)
            
            if resp.status_code == 200:
                print(f"✅ Generated: {incident['id']} - {incident['title']}")
            else:
                print(f"❌ Failed: {resp.status_code} - {resp.text}")
                
            # Wait random time (e.g. 5 to 15 seconds)
            sleep_time = random.uniform(5, 15)
            time.sleep(sleep_time)
            
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    simulate()
