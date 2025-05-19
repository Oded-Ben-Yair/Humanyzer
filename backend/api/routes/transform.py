"""
API routes for text transformation.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
from backend.services.ai.bedrock_service import BedrockService, ModelType

router = APIRouter()
logger = logging.getLogger(__name__)

class TransformRequest(BaseModel):
    """Request model for text transformation."""
    text: str
    style: str = "casual"
    creativity: float = 0.7


class TransformResponse(BaseModel):
    """Response model for text transformation."""
    original_text: str
    transformed_text: str
    metadata: Dict[str, Any] = {}


@router.post("/transform", response_model=TransformResponse)
async def transform_text(
    request: TransformRequest,
    background_tasks: BackgroundTasks
):
    """Transform text to make it more human-like."""
    try:
        # Initialize the Bedrock service
        bedrock_service = BedrockService()
        
        # Transform the text
        transformed_text = bedrock_service.humanize_text(
            text=request.text,
            style=request.style,
            creativity=request.creativity
        )
        
        # Add background task to log usage (could be extended to store in database)
        background_tasks.add_task(
            log_transformation_usage,
            len(request.text),
            len(transformed_text)
        )
        
        return TransformResponse(
            original_text=request.text,
            transformed_text=transformed_text,
            metadata={
                "style": request.style,
                "creativity": request.creativity
            }
        )
    
    except Exception as e:
        logger.error(f"Error transforming text: {e}")
        raise HTTPException(status_code=500, detail=f"Error transforming text: {str(e)}")


def log_transformation_usage(input_length: int, output_length: int):
    """Log transformation usage for analytics."""
    logger.info(f"Transformation usage: input_length={input_length}, output_length={output_length}")
