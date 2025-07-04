import os
import openai
from openai import OpenAI
from typing import Dict, Any
from dotenv import load_dotenv
from src.nuvai.utils.logger import get_logger

logger = get_logger(__name__)

load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

DEFAULT_MODEL ="gpt-4o-2024-08-06"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 1000

SYSTEM_PROMPT = """You are a cybersecurity expert. Analyze this scan result and provide:
1. A brief summary of findings
2. Risk assessment
3. Prioritized recommendations
Be concise and focus on actionable insights."""

demo_object = {
    "ai_analysis": "This is a demo response from the AI analysis.",
    "model_used": DEFAULT_MODEL
}

def analyze_scan_results(scan_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze scan results using OpenAI API
    """
    try:
        scan_text = f"""File: {scan_result['filename']}
        Language: {scan_result['language']}
        Vulnerabilities Found: {len(scan_result['vulnerabilities'])}
        Detailed Findings:
        {format_vulnerabilities(scan_result['vulnerabilities'])}
        """
        # return demo_object
        model_to_use = DEFAULT_MODEL
        logger.debug(f"Attempting to use model: {model_to_use}")

        logger.debug(f"Making API call with model {model_to_use}")
        response = client.chat.completions.create(
            model=model_to_use,
            temperature=DEFAULT_TEMPERATURE,
            max_tokens=DEFAULT_MAX_TOKENS,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": scan_text}
            ]
        )
  
        ai_analysis = response.choices[0].message.content
        logger.debug(f"AI analysis completed using {model_to_use}")
        return {
            "ai_analysis": ai_analysis,
            "model_used": model_to_use
        }

    except Exception as e:
        logger.error(f"Fatal error in analyze_scan_results: {str(e)}")
        return {
            "ai_analysis": f"Error performing AI analysis: {str(e)}",
            "error": True
        }

def format_vulnerabilities(vulnerabilities: list) -> str:
    """
    Format vulnerabilities list for better AI processing
    """
    formatted = []
    for v in vulnerabilities:
        formatted.append(f"""
        Severity: {v.get('severity', v.get('level', 'info')).upper()}
        Finding: {v.get('title', v.get('type', 'Unknown Finding'))}
        Description: {v.get('description', v.get('message', 'No description provided.'))}
        Recommendation: {v.get('recommendation', 'No recommendation available.')}
        """)
    return "\n".join(formatted)
