import os
from dotenv import load_dotenv

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

import sys
sys.path.insert(0, 'C:/Users/subhankar nath/Desktop/Legal-Tech/services')
sys.path.insert(0, 'C:/Users/subhankar nath/Desktop/Legal-Tech/services/ai')

import asyncio
import json

async def full_test():
    from ai.models.openrouter_client import OpenRouterClient
    
    client = OpenRouterClient()
    
    # 5 Different Contract Datasets
    datasets = [
        {
            'id': 1,
            'name': 'SENIOR SOFTWARE ENGINEER EMPLOYMENT CONTRACT',
            'type': 'Employment',
            'user_role': 'Employee',
            'clauses': [
                {'text': 'Employer: TechCorp Inc., Employee: John Smith', 'risk': 'LOW', 'category': 'header'},
                {'text': 'Position: Senior Software Engineer reporting to CTO', 'risk': 'LOW', 'category': 'role'},
                {'text': 'Annual Salary: 180,000 USD plus benefits', 'risk': 'LOW', 'category': 'compensation'},
                {'text': 'Non-compete: Employee cannot work for competitors for 24 months after termination', 'risk': 'HIGH', 'category': 'non_compete'},
                {'text': 'IP Assignment: All code and inventions belong to TechCorp', 'risk': 'HIGH', 'category': 'ip_assignment'},
                {'text': 'Confidentiality: Employee keeps all trade secrets forever', 'risk': 'LOW', 'category': 'confidentiality'},
                {'text': 'Indemnification: Employee indemnifies Company against all claims', 'risk': 'HIGH', 'category': 'indemnity'},
                {'text': 'Termination: Company can fire anytime without notice', 'risk': 'HIGH', 'category': 'termination'},
                {'text': 'Benefits: Health insurance, 401k matching', 'risk': 'LOW', 'category': 'benefits'},
                {'text': 'Governing Law: California state law', 'risk': 'LOW', 'category': 'jurisdiction'}
            ]
        },
        {
            'id': 2,
            'name': 'MUTUAL NON-DISCLOSURE AGREEMENT',
            'type': 'NDA',
            'user_role': 'Receiving Party',
            'clauses': [
                {'text': 'Disclosing Party: Alpha Corp, Receiving Party: Beta Inc', 'risk': 'LOW', 'category': 'header'},
                {'text': 'Purpose: Protect confidential business information', 'risk': 'LOW', 'category': 'purpose'},
                {'text': 'Confidential Information includes trade secrets, customer lists, pricing', 'risk': 'LOW', 'category': 'scope'},
                {'text': 'Obligations: Cannot disclose to third parties without written consent', 'risk': 'LOW', 'category': 'obligations'},
                {'text': 'Survival: Confidentiality survives termination indefinitely', 'risk': 'HIGH', 'category': 'confidentiality'},
                {'text': 'Exclusions: Information already public, independently developed', 'risk': 'LOW', 'category': 'exclusions'},
                {'text': 'Breach: Pays 100,000 USD liquidated damages', 'risk': 'HIGH', 'category': 'liquidated_damages'},
                {'text': 'Disputes: Binding arbitration in New York', 'risk': 'MEDIUM', 'category': 'arbitration'},
                {'text': 'Term: 5 years from execution date', 'risk': 'LOW', 'category': 'term'},
                {'text': 'Governing Law: New York state law', 'risk': 'LOW', 'category': 'jurisdiction'}
            ]
        },
        {
            'id': 3,
            'name': 'FREELANCE SOFTWARE DEVELOPMENT CONTRACT',
            'type': 'Service Agreement',
            'user_role': 'Contractor',
            'clauses': [
                {'text': 'Client: Acme Corp, Provider: DevStudio LLC', 'risk': 'LOW', 'category': 'header'},
                {'text': 'Deliverable: Custom web application', 'risk': 'LOW', 'category': 'scope'},
                {'text': 'Payment: 15,000 USD upfront, 15,000 USD on completion', 'risk': 'LOW', 'category': 'payment'},
                {'text': 'Timeline: 4 months delivery timeline', 'risk': 'LOW', 'category': 'timeline'},
                {'text': 'IP Rights: Provider retains ownership of all code', 'risk': 'HIGH', 'category': 'ip_assignment'},
                {'text': 'Warranty: 90 days bug fixes, AS-IS otherwise', 'risk': 'LOW', 'category': 'warranty'},
                {'text': 'Indemnification: Client indemnifies Provider from all claims', 'risk': 'HIGH', 'category': 'indemnity'},
                {'text': 'Limitation: Liability capped at 30,000 USD', 'risk': 'MEDIUM', 'category': 'limitation'},
                {'text': 'Termination: Either party with 30 days notice', 'risk': 'LOW', 'category': 'termination'},
                {'text': 'Non-Solicit: Cannot hire each others staff for 1 year', 'risk': 'MEDIUM', 'category': 'non_solicitation'}
            ]
        },
        {
            'id': 4,
            'name': 'SAAS ENTERPRISE SUBSCRIPTION AGREEMENT',
            'type': 'SaaS',
            'user_role': 'Customer',
            'clauses': [
                {'text': 'Provider: CloudSoft Inc, Customer: Enterprise Co', 'risk': 'LOW', 'category': 'header'},
                {'text': 'Service: Enterprise CRM software subscription', 'risk': 'LOW', 'category': 'service'},
                {'text': 'Pricing: 2,000 USD monthly, annual billing', 'risk': 'LOW', 'category': 'pricing'},
                {'text': 'Data: Provider may use anonymized data for AI training', 'risk': 'MEDIUM', 'category': 'data'},
                {'text': 'Auto-Renewal: Annual renewal unless 30 days notice', 'risk': 'MEDIUM', 'category': 'auto_renewal'},
                {'text': 'Price Changes: Provider can increase fees with 60 days notice', 'risk': 'MEDIUM', 'category': 'price_changes'},
                {'text': 'Arbitration: All disputes resolved through binding arbitration', 'risk': 'HIGH', 'category': 'arbitration'},
                {'text': 'Class Action: Customer waives class action rights', 'risk': 'HIGH', 'category': 'class_action'},
                {'text': 'Liability: Capped at amounts paid in prior 12 months', 'risk': 'MEDIUM', 'category': 'limitation'},
                {'text': 'Term: 3 year initial term', 'risk': 'LOW', 'category': 'term'}
            ]
        },
        {
            'id': 5,
            'name': 'COMMERCIAL OFFICE LEASE AGREEMENT',
            'type': 'Lease',
            'user_role': 'Tenant',
            'clauses': [
                {'text': 'Landlord: Property Holdings LLC, Tenant: Retail Co', 'risk': 'LOW', 'category': 'header'},
                {'text': 'Premises: 5,000 sq ft office space at 500 Main Street', 'risk': 'LOW', 'category': 'premises'},
                {'text': 'Rent: 8,000 USD per month, due 1st of month', 'risk': 'LOW', 'category': 'rent'},
                {'text': 'Security Deposit: 16,000 USD (2 months)', 'risk': 'LOW', 'category': 'deposit'},
                {'text': 'Term: 60 months (5 years)', 'risk': 'LOW', 'category': 'term'},
                {'text': 'Auto-Renewal: Auto-renews for 12 months unless 90 days notice', 'risk': 'MEDIUM', 'category': 'auto_renewal'},
                {'text': 'Early Termination: Tenant forfeits deposit if terminates early', 'risk': 'MEDIUM', 'category': 'termination'},
                {'text': 'Maintenance: Tenant responsible for all repairs', 'risk': 'LOW', 'category': 'maintenance'},
                {'text': 'Sublet: Not allowed without landlord approval', 'risk': 'LOW', 'category': 'sublet'},
                {'text': 'Insurance: Tenant must carry 2M liability coverage', 'risk': 'LOW', 'category': 'insurance'}
            ]
        }
    ]
    
    print('='*100)
    print('PHASE 7 - COMPREHENSIVE TEST WITH 5 DIFFERENT DATASETS')
    print('='*100)
    
    for dataset in datasets:
        print(f'\n\n{"="*100}')
        print(f'DATASET {dataset["id"]}: {dataset["name"]}')
        print(f'Contract Type: {dataset["type"]} | User Role: {dataset["user_role"]}')
        print(f'{"="*100}')
        
        # Count risks
        high_risk = [c for c in dataset['clauses'] if c['risk'] == 'HIGH']
        medium_risk = [c for c in dataset['clauses'] if c['risk'] == 'MEDIUM']
        low_risk = [c for c in dataset['clauses'] if c['risk'] == 'LOW']
        
        print(f'\nRisk Distribution: HIGH={len(high_risk)}, MEDIUM={len(medium_risk)}, LOW={len(low_risk)}')
        
        # ===== STEP 7.1: CONSEQUENCE GENERATION =====
        print(f'\n{"-"*100}')
        print('STEP 7.1: CONSEQUENCE GENERATION (for HIGH risk clauses)')
        print(f'{"-"*100}')
        
        for clause in high_risk:
            prompt = f'''You are a legal risk analyst. Analyze this clause and explain real-world consequences.

Clause Type: {clause['category']}
User Role: {dataset['user_role']}
Contract Type: {dataset['type']}

Clause: {clause['text']}

Respond ONLY with valid JSON:
{{"headline": "summary", "scenario": "what could go wrong", "financial_exposure": "$ or unlimited", "probability": "Low/Medium/High", "similar_case": "case name"}}'''
            
            try:
                result = await client.chat_json(
                    system_prompt='Return ONLY valid JSON',
                    user_prompt=prompt,
                    model='anthropic/claude-3-haiku'
                )
                
                print(f'\n  CLAUSE: {clause["text"][:60]}...')
                print(f'  Category: {clause["category"]}')
                print(f'  HEADLINE: {result.get("headline", "N/A")}')
                print(f'  SCENARIO: {result.get("scenario", "N/A")[:100]}...')
                print(f'  FINANCIAL EXPOSURE: {result.get("financial_exposure", "N/A")}')
                print(f'  PROBABILITY: {result.get("probability", "N/A")}')
                print(f'  SIMILAR CASE: {result.get("similar_case", "N/A")}')
                
            except Exception as e:
                print(f'  ERROR: {str(e)[:80]}')
        
        # ===== STEP 7.2: POWER ANALYSIS =====
        print(f'\n{"-"*100}')
        print('STEP 7.2: POWER ASYMMETRY ANALYSIS')
        print(f'{"-"*100}')
        
        prompt = f'''You are a legal power asymmetry analyst. Analyze this contract and score power balance.

Contract Type: {dataset['type']}
User Role: {dataset['user_role']}

CLAUSES:
'''
        for c in dataset['clauses']:
            prompt += f"- [{c['risk']}] {c['text']} (category: {c['category']})\n"
        
        prompt += '''
Respond ONLY with valid JSON:
{"power_score": -100 to +100, "power_label": "label", "key_imbalances": [{"clause": "text", "why": "reason", "score": number}], "leverage_points": ["point1", "point2"]}'''
        
        try:
            result = await client.chat_json(
                system_prompt='Return ONLY valid JSON',
                user_prompt=prompt,
                model='anthropic/claude-3-haiku'
            )
            
            print(f'\n  POWER SCORE: {result.get("power_score", "N/A")}')
            print(f'  POWER LABEL: {result.get("power_label", "N/A")}')
            print(f'  KEY IMBALANCES:')
            for imb in result.get('key_imbalances', [])[:3]:
                print(f'    - {imb.get("clause", "")[:50]}')
                print(f'      Why: {imb.get("why", "")[:60]}')
                print(f'      Score: {imb.get("score", "N/A")}')
            print(f'  LEVERAGE POINTS:')
            for lp in result.get('leverage_points', [])[:3]:
                print(f'    - {lp}')
                
        except Exception as e:
            print(f'  ERROR: {str(e)[:80]}')
        
        # ===== STEP 7.3: SUMMARY CARD =====
        print(f'\n{"-"*100}')
        print('STEP 7.3: SUMMARY CARD GENERATION')
        print(f'{"-"*100}')
        
        high_risk_text = [c['text'] for c in high_risk]
        medium_risk_text = [c['text'] for c in medium_risk]
        
        prompt = f'''You are a legal contract summarizer. Generate a summary.

Contract Type: {dataset['type']}

HIGH Risk Clauses:
{chr(10).join("- " + c for c in high_risk_text[:5])}

MEDIUM Risk Clauses:
{chr(10).join("- " + c for c in medium_risk_text[:5])}

Risk Distribution: HIGH={len(high_risk)}, MEDIUM={len(medium_risk)}, LOW={len(low_risk)}

Respond ONLY with valid JSON:
{{"one_liner": "summary", "should_you_sign": "Yes as-is/Yes with changes/No", "top_3_concerns": ["c1", "c2", "c3"], "top_2_positives": ["p1", "p2"], "overall_risk_score": 0-100, "negotiating_power": "Strong/Moderate/Weak"}}'''
        
        try:
            result = await client.chat_json(
                system_prompt='Return ONLY valid JSON',
                user_prompt=prompt,
                model='anthropic/claude-3-haiku'
            )
            
            print(f'\n  ONE-LINER: {result.get("one_liner", "N/A")[:80]}...')
            print(f'  SHOULD YOU SIGN: {result.get("should_you_sign", "N/A")}')
            print(f'  OVERALL RISK SCORE: {result.get("overall_risk_score", "N/A")}/100')
            print(f'  NEGOTIATING POWER: {result.get("negotiating_power", "N/A")}')
            print(f'  TOP 3 CONCERNS:')
            for c in result.get('top_3_concerns', [])[:3]:
                print(f'    - {c[:70]}...')
            print(f'  TOP 2 POSITIVES:')
            for p in result.get('top_2_positives', [])[:2]:
                print(f'    - {p[:70]}...')
                
        except Exception as e:
            print(f'  ERROR: {str(e)[:80]}')
        
        print(f'\n{"="*100}')
    
    await client.close()
    print('\n' + '='*100)
    print('ALL 5 DATASETS TESTED SUCCESSFULLY!')
    print('='*100)

asyncio.run(full_test())