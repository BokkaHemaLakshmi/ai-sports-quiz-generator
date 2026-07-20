import os
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List

# Define the structured output format using Pydantic
class QuestionSchema(BaseModel):
    id: int
    question: str = Field(description="The athletic trivia question statement.")
    options: List[str] = Field(description="Exactly 4 unique multiple-choice options.")
    correct: str = Field(description="The exact string matching the correct option from options.")
    explanation: str = Field(description="A concise background explanation of why the answer is correct.")

class QuizSchema(BaseModel):
    quiz_data: List[QuestionSchema]

def generate_dynamic_quiz(topic: str, num_questions: int = 5) -> list:
    """
    Generates a structured, clean list of quiz questions based on the topic using Gemini.
    """
    # Initializes using GEMINI_API_KEY environment variable by default
    client = genai.Client()
    
    prompt = f"""
    Generate a challenging and engaging quiz about the sports topic: "{topic}".
    Provide exactly {num_questions} unique multiple-choice questions.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=QuizSchema, # Strict schema enforcement
                temperature=0.7
            )
        )
        
        # The response.text is guaranteed valid JSON matching our schema
        import json
        data = json.loads(response.text)
        return data.get("quiz_data", [])
        
    except Exception as e:
        print(f"Error generating quiz: {e}")
        # Graceful fallback data if API issues occur
        return [
            {
                "id": 1,
                "question": f"What is a core milestone in {topic} history?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct": "Option A",
                "explanation": "This is a placeholder fallback explanation."
            }
        ]