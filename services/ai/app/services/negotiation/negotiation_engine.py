import os
import json

from openai import OpenAI

from .coach_prompts import (
    SYSTEM_PROMPT,
    build_negotiation_prompt,
)

from .schemas import (
    NegotiationRequest,
    NegotiationResponse,
)

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)


MODEL_NAME = "openai/gpt-4.1-mini"


def generate_negotiation_response(
    data: NegotiationRequest,
) -> NegotiationResponse:

    user_prompt = build_negotiation_prompt(
        clause=data.clause,
        risk_level=data.risk_level,
        contract_type=data.contract_type,
        jurisdiction=data.jurisdiction,
    )

    completion = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0.5,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": f"""
Return ONLY valid JSON.

JSON format:

{{
  "risk_explanation": "...",
  "leverage_points": ["...", "..."],
  "counter_offer": "...",
  "negotiation_strategy": "...",
  "communication_tone": "...",
  "avatar_message": "..."
}}

{user_prompt}
""",
            },
        ],
    )

    content = completion.choices[0].message.content

    parsed = json.loads(content)

    return NegotiationResponse(**parsed)