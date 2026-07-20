import streamlit as st
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List
import os
import json
from dotenv import load_dotenv
from src.search import DDGS 

# Load environment variables
load_dotenv()

# Configure page settings
st.set_page_config(
    page_title="AI Sports Quiz Generator",
    page_icon="🏆",
    layout="centered" # Changed to centered for a focused quiz experience
)

# --- FOCUSED CARD STYLING ---
def set_quiz_card_theme(image_url):
    st.markdown(f"""
    <style>
    /* Styling for the container holding the quiz questions */
    [data-testid="stVerticalBlock"] > div:has(div.quiz-card) {{
        background-image: url("{image_url}");
        background-size: cover;
        background-position: center;
        padding: 40px;
        border-radius: 20px;
        border: 1px solid rgba(128, 128, 128, 0.2);
    }}
    
    /* Internal card overlay for text readability */
    .quiz-card {{
        background-color: var(--theme-secondary-background-color);
        padding: 25px;
        border-radius: 15px;
        opacity: 0.95;
    }}
    </style>
    """, unsafe_allow_html=True)

# Wallpaper URL
quiz_wallpaper = "https://wallpapers.com/images/hd/olympics-background-7hy1bybz6vn6riza.jpg"
set_quiz_card_theme(quiz_wallpaper)

# --- Pydantic Schema ---
class QuestionSchema(BaseModel):
    id: int
    question: str = Field(description="The sports trivia question statement.")
    options: List[str] = Field(description="Exactly 4 unique multiple-choice options.")
    correct: str = Field(description="The exact string matching the correct option.")
    explanation: str = Field(description="A concise summary.")

class QuizSchema(BaseModel):
    quiz_data: List[QuestionSchema]

@st.cache_resource
def get_gemini_client():
    return genai.Client()

client = get_gemini_client()

# --- Initialize Session States ---
if "quiz_list" not in st.session_state: st.session_state.quiz_list = None
if "current_q_idx" not in st.session_state: st.session_state.current_q_idx = 0
if "score" not in st.session_state: st.session_state.score = 0
if "is_answer_submitted" not in st.session_state: st.session_state.is_answer_submitted = False

# Title and UI
st.title("🏆 AI Sports Quiz Generator")

with st.sidebar:
    st.header("Quiz Settings")
    sports_topic = st.text_input("Enter Sports Topic:", placeholder="e.g., ICC T20 World Cup")
    num_questions = st.slider("Questions:", 3, 10, 5)
    difficulty = st.selectbox("Difficulty:", ["Easy", "Medium", "Hard"])

    if st.button("Generate Quiz", type="primary"):
        if not sports_topic.strip():
            st.warning("Please enter a topic!")
        else:
            st.session_state.quiz_list = None
            with st.spinner("Fetching data and generating quiz..."):
                try:
                    with DDGS() as ddgs:
                        search_results = ddgs.text(f"latest updates {sports_topic}", max_results=3)
                        search_context = "\n".join([f"- {res['body']}" for res in search_results])
                    
                    prompt = f"Generate {num_questions} {difficulty} questions about {sports_topic}. Context: {search_context}"
                    response = client.models.generate_content(
                        model='gemini-3.5-flash',
                        contents=prompt,
                        config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=QuizSchema)
                    )
                    st.session_state.quiz_list = json.loads(response.text).get("quiz_data", [])
                    st.session_state.current_q_idx = 0
                    st.session_state.score = 0
                    st.session_state.is_answer_submitted = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Generation error: {e}")

# --- Quiz Presentation Layer ---
if st.session_state.quiz_list:
    # Wrap quiz content in the styled card
    st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
    
    questions = st.session_state.quiz_list
    q_item = questions[st.session_state.current_q_idx]
    
    st.markdown(f"### **Question {st.session_state.current_q_idx + 1}**")
    st.markdown(f"**{q_item['question']}**")
    
    user_selection = st.radio("Select option:", options=q_item["options"], key=f"q_{st.session_state.current_q_idx}")
    
    if not st.session_state.is_answer_submitted:
        if st.button("Submit Answer"):
            st.session_state.is_answer_submitted = True
            st.rerun()
    else:
        if user_selection == q_item["correct"]:
            st.success("🎯 Correct!")
            if st.session_state.current_q_idx == st.session_state.current_q_idx: # Just to trigger increment
                pass 
        else:
            st.error(f"❌ Incorrect. Correct: {q_item['correct']}")
            st.info(f"💡 {q_item['explanation']}")
            
        if st.button("Next Question ➡️"):
            if user_selection == q_item["correct"]: st.session_state.score += 1
            st.session_state.current_q_idx += 1
            st.session_state.is_answer_submitted = False
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True) # End quiz-card
else:
    st.info("👋 Set up your topic in the sidebar to start!")