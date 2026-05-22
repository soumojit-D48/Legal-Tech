import os
from dotenv import load_dotenv

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

import sys
sys.path.insert(0, 'C:/Users/subhankar nath/Desktop/Legal-Tech/services')
sys.path.insert(0, 'C:/Users/subhankar nath/Desktop/Legal-Tech/services/ai')

import asyncio
import json

async def test_power_analysis():
    from ai.models.openrouter_client import OpenRouterClient
    
    print('='*80)
    print('PHASE 7.2 - POWER ASYMMETRY ANALYSIS TEST (REAL AI)')
    print('='*80)
    
    client = OpenRouterClient()
    
    # Test with a contract that has HIGH risk clauses
    contract_data = {
        'contract_type': 'Employment',
        'user_role': 'Employee',
        'clauses': [
            {'text': 'Employer shall pay 150,000 USD salary', 'risk': 'LOW', 'category': 'payment'},
            {'text': 'Employee shall not work for competitors for 24 months', 'risk': 'HIGH', 'category': 'non_compete'},
            {'text': 'All IP created belongs to Employer', 'risk': 'HIGH', 'category': 'ip_assignment'},
            {'text': 'Employee indemnifies Employer against all claims', 'risk': 'HIGH', 'category': 'indemnity'},
            {'text': 'Employer may terminate anytime without notice', 'risk': 'HIGH', 'category': 'termination'},
            {'text': 'Employee receives health benefits', 'risk': 'LOW', 'category': 'benefits'},
        ]
    }
    
    prompt = f'''You are a legal power asymmetry analyst. Analyze this contract and score the power balance between the parties.

Contract Type: {contract_data['contract_type']}
User Role: {contract_data['user_role']}

CLAUSES ANALYSIS:
'''
    
    for c in contract_data['clauses']:
        prompt += f"- [{c['risk']}] {c['text']} (category: {c['category']})\n"
    
    prompt += '''
Respond ONLY with valid JSON:
{
  "power_score": -100 to +100 (integer),
  "power_label": "Strongly Favors Counterparty" / "Slightly Favors Counterparty" / "Balanced" / "Slightly Favors User" / "Strongly Favors User",
  "key_imbalances": [
    {"clause": "clause text", "why": "reason it's one-sided", "score": -50 to +50}
  ],
  "leverage_points": ["what user can negotiate on"]
}'''
    
    print('Analyzing contract with 3 HIGH risk clauses...')
    
    try:
        result = await client.chat_json(
            system_prompt='Return ONLY valid JSON',
            user_prompt=prompt,
            model='anthropic/claude-3-haiku'
        )
        
        print('\n>>> POWER ANALYSIS RESULT:')
        print('  Power Score:', result.get('power_score', 'N/A'))
        print('  Power Label:', result.get('power_label', 'N/A'))
        print('  Key Imbalances:', len(result.get('key_imbalances', [])))
        for imb in result.get('key_imbalances', [])[:3]:
            print(f'    - {imb.get("clause", "")[:40]}')
            print(f'      Why: {imb.get("why", "")[:50]}')
            print(f'      Score: {imb.get("score", "N/A")}')
        print('  Leverage Points:', result.get('leverage_points', []))
        
    except Exception as e:
        print('Error:', str(e)[:150])
    
    await client.close()

asyncio.run(test_power_analysis())
print('\n' + '='*80)
print('POWER ANALYSIS COMPLETE')
print('='*80)