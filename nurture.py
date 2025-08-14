import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
import gradio as gr
from gtts import gTTS
import tempfile


# System prompt
chat_history = [
    {
        "role": "system",
        "content": "You are an empathetic, conversational nutritionist who gently guides users to share their name, fitness goals, lifestyle, allergies, dietary preferences, and typical meals. Start with a warm greeting and then ask follow-up questions to eventually create a personalized diet plan."
    }
]

def ask_openai(question):
    """
    Sends user input to OpenAI's GPT-5 model and returns the response.
    Maintains conversation context by appending to chat_history.
    """
    try:
        chat_history.append({"role": "user", "content": question})

        response = client.chat.completions.create(model="gpt-5",
        messages=chat_history,
        temperature=0.4,
        max_tokens=400)

        reply = response.choices[0].message.content
        chat_history.append({"role": "assistant", "content": reply})
        return reply

    except Exception as e:
        return f"Error: {str(e)}"

def speak(text):
    """
    Converts text to speech using gTTS and saves it to a temporary MP3 file.
    Returns the file path for playback.
    """

    tts = gTTS(text)
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(tmp_file.name)
    return tmp_file.name

def calculate_bmi(height_cm, weight_kg):
    """
    Calculates BMI based on height (cm) and weight (kg).
    Returns BMI value and weight category.
    """

    try:
        height_m = height_cm / 100
        bmi = weight_kg / (height_m ** 2)
        category = (
            "Underweight" if bmi < 18.5 else
            "Normal weight" if bmi < 25 else
            "Overweight" if bmi < 30 else
            "Obese"
        )
        return f"Your BMI is {bmi:.2f} - {category}"

    except:
        return "Please enter valid height and weight."

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("<h1 style='text-align:center'>Nurture : Your AI Nurtition Coach</h1>")

    with gr.Row():
        #Chat Section
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(height=350, label="Chat with Nurture")
            message = gr.Textbox(placeholder="Ask something...", label="Your Message")
            send_btn = gr.Button("Send")
            audio_output = gr.Audio(label="AI Voice", type="filepath", interactive=False)

            def respond(user_message, chat_log):
                """
                Handles user input, gets AI response, updates chat log, and generates audio
                """
                bot_reply = ask_openai(user_message)
                chat_log.append((user_message, bot_reply))
                audio_path = speak(bot_reply)
                return "", chat_log, audio_output

            send_btn.click(respond, inputs=[message, chatbot], outputs=[message, chatbot, audio_output])

        # BMI + Tools Section
        with gr.Column(scale=1):
            gr.Markdown("### Check Your BMI")
            height = gr.Number(label="Height (in cm)")
            weight = gr.Number(label="Weight (in kg)")
            bmi_output = gr.Textbox(label="result")
            bmi_btn = gr.Button("Calculate BMI")
            bmi_btn.click(fn=calculate_bmi, inputs=[height, weight], outputs=bmi_output)

demo.launch(share=True)