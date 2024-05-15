import streamlit as st
import openai
from dotenv import load_dotenv
import os
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
youtube_api_key = os.getenv("Youtube_api_key")

# Set Google credentials
credential_path = r"C:\Users\ADMIN\Downloads\youtube key\majestic-poetry-422308-a9-be534c7717c0.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

def get_chatgpt_response(question, chat_history):
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    messages.extend(chat_history)
    messages.insert(0,({"role": "user", "content": question}))

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        stream=True
    )
    return response


# Define functions for generating course content
def generate_topics(course_name, level_of_understanding):
    prompt = f"You are a knowledgeable and highly experienced professor and coach. You have to generate the best curriculum for your students who have {level_of_understanding} level of understanding of {course_name}. Create a comma-separated list of 5 essential topics for the course {course_name}. No detailed description required, keep it short and simple."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.7,
    )
    topics = response.choices[0].message.content.split("\n")
    return [topic.strip() for topic in topics]

def generate_subtopics(topic):
    prompt = f"Create a list of 5 main subtopics for the topic '{topic}' for a detailed understanding. No detailed description required, keep it short and simple."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.7,
    )
    subtopics = response.choices[0].message.content.split("\n")
    return [subtopic.strip() for subtopic in subtopics]

def generate_content(subtopic):
    prompt = f"Provide detailed information about the subtopic: {subtopic}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2048,
        n=1,
        stop=None,
        temperature=0.7,
    )
    content = response.choices[0].message.content
    return content

def generate_mcqs(subtopic):
    prompt = f"Generate 5 multiple-choice questions with 4 options each for the subtopic: {subtopic}. mcq format should be like this (In a phase diagram, what does the x-axis typically represent? A.Temperature B.Pressure C.Pressure D.Pressure) it is A dot option it should not be A close bracket option"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2048,
        n=1,
        stop=None,
        temperature=0.7,
    )
    mcqs = response.choices[0].message.content.strip().split("\n\n")
    return mcqs
    

def generate_mcqs_answer(mcqs):
    prompt = f"Generate correct answers for multiple-choice questions: {mcqs}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2048,
        n=1,
        stop=None,
        temperature=0.7,
    )
    mcq_answers = response.choices[0].message.content.split("\n")
    return mcq_answers

def get_youtube_videos(search_query):
    youtube = build("youtube", "v3", developerKey=youtube_api_key)
    search_response = youtube.search().list(
        q=search_query,
        type="video",
        part="id,snippet",
        maxResults=1
    ).execute()

    video_links = []
    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            video_links.append(f"https://www.youtube.com/watch?v={search_result['id']['videoId']}")

    return video_links

def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("=")[1]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)

        transcript = " ".join([i["text"] for i in transcript_text])
        return transcript

    except Exception as e:
        raise e

def generate_youtube_summary(transcript):
    prompt = f"You are a YouTube video summarizer. You will be taking the transcript text and summarizing the entire video and providing the important summary in points within 250 words. Please provide the summary of the text given here: {transcript}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2048,
        n=1,
        stop=None,
        temperature=0.7,
    )
    ytsummary = response.choices[0].message.content
    return ytsummary
def take_notes(content):
    prompt = f"Provide short and detailed summary notes in a bulleted list format with important words highlighted in bold for the given content: {content}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2048,
        n=1,
        stop=None,
        temperature=0.7,
    )
    summary = response.choices[0].message.content
    return summary



# Initialize session state if not already done
if 'intro_complete' not in st.session_state:
    st.session_state.intro_complete = False

# Function to skip the introduction screens
def skip_intro():
    st.session_state.intro_complete = True

# Define the introduction screens
def intro_screens():
    st.title("Welcome to Self Study Course Generator with AI!")
    st.image("img.jpg", caption="Introduction Image")
    # st.video("intro.mp4")
    if st.button("Skip Intro"):
        skip_intro()

# Main content of the app
def main_content():
    


    st.title(f":violet[Learn Any Course With AI]")

    with st.sidebar:
        st.header("Course Configuration")
        api_key = st.text_input("Enter your OpenAI API key", type="password")
        st.write("Get your OpenAI API key from here [https://platform.openai.com/api-keys]")
        course_name = st.text_input("Enter the course name")
        level_of_understanding = st.selectbox("Select the level of understanding", ["basic", "intermediate", "advanced"])
        generate_button = st.button("Generate Study Material")

    if api_key:
        openai.api_key = api_key

    if generate_button:
        if not api_key:
            st.error("Please enter your OpenAI API key.")
        elif not course_name:
            st.error("Please enter the course name.")
        else:
            topics = generate_topics(course_name, level_of_understanding)
            st.session_state['topics'] = topics
            anything=f"{course_name}"

    if 'topics' in st.session_state:
        
        topics = st.session_state['topics']

        for topic in topics:
            
            container = st.container()
                
            container.subheader(topic)
            generate_subtopics_btn = container.button(f"Start Learning {topic.split('.')[1].strip()}", key=f"subtopics_btn_{topic}")
            
            if generate_subtopics_btn:
                subtopics = generate_subtopics(topic)
                st.session_state[f"subtopics_{topic}"] = subtopics

            if f"subtopics_{topic}" in st.session_state:
                subtopics = st.session_state[f"subtopics_{topic}"]

                for subtopic in subtopics:
                    expander = container.expander(f"{subtopic}")
                    expander.markdown(f"### {subtopic}")
                    notes=[]

                    tab1, tab2, tab3, tab4, tab5 = expander.tabs(["Content", "MCQs", "Videos", "Doubts", "Notes"])
                    
                    with tab1:
                        if st.button(f"Generate Content for {subtopic.split('.')[1].strip()}", key=f"content_btn_{subtopic}"):
                            content = generate_content(subtopic)
                            st.session_state[f"content_{subtopic}"] = content
                        if f"content_{subtopic}" in st.session_state:
                            st.write(st.session_state[f"content_{subtopic}"])
                            content = st.session_state[f"content_{subtopic}"]

                            if st.button(f"Generate notes", key=f"notes_btn_{content}"):
                                note = take_notes(content)
                                st.session_state[f"notes_{content}"] = note
                                notes.append(note)
                                st.success("Notes have been updated, check the Notes section")

                            # if f"notes_{content}" in st.session_state:
                            #     st.markdown(st.session_state[f"notes_{content}"])

                    with tab2:
                        if st.button(f"Generate MCQs for {subtopic.split('.')[1].strip()}", key=f"mcqs_btn_{subtopic}"):
                            mcqs = generate_mcqs(subtopic)
                            mcq_answers = generate_mcqs_answer(mcqs)
                            questions = []
                            for mcq in mcqs:
                                parts = mcq.split("\n")
                                question = parts[0].strip()
                                options = [opt.strip() for opt in parts[1:]]
                                questions.append({"question": question, "options": options})
                            st.session_state[f"mcqs_{subtopic}"] = questions
                            st.session_state[f"mcq_answers_{subtopic}"] = mcq_answers

                        if f"mcqs_{subtopic}" in st.session_state:
                            st.subheader("MCQs")
                            questions = st.session_state[f"mcqs_{subtopic}"]
                            mcq_answers = st.session_state[f"mcq_answers_{subtopic}"]

                            # Debugging line to print mcqs structure
                            # st.write(mcq_answers)

                            for idx, question in enumerate(questions):
                                st.write(question['question'])  # This line causes the error
                                selected_option = st.radio(
                                    "options",
                                    question['options'],
                                    key=f"mcq_{subtopic}_{idx}"
                                )
                                # st.write(selected_option.split(")")[1])
                                # st.write(mcq_answers[idx].split(")")[1])
                                if selected_option:
                                    if ((selected_option.split(".")[1])  == (mcq_answers[idx].split(".")[2])):
                                        st.success("Correct Answer")
                                    else:
                                        st.error("Wrong answer. Try again.")
                                        


                    with tab3:
                        if st.button(f"Search Relevant Videos on YouTube for {subtopic.split('.')[1].strip()}", key=f"videos_btn_{subtopic}"):
                            videos = get_youtube_videos(f'{subtopic} video tutorial for topic name {course_name}')
                            if videos:
                                st.session_state[f"videos_{subtopic}"] = videos

                        if f"videos_{subtopic}" in st.session_state:
                            for video in st.session_state[f"videos_{subtopic}"]:
                                st.video(video)

                            if st.button("Generate Summary", key=f"generate_summary_btn_{subtopic}"):
                                transcripts = []
                                summaries = []
                                for video in st.session_state[f"videos_{subtopic}"]:
                                    try:
                                        transcript = extract_transcript_details(video)
                                        transcripts.append(transcript)
                                        summary = generate_youtube_summary(transcript)
                                        summaries.append(summary)
                                    except Exception as e:
                                        st.error(f"No transcript found for {video}")

                                if transcripts:
                                    st.session_state[f"video_summaries_{subtopic}"] = summaries
                                    for summary in st.session_state[f"video_summaries_{subtopic}"]:
                                        st.write(summary)
                                else:
                                    st.warning("No transcripts found for the selected videos.")

                    with tab4:
                        if "chat_history" not in st.session_state:
                            st.session_state["chat_history"] = []

                        input_text = st.text_input("Input: ", key=f"input{subtopic}")
                        submit = st.button("Ask the question", key=f"submit_button{subtopic}")

                        if submit and input_text:
                            response = get_chatgpt_response(input_text, st.session_state["chat_history"])
                            st.session_state["chat_history"].insert(0,({"role": "user", "content": input_text}))

                            
                            response_text = ""
                            for chunk in response:
                                if "choices" in chunk and len(chunk.choices) > 0 and "delta" in chunk.choices[0] and "content" in chunk.choices[0].delta:
                                    content = chunk.choices[0].delta['content']
                                    response_text += content
                                    # st.write(content)

                            st.session_state["chat_history"].insert(1,({"role": "assistant", "content": response_text}))

                            
                            for message in st.session_state["chat_history"]:
                                st.write(f"{message['role']}: {message['content']}")

                    with tab5:
                    
                        for note in notes:
                            st.markdown(note)
                        
                        
    else:
        st.info("Please enter your OpenAI API key and course details to generate content.")


if st.session_state.intro_complete:
    main_content()
else:
    intro_screens()

