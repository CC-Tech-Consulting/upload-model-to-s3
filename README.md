# 🚀 Upload Model to S3

This guide walks you through setting up a Python environment and running a script to upload a model to AWS S3.

### 1. Create a Python Virtual Environment

First, set up a dedicated virtual environment for your project:

```bash
mkdir llm
cd llm
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

Next, install the required Python packages:

```bash
pip install boto3 huggingface_hub
```

### 3. Run the Upload Script

Now, execute the script to upload your model to S3:

```bash
python main.py
```

🎉 You're all set! Your model should now be uploaded to AWS S3.
