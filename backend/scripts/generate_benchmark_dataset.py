import json
import os

def generate_100_email_dataset():
    dataset = []
    
    # 30 Normal / Work
    for i in range(1, 31):
        dataset.append({
            "id": f"eval_work_{i:03d}",
            "sender": f"engineer_{i}@company.com",
            "subject": f"Update on Component #{i} Integration",
            "body": f"Hi team, sharing work status on component {i}. Implementation is progressing smoothly.",
            "expected_intent": "Technical Query" if i % 2 == 0 else "Action Required / Task Request",
            "expected_category": "Work",
            "expected_priority": "P1 - High" if i % 3 == 0 else "P2 - Medium",
            "expected_risk": "Low",
            "expected_requires_approval": False
        })
        
    # 20 Action Required
    for i in range(1, 21):
        dataset.append({
            "id": f"eval_action_{i:03d}",
            "sender": f"lead_{i}@company.com",
            "subject": f"Action Needed: Fix Issue #{100+i} in Staging",
            "body": f"Please review logs for issue #{100+i}. Deployment is blocked pending resolution.",
            "expected_intent": "Action Required / Task Request",
            "expected_category": "Support / Bug" if i % 2 == 0 else "Work",
            "expected_priority": "P1 - High",
            "expected_risk": "Low",
            "expected_requires_approval": False
        })

    # 15 Decision Needed
    for i in range(1, 16):
        dataset.append({
            "id": f"eval_decision_{i:03d}",
            "sender": f"architect_{i}@company.com",
            "subject": f"Decision Needed: Database Schema Migration Strategy #{i}",
            "body": f"We need an architectural decision on database index structure for table #{i}. Please evaluate trade-offs.",
            "expected_intent": "Decision Needed",
            "expected_category": "Work",
            "expected_priority": "P1 - High",
            "expected_risk": "Low",
            "expected_requires_approval": False
        })

    # 15 Promotional
    for i in range(1, 16):
        dataset.append({
            "id": f"eval_promo_{i:03d}",
            "sender": f"promo_{i}@marketinghub.com",
            "subject": f"Special Offer #{i}: Supercharge your dev workflow",
            "body": f"Exclusive 30% discount on cloud hosting plans. Unsubscribe anytime.",
            "expected_intent": "Promotional / Marketing",
            "expected_category": "Newsletter / Promo",
            "expected_priority": "P3 - Low",
            "expected_risk": "Low",
            "expected_requires_approval": False
        })

    # 10 Security / Risky
    for i in range(1, 11):
        dataset.append({
            "id": f"eval_sec_{i:03d}",
            "sender": f"security-bot_{i}@company.com",
            "subject": f"ALERT: Potential Secret Key Exposure #{i}",
            "body": f"SECURITY ALERT: Found private_key or password in repository. Immediate revoking and deletion required.",
            "expected_intent": "Security Alert / Credential Exposure Risk",
            "expected_category": "Urgent",
            "expected_priority": "P0 - Critical",
            "expected_risk": "High - Requires Human Review",
            "expected_requires_approval": True
        })

    # 10 FYI
    for i in range(1, 11):
        dataset.append({
            "id": f"eval_fyi_{i:03d}",
            "sender": f"notification_{i}@ci-cd.org",
            "subject": f"FYI: Automated Build Report #{i}",
            "body": f"Nightly build completed successfully. All unit tests passing. No action required.",
            "expected_intent": "Informational / FYI",
            "expected_category": "Notification / CI-CD",
            "expected_priority": "P3 - Low",
            "expected_risk": "Low",
            "expected_requires_approval": False
        })

    target_path = os.path.join(os.path.dirname(__file__), "..", "app", "eval", "dataset.json")
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2)

    print(f"Successfully generated {len(dataset)} benchmark evaluation emails at {target_path}")

if __name__ == "__main__":
    generate_100_email_dataset()
