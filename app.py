import streamlit as st
from groq import Groq 
import os
from dotenv import load_dotenv
import time


load_dotenv()

api_key = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=api_key)

LANGCHAIN_API_KEY= st.secrets["LANGCHAIN_API_KEY"]
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
LANGCHAIN_TRACING_V2 = "true"
LANGCHAIN_PROJECT = st.secrets["LANGCHAIN_PROJECT"]

# Initialize session state
if 'time_remaining' not in st.session_state:
    st.session_state.time_remaining = 26 * 60
if 'timer_active' not in st.session_state:
    st.session_state.timer_active = False
if 'evaluate_clicked' not in st.session_state:
    st.session_state.evaluate_clicked = False

rubricdescription = {
    "Content/Coherence": "The Number of ideas, Quality of ideas, Organization of ideas, Examples and supporting details of the response.",
    "Vocabulary": "The Word choice, Suitable usage of words and phrases, Range of words and phrases, Precision and accuracy of the response.",
    "Readability": "The Format and paragraphing, Usage of Connectors and transitions, Grammar and sentence structure, Spelling and punctuation of the response.",
    "Task Fulfillment": "The Relevance, Completeness, Tone and Word count of the response."
}

rubric = {
        "Content/Coherence": {
            "factors": ["Number of ideas", "Quality of ideas", "Organization of ideas", "Examples and supporting details"],
            "level_descriptors": {
                12: "Complex formal/informal texts for full range of purposes with relevant extended details",
                11: "Formal/informal texts for range of purposes with relevant facts",
                10: "Short formal/informal texts of complexity with range of facts",
                9: "Short formal/informal texts with relevant facts",
                8: "Short moderately complex texts with main idea and supporting details",
                7: "Short moderately complex factual texts with main idea",
                6: "Short coherent texts with some supporting details",
                5: "Short simple to moderately complex texts with related ideas",
                4: "Simple sentences and paragraphs with personal information",
                3: "Short simple sentences",
                "0-2": "Very short simple sentences and phrases"
            }
        },
        "Vocabulary": {
            "factors": ["Word choice", "Suitable use of words and phrases", "Range of words and phrases", "Precision and accuracy"],
            "level_descriptors": {
                12: "Specialized, formal, common vocabulary with precise meaning",
                11: "Specialized, formal, common vocabulary with meaning",
                10: "Precise details, descriptions, and comparisons",
                9: "Accurate details, descriptions, and comparisons",
                8: "Common or context-specific words",
                7: "Common and some context-specific words",
                6: "Common words and phrases",
                5: "Common words and phrases",
                4: "Common words",
                3: "Very common words",
                "0-2": "Alphabet, numbers, and very common words"
            }
        },
        "Readability": {
            "factors": ["Format and paragraphing", "Connectors and transitions", "Grammar and sentence structure", "Spelling and punctuation"],
            "level_descriptors": {
                12: "Very good control of very broad range of complex structures",
                11: "Good control of broad range of complex structures",
                10: "Good control of range of complex structures",
                9: "Control of range of complex structures",
                8: "Good control of complex structures",
                7: "Good control of complex and simple structures",
                6: "Good control of simple grammar",
                5: "Good control of simple grammar",
                4: "Some control of simple grammar",
                3: "Sometimes correct grammar",
                "0-2": "Rarely correct grammar"
            }
        },
        "Task_Fulfillment": {
            "factors": ["Relevance", "Completeness", "Tone", "Word count"],
            "level_descriptors": {
                12: "Precise communication with appropriate tone",
                11: "Accurate communication with usually appropriate tone",
                10: "Convey intended meaning following conventions",
                9: "Convey intended meaning with some conventions",
                8: "Convey main ideas following common conventions",
                7: "Convey factual information with common conventions",
                6: "Convey some information with sometimes appropriate tone",
                5: "Convey information about familiar topics",
                4: "Convey information about very familiar topics",
                3: "Write some information about me",
                "0-2": "Write very simple information about me"
            }
        }
    }

def evaluate_writing(task_type, question, answer):
    prompt = f"""
    You are an expert CELPIP writing evaluator. Evaluate the following {task_type} response using the official CELPIP standards:

    Question: {question}
    Answer: {answer}

    For each category, provide:
    1. Detailed evaluation of all factors
    2. Specific examples from the text
    3. Score (0-12) based on CELPIP level descriptors
    4. Justification for the score

    Categories to evaluate:
    1. Content/Coherence:
       - Number of ideas
       - Quality of ideas
       - Organization of ideas
       - Examples and supporting details

    2. Vocabulary:
       - Word choice
       - Suitable use of words/phrases
       - Range of words/phrases
       - Precision and accuracy

    3. Readability:
       - Format and paragraphing
       - Connectors and transitions
       - Grammar and sentence structure
       - Spelling and punctuation

    4. Task Fulfillment:
       - Relevance
       - Completeness
       - Tone
       - Word count

    For the overall score, round the average score of all the desscriptors to the nearest whole number.

    Format:
    Category: [Name] \n
    Evaluation: [Detailed analysis] \n
    Examples: [From text] \n
    Score: [0-12] \n
    Justification: [Based on level descriptors]\n
    Overall Grade: [0-12] \n
    Key Strengths: [List]\n
    Areas for Improvement: [List]
    """

    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        temperature=0,
        max_tokens=2000,
        stream=False,
    )

    return chat_completion.choices[0].message.content

def start_timer():
    st.session_state.timer_active = True
    st.session_state.time_remaining = 26 * 60

def handle_evaluate():
    st.session_state.evaluate_clicked = True
    st.session_state.timer_active = False

# Main UI
st.title("CELPIP Writing Task Evaluator")

# Timer section with placeholder
timer_col1, timer_col2 = st.columns([3,1])
with timer_col1:
    if not st.session_state.timer_active:
        if st.button("Start Timer (26 minutes)"):
            start_timer()
            
timer_placeholder = st.empty()
if st.session_state.timer_active:
    mins, secs = divmod(st.session_state.time_remaining, 60)
    timer_placeholder.header(f"Time Remaining: {mins:02d}:{secs:02d}")
    if st.session_state.time_remaining > 0:
        st.session_state.time_remaining -= 1
        time.sleep(1)
        st.rerun()
    else:
        timer_placeholder.header("Time's Up!")
else:
    mins, secs = divmod(st.session_state.time_remaining, 60)
    timer_placeholder.header(f"Time Remaining: {mins:02d}:{secs:02d}")

# Main content
task_type = st.selectbox("Select Task Type", ["Task 1 (Email)", "Task 2 (Survey Response)"])

question_placeholder = st.empty()
question = question_placeholder.text_area("Enter the question here:", height=250, key="question")

answer_placeholder = st.empty()
word_count_placeholder = st.empty()

def update_word_count():
    word_count = len(st.session_state.answer.split())
    word_count_placeholder.text(f"Word Count: {word_count}")

answer = answer_placeholder.text_area("Write your answer in 150-200 words:", height=600, key="answer", on_change=update_word_count)

# Initialize word count on first load
if 'answer' in st.session_state:
    update_word_count()

evaluate_button = st.button("Evaluate", on_click=handle_evaluate)

if st.session_state.evaluate_clicked:
    if question and answer:
        with st.spinner("Evaluating your response..."):
            evaluation = evaluate_writing(task_type, question, answer)
        st.balloons()
        st.subheader("Evaluation Results")
        st.write(evaluation)
        st.session_state.evaluate_clicked = False
    else:
        st.warning("Please enter both the question and your response.")

# Sidebar
st.sidebar.header("CELPIP Writing Rubric")
for criterion, description in rubricdescription.items():
    st.sidebar.subheader(criterion)
    st.sidebar.write(description)
