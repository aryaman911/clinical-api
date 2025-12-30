"""
Data Preparation Script for OpenAI Fine-Tuning
Uses only built-in Python modules (no pandas required)
"""

import json
import csv
import os
import random
import argparse
from pathlib import Path

# Component taxonomy for labeling
COMPONENT_TYPES = {
    "boilerplate": ["compliance", "regulatory", "gcp", "ich", "fda", "confidential", "agreement", "ethical"],
    "definition": ["defined as", "means", "refers to", "definition", "endpoint", "primary endpoint", "secondary endpoint"],
    "study_section": ["inclusion criteria", "exclusion criteria", "objective", "purpose", "eligibility", "criteria"],
    "drug_info": ["dose", "dosage", "formulation", "mechanism", "pharmacokinetic", "administration", "drug", "medication"],
    "safety": ["adverse event", "serious adverse", "safety", "monitoring", "reporting", "side effect", "toxicity"],
    "procedure": ["procedure", "assessment", "visit", "schedule", "measurement", "evaluation", "blood", "sample", "test"]
}


def classify_text(text):
    """Classify text into component type based on keywords"""
    text_lower = text.lower()
    
    scores = {}
    for comp_type, keywords in COMPONENT_TYPES.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        scores[comp_type] = score
    
    max_type = max(scores, key=scores.get)
    return max_type if scores[max_type] > 0 else "study_section"


def estimate_reuse_potential(text, comp_type):
    """Estimate reuse potential"""
    if comp_type == "boilerplate":
        return "high"
    if comp_type == "definition":
        return "medium" if len(text) > 200 else "high"
    return "medium"


def create_training_example(text, components):
    """Create a single training example in OpenAI format"""
    
    system_message = """You are an expert clinical documentation analyst. Identify reusable components in clinical documents.

Return a JSON array of components with this structure:
[{"type": "component_type", "title": "Descriptive title", "text": "Exact text", "confidence": 0.95, "reuse_potential": "high|medium|low", "rationale": "Why this is reusable"}]

Component types: boilerplate, definition, study_section, drug_info, safety, procedure"""

    user_message = f"Identify components in this clinical text:\n\n{text}"
    
    assistant_message = json.dumps(components)
    
    return {
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": assistant_message}
        ]
    }


def process_csv_file(csv_path):
    """Process CSV file using built-in csv module"""
    examples = []
    
    with open(csv_path, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            # Try different column names
            text = row.get('transcription', '') or row.get('description', '') or row.get('text', '')
            specialty = row.get('medical_specialty', '') or row.get('specialty', 'General')
            
            if not text or len(text) < 100:
                continue
            
            # Split into paragraphs
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip() and len(p.strip()) > 50]
            
            if not paragraphs:
                paragraphs = [text[:1000]]
            
            # Create components
            components = []
            for i, para in enumerate(paragraphs[:5]):
                comp_type = classify_text(para)
                
                component = {
                    "type": comp_type,
                    "title": f"{specialty} - Section {i+1}".strip(),
                    "text": para[:500],
                    "confidence": round(random.uniform(0.85, 0.98), 2),
                    "reuse_potential": estimate_reuse_potential(para, comp_type),
                    "rationale": f"Self-contained {comp_type} section"
                }
                components.append(component)
            
            if components:
                example = create_training_example(text[:2000], components)
                examples.append(example)
    
    return examples


def create_synthetic_examples():
    """Create synthetic training examples"""
    
    synthetic_data = [
        {
            "text": "This study will be conducted in accordance with Good Clinical Practice (GCP) as defined by the International Council for Harmonisation (ICH) and in accordance with the ethical principles underlying European Union Directive 2001/20/EC.",
            "components": [{
                "type": "boilerplate",
                "title": "GCP Compliance Statement",
                "text": "This study will be conducted in accordance with Good Clinical Practice (GCP) as defined by the International Council for Harmonisation (ICH) and in accordance with the ethical principles underlying European Union Directive 2001/20/EC.",
                "confidence": 0.97,
                "reuse_potential": "high",
                "rationale": "Standard regulatory compliance statement"
            }]
        },
        {
            "text": "Primary Endpoint: The primary endpoint is overall survival (OS), defined as the time from randomization to death from any cause. Patients lost to follow-up will be censored at last contact.",
            "components": [{
                "type": "definition",
                "title": "Overall Survival Definition",
                "text": "The primary endpoint is overall survival (OS), defined as the time from randomization to death from any cause. Patients lost to follow-up will be censored at last contact.",
                "confidence": 0.95,
                "reuse_potential": "high",
                "rationale": "Standard endpoint definition"
            }]
        },
        {
            "text": "Inclusion Criteria: 1. Age >= 18 years 2. Histologically confirmed diagnosis 3. ECOG performance status 0-1 4. Adequate organ function 5. Written informed consent",
            "components": [{
                "type": "study_section",
                "title": "Inclusion Criteria",
                "text": "1. Age >= 18 years 2. Histologically confirmed diagnosis 3. ECOG performance status 0-1 4. Adequate organ function 5. Written informed consent",
                "confidence": 0.94,
                "reuse_potential": "medium",
                "rationale": "Standard inclusion criteria structure"
            }]
        },
        {
            "text": "The investigational product XYZ-123 is administered orally at 100mg twice daily with food. The drug has a half-life of 12 hours.",
            "components": [{
                "type": "drug_info",
                "title": "Drug Administration",
                "text": "The investigational product XYZ-123 is administered orally at 100mg twice daily with food. The drug has a half-life of 12 hours.",
                "confidence": 0.92,
                "reuse_potential": "medium",
                "rationale": "Drug dosing information"
            }]
        },
        {
            "text": "Adverse events will be graded according to NCI-CTCAE version 5.0. All serious adverse events must be reported within 24 hours.",
            "components": [{
                "type": "safety",
                "title": "Adverse Event Reporting",
                "text": "Adverse events will be graded according to NCI-CTCAE version 5.0. All serious adverse events must be reported within 24 hours.",
                "confidence": 0.96,
                "reuse_potential": "high",
                "rationale": "Standard safety reporting procedures"
            }]
        },
        {
            "text": "Blood samples for pharmacokinetic analysis will be collected at pre-dose, 1, 2, 4, 8, and 24 hours post-dose.",
            "components": [{
                "type": "procedure",
                "title": "PK Sampling Schedule",
                "text": "Blood samples for pharmacokinetic analysis will be collected at pre-dose, 1, 2, 4, 8, and 24 hours post-dose.",
                "confidence": 0.93,
                "reuse_potential": "medium",
                "rationale": "Standard PK sampling procedure"
            }]
        }
    ]
    
    examples = []
    
    # Create base examples
    for data in synthetic_data:
        example = create_training_example(data["text"], data["components"])
        examples.append(example)
    
    # Duplicate with variations for more training data
    for _ in range(15):
        for data in synthetic_data:
            varied_components = []
            for comp in data["components"]:
                varied_comp = comp.copy()
                varied_comp["confidence"] = round(random.uniform(0.85, 0.98), 2)
                varied_components.append(varied_comp)
            
            example = create_training_example(data["text"], varied_components)
            examples.append(example)
    
    return examples


def validate_jsonl(examples):
    """Validate training examples"""
    valid = []
    
    for ex in examples:
        try:
            if "messages" not in ex:
                continue
            if len(ex["messages"]) != 3:
                continue
            if not all(m.get("content") for m in ex["messages"]):
                continue
            json.loads(ex["messages"][2]["content"])
            valid.append(ex)
        except:
            continue
    
    return valid


def save_jsonl(examples, output_path):
    """Save to JSONL file"""
    with open(output_path, 'w', encoding='utf-8') as f:
        for example in examples:
            f.write(json.dumps(example) + '\n')


def main():
    parser = argparse.ArgumentParser(description='Prepare training data')
    parser.add_argument('--input', type=str, help='Input CSV file')
    parser.add_argument('--output', type=str, default='data', help='Output directory')
    parser.add_argument('--synthetic-only', action='store_true', help='Use only synthetic data')
    parser.add_argument('--train-split', type=float, default=0.8, help='Training split ratio')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    examples = []
    
    # Add synthetic examples
    print("Generating synthetic training examples...")
    synthetic = create_synthetic_examples()
    examples.extend(synthetic)
    print(f"  Generated {len(synthetic)} synthetic examples")
    
    # Process CSV if provided
    if args.input and not args.synthetic_only:
        print(f"Processing CSV file: {args.input}")
        csv_examples = process_csv_file(args.input)
        examples.extend(csv_examples)
        print(f"  Extracted {len(csv_examples)} examples from CSV")
    
    # Validate
    print("\nValidating examples...")
    valid_examples = validate_jsonl(examples)
    print(f"  Valid: {len(valid_examples)} / {len(examples)}")
    
    # Shuffle and split
    random.shuffle(valid_examples)
    split_idx = int(len(valid_examples) * args.train_split)
    train = valid_examples[:split_idx]
    val = valid_examples[split_idx:]
    
    # Save
    train_path = os.path.join(args.output, 'training_data.jsonl')
    val_path = os.path.join(args.output, 'validation_data.jsonl')
    
    save_jsonl(train, train_path)
    save_jsonl(val, val_path)
    
    print(f"\nSaved:")
    print(f"  Training: {train_path} ({len(train)} examples)")
    print(f"  Validation: {val_path} ({len(val)} examples)")


if __name__ == "__main__":
    main()