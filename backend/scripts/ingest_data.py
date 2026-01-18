"""
Knowledge Base Ingestion Script for RAG System.
Loads MITRE ATT&CK, Azure Policies, and CIS Benchmarks into Pinecone vector database.
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any

# Add backend to path to import app modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.rag.embeddings import generate_embedding
from app.rag.vector_db import upsert_documents, get_index

# =============================================================================
# DATA LOADERS
# =============================================================================

def load_mitre_techniques(filepath: Path) -> List[Dict[str, Any]]:
    """
    Parse MITRE ATT&CK STIX JSON into documents for vector database.
    
    Returns list of documents with id, text, and metadata.
    """
    print(f"Loading MITRE ATT&CK from {filepath}...")
    
    if not filepath.exists():
        print(f"Warning: MITRE file not found at {filepath}")
        return []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    documents = []
    
    for obj in data.get("objects", []):
        # Only process attack patterns (techniques)
        if obj.get("type") != "attack-pattern":
            continue
        
        # Extract technique ID from external references
        tech_id = ""
        url = ""
        for ref in obj.get("external_references", []):
            if ref.get("source_name") == "mitre-attack":
                tech_id = ref.get("external_id", "")
                url = ref.get("url", "")
                break
        
        if not tech_id:
            continue
        
        # Extract tactics (kill chain phases)
        tactics = []
        for phase in obj.get("kill_chain_phases", []):
            if phase.get("kill_chain_name") == "mitre-attack":
                tactics.append(phase.get("phase_name", ""))
        
        # Build document text
        name = obj.get("name", "")
        description = obj.get("description", "")[:1500]  # Truncate for embedding limits
        
        # Clean description (remove markdown links, etc.)
        description = description.replace("[", "").replace("]", "").replace("(", "").replace(")", "")
        
        doc_text = f"{name} ({tech_id}): {description}"
        
        documents.append({
            "id": f"mitre-{tech_id.lower()}",
            "text": doc_text,
            "metadata": {
                "text": doc_text,
                "source": "MITRE ATT&CK",
                "technique_id": tech_id,
                "technique_name": name,
                "tactics": ", ".join(tactics),
                "url": url,
                "category": "Threat Intelligence"
            }
        })
    
    print(f"  Loaded {len(documents)} MITRE techniques")
    return documents


def load_cis_benchmarks() -> List[Dict[str, Any]]:
    """
    Load CIS Benchmark controls (hardcoded key controls for Azure).
    In production, these would be parsed from the actual CIS PDF/Excel exports.
    """
    print("Loading CIS Benchmarks (built-in controls)...")
    
    # Key CIS Azure Foundation Benchmark v2.0 controls
    cis_controls = [
        {
            "id": "cis-azure-1.1",
            "control": "1.1",
            "title": "Ensure Security Defaults is enabled on Azure Active Directory",
            "description": "Security defaults in Azure Active Directory (Azure AD) make it easier to be secure and help protect your organization. Security defaults contain preconfigured security settings for common attacks.",
            "rationale": "Security defaults provide secure default settings that we manage on behalf of organizations to keep customers safe until they are ready to manage their own identity security settings.",
            "remediation": "Navigate to Azure Active Directory > Properties > Manage Security defaults. Set 'Enable Security defaults' to Yes."
        },
        {
            "id": "cis-azure-1.3",
            "control": "1.3", 
            "title": "Ensure that multi-factor authentication is enabled for all privileged users",
            "description": "Enable multi-factor authentication for all user credentials who have write access to Azure resources. This includes roles like Service Co-Administrators, Subscription Owners, and Contributors.",
            "rationale": "Multi-factor authentication requires an individual to present a minimum of two separate forms of authentication before access is granted.",
            "remediation": "Navigate to Azure AD > Security > MFA. Configure per-user MFA or Conditional Access policies to require MFA for privileged roles."
        },
        {
            "id": "cis-azure-2.1",
            "control": "2.1",
            "title": "Ensure that Microsoft Defender for Cloud is set to On",
            "description": "Microsoft Defender for Cloud is a unified infrastructure security management system that strengthens the security posture of your data centers.",
            "rationale": "Turning on Microsoft Defender for Cloud enables threat detection for compute, database, storage and other Azure resources.",
            "remediation": "Navigate to Microsoft Defender for Cloud > Environment settings. Select subscription and enable Defender plans."
        },
        {
            "id": "cis-azure-3.1",
            "control": "3.1",
            "title": "Ensure that 'Secure transfer required' is set to 'Enabled' for Storage Accounts",
            "description": "Enable data encryption in transit by requiring secure transfer for all Storage Account operations.",
            "rationale": "The secure transfer option enhances the security by only allowing requests to the storage account by a secure connection (HTTPS).",
            "remediation": "Navigate to Storage Accounts > Configuration. Set 'Secure transfer required' to Enabled."
        },
        {
            "id": "cis-azure-3.7",
            "control": "3.7",
            "title": "Ensure default network access rule for Storage Accounts is set to deny",
            "description": "Restricting default network access helps to provide a new layer of security to storage accounts.",
            "rationale": "By default, storage accounts accept connections from clients on any network. To limit access, you should deny access from all networks and allow access only from specific virtual networks.",
            "remediation": "Navigate to Storage Accounts > Networking. Under 'Public network access', select 'Enabled from selected virtual networks and IP addresses'."
        },
        {
            "id": "cis-azure-4.1",
            "control": "4.1",
            "title": "Ensure that 'Auditing' is set to 'On' for SQL Servers",
            "description": "Enable auditing on SQL Servers to track database activities and maintain regulatory compliance.",
            "rationale": "Auditing tracks database events and writes them to an audit log. This helps you understand database activity and gain insight into discrepancies and anomalies.",
            "remediation": "Navigate to SQL Servers > Auditing. Set 'Enable Azure SQL Auditing' to On and configure storage account."
        },
        {
            "id": "cis-azure-4.4",  
            "control": "4.4",
            "title": "Ensure that Advanced Threat Protection is enabled on SQL Servers",
            "description": "Enable Advanced Threat Protection to detect anomalous activities indicating unusual and potentially harmful attempts to access or exploit databases.",
            "rationale": "Advanced Threat Protection provides a new layer of security, which enables customers to detect and respond to potential threats as they occur.",
            "remediation": "Navigate to SQL Servers > Microsoft Defender for Cloud. Enable Microsoft Defender for SQL."
        },
        {
            "id": "cis-azure-5.1",
            "control": "5.1",
            "title": "Ensure that a 'Diagnostic Setting' exists for Subscription Activity Logs",
            "description": "Enable diagnostic settings to export subscription activity logs to a Log Analytics workspace, Storage Account, or Event Hub.",
            "rationale": "A diagnostic setting enables export of platform logs and metrics to the destination of your choice for long-term retention and analysis.",
            "remediation": "Navigate to Monitor > Activity log > Diagnostic settings. Create diagnostic setting sending to Log Analytics workspace."
        },
        {
            "id": "cis-azure-6.1",
            "control": "6.1",
            "title": "Ensure that RDP access is restricted from the internet",
            "description": "Disable RDP access on network security groups from the Internet to protect against brute force attacks.",
            "rationale": "Open RDP ports to the internet are frequently targeted by attackers attempting to brute force credentials or exploit vulnerabilities.",
            "remediation": "Navigate to Network Security Groups. Remove or modify inbound rules allowing RDP (port 3389) from 'Any' or 'Internet' source."
        },
        {
            "id": "cis-azure-6.2",
            "control": "6.2",  
            "title": "Ensure that SSH access is restricted from the internet",
            "description": "Disable SSH access on network security groups from the Internet to prevent unauthorized remote access.",
            "rationale": "Open SSH ports are targeted by attackers performing brute force attacks or exploiting authentication vulnerabilities.",
            "remediation": "Navigate to Network Security Groups. Remove or modify inbound rules allowing SSH (port 22) from 'Any' or 'Internet' source."
        },
        {
            "id": "cis-azure-7.1",
            "control": "7.1",
            "title": "Ensure Virtual Machines are utilizing Managed Disks",
            "description": "Migrate blob-based VHDs to managed disks for improved reliability and security of VM storage.",
            "rationale": "Managed disks provide better reliability, simple scalability, and better security. They use storage service encryption by default.",
            "remediation": "Navigate to Virtual Machines. For VMs with unmanaged disks, select 'Migrate to managed disks'."
        },
        {
            "id": "cis-azure-8.1",
            "control": "8.1",
            "title": "Ensure that the expiration date is set on all keys in Azure Key Vault",
            "description": "Set expiration dates for all keys to ensure keys are rotated within a specified timeframe.",
            "rationale": "Keys without expiration may remain valid indefinitely, increasing the risk if compromised.",
            "remediation": "Navigate to Key Vault > Keys. For each key, set an expiration date in the key properties."
        },
        {
            "id": "cis-azure-8.2",
            "control": "8.2",
            "title": "Ensure that the expiration date is set on all secrets in Azure Key Vault",
            "description": "Set expiration dates for all secrets to enforce secret rotation policies.",
            "rationale": "Secrets without expiration pose security risks if compromised credentials are never invalidated.",
            "remediation": "Navigate to Key Vault > Secrets. For each secret, set an expiration date in the secret properties."
        },
        {
            "id": "cis-azure-9.1",
            "control": "9.1",
            "title": "Ensure App Service Authentication is set up for apps in Azure App Service",
            "description": "Azure App Service Authentication is a feature that prevents anonymous HTTP requests from reaching the API app.",
            "rationale": "App Service provides built-in authentication and authorization capabilities, letting you sign in users without writing code.",
            "remediation": "Navigate to App Services > Authentication. Enable authentication and configure an identity provider."
        },
        {
            "id": "cis-azure-9.3",
            "control": "9.3",
            "title": "Ensure web app redirects all HTTP traffic to HTTPS",
            "description": "Azure Web Apps allows sites to run under both HTTP and HTTPS by default. An app can be configured to always use HTTPS.",
            "rationale": "Enabling HTTPS-only traffic ensures all communication between clients and the web application is encrypted.",
            "remediation": "Navigate to App Services > Configuration > General settings. Set 'HTTPS Only' to On."
        }
    ]
    
    documents = []
    for control in cis_controls:
        doc_text = f"CIS Azure Benchmark Control {control['control']}: {control['title']}. {control['description']} Remediation: {control['remediation']}"
        
        documents.append({
            "id": control["id"],
            "text": doc_text,
            "metadata": {
                "text": doc_text,
                "source": "CIS Benchmark",
                "control_id": control["control"],
                "title": control["title"],
                "category": "Compliance",
                "benchmark": "CIS Azure Foundations v2.0"
            }
        })
    
    print(f"  Loaded {len(documents)} CIS Benchmark controls")
    return documents


def load_azure_policies() -> List[Dict[str, Any]]:
    """
    Load common Azure Policy definitions (built-in key policies).
    These represent the most important security policies for cloud environments.
    """
    print("Loading Azure Policies (built-in definitions)...")
    
    azure_policies = [
        {
            "id": "azure-policy-storage-https",
            "name": "Secure transfer to storage accounts should be enabled",
            "description": "Audit requirement of Secure transfer in your storage account. Secure transfer is an option that forces your storage account to accept requests only from secure connections (HTTPS). Use of HTTPS ensures authentication between the server and the service and protects data in transit from network layer attacks such as man-in-the-middle, eavesdropping, and session-hijacking.",
            "category": "Storage",
            "effect": "Audit"
        },
        {
            "id": "azure-policy-sql-encryption",
            "name": "Transparent Data Encryption on SQL databases should be enabled",
            "description": "Transparent data encryption should be enabled to protect data-at-rest and meet compliance requirements. TDE encrypts SQL Database, Azure Synapse Analytics, and Parallel Data Warehouse data files.",
            "category": "SQL",
            "effect": "AuditIfNotExists"
        },
        {
            "id": "azure-policy-vm-encryption",
            "name": "Virtual machines should encrypt temp disks, caches, and data flows",
            "description": "By default, a virtual machine's OS and data disks are encrypted at rest using platform-managed keys. Temp disks, data caches, and data flowing between compute and storage are not encrypted. Enable encryption of all these components.",
            "category": "Compute",
            "effect": "AuditIfNotExists"
        },
        {
            "id": "azure-policy-keyvault-purge",
            "name": "Key vaults should have purge protection enabled",
            "description": "Malicious deletion of a key vault can lead to permanent data loss. A malicious insider in your organization can potentially delete and purge key vaults. Purge protection protects you from insider attacks by enforcing a mandatory retention period.",
            "category": "Key Vault",
            "effect": "Audit"
        },
        {
            "id": "azure-policy-keyvault-softdelete",
            "name": "Key vaults should have soft delete enabled",
            "description": "Deleting a key vault without soft delete enabled permanently deletes all secrets, keys, and certificates stored in the key vault. Accidental deletion of a key vault can lead to permanent data loss.",
            "category": "Key Vault",
            "effect": "Audit"
        },
        {
            "id": "azure-policy-nsg-flow-logs",
            "name": "Flow logs should be configured for every network security group",
            "description": "Audit for network security groups to verify if flow logs are configured. Enabling flow logs allows to log information about IP traffic flowing through network security group.",
            "category": "Network",
            "effect": "Audit"
        },
        {
            "id": "azure-policy-defender-servers",
            "name": "Azure Defender for servers should be enabled",
            "description": "Azure Defender for servers provides real-time threat protection for server workloads and generates hardening recommendations as well as alerts about suspicious activities.",
            "category": "Security Center",
            "effect": "AuditIfNotExists"
        },
        {
            "id": "azure-policy-defender-sql",
            "name": "Azure Defender for SQL should be enabled for unprotected Azure SQL servers",
            "description": "Audit SQL servers without Advanced Data Security to detect anomalous activities indicating unusual attempts to access or exploit databases.",
            "category": "SQL",
            "effect": "AuditIfNotExists"
        },
        {
            "id": "azure-policy-public-ip",
            "name": "Public IP addresses should have resource logs enabled",
            "description": "Enable resource logs for Public IP addresses to be able to view traffic patterns and detect anomalies. This is useful for security monitoring and incident investigation.",
            "category": "Network",
            "effect": "AuditIfNotExists"
        },
        {
            "id": "azure-policy-webapp-https",
            "name": "Web Application should only be accessible over HTTPS",
            "description": "Use of HTTPS ensures server/service authentication and protects data in transit from network layer eavesdropping attacks.",
            "category": "App Service",
            "effect": "Audit"
        },
        {
            "id": "azure-policy-function-https",
            "name": "Function apps should only be accessible over HTTPS",
            "description": "Use of HTTPS ensures server/service authentication and protects data in transit from network layer eavesdropping attacks.",
            "category": "App Service",
            "effect": "Audit"
        },
        {
            "id": "azure-policy-aks-rbac",
            "name": "Role-Based Access Control (RBAC) should be used on Kubernetes Services",
            "description": "To provide granular filtering on the actions that users can perform, use Role-Based Access Control (RBAC) to manage permissions in Kubernetes Service Clusters.",
            "category": "Kubernetes",
            "effect": "Audit"
        },
        {
            "id": "azure-policy-storage-firewall",
            "name": "Storage accounts should restrict network access using virtual network rules",
            "description": "Protect your storage accounts from potential threats using virtual network rules as a preferred method instead of IP-based filtering.",
            "category": "Storage",
            "effect": "Audit"
        },
        {
            "id": "azure-policy-diagnostic-logs",
            "name": "Resource logs in Azure Key Vault should be enabled",
            "description": "Enable resource logs for Key Vault to track activities. Having visibility into Key Vault operations enables you to monitor how your key vaults are being accessed.",
            "category": "Key Vault",
            "effect": "AuditIfNotExists"
        },
        {
            "id": "azure-policy-mfa-owner",
            "name": "MFA should be enabled for accounts with owner permissions",
            "description": "Multi-Factor Authentication (MFA) should be enabled for all subscription accounts with owner permissions to prevent a breach of accounts or resources.",
            "category": "Security Center",
            "effect": "AuditIfNotExists"
        },
        {
            "id": "azure-policy-deprecated-accounts",
            "name": "Deprecated accounts should be removed from your subscription",
            "description": "Deprecated accounts should be removed from your subscriptions. Deprecated accounts are accounts that have been blocked from signing in.",
            "category": "Security Center",
            "effect": "AuditIfNotExists"
        },
        {
            "id": "azure-policy-jit-access",
            "name": "Management ports of virtual machines should be protected with JIT",
            "description": "Possible network Just In Time (JIT) access will be monitored by Azure Security Center as recommendations to protect management ports.",
            "category": "Compute",
            "effect": "AuditIfNotExists"
        },
        {
            "id": "azure-policy-disk-encryption",
            "name": "Disk encryption should be applied on virtual machines",
            "description": "Virtual machines without an enabled disk encryption will be monitored by Azure Security Center as recommendations.",
            "category": "Compute",
            "effect": "AuditIfNotExists"
        }
    ]
    
    documents = []
    for policy in azure_policies:
        doc_text = f"Azure Policy: {policy['name']}. {policy['description']} Effect: {policy['effect']}."
        
        documents.append({
            "id": policy["id"],
            "text": doc_text,
            "metadata": {
                "text": doc_text,
                "source": "Azure Policy",
                "policy_name": policy["name"],
                "category": policy["category"],
                "effect": policy["effect"]
            }
        })
    
    print(f"  Loaded {len(documents)} Azure Policy definitions")
    return documents


# =============================================================================
# MAIN INGESTION
# =============================================================================

def main():
    print("=" * 60)
    print("RAG Knowledge Base Ingestion")
    print("=" * 60)
    
    # Check Pinecone connection first
    index = get_index()
    if index is None:
        print("\nERROR: Cannot connect to Pinecone. Check your PINECONE_API_KEY.")
        print("Aborting ingestion.")
        return
    
    print("\n✓ Pinecone connection verified")
    
    # Paths
    data_dir = Path(__file__).resolve().parent.parent / "data" / "raw"
    
    # Collect all documents
    all_docs = []
    
    # 1. Load MITRE ATT&CK
    mitre_path = data_dir / "mitre_attack.json"
    all_docs.extend(load_mitre_techniques(mitre_path))
    
    # 2. Load CIS Benchmarks (built-in)
    all_docs.extend(load_cis_benchmarks())
    
    # 3. Load Azure Policies (built-in)  
    all_docs.extend(load_azure_policies())
    
    print(f"\nTotal documents to ingest: {len(all_docs)}")
    
    if len(all_docs) == 0:
        print("No documents to ingest. Exiting.")
        return
    
    # Batch upsert to Pinecone
    BATCH_SIZE = 50
    total_batches = (len(all_docs) + BATCH_SIZE - 1) // BATCH_SIZE
    
    print(f"\nUpserting in {total_batches} batches of {BATCH_SIZE}...")
    
    for i in range(0, len(all_docs), BATCH_SIZE):
        batch = all_docs[i:i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        
        print(f"  Batch {batch_num}/{total_batches}: Generating embeddings...")
        
        # Generate embeddings for batch
        embeddings = []
        for doc in batch:
            emb = generate_embedding(doc["text"])
            embeddings.append(emb)
        
        # Upsert batch
        print(f"  Batch {batch_num}/{total_batches}: Upserting to Pinecone...")
        upsert_documents(batch, embeddings)
        
        print(f"  Batch {batch_num}/{total_batches}: Done ✓")
    
    print("\n" + "=" * 60)
    print(f"SUCCESS: Ingested {len(all_docs)} documents into Pinecone")
    print("=" * 60)
    
    # Print summary
    print("\nKnowledge Base Summary:")
    sources = {}
    for doc in all_docs:
        source = doc["metadata"].get("source", "Unknown")
        sources[source] = sources.get(source, 0) + 1
    
    for source, count in sorted(sources.items()):
        print(f"  - {source}: {count} documents")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    main()
