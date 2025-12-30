"""
Clinical Component Identifier - Flask Backend API
Few-Shot Prompting Version (No Fine-Tuning Required)
"""

import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Use standard model (no fine-tuning needed)
MODEL = "gpt-4o-mini"

# Few-shot examples for better accuracy
FEW_SHOT_EXAMPLES = """
EXAMPLE 1:
Input: "This study will be conducted in accordance with Good Clinical Practice (GCP) as defined by the International Council for Harmonisation (ICH) and in accordance with the ethical principles underlying European Union Directive 2001/20/EC."
Output: [{"type": "boilerplate", "title": "GCP Compliance Statement", "text": "This study will be conducted in accordance with Good Clinical Practice (GCP) as defined by the International Council for Harmonisation (ICH) and in accordance with the ethical principles underlying European Union Directive 2001/20/EC.", "confidence": 0.97, "reuse_potential": "high", "rationale": "Standard regulatory compliance statement used across multiple protocols"}]

EXAMPLE 2:
Input: "Primary Endpoint: The primary endpoint is overall survival (OS), defined as the time from randomization to death from any cause."
Output: [{"type": "definition", "title": "Overall Survival Definition", "text": "The primary endpoint is overall survival (OS), defined as the time from randomization to death from any cause.", "confidence": 0.95, "reuse_potential": "high", "rationale": "Standard endpoint definition used in oncology trials"}]

EXAMPLE 3:
Input: "Inclusion Criteria: 1. Age >= 18 years 2. Histologically confirmed diagnosis 3. ECOG performance status 0-1"
Output: [{"type": "study_section", "title": "Inclusion Criteria", "text": "1. Age >= 18 years 2. Histologically confirmed diagnosis 3. ECOG performance status 0-1", "confidence": 0.94, "reuse_potential": "medium", "rationale": "Common inclusion criteria structure for clinical trials"}]

EXAMPLE 4:
Input: "Adverse events will be graded according to NCI-CTCAE version 5.0. All serious adverse events must be reported within 24 hours."
Output: [{"type": "safety", "title": "Adverse Event Reporting", "text": "Adverse events will be graded according to NCI-CTCAE version 5.0. All serious adverse events must be reported within 24 hours.", "confidence": 0.96, "reuse_potential": "high", "rationale": "Standard safety reporting procedures"}]

EXAMPLE 5:
Input: "The investigational product is administered orally at 100mg twice daily with food."
Output: [{"type": "drug_info", "title": "Drug Administration", "text": "The investigational product is administered orally at 100mg twice daily with food.", "confidence": 0.92, "reuse_potential": "medium", "rationale": "Drug dosing information"}]
"""

SYSTEM_PROMPT = f"""You are an expert clinical documentation analyst specializing in identifying reusable content components in medical and clinical documents.

TASK: Analyze clinical text and identify all reusable components.

COMPONENT TYPES:
- boilerplate: Standard regulatory or administrative text (GCP statements, confidentiality clauses)
- definition: Precise definitions of terms, endpoints, or events
- study_section: Study-specific methodology (inclusion/exclusion criteria, objectives)
- drug_info: Information about investigational product (dosing, mechanism)
- safety: Safety monitoring or reporting procedures
- procedure: Clinical or administrative procedures

RULES:
1. Components must be self-contained and semantically complete
2. Assign confidence score 0.0-1.0 based on clarity of component boundaries
3. Assign reuse_potential: "high", "medium", or "low"
4. Provide brief rationale for each component

{FEW_SHOT_EXAMPLES}

OUTPUT FORMAT:
Return ONLY a valid JSON array with this structure (no other text):
[{{"type": "component_type", "title": "Descriptive title", "text": "Exact extracted text", "confidence": 0.95, "reuse_potential": "high", "rationale": "Brief explanation"}}]
"""


@app.route("/", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "Clinical Component Identifier API",
        "model": MODEL,
        "version": "1.0.0 (Few-Shot)"
    })


@app.route("/api/identify", methods=["POST"])
def identify_components():
    try:
        data = request.get_json()
        
        if not data or "text" not in data:
            return jsonify({"error": "Text field is required"}), 400
        
        text = data["text"].strip()
        if not text:
            return jsonify({"error": "Text cannot be empty"}), 400
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Identify all reusable components in this clinical text:\n\n{text}"}
            ],
            temperature=0.0,
            max_tokens=4000
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Parse JSON response
        try:
            # Remove markdown code blocks if present
            if result_text.startswith("```"):
                result_text = result_text.split("```")[1]
                if result_text.startswith("json"):
                    result_text = result_text[4:]
            
            components = json.loads(result_text)
            
            if isinstance(components, dict):
                components = components.get("components", [components])
            
        except json.JSONDecodeError:
            # Try to extract JSON array
            import re
            match = re.search(r'\[.*\]', result_text, re.DOTALL)
            if match:
                components = json.loads(match.group())
            else:
                components = []
        
        # Add component IDs
        for i, comp in enumerate(components):
            comp["component_id"] = f"comp_{i+1:03d}"
        
        return jsonify({
            "success": True,
            "components": components,
            "total_components": len(components),
            "model_used": MODEL,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        })
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "components": []
        }), 500


@app.route("/api/taxonomy", methods=["GET"])
def get_taxonomy():
    return jsonify({
        "component_types": [
            {"name": "boilerplate", "description": "Standard regulatory or administrative text"},
            {"name": "definition", "description": "Precise definitions of terms or endpoints"},
            {"name": "study_section", "description": "Study-specific methodology or procedures"},
            {"name": "drug_info", "description": "Information about investigational product"},
            {"name": "safety", "description": "Safety monitoring or reporting procedures"},
            {"name": "procedure", "description": "Clinical or administrative procedures"}
        ]
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)