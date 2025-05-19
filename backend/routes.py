
"""
API routes for the AI Content Humanizer service.
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import Dict, Any, Optional, AsyncGenerator
import uuid
import json
import asyncio
import time
from datetime import datetime
from backend.auth.dependencies import get_current_user

from backend.models.api_models import (
    HumanizeRequest, 
    HumanizeResponse, 
    AnalyzeRequest, 
    AnalyzeResponse
)
from backend.handlers.input_handler import InputHandler
from backend.handlers.output_handler import OutputHandler
from backend.core.pattern_analyzer import PatternAnalyzer
from backend.core.transformation_engine import TransformationEngine
# Commented out for now as we don't need vector store for the MVP
# from backend.db.vector import get_vector_store

# Create router
router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint to verify the API is running."""
    return {"status": "ok", "version": "1.0.0"}

# Initialize components
input_handler = InputHandler()
output_handler = OutputHandler()
pattern_analyzer = PatternAnalyzer()
transformation_engine = TransformationEngine()

# In-memory cache for storing transformation results
# In a production system, this would be replaced with a proper database
transformation_cache = {}

@router.post("/humanize", response_model=HumanizeResponse)
async def humanize(request: HumanizeRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Transform AI-generated text to sound more human-like.
    
    - text: The AI-generated text to humanize
    - style: The desired tone (casual, professional, creative)
    """
    try:
        # Import token counter
        from utils.token_counter import token_counter
        from app.db.subscriptions import check_subscription_limit
        
        # Check subscription limits
        character_count = len(request.text)
        limit_check = await check_subscription_limit(current_user["id"], character_count)
        
        if not limit_check.get("allowed", False):
            raise HTTPException(
                status_code=402,  # Payment Required
                detail={
                    "message": "Subscription limit reached",
                    "limit_info": limit_check
                }
            )
        
        # Start tracking token usage
        start_time = time.time()
        
        # Validate and preprocess input
        processed_input = input_handler.validate_and_preprocess(request.text, request.style)
        
        # Import chunking utility
        from utils.chunking import chunk_text, merge_chunk_results
        
        # For large texts, use chunking
        max_chunk_size = 4000
        if len(processed_input["text"]) > max_chunk_size:
            # Split text into chunks for more efficient processing
            chunks = chunk_text(processed_input["text"], max_chunk_size, 200)
            
            # Process each chunk
            results = []
            for chunk in chunks:
                # Analyze chunk for AI patterns
                chunk_analysis = pattern_analyzer.analyze(chunk)
                
                # Import coordinator agent here to avoid circular imports
                from agents.coordinator_agent import CoordinatorAgent
                from agents.style_agent import StyleAgent
                from agents.restructuring_agent import RestructuringAgent
                from agents.vocabulary_agent import VocabularyAgent
                from agents.validator_agent import ValidatorAgent
                
                # Create coordinator agent and register specialist agents
                coordinator = CoordinatorAgent()
                coordinator.register_agents([
                    StyleAgent(),
                    RestructuringAgent(),
                    VocabularyAgent(),
                    ValidatorAgent()
                ])
                
                # Transform chunk using the coordinator agent
                chunk_result = coordinator.transform(
                    chunk, 
                    request.style,
                    request.profile_id
                )
                
                results.append(chunk_result)
            
            # Merge results
            humanized_chunks = [r["transformed_text"] for r in results]
            humanized_text = merge_chunk_results(humanized_chunks, processed_input["text"])
            
            # Combine analyses
            combined_analysis = {
                "is_likely_ai": any(r["analysis"].get("is_likely_ai", False) for r in results if "analysis" in r),
                "patterns_found": [],
                "metrics": {}
            }
            
            # Merge patterns and metrics
            pattern_types = set()
            for result in results:
                if "analysis" in result and "patterns_found" in result["analysis"]:
                    for pattern in result["analysis"]["patterns_found"]:
                        if pattern["type"] not in pattern_types:
                            pattern_types.add(pattern["type"])
                            combined_analysis["patterns_found"].append(pattern)
            
            # Use the last result's transformation_id
            transformation_id = results[-1].get("transformation_id") if results else None
            
            analysis = combined_analysis
        else:
            # For smaller texts, process normally
            # Analyze text for AI patterns
            analysis = pattern_analyzer.analyze(processed_input["text"])
            
            # Import coordinator agent here to avoid circular imports
            from agents.coordinator_agent import CoordinatorAgent
            from agents.style_agent import StyleAgent
            from agents.restructuring_agent import RestructuringAgent
            from agents.vocabulary_agent import VocabularyAgent
            from agents.validator_agent import ValidatorAgent
            from utils.context_manager import ContextManager
            
            # Create context manager to optimize token usage
            context_manager = ContextManager()
            
            # Create coordinator agent and register specialist agents
            coordinator = CoordinatorAgent()
            coordinator.register_agents([
                StyleAgent(),
                RestructuringAgent(),
                VocabularyAgent(),
                ValidatorAgent()
            ])
            
            # Transform text using the coordinator agent with profile_id
            result = coordinator.transform(
                processed_input["text"], 
                request.style,
                request.profile_id
            )
            
            humanized_text = result["transformed_text"]
            transformation_id = result.get("transformation_id")
        
        # Calculate token usage
        input_tokens = token_counter.count_tokens(request.text)
        output_tokens = token_counter.count_tokens(humanized_text)
        
        # Log token usage
        token_counter.log_request(
            component="api_humanize",
            input_text=request.text,
            output_text=humanized_text,
            metadata={
                "style": request.style,
                "profile_id": request.profile_id,
                "word_count": processed_input["word_count"]
            }
        )
        
        # Format output
        output = output_handler.format_output(
            original_text=request.text,
            transformed_text=humanized_text,
            analysis=analysis,
            metadata={
                "style": request.style,
                "word_count": processed_input["word_count"],
                "sentence_count": processed_input["sentence_count"],
                "transformation_id": transformation_id,
                "transformation_time": time.time() - start_time,
                "token_usage": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens
                }
            }
        )
        
        return output
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.post("/humanize/stream")
async def humanize_stream(request: HumanizeRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Transform AI-generated text to sound more human-like with streaming response.
    
    - text: The AI-generated text to humanize
    - style: The desired tone (casual, professional, creative)
    
    Returns a streaming response with progress updates and the final result.
    """
    async def generate_stream():
        try:
            # Import token counter and subscription check
            from utils.token_counter import token_counter
            from app.db.subscriptions import check_subscription_limit
            
            # Check subscription limits
            character_count = len(request.text)
            limit_check = await check_subscription_limit(current_user["id"], character_count)
            
            if not limit_check.get("allowed", False):
                yield json.dumps({
                    "status": "error",
                    "error": "Subscription limit reached",
                    "limit_info": limit_check
                }) + "\n"
                return
            
            # Start tracking token usage
            start_time = time.time()
            
            # Send initial progress update
            yield json.dumps({
                "status": "processing",
                "progress": 0,
                "step": "Starting transformation"
            }) + "\n"
            
            # Validate and preprocess input
            processed_input = input_handler.validate_and_preprocess(request.text, request.style)
            
            yield json.dumps({
                "status": "processing",
                "progress": 10,
                "step": "Input validated"
            }) + "\n"
            
            # Import chunking utility
            from utils.chunking import chunk_text, merge_chunk_results
            
            # For large texts, use chunking
            max_chunk_size = 4000
            if len(processed_input["text"]) > max_chunk_size:
                # Split text into chunks for more efficient processing
                chunks = chunk_text(processed_input["text"], max_chunk_size, 200)
                
                yield json.dumps({
                    "status": "processing",
                    "progress": 15,
                    "step": f"Text split into {len(chunks)} chunks for efficient processing"
                }) + "\n"
                
                # Process each chunk
                results = []
                for i, chunk in enumerate(chunks):
                    # Update progress
                    chunk_progress = 15 + (65 * (i / len(chunks)))
                    yield json.dumps({
                        "status": "processing",
                        "progress": int(chunk_progress),
                        "step": f"Processing chunk {i+1} of {len(chunks)}"
                    }) + "\n"
                    
                    # Analyze chunk for AI patterns
                    chunk_analysis = pattern_analyzer.analyze(chunk)
                    
                    # Import coordinator agent here to avoid circular imports
                    from agents.coordinator_agent import CoordinatorAgent
                    from agents.style_agent import StyleAgent
                    from agents.restructuring_agent import RestructuringAgent
                    from agents.vocabulary_agent import VocabularyAgent
                    from agents.validator_agent import ValidatorAgent
                    from utils.context_manager import ContextManager
                    
                    # Create context manager to optimize token usage
                    context_manager = ContextManager()
                    
                    # Create coordinator agent and register specialist agents
                    coordinator = CoordinatorAgent()
                    coordinator.register_agents([
                        StyleAgent(),
                        RestructuringAgent(),
                        VocabularyAgent(),
                        ValidatorAgent()
                    ])
                    
                    # Transform chunk using the coordinator agent
                    chunk_result = await asyncio.to_thread(
                        coordinator.transform,
                        chunk, 
                        request.style,
                        request.profile_id
                    )
                    
                    results.append(chunk_result)
                
                yield json.dumps({
                    "status": "processing",
                    "progress": 80,
                    "step": "Merging processed chunks"
                }) + "\n"
                
                # Merge results
                humanized_chunks = [r["transformed_text"] for r in results]
                humanized_text = merge_chunk_results(humanized_chunks, processed_input["text"])
                
                # Combine analyses
                combined_analysis = {
                    "is_likely_ai": any(r["analysis"].get("is_likely_ai", False) for r in results if "analysis" in r),
                    "patterns_found": [],
                    "metrics": {}
                }
                
                # Merge patterns and metrics
                pattern_types = set()
                for result in results:
                    if "analysis" in result and "patterns_found" in result["analysis"]:
                        for pattern in result["analysis"]["patterns_found"]:
                            if pattern["type"] not in pattern_types:
                                pattern_types.add(pattern["type"])
                                combined_analysis["patterns_found"].append(pattern)
                
                # Use the last result's transformation_id
                transformation_id = results[-1].get("transformation_id") if results else None
                
                analysis = combined_analysis
            else:
                # For smaller texts, process normally
                # Analyze text for AI patterns
                analysis = pattern_analyzer.analyze(processed_input["text"])
                
                yield json.dumps({
                    "status": "processing",
                    "progress": 20,
                    "step": "Analysis complete",
                    "is_likely_ai": analysis.get("is_likely_ai", False)
                }) + "\n"
                
                # Import coordinator agent here to avoid circular imports
                from agents.coordinator_agent import CoordinatorAgent
                from agents.style_agent import StyleAgent
                from agents.restructuring_agent import RestructuringAgent
                from agents.vocabulary_agent import VocabularyAgent
                from agents.validator_agent import ValidatorAgent
                from utils.context_manager import ContextManager
                
                yield json.dumps({
                    "status": "processing",
                    "progress": 30,
                    "step": "Initializing transformation agents"
                }) + "\n"
                
                # Create context manager to optimize token usage
                context_manager = ContextManager()
                
                # Create coordinator agent and register specialist agents
                coordinator = CoordinatorAgent()
                coordinator.register_agents([
                    StyleAgent(),
                    RestructuringAgent(),
                    VocabularyAgent(),
                    ValidatorAgent()
                ])
                
                yield json.dumps({
                    "status": "processing",
                    "progress": 40,
                    "step": "Applying style transformations"
                }) + "\n"
                
                # Transform text using the coordinator agent with profile_id
                # We'll simulate progress updates during the transformation
                transformation_start = time.time()
                
                # Start the transformation in a separate task
                transformation_task = asyncio.create_task(
                    asyncio.to_thread(
                        coordinator.transform,
                        processed_input["text"],
                        request.style,
                        request.profile_id
                    )
                )
                
                # Send progress updates while waiting for the transformation
                progress = 40
                while not transformation_task.done():
                    await asyncio.sleep(0.5)
                    if progress < 80:
                        progress += 2
                        current_step = "Applying transformations"
                        if progress > 60:
                            current_step = "Refining text"
                        if progress > 70:
                            current_step = "Validating transformation"
                        
                        yield json.dumps({
                            "status": "processing",
                            "progress": progress,
                            "step": current_step
                        }) + "\n"
                
                # Get the transformation result
                result = await transformation_task
                
                humanized_text = result["transformed_text"]
                transformation_id = result.get("transformation_id")
            
            yield json.dumps({
                "status": "processing",
                "progress": 90,
                "step": "Finalizing transformation"
            }) + "\n"
            
            # Calculate token usage
            input_tokens = token_counter.count_tokens(request.text)
            output_tokens = token_counter.count_tokens(humanized_text)
            
            # Log token usage
            token_counter.log_request(
                component="api_humanize_stream",
                input_text=request.text,
                output_text=humanized_text,
                metadata={
                    "style": request.style,
                    "profile_id": request.profile_id,
                    "word_count": processed_input["word_count"]
                }
            )
            
            # Format output
            output = output_handler.format_output(
                original_text=request.text,
                transformed_text=humanized_text,
                analysis=analysis,
                metadata={
                    "style": request.style,
                    "word_count": processed_input["word_count"],
                    "sentence_count": processed_input["sentence_count"],
                    "transformation_id": transformation_id,
                    "transformation_time": time.time() - start_time,
                    "token_usage": {
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "total_tokens": input_tokens + output_tokens
                    }
                }
            )
            
            # Send final result
            yield json.dumps({
                "status": "completed",
                "progress": 100,
                "step": "Transformation complete",
                "result": output
            }) + "\n"
            
        except ValueError as e:
            yield json.dumps({
                "status": "error",
                "error": str(e)
            }) + "\n"
        except Exception as e:
            yield json.dumps({
                "status": "error",
                "error": f"An error occurred: {str(e)}"
            }) + "\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="application/x-ndjson"
    )

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    """
    Analyze text for AI-generated patterns without transforming it.
    
    - text: The text to analyze
    """
    try:
        # Validate and preprocess input
        processed_input = input_handler.validate_and_preprocess(request.text)
        
        # Analyze text for AI patterns
        analysis = pattern_analyzer.analyze(processed_input["text"])
        
        return {
            "text": request.text,
            "analysis": analysis,
            "timestamp": datetime.now()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.post("/humanize/async", status_code=202)
async def humanize_async(request: HumanizeRequest, background_tasks: BackgroundTasks, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Asynchronously transform AI-generated text to sound more human-like.
    Returns a job ID that can be used to retrieve the results later.
    
    - text: The AI-generated text to humanize
    - style: The desired tone (casual, professional, creative)
    """
    try:
        # Check subscription limits
        from app.db.subscriptions import check_subscription_limit
        
        character_count = len(request.text)
        limit_check = await check_subscription_limit(current_user["id"], character_count)
        
        if not limit_check.get("allowed", False):
            raise HTTPException(
                status_code=402,  # Payment Required
                detail={
                    "message": "Subscription limit reached",
                    "limit_info": limit_check
                }
            )
        
        # Validate input
        input_handler.validate_and_preprocess(request.text, request.style)
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Store initial job status
        transformation_cache[job_id] = {
            "status": "processing",
            "created_at": datetime.now().isoformat(),
            "request": {
                "text": request.text,
                "style": request.style
            }
        }
        
        # Add task to background queue
        background_tasks.add_task(
            process_humanization_job,
            job_id,
            request.text,
            request.style,
            request.profile_id,
            current_user["id"]
        )
        
        return {"job_id": job_id, "status": "processing"}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.get("/humanize/status/{job_id}")
async def get_humanize_status(job_id: str):
    """
    Get the status of an asynchronous humanization job.
    
    - job_id: The ID of the job to check
    """
    if job_id not in transformation_cache:
        raise HTTPException(status_code=404, detail=f"Job ID {job_id} not found")
    
    job = transformation_cache[job_id]
    
    # If job is complete, include the result
    if job["status"] == "completed":
        return {
            "job_id": job_id,
            "status": job["status"],
            "created_at": job["created_at"],
            "completed_at": job["completed_at"],
            "result": job["result"]
        }
    
    # If job is still processing or failed
    return {
        "job_id": job_id,
        "status": job["status"],
        "created_at": job["created_at"]
    }

def process_humanization_job(job_id: str, text: str, style: str, profile_id: Optional[str] = None, user_id: Optional[str] = None):
    """
    Process a humanization job in the background.
    
    Args:
        job_id: The ID of the job
        text: The text to humanize
        style: The style to use
        profile_id: ID of the style profile to use (optional)
        user_id: ID of the user who submitted the job (optional)
    """
    try:
        # Validate and preprocess input
        processed_input = input_handler.validate_and_preprocess(text, style)
        
        # Analyze text for AI patterns
        analysis = pattern_analyzer.analyze(processed_input["text"])
        
        # Import coordinator agent here to avoid circular imports
        from agents.coordinator_agent import CoordinatorAgent
        from agents.style_agent import StyleAgent
        from agents.restructuring_agent import RestructuringAgent
        from agents.vocabulary_agent import VocabularyAgent
        from agents.validator_agent import ValidatorAgent
        
        # Create coordinator agent and register specialist agents
        coordinator = CoordinatorAgent()
        coordinator.register_agents([
            StyleAgent(),
            RestructuringAgent(),
            VocabularyAgent(),
            ValidatorAgent()
        ])
        
        # Transform text using the coordinator agent with profile_id
        result = coordinator.transform(
            processed_input["text"], 
            style,
            profile_id
        )
        
        humanized_text = result["transformed_text"]
        
        # Format output
        output = output_handler.format_output(
            original_text=text,
            transformed_text=humanized_text,
            analysis=analysis,
            metadata={
                "style": style,
                "word_count": processed_input["word_count"],
                "sentence_count": processed_input["sentence_count"]
            }
        )
        
        # Update job status
        transformation_cache[job_id] = {
            "status": "completed",
            "created_at": transformation_cache[job_id]["created_at"],
            "completed_at": datetime.now().isoformat(),
            "result": output
        }
        
    except Exception as e:
        # Update job status with error
        transformation_cache[job_id] = {
            "status": "failed",
            "created_at": transformation_cache[job_id]["created_at"],
            "error": str(e)
        }

@router.get("/history")
async def get_transformation_history():
    """History of transformations."""
    # For the MVP, we'll return the last 10 transformations from the in-memory cache
    history_items = []
    
    for job_id, job in list(transformation_cache.items())[-10:]:
        if job["status"] == "completed":
            history_items.append({
                "id": job_id,
                "created_at": job["created_at"],
                "completed_at": job.get("completed_at"),
                "original_text_preview": job["request"]["text"][:100] + "..." if len(job["request"]["text"]) > 100 else job["request"]["text"],
                "style": job["request"]["style"]
            })
    
    return {"history": history_items, "count": len(history_items)}
