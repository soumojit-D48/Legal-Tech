import os
from dotenv import load_dotenv

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

import sys
sys.path.insert(0, 'C:/Users/subhankar nath/Desktop/Legal-Tech/services')
sys.path.insert(0, 'C:/Users/subhankar nath/Desktop/Legal-Tech/services/ai')

import asyncio
import json

async def test_consequence():
    from ai.models.openrouter_client import OpenRouterClient
    
    print('='*80)
    print('PHASE 7 - CONSEQUENCE GENERATION TEST (REAL AI)')
    print('='*80)
    
    client = OpenRouterClient()
    
    test_cases = [
        {
            'name': '1. Employment - Indemnity',
            'clause_type': 'indemnity',
            'clause_text': 'Employee shall indemnify Company against any claims arising from Employee work.',
            'user_role': 'Employee',
            'risk_category': 'Financial'
        },
        {
            'name': '2. NDA - IP Assignment', 
            'clause_type': 'ip_assignment',
            'clause_text': 'All intellectual property, inventions, and work product created belongs to Company.',
            'user_role': 'Receiving Party',
            'risk_category': 'IP'
        },
        {
            'name': '3. Service - Non-Compete',
            'clause_type': 'non_compete',
            'clause_text': 'Provider shall not work for competitors for 24 months after termination.',
            'user_role': 'Service Provider',
            'risk_category': 'Employment'
        },
        {
            'name': '4. Lease - Auto-Renewal',
            'clause_type': 'auto_renewal',
            'clause_text': 'Lease automatically renews for 12 months unless 60 days notice given.',
            'user_role': 'Tenant',
            'risk_category': 'Terms'
        },
        {
            'name': '5. Vendor - Limitation of Liability',
            'clause_type': 'limitation_of_liability',
            'clause_text': 'Vendor liability capped at fees paid in prior 12 months.',
            'user_role': 'Customer',
            'risk_category': 'Financial'
        }
    ]
    
    for test in test_cases:
        print(f'\n{test["name"]}')
        print('-'*60)
        print(f'Clause: {test["clause_text"][:50]}...')
        
        prompt = f'''You are a legal risk analyst. Analyze this contract clause and explain real-world consequences.

Clause Type: {test["clause_type"]}
User Role: {test["user_role"]}
Risk Category: {test["risk_category"]}
Clause: {test["clause_text"]}

Respond ONLY with valid JSON with exactly these fields:
{{
  "headline": "short summary of the risk",
  "scenario": "2-3 sentence realistic scenario of what could go wrong",
  "financial_exposure": "dollar amount like $50,000 or unlimited",
  "probability": "Low, Medium, or High",
  "similar_case": "brief reference to a legal case"
}}'''
        
        try:
            result = await client.chat_json(
                system_prompt='Return ONLY valid JSON',
                user_prompt=prompt,
                model='anthropic/claude-3-haiku'
            )
            
            print('\n>>> CONSEQUENCE RESULT:')
            print('  Headline:', result.get('headline', 'N/A'))
            print('  Scenario:', result.get('scenario', 'N/A')[:80], '...')
            print('  Financial Exposure:', result.get('financial_exposure', 'N/A'))
            print('  Probability:', result.get('probability', 'N/A'))
            print('  Similar Case:', result.get('similar_case', 'N/A'))
            
        except Exception as e:
            print('Error:', str(e)[:150])
    
    await client.close()

asyncio.run(test_consequence())
print('\n' + '='*80)
print('ALL 5 TEST CASES COMPLETE')
print('='*80)