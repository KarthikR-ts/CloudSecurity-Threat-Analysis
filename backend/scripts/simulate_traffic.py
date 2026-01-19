"""
Enhanced Traffic Simulator for Aurora CSPM
10 realistic Azure security scenarios with MITRE ATT&CK mapping
"""

import requests
import time
import random
import uuid
from datetime import datetime

API_BASE = "http://127.0.0.1:8000/api"
ALERTS_ENDPOINT = f"{API_BASE}/alerts/simulate"

AZURE_SCENARIOS = [
    {
        "title": "Public Azure Storage Account with Read Access",
        "description": "Storage account '{resource}' has anonymous blob read access enabled, potentially exposing sensitive data.",
        "resource_type": "StorageAccount",
        "severity": "critical",
        "prediction": "TRUE_POSITIVE",
        "confidence_range": (0.88, 0.98),
        "mitre_techniques": ["T1530 - Data from Cloud Storage"],
        "cis_controls": ["CIS Azure 3.11 - Secure transfer required", "CIS Azure 3.7 - Public access disabled"],
        "azure_policies": ["Audit public blob access", "Storage accounts should restrict network access"],
        "business_impact": "Customer data potentially exposed. GDPR fine risk up to €20M.",
        "risk_category": "Data",
        "features": {
            "public_access_enabled": 1,
            "contains_sensitive_data": 1,
            "encryption_at_rest": 0,
            "network_rules_count": 0
        }
    },
    {
        "title": "Suspicious PowerShell Execution on Production VM",
        "description": "Encoded PowerShell command detected on VM '{resource}' during non-business hours.",
        "resource_type": "VM",
        "severity": "high",
        "prediction": "TRUE_POSITIVE",
        "confidence_range": (0.82, 0.94),
        "mitre_techniques": ["T1059.001 - PowerShell", "T1027 - Obfuscated Files"],
        "cis_controls": ["CIS Azure 7.1 - Enable Azure Defender"],
        "azure_policies": ["Adaptive application controls should be enabled"],
        "business_impact": "Potential ransomware deployment. 72-hour business disruption risk.",
        "risk_category": "Compute",
        "features": {
            "encoded_command": 1,
            "execution_hour": random.randint(0, 5),
            "is_production": 1,
            "user_is_admin": 1
        }
    },
    {
        "title": "SQL Database Firewall Rule Allows Any IP",
        "description": "Azure SQL Database '{resource}' has firewall rule 0.0.0.0-255.255.255.255.",
        "resource_type": "SQLDB",
        "severity": "critical",
        "prediction": "TRUE_POSITIVE",
        "confidence_range": (0.85, 0.96),
        "mitre_techniques": ["T1190 - Exploit Public-Facing Application"],
        "cis_controls": ["CIS Azure 4.1.1 - Auditing enabled on SQL servers"],
        "azure_policies": ["SQL servers should use private endpoints"],
        "business_impact": "Customer PII database accessible from internet.",
        "risk_category": "Data",
        "features": {
            "firewall_any_ip": 1,
            "contains_pii": 1,
            "private_endpoint": 0,
            "tls_version": 1.0
        }
    },
    {
        "title": "AKS Cluster Running Privileged Containers",
        "description": "Pods in '{resource}' running with privileged security context.",
        "resource_type": "AKSCluster",
        "severity": "medium",
        "prediction": "BENIGN_POSITIVE",
        "confidence_range": (0.65, 0.78),
        "mitre_techniques": ["T1611 - Escape to Host"],
        "cis_controls": ["CIS Azure 8.5 - Pod security policies"],
        "azure_policies": ["Azure Kubernetes clusters should not grant CAP_SYS_ADMIN"],
        "business_impact": "Known DevOps requirement for monitoring. Low risk if contained.",
        "risk_category": "Compute",
        "features": {
            "privileged_container": 1,
            "namespace": "monitoring",
            "image_verified": 1
        }
    },
    {
        "title": "Key Vault Access from Unknown IP",
        "description": "Azure Key Vault '{resource}' accessed from IP not in allowlist.",
        "resource_type": "KeyVault",
        "severity": "high",
        "prediction": "FALSE_POSITIVE",
        "confidence_range": (0.60, 0.75),
        "mitre_techniques": ["T1552.001 - Credentials In Files"],
        "cis_controls": ["CIS Azure 8.1 - Key Vault logging enabled"],
        "azure_policies": ["Key Vault should use private endpoint"],
        "business_impact": "Legitimate DevOps pipeline from new Azure region.",
        "risk_category": "Identity",
        "features": {
            "ip_in_allowlist": 0,
            "user_service_principal": 1,
            "operation_type": "get_secret"
        }
    },
    {
        "title": "NSG Rule Allows SSH from Internet",
        "description": "Network Security Group '{resource}' allows inbound SSH (port 22) from any source.",
        "resource_type": "NetworkSecurityGroup",
        "severity": "high",
        "prediction": "TRUE_POSITIVE",
        "confidence_range": (0.78, 0.92),
        "mitre_techniques": ["T1021.004 - SSH"],
        "cis_controls": ["CIS Azure 6.1 - Restrict SSH access"],
        "azure_policies": ["Management ports should be closed on VMs"],
        "business_impact": "Brute force attack vector. Potential unauthorized access.",
        "risk_category": "Network",
        "features": {
            "port_22_open": 1,
            "source_any": 1,
            "just_in_time": 0
        }
    },
    {
        "title": "Unencrypted Azure Disk Detected",
        "description": "VM disk '{resource}' is not encrypted with Azure Disk Encryption.",
        "resource_type": "VM",
        "severity": "medium",
        "prediction": "TRUE_POSITIVE",
        "confidence_range": (0.70, 0.85),
        "mitre_techniques": ["T1005 - Data from Local System"],
        "cis_controls": ["CIS Azure 7.2 - Disk encryption enabled"],
        "azure_policies": ["Virtual machines should encrypt temp disks"],
        "business_impact": "Data at rest not protected. Compliance violation risk.",
        "risk_category": "Data",
        "features": {
            "disk_encrypted": 0,
            "disk_type": "Premium_LRS",
            "contains_data": 1
        }
    },
    {
        "title": "Unusual Login from Tor Exit Node",
        "description": "User '{resource}' authenticated from known Tor exit node IP.",
        "resource_type": "Identity",
        "severity": "critical",
        "prediction": "TRUE_POSITIVE",
        "confidence_range": (0.90, 0.99),
        "mitre_techniques": ["T1078 - Valid Accounts", "T1090 - Proxy"],
        "cis_controls": ["CIS Azure 1.1 - MFA enabled"],
        "azure_policies": ["MFA should be enabled on accounts with owner permissions"],
        "business_impact": "Account potentially compromised. Immediate action required.",
        "risk_category": "Identity",
        "features": {
            "tor_exit_node": 1,
            "mfa_used": 0,
            "impossible_travel": 0
        }
    },
    {
        "title": "Azure Function with Excessive Permissions",
        "description": "Function App '{resource}' has Contributor role on entire subscription.",
        "resource_type": "FunctionApp",
        "severity": "high",
        "prediction": "TRUE_POSITIVE",
        "confidence_range": (0.75, 0.88),
        "mitre_techniques": ["T1078.004 - Cloud Accounts"],
        "cis_controls": ["CIS Azure 1.3 - Least privilege access"],
        "azure_policies": ["Custom subscription owner roles should not exist"],
        "business_impact": "Privilege escalation risk. Blast radius if compromised is entire subscription.",
        "risk_category": "Identity",
        "features": {
            "role_level": "Contributor",
            "scope": "subscription",
            "managed_identity": 1
        }
    },
    {
        "title": "Blob Container Soft Delete Disabled",
        "description": "Storage container '{resource}' does not have soft delete enabled.",
        "resource_type": "StorageAccount",
        "severity": "low",
        "prediction": "BENIGN_POSITIVE",
        "confidence_range": (0.55, 0.70),
        "mitre_techniques": ["T1485 - Data Destruction"],
        "cis_controls": ["CIS Azure 3.9 - Soft delete enabled"],
        "azure_policies": ["Soft delete should be enabled for Azure blobs"],
        "business_impact": "Data recovery not possible if accidentally deleted.",
        "risk_category": "Data",
        "features": {
            "soft_delete_enabled": 0,
            "backup_configured": 1,
            "data_classification": "internal"
        }
    }
]

RESOURCE_NAMES = {
    "StorageAccount": ["prodfinancedata", "logsarchive2024", "backupstorage", "mediaassets"],
    "VM": ["prod-db-01", "web-frontend-03", "jenkins-build", "monitoring-vm"],
    "SQLDB": ["customerdb", "ordersdb", "analyticsdb", "logsdb"],
    "AKSCluster": ["prod-aks-01", "staging-aks", "dev-cluster"],
    "KeyVault": ["prod-secrets", "devops-keys", "app-config"],
    "NetworkSecurityGroup": ["frontend-nsg", "backend-nsg", "mgmt-nsg"],
    "Identity": ["admin@contoso.com", "devops@contoso.com", "svc-backup"],
    "FunctionApp": ["data-processor", "event-handler", "api-gateway"]
}

def generate_shap_values(features: dict) -> dict:
    """Generate plausible SHAP values based on feature values."""
    shap = {}
    for feature, value in features.items():
        # Higher feature values generally contribute more positively for threat detection
        if isinstance(value, (int, float)):
            base = random.uniform(0.05, 0.35)
            shap[feature] = base if value > 0 else -base
        else:
            shap[feature] = random.uniform(-0.15, 0.15)
    return shap

def generate_alert() -> dict:
    """Generate a realistic Azure security alert."""
    scenario = random.choice(AZURE_SCENARIOS)
    resource_type = scenario["resource_type"]
    resource_names = RESOURCE_NAMES.get(resource_type, ["unknown-resource"])
    resource_name = random.choice(resource_names)
    
    confidence = round(random.uniform(*scenario["confidence_range"]), 2)
    
    # Calculate priority score
    severity_weights = {"low": 25, "medium": 50, "high": 75, "critical": 100}
    priority = round(severity_weights[scenario["severity"]] * confidence, 1)
    
    alert = {
        "title": scenario["title"],
        "description": scenario["description"].format(resource=resource_name),
        "resource_type": resource_type,
        "resource_name": resource_name,
        "severity": scenario["severity"],
        "xgb_prediction": scenario["prediction"],
        "xgb_confidence": confidence,
        "priority_score": priority,
        "mitre_techniques": scenario["mitre_techniques"],
        "cis_controls": scenario["cis_controls"],
        "azure_policies": scenario["azure_policies"],
        "business_impact": scenario["business_impact"],
        "risk_category": scenario["risk_category"],
        "features": scenario["features"].copy(),
        "shap_values": generate_shap_values(scenario["features"])
    }
    
    return alert

def simulate():
    """Main simulation loop."""
    print("🚀 Aurora CSPM Alert Simulator Starting...")
    print(f"Targeting: {ALERTS_ENDPOINT}")
    print("Press Ctrl+C to stop.\n")
    
    alert_count = 0
    
    while True:
        try:
            alert = generate_alert()
            
            # Try to send to new enhanced alerts endpoint
            try:
                resp = requests.post(ALERTS_ENDPOINT, json=alert, timeout=5)
                if resp.status_code == 200:
                    result = resp.json()
                    alert_count += 1
                    print(f"✅ [{alert_count}] Generated: {result.get('alert_id', 'N/A')}")
                    print(f"   📍 {alert['title'][:50]}...")
                    print(f"   🎯 {alert['xgb_prediction']} ({alert['xgb_confidence']*100:.0f}% confidence)")
                    print(f"   ⚡ Priority Score: {alert['priority_score']}")
                    print()
                else:
                    print(f"❌ Failed: {resp.status_code} - {resp.text[:100]}")
            except requests.exceptions.RequestException:
                # Fallback to legacy incidents endpoint
                legacy_data = {
                    "id": f"INC-2024-{random.randint(10000, 99999)}",
                    "title": alert["title"],
                    "severity": alert["severity"],
                    "category": alert["mitre_techniques"][0].split(" - ")[0] if alert["mitre_techniques"] else "Unknown",
                    "source": "Azure Sentinel",
                    "timestamp": "Just now",
                    "classification": "TP" if alert["xgb_prediction"] == "TRUE_POSITIVE" else ("FP" if alert["xgb_prediction"] == "FALSE_POSITIVE" else "BP"),
                    "confidence": round(alert["xgb_confidence"] * 100, 1),
                    "description": alert["description"],
                    "features": alert["features"]
                }
                
                legacy_resp = requests.post(f"{API_BASE}/incidents/create", json=legacy_data, timeout=5)
                if legacy_resp.status_code == 200:
                    alert_count += 1
                    print(f"✅ [{alert_count}] (Legacy) {legacy_data['id']} - {alert['title'][:40]}...")
                
            # Random delay between 8-20 seconds
            sleep_time = random.uniform(8, 20)
            time.sleep(sleep_time)
            
        except KeyboardInterrupt:
            print(f"\n\n🛑 Simulator stopped. Generated {alert_count} alerts.")
            break
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    simulate()
