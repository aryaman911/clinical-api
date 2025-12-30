"""
OpenAI Fine-Tuning Script for Clinical Component Identification
This script handles the complete fine-tuning workflow

Usage:
    python fine_tune.py                    # Full workflow
    python fine_tune.py --upload-only      # Only upload files
    python fine_tune.py --status JOB_ID    # Check job status
    python fine_tune.py --list             # List all jobs
"""

import os
import json
import time
import argparse
from pathlib import Path
from openai import OpenAI

# Initialize client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Configuration
CONFIG = {
    "base_model": "gpt-4o-mini-2024-07-18",  # Model to fine-tune
    "training_file": "data/training_data.jsonl",
    "validation_file": "data/validation_data.jsonl",
    "suffix": "clinical-components",  # Custom model suffix
    "hyperparameters": {
        "n_epochs": 3,  # Number of training epochs (auto if not set)
        # "batch_size": "auto",
        # "learning_rate_multiplier": "auto"
    }
}


def validate_api_key():
    """Check if API key is set"""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("\nSet it with:")
        print('  export OPENAI_API_KEY="sk-your-key-here"')
        return False
    
    if not api_key.startswith("sk-"):
        print("⚠️  Warning: API key doesn't start with 'sk-'")
    
    return True


def validate_training_file(file_path: str) -> dict:
    """Validate JSONL training file format"""
    print(f"\n📋 Validating: {file_path}")
    
    if not os.path.exists(file_path):
        return {"valid": False, "error": f"File not found: {file_path}"}
    
    errors = []
    warnings = []
    examples = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            try:
                data = json.loads(line)
                examples.append(data)
                
                # Check structure
                if "messages" not in data:
                    errors.append(f"Line {i}: Missing 'messages' key")
                    continue
                
                messages = data["messages"]
                
                # Check message count
                if len(messages) < 2:
                    errors.append(f"Line {i}: Need at least 2 messages (user + assistant)")
                
                # Check roles
                roles = [m.get("role") for m in messages]
                if "assistant" not in roles:
                    errors.append(f"Line {i}: Missing assistant message")
                
                # Check content
                for j, msg in enumerate(messages):
                    if not msg.get("content"):
                        warnings.append(f"Line {i}, message {j}: Empty content")
                
            except json.JSONDecodeError as e:
                errors.append(f"Line {i}: Invalid JSON - {e}")
    
    # Summary
    result = {
        "valid": len(errors) == 0,
        "total_examples": len(examples),
        "errors": errors[:10],  # First 10 errors
        "warnings": warnings[:5],
        "error_count": len(errors),
        "warning_count": len(warnings)
    }
    
    if result["valid"]:
        print(f"  ✅ Valid - {result['total_examples']} examples")
    else:
        print(f"  ❌ Invalid - {result['error_count']} errors")
        for err in result["errors"]:
            print(f"     {err}")
    
    return result


def upload_file(file_path: str, purpose: str = "fine-tune") -> str:
    """Upload a file to OpenAI"""
    print(f"\n📤 Uploading: {file_path}")
    
    with open(file_path, "rb") as f:
        response = client.files.create(
            file=f,
            purpose=purpose
        )
    
    print(f"  ✅ Uploaded: {response.id}")
    print(f"     Filename: {response.filename}")
    print(f"     Size: {response.bytes:,} bytes")
    print(f"     Status: {response.status}")
    
    return response.id


def create_fine_tuning_job(training_file_id: str, validation_file_id: str = None) -> str:
    """Create a fine-tuning job"""
    print("\n🚀 Creating fine-tuning job...")
    
    job_params = {
        "training_file": training_file_id,
        "model": CONFIG["base_model"],
        "suffix": CONFIG["suffix"],
    }
    
    if validation_file_id:
        job_params["validation_file"] = validation_file_id
    
    if CONFIG.get("hyperparameters"):
        job_params["hyperparameters"] = CONFIG["hyperparameters"]
    
    response = client.fine_tuning.jobs.create(**job_params)
    
    print(f"  ✅ Job created: {response.id}")
    print(f"     Model: {response.model}")
    print(f"     Status: {response.status}")
    
    return response.id


def check_job_status(job_id: str) -> dict:
    """Check the status of a fine-tuning job"""
    job = client.fine_tuning.jobs.retrieve(job_id)
    
    status = {
        "id": job.id,
        "status": job.status,
        "model": job.model,
        "fine_tuned_model": job.fine_tuned_model,
        "created_at": job.created_at,
        "finished_at": job.finished_at,
        "trained_tokens": job.trained_tokens,
        "error": job.error
    }
    
    return status


def wait_for_completion(job_id: str, poll_interval: int = 60):
    """Wait for fine-tuning job to complete"""
    print(f"\n⏳ Waiting for job {job_id} to complete...")
    print(f"   (Checking every {poll_interval} seconds)\n")
    
    while True:
        status = check_job_status(job_id)
        current_status = status["status"]
        
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] Status: {current_status}")
        
        if current_status == "succeeded":
            print(f"\n🎉 Fine-tuning completed!")
            print(f"   Fine-tuned model: {status['fine_tuned_model']}")
            print(f"   Trained tokens: {status['trained_tokens']:,}")
            return status
        
        elif current_status == "failed":
            print(f"\n❌ Fine-tuning failed!")
            print(f"   Error: {status['error']}")
            return status
        
        elif current_status == "cancelled":
            print(f"\n⚠️ Fine-tuning was cancelled")
            return status
        
        # Still running
        time.sleep(poll_interval)


def list_fine_tuning_jobs(limit: int = 10):
    """List recent fine-tuning jobs"""
    print(f"\n📋 Recent fine-tuning jobs (last {limit}):\n")
    
    jobs = client.fine_tuning.jobs.list(limit=limit)
    
    for job in jobs.data:
        status_emoji = {
            "succeeded": "✅",
            "failed": "❌",
            "cancelled": "⚠️",
            "running": "🔄",
            "queued": "⏳"
        }.get(job.status, "❓")
        
        print(f"{status_emoji} {job.id}")
        print(f"   Model: {job.model}")
        print(f"   Status: {job.status}")
        if job.fine_tuned_model:
            print(f"   Fine-tuned: {job.fine_tuned_model}")
        print()


def list_uploaded_files():
    """List uploaded files"""
    print("\n📁 Uploaded files:\n")
    
    files = client.files.list(purpose="fine-tune")
    
    for f in files.data:
        print(f"  {f.id}")
        print(f"     Filename: {f.filename}")
        print(f"     Size: {f.bytes:,} bytes")
        print(f"     Created: {f.created_at}")
        print()


def test_fine_tuned_model(model_id: str, test_text: str = None):
    """Test the fine-tuned model"""
    if not test_text:
        test_text = """This study will be conducted in accordance with Good Clinical Practice (GCP) guidelines. 
        The primary endpoint is overall survival, defined as time from randomization to death. 
        Inclusion criteria include age ≥18 years and ECOG status 0-1."""
    
    print(f"\n🧪 Testing model: {model_id}\n")
    print(f"Input text:\n{test_text[:200]}...\n")
    
    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {
                "role": "system",
                "content": "Identify reusable components in clinical documents. Return JSON array."
            },
            {
                "role": "user",
                "content": f"Identify components:\n\n{test_text}"
            }
        ],
        temperature=0.0,
        max_tokens=2000
    )
    
    result = response.choices[0].message.content
    print(f"Model output:\n{result}")
    
    return result


def run_full_workflow():
    """Run the complete fine-tuning workflow"""
    print("=" * 60)
    print("🏥 Clinical Component Identifier - Fine-Tuning Workflow")
    print("=" * 60)
    
    # Step 1: Validate API key
    if not validate_api_key():
        return
    
    # Step 2: Validate training data
    train_result = validate_training_file(CONFIG["training_file"])
    if not train_result["valid"]:
        print("\n❌ Training file validation failed. Please fix errors.")
        return
    
    val_result = None
    if os.path.exists(CONFIG["validation_file"]):
        val_result = validate_training_file(CONFIG["validation_file"])
    
    # Step 3: Upload files
    print("\n" + "=" * 60)
    print("📤 Uploading Files")
    print("=" * 60)
    
    training_file_id = upload_file(CONFIG["training_file"])
    
    validation_file_id = None
    if val_result and val_result["valid"]:
        validation_file_id = upload_file(CONFIG["validation_file"])
    
    # Wait for files to be processed
    print("\n⏳ Waiting for files to be processed...")
    time.sleep(10)
    
    # Step 4: Create fine-tuning job
    print("\n" + "=" * 60)
    print("🚀 Starting Fine-Tuning")
    print("=" * 60)
    
    job_id = create_fine_tuning_job(training_file_id, validation_file_id)
    
    # Step 5: Wait for completion
    print("\n" + "=" * 60)
    print("⏳ Training in Progress")
    print("=" * 60)
    
    final_status = wait_for_completion(job_id)
    
    # Step 6: Save model ID
    if final_status["status"] == "succeeded":
        model_id = final_status["fine_tuned_model"]
        
        # Save to file
        with open("fine_tuned_model.txt", "w") as f:
            f.write(model_id)
        
        print("\n" + "=" * 60)
        print("🎉 Fine-Tuning Complete!")
        print("=" * 60)
        print(f"\nYour fine-tuned model ID: {model_id}")
        print("\nNext steps:")
        print(f"  1. Set environment variable:")
        print(f'     export FINE_TUNED_MODEL="{model_id}"')
        print(f"  2. Update Render environment variables")
        print(f"  3. Test with: python fine_tune.py --test {model_id}")
        
        # Optional: Test the model
        print("\n" + "=" * 60)
        print("🧪 Testing Fine-Tuned Model")
        print("=" * 60)
        test_fine_tuned_model(model_id)


def main():
    parser = argparse.ArgumentParser(description='OpenAI Fine-Tuning for Clinical Components')
    parser.add_argument('--upload-only', action='store_true', help='Only upload files')
    parser.add_argument('--status', type=str, help='Check status of a job')
    parser.add_argument('--list', action='store_true', help='List fine-tuning jobs')
    parser.add_argument('--files', action='store_true', help='List uploaded files')
    parser.add_argument('--test', type=str, help='Test a fine-tuned model')
    parser.add_argument('--cancel', type=str, help='Cancel a fine-tuning job')
    
    args = parser.parse_args()
    
    if not validate_api_key():
        return
    
    if args.list:
        list_fine_tuning_jobs()
    
    elif args.files:
        list_uploaded_files()
    
    elif args.status:
        status = check_job_status(args.status)
        print(json.dumps(status, indent=2, default=str))
    
    elif args.test:
        test_fine_tuned_model(args.test)
    
    elif args.cancel:
        client.fine_tuning.jobs.cancel(args.cancel)
        print(f"Cancelled job: {args.cancel}")
    
    elif args.upload_only:
        training_file_id = upload_file(CONFIG["training_file"])
        if os.path.exists(CONFIG["validation_file"]):
            upload_file(CONFIG["validation_file"])
        print(f"\nTraining file ID: {training_file_id}")
    
    else:
        run_full_workflow()


if __name__ == "__main__":
    main()
