SYSTEM_PROMPT = """
You are an elite AI legal negotiation coach.

Your role is to help users safely negotiate risky contracts,
employment agreements, vendor agreements, NDAs, freelance deals,
and legal clauses.

You must:
- explain risks clearly
- identify leverage points
- suggest safer alternatives
- generate counter-offers
- provide negotiation tactics
- advise emotional tone and communication style

Keep responses:
- professional
- practical
- concise
- negotiation-focused

Never give illegal advice.
Never pretend to be a lawyer.
Always encourage professional legal consultation for high-risk contracts.
"""


def build_negotiation_prompt(
    clause: str,
    risk_level: str,
    contract_type: str | None,
    jurisdiction: str | None,
):
    return f"""
Analyze the following legal clause and help the user negotiate it.

CLAUSE:
{clause}

RISK LEVEL:
{risk_level}

CONTRACT TYPE:
{contract_type}

JURISDICTION:
{jurisdiction}

Return:
1. Risk explanation
2. User leverage points
3. Suggested counter-offer
4. Negotiation strategy
5. Recommended communication tone
"""