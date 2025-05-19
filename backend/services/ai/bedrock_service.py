"""
AWS Bedrock service for AI text transformation.
"""
import boto3
import json
import logging
from typing import Dict, Any, Optional, List
from enum import Enum

logger = logging.getLogger(__name__)

class ModelType(str, Enum):
    """Enum for model types."""
    COORDINATOR = "coordinator"
    STYLE = "style"
    RESTRUCTURING = "restructuring"
    VOCABULARY = "vocabulary"
    VALIDATOR = "validator"

class BedrockService:
    """Service for interacting with AWS Bedrock."""

    def __init__(self, region_name: str = "us-east-1"):
        """Initialize the Bedrock service."""
        self.bedrock_runtime = boto3.client(
            service_name="bedrock-runtime",
            region_name=region_name
        )
        # Model mapping from your guide
        self.model_mapping = {
            ModelType.COORDINATOR: "anthropic.claude-3-sonnet-20240229-v1:0", # Corrected model ID from guide
            ModelType.STYLE: "anthropic.claude-3-haiku-20240307-v1:0",
            ModelType.RESTRUCTURING: "anthropic.claude-3-sonnet-20240229-v1:0", # Corrected model ID from guide
            ModelType.VOCABULARY: "anthropic.claude-3-haiku-20240307-v1:0",
            ModelType.VALIDATOR: "anthropic.claude-3-sonnet-20240229-v1:0"  # Corrected model ID from guide
        }

    def transform_text(
        self,
        text: str,
        model_type: ModelType,
        style: str = "casual",
        creativity: float = 0.7,
        max_tokens: int = 4096
    ) -> str:
        """Transform text using the specified model type."""
        model_id = self.model_mapping[model_type]
        prompt = self._create_prompt(text, model_type, style)
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": creativity,
            "top_p": 0.9,
            "top_k": 250,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        try:
            response = self.bedrock_runtime.invoke_model(
                modelId=model_id,
                body=json.dumps(request_body),
                contentType="application/json",
                accept="application/json"
            )
            response_body = json.loads(response.get('body').read())
            transformed_text = response_body.get('content')[0].get('text')
            if transformed_text is None:
                logger.error(f"Transformed text is None. Response body: {response_body}")
                raise ValueError("Failed to get transformed text from Bedrock model response.")
            return transformed_text
        except Exception as e:
            logger.error(f"Error invoking Bedrock model {model_id}: {e}")
            raise

    def _create_prompt(self, text: str, model_type: ModelType, style: str) -> str:
        """Create a prompt based on the model type."""
        # Using simplified prompts based on guide structure for brevity here
        # Ensure you use the full, correct prompts from your guide (pages 6-7)
        if model_type == ModelType.COORDINATOR:
            return f"You are the coordinator agent... Original text: {text}\nTransformed text:"
        elif model_type == ModelType.STYLE:
            return f"Transform the AI-generated text to be human-like. Style: {style}... Original text: {text}\nTransformed text:"
        elif model_type == ModelType.RESTRUCTURING:
            return f"Restructure the AI-generated text... Original text: {text}\nRestructured text:"
        elif model_type == ModelType.VOCABULARY:
            return f"Enhance the vocabulary... Style: {style}... Original text: {text}\nEnhanced text:"
        elif model_type == ModelType.VALIDATOR:
            return f"Validate and finalize text... Text to validate: {text}\nFinalized text:"
        else:
            raise ValueError(f"Unknown model type: {model_type}")

    def humanize_text(self, text: str, style: str = "casual", creativity: float = 0.7) -> str:
        """Humanize text using a multi-agent approach."""
        try:
            styled_text = self.transform_text(text=text, model_type=ModelType.STYLE, style=style, creativity=creativity)
            restructured_text = self.transform_text(text=styled_text, model_type=ModelType.RESTRUCTURING, style=style, creativity=creativity)
            vocabulary_enhanced_text = self.transform_text(text=restructured_text, model_type=ModelType.VOCABULARY, style=style, creativity=creativity)
            final_text = self.transform_text(text=vocabulary_enhanced_text, model_type=ModelType.VALIDATOR, style=style, creativity=creativity)
            return final_text
        except Exception as e:
            logger.error(f"Error in multi-agent humanize_text: {e}. Falling back to coordinator.")
            # Fallback to simpler approach if the multi-agent approach fails
            return self.transform_text(
                text=text,
                model_type=ModelType.COORDINATOR, # Ensure this matches your enum
                style=style,
                creativity=creativity
            )
