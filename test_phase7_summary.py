import os
from dotenv import load_dotenv

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

import sys
sys.path.insert(0, 'C:/Users/subhankar nath/Desktop/Legal-Tech/services')
sys.path.insert(0, 'C:/Users/subhankar nath/Desktop/Legal-Tech/services/ai')

import asyncio
import json

async def test_summary():
    from ai.models.openrouter_client import OpenRouterClient
    
    print('='*80)
    print('PHASE 7.3 - SUMMARY CARD GENERATION TEST (REAL AI)')
    print('='*80)
    
    client = OpenRouterClient()
    
    # Test with employment contract data
    test_cases = [
        {
            'name': '1. Employment Contract with HIGH risks',
            'contract_type': 'Employment',
            'high_risk': ['Non-compete 24 months restricts future work', 'IP assignment gives employer full ownership', 'Indemnity exposes employee to unlimited liability'],
            'medium_risk': ['Auto-renewal clause', 'Termination without cause'],
            'risk_counts': {'HIGH': 3, 'MEDIUM': 2, 'LOW': 5}
        },
        {
            'name': '2. NDA - Balanced',
            'contract_type': 'NDA',
            'high_risk': ['Perpetual confidentiality obligation'],
            'medium_risk': ['Liquidated damages clause'],
            'risk_counts': {'HIGH': 1, 'MEDIUM': 1, 'LOW': 8}
        },
        {
            'name': '3. Service Agreement',
            'contract_type': 'Service Agreement',
            'high_risk': ['IP belongs to provider', 'Client indemnifies provider'],
            'medium_risk': ['Liability cap'],
            'risk_counts': {'HIGH': 2, 'MEDIUM': 1, 'LOW': 7}
        },
        {
            'name': '4. SaaS Subscription',
            'contract_type': 'SaaS',
            'high_risk': ['Arbitration only', 'Class action waiver'],
            'medium_risk': ['Auto-renewal', 'Price changes'],
            'risk_counts': {'HIGH': 2, 'MEDIUM': 2, 'LOW': 6}
        },
        {
            'name': '5. Vendor Agreement - Low Risk',
            'contract_type': 'Vendor',
            'high_risk': [],
            'medium_risk': ['Standard payment terms'],
            'risk_counts': {'HIGH': 0, 'MEDIUM': 1, 'LOW': 10}
        }
    ]
    
    for test in test_cases:
        print(f'\n{test["name"]}')
        print('-'*60)
        
        prompt = f'''You are a legal contract summarizer. Generate a plain-language summary.

Contract Type: {test['contract_type']}
HIGH Risk Clauses:
{chr(10).join('- ' + c for c in test['high_risk'])}

MEDIUM Risk Clauses:
{chr(10).join('- ' + c for c in test['medium_risk'])}

Risk Distribution: {test['risk_counts']}

Respond ONLY with valid JSON:
{{
  "one_liner": "single sentence summary",
  "should_you_sign": "Yes as-is" or "Yes with changes" or "No",
  "top_3_concerns": ["concern 1", "concern 2", "concern 3"],
  "top_2_positives": ["positive 1", "positive 2"],
  "overall_risk_score": 0-100,
  "negotiating_power": "Strong" or "Moderate" or "Weak"
}}'''
        
        try:
            result = await client.chat_json(
                system_prompt='Return ONLY valid JSON',
                user_prompt=prompt,
                model='anthropic/claude-3-haiku'
            )
            
            print('>>> SUMMARY RESULT:')
            print('  One Liner:', result.get('one_liner', 'N/A')[:60], '...')
            print('  Should You Sign:', result.get('should_you_sign', 'N/A'))
            print('  Overall Risk Score:', result.get('overall_risk_score', 'N/A'))
            print('  Negotiating Power:', result.get('negotiating_power', 'N/A'))
            print('  Top 3 Concerns:', result.get('top_3_concerns', [])[:2])
            print('  Top 2 Positives:', result.get('top_2_positives', [])[:2])
            
        except Exception as e:
            print('Error:', str(e)[:150])
    
    await client.close()

asyncio.run(test_summary())
print('\n' + '='*80)
print('ALL 5 SUMMARY TESTS COMPLETE')
print('='*80)