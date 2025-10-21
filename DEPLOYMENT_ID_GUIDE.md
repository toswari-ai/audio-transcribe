# Deployment ID Configuration Guide

This guide explains how to configure and use `deployment_id` for dedicated deployed models in the Audio Transcription App.

## Overview

Deployment IDs allow you to use dedicated deployed models on Clarifai, which provide:
- **Better Performance**: Guaranteed compute resources
- **Custom Models**: Access to fine-tuned or custom model versions
- **Enterprise Features**: Enhanced reliability and dedicated infrastructure

## Configuration Options

### Option 1: Per-Model Configuration (config.py)

Add `deployment_id` directly to specific models in `config.py`:

```python
"OpenAI Whisper Large V3": {
    "model_id": "whisper-large-v3",
    "user_id": "openai",
    "app_id": "transcription",
    "description": "Latest Whisper v3...",
    "status": "working",
    "deployment_id": "deploy-whisper-large-v3-cr4h"  # Your deployment ID
}
```

### Option 2: Global Environment Variable (.env)

Set `CLARIFAI_DEPLOYMENT_ID` in your `.env` file to override all models:

```properties
# Optional: For dedicated deployed models (overrides model-specific deployment_id)
CLARIFAI_DEPLOYMENT_ID=deploy-whisper-large-v3-cr4h
```

### Option 3: Runtime Environment Variable

Set the environment variable when running the application:

```bash
CLARIFAI_DEPLOYMENT_ID=your-deployment-id python3 app.py
```

## Priority Order

The deployment ID is resolved in this order:
1. **Environment Variable** (`CLARIFAI_DEPLOYMENT_ID`) - **Highest Priority**
2. **Model-Specific Config** (in `config.py`) - **Fallback**
3. **No Deployment ID** (uses standard shared models) - **Default**

## How It Works

When a deployment ID is configured, the Clarifai API request includes it:

```python
# Standard model request
PostModelOutputsRequest(
    user_app_id=user_app_id,
    model_id="whisper-large-v3",
    inputs=[input_obj]
)

# Deployed model request (with deployment_id)
PostModelOutputsRequest(
    user_app_id=user_app_id,
    model_id="whisper-large-v3",
    deployment_id="deploy-whisper-large-v3-cr4h",  # 🎯 Added for dedicated deployment
    inputs=[input_obj]
)
```

## Usage Examples

### Example 1: Whisper V3 with Dedicated Deployment

Current configuration includes deployment ID for Whisper Large V3:

```python
model_info = config.get_model_info("OpenAI Whisper Large V3")
print(model_info["deployment_id"])  # deploy-whisper-large-v3-cr4h
```

### Example 2: Testing Different Deployments

```bash
# Test with production deployment
CLARIFAI_DEPLOYMENT_ID=prod-whisper-v3 python3 test_whisper_v3.py

# Test with staging deployment  
CLARIFAI_DEPLOYMENT_ID=staging-whisper-v3 python3 test_whisper_v3.py

# Test without deployment (standard shared model)
unset CLARIFAI_DEPLOYMENT_ID
python3 test_whisper_v3.py
```

## Getting Deployment IDs

To get deployment IDs for your models:

1. Visit your [Clarifai Dashboard](https://clarifai.com/apps)
2. Navigate to your app and model
3. Go to the "Deployments" section
4. Create or view existing deployments
5. Copy the deployment ID (format: `deploy-model-name-xxxx`)

## Troubleshooting

### Common Issues

1. **Invalid Deployment ID**
   ```
   Error: Deployment not found: deploy-invalid-xxxx
   ```
   - Verify deployment ID exists and is active
   - Check spelling and format

2. **Deployment Not Ready**
   ```
   Error: Deployment is starting up, please retry in a few seconds
   ```
   - Wait for deployment to complete initialization
   - Retry after 30-60 seconds

3. **Permission Issues**
   ```
   Error: Access denied to deployment
   ```
   - Verify your PAT has access to the deployment
   - Check if deployment belongs to your account/organization

### Testing Deployment Configuration

Use the test script to verify your configuration:

```bash
python3 test_deployment_id.py
```

This will show:
- Current deployment ID configuration
- Environment variable status
- Expected API request structure
- Configuration options summary

## Benefits of Dedicated Deployments

- **🚀 Performance**: Faster inference with dedicated compute
- **📊 Reliability**: Guaranteed availability and SLA
- **🔒 Isolation**: Your models run in isolated environments
- **📈 Scalability**: Auto-scaling based on your usage
- **🎯 Customization**: Deploy fine-tuned or custom models

## Cost Considerations

- Dedicated deployments typically cost more than shared models
- Check Clarifai pricing for deployment-specific rates
- Monitor usage through the Clarifai dashboard
- Consider using shared models for development/testing

---

**Note**: Deployment IDs are optional. If not configured, the app will use standard shared models which work perfectly for most use cases.