"""
Mock UI utilities for testing the Humanyzer UI.
"""
import random
import time
import uuid
from datetime import datetime

def humanize_text(text, style, profile_id=None):
    """
    Mock function to simulate humanizing text.
    
    Args:
        text: Input text to humanize
        style: Writing style to apply
        profile_id: Optional profile ID to use
        
    Returns:
        Dictionary with humanized text and analysis
    """
    # Simulate processing time
    time.sleep(1)
    
    # Generate a slightly modified version of the input text
    words = text.split()
    if len(words) > 10:
        # Swap some words
        for i in range(min(5, len(words) // 10)):
            idx = random.randint(0, len(words) - 2)
            words[idx], words[idx + 1] = words[idx + 1], words[idx]
        
        # Replace some words
        replacements = {
            "important": "crucial",
            "very": "extremely",
            "good": "excellent",
            "bad": "poor",
            "big": "large",
            "small": "tiny",
            "is not": "isn't",
            "are not": "aren't",
            "will not": "won't",
            "cannot": "can't"
        }
        
        for i, word in enumerate(words):
            if word.lower() in replacements:
                words[i] = replacements[word.lower()]
    
    humanized = " ".join(words)
    
    # Generate mock analysis
    analysis = {
        "is_likely_ai": random.random() < 0.3,
        "metrics": {
            "avg_sentence_length": random.uniform(12, 25),
            "repeated_ngrams_count": random.randint(0, 5),
            "contraction_ratio": random.uniform(0.3, 0.8)
        },
        "patterns_found": []
    }
    
    # Add some patterns
    pattern_types = ["long_sentences", "repetitive_phrases", "formal_language", "lack_of_contractions"]
    severities = ["low", "medium", "high"]
    
    for _ in range(random.randint(1, 4)):
        pattern_type = random.choice(pattern_types)
        severity = random.choice(severities)
        
        pattern = {
            "type": pattern_type,
            "severity": severity,
            "description": f"Found {pattern_type} pattern with {severity} severity.",
            "examples": [f"Example {i+1} for {pattern_type}" for i in range(2)]
        }
        
        analysis["patterns_found"].append(pattern)
    
    return {
        "humanized": humanized,
        "analysis": analysis
    }

def humanize_text_async(text, style, profile_id=None):
    """
    Mock function to simulate asynchronous humanizing text.
    
    Args:
        text: Input text to humanize
        style: Writing style to apply
        profile_id: Optional profile ID to use
        
    Returns:
        Dictionary with job ID and status
    """
    job_id = str(uuid.uuid4())
    
    return {
        "job_id": job_id,
        "status": "processing"
    }

def get_humanize_status(job_id):
    """
    Mock function to get the status of an asynchronous humanization job.
    
    Args:
        job_id: Job ID to check
        
    Returns:
        Dictionary with job status and result
    """
    # Simulate a 50% chance of completion
    if random.random() < 0.5:
        return {
            "status": "processing"
        }
    else:
        # Generate mock result
        result = {
            "humanized": "This is a mock humanized text that would be the result of an asynchronous job.",
            "analysis": {
                "is_likely_ai": random.random() < 0.3,
                "metrics": {
                    "avg_sentence_length": random.uniform(12, 25),
                    "repeated_ngrams_count": random.randint(0, 5),
                    "contraction_ratio": random.uniform(0.3, 0.8)
                },
                "patterns_found": []
            }
        }
        
        # Add some patterns
        pattern_types = ["long_sentences", "repetitive_phrases", "formal_language", "lack_of_contractions"]
        severities = ["low", "medium", "high"]
        
        for _ in range(random.randint(1, 4)):
            pattern_type = random.choice(pattern_types)
            severity = random.choice(severities)
            
            pattern = {
                "type": pattern_type,
                "severity": severity,
                "description": f"Found {pattern_type} pattern with {severity} severity.",
                "examples": [f"Example {i+1} for {pattern_type}" for i in range(2)]
            }
            
            result["analysis"]["patterns_found"].append(pattern)
        
        return {
            "status": "completed",
            "result": result
        }

def analyze_text(text):
    """
    Mock function to analyze text for AI patterns.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Dictionary with analysis results
    """
    # Simulate processing time
    time.sleep(1)
    
    # Generate mock analysis
    analysis = {
        "is_likely_ai": random.random() < 0.7,
        "metrics": {
            "avg_sentence_length": random.uniform(12, 25),
            "repeated_ngrams_count": random.randint(0, 5),
            "contraction_ratio": random.uniform(0.3, 0.8)
        },
        "patterns_found": []
    }
    
    # Add some patterns
    pattern_types = ["long_sentences", "repetitive_phrases", "formal_language", "lack_of_contractions"]
    severities = ["low", "medium", "high"]
    
    for _ in range(random.randint(2, 6)):
        pattern_type = random.choice(pattern_types)
        severity = random.choice(severities)
        
        pattern = {
            "type": pattern_type,
            "severity": severity,
            "description": f"Found {pattern_type} pattern with {severity} severity.",
            "examples": [f"Example {i+1} for {pattern_type}" for i in range(2)]
        }
        
        analysis["patterns_found"].append(pattern)
    
    return analysis

def get_profiles():
    """
    Mock function to get user profiles.
    
    Returns:
        Dictionary with profiles
    """
    profiles = [
        {
            "id": "profile1",
            "name": "Professional Writer",
            "description": "Formal and professional writing style suitable for business documents.",
            "base_style": "professional",
            "tone": "formal",
            "formality_level": 8,
            "contraction_probability": 0.3,
            "conversational_element_frequency": 3,
            "sentence_variation_level": 7,
            "vocabulary_richness": 8,
            "custom_phrases": ["In conclusion", "Furthermore", "Nevertheless"],
            "avoid_phrases": ["like", "you know", "stuff"]
        },
        {
            "id": "profile2",
            "name": "Casual Blogger",
            "description": "Relaxed and conversational style for blog posts and social media.",
            "base_style": "casual",
            "tone": "friendly",
            "formality_level": 3,
            "contraction_probability": 0.8,
            "conversational_element_frequency": 8,
            "sentence_variation_level": 6,
            "vocabulary_richness": 5,
            "custom_phrases": ["By the way", "Honestly", "I think"],
            "avoid_phrases": ["therefore", "henceforth", "subsequently"]
        },
        {
            "id": "profile3",
            "name": "Creative Writer",
            "description": "Expressive and vivid style for creative writing and storytelling.",
            "base_style": "creative",
            "tone": "enthusiastic",
            "formality_level": 5,
            "contraction_probability": 0.6,
            "conversational_element_frequency": 6,
            "sentence_variation_level": 9,
            "vocabulary_richness": 9,
            "custom_phrases": ["Suddenly", "Meanwhile", "In that moment"],
            "avoid_phrases": ["in conclusion", "to summarize", "in essence"]
        }
    ]
    
    return {"profiles": profiles}

def create_profile(profile_data):
    """
    Mock function to create a new profile.
    
    Args:
        profile_data: Profile data to create
        
    Returns:
        Dictionary with created profile
    """
    profile_id = str(uuid.uuid4())
    
    return {
        "id": profile_id,
        "name": profile_data.get("name", "New Profile"),
        "created_at": datetime.now().isoformat()
    }

def update_profile(profile_id, profile_data):
    """
    Mock function to update a profile.
    
    Args:
        profile_id: Profile ID to update
        profile_data: Updated profile data
        
    Returns:
        Dictionary with updated profile
    """
    return {
        "id": profile_id,
        "name": profile_data.get("name", "Updated Profile"),
        "updated_at": datetime.now().isoformat()
    }

def delete_profile(profile_id):
    """
    Mock function to delete a profile.
    
    Args:
        profile_id: Profile ID to delete
        
    Returns:
        Dictionary with deletion status
    """
    return {
        "id": profile_id,
        "deleted": True
    }

def get_profile(profile_id):
    """
    Mock function to get a profile.
    
    Args:
        profile_id: Profile ID to get
        
    Returns:
        Dictionary with profile data
    """
    profiles = get_profiles()["profiles"]
    
    for profile in profiles:
        if profile["id"] == profile_id:
            return profile
    
    return None
