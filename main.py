import tkinter as tk
from tkinter import scrolledtext
from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration
import speech_recognition as sr
import pyttsx3
import wikipedia
import webbrowser
import threading

# Initialize text-to-speech engine
engine = pyttsx3.init()
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[1].id)

# Function to handle text-to-speech
def speak(audio):
    engine.say(audio)
    engine.runAndWait()

# Load the Blenderbot model and tokenizer
tokenizer = BlenderbotTokenizer.from_pretrained("facebook/blenderbot-400M-distill")
model = BlenderbotForConditionalGeneration.from_pretrained("facebook/blenderbot-400M-distill")

# Function to get chatbot text-response
def get_response(user_input):
    inputs = tokenizer(user_input, return_tensors="pt")
    reply_ids = model.generate(**inputs)
    response = tokenizer.decode(reply_ids[0], skip_special_tokens=True)
    return response

# Speech recognition function
def takecommand():
    r = sr.Recognizer()
    with sr.Microphone(device_index=0) as source:
        r.adjust_for_ambient_noise(source)
        try:
            print("Listening....")
            audio = r.listen(source, phrase_time_limit=5)
            print("Recognizing....")
            query = r.recognize_google(audio, language='eng-in')
            print(f"User said: {query}\n")
            return query
        except sr.WaitTimeoutError:
            speak("Sorry, no speech detected within the timeout period.")
        except sr.UnknownValueError:
            speak("Sorry, I could not understand the audio.")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
        return ""

# Function to handle voice input
def handle_voice_input():
    query = takecommand()
    if query:
        process_voice_query(query)

# Function to process text input (with different behavior for text mode)
def process_text_query(query):
    chat_window.insert(tk.END, f"You (text): {query}\n")
    query = query.lower()

    response = get_response(query)
    chat_window.insert(tk.END, f"botXdir (text): {response}\n\n")
    print(f"botXdir: {response}")

# Function to process voice input (with different behavior for voice mode)
def process_voice_query(query):
    chat_window.insert(tk.END, f"You (voice): {query}\n")
    query = query.lower()

    if 'wikipedia' in query:
        speak('Searching Wikipedia via voice...')
        query = query.replace("wikipedia", "")
        try:
            results = wikipedia.summary(query, sentences=2)
            speak("According to Wikipedia")
            chat_window.insert(tk.END, f"botXdir (voice): {results}\n\n")
            speak(results)
        except wikipedia.exceptions.DisambiguationError as e:
            chat_window.insert(tk.END, f"botXdir (voice): Multiple results found. Be more specific.\n\n")
            speak("Multiple results found. Be more specific.")
        except wikipedia.exceptions.PageError:
            chat_window.insert(tk.END, f"botXdir (voice): No results found on Wikipedia.\n\n")
            speak("No results found on Wikipedia.")
    
    elif 'search' in query:
        speak(f"Searching {query} via voice")
        chat_window.insert(tk.END, f"botXdir (voice): Searching for {query}\n\n")
        webbrowser.open(f"https://www.google.com/search?q={query}")
    
    else:
        response = get_response(query)
        chat_window.insert(tk.END, f"botXdir (voice): {response}\n\n")
        speak(response)

# Function to handle text input from the user
def handle_text_input():
    user_input = user_entry.get()
    process_text_query(user_input)
    user_entry.delete(0, tk.END)

# Function to handle voice input from a button
def voice_input_thread():
    threading.Thread(target=handle_voice_input).start()

# Function to toggle between normal chat and voice chat
def toggle_chat_mode():
    global mode
    if mode == "text":
        mode = "voice"
        chat_mode_button.config(text="Switch to Text Chat",font=("Helvetica", 10, "bold"))
        user_entry.config(state=tk.DISABLED)
        send_button.config(state=tk.DISABLED)
        voice_button.config(state=tk.NORMAL)
    else:
        mode = "text"
        chat_mode_button.config(text="Switch to Voice Chat",font=("Helvetica", 10, "bold"))
        user_entry.config(state=tk.NORMAL)
        send_button.config(state=tk.NORMAL)
        voice_button.config(state=tk.DISABLED)

# Create the main window
root = tk.Tk()
root.title("botXdir")
root.geometry("600x500")

# Chat window (scrollable text area)
chat_window = scrolledtext.ScrolledText(root, width=70, height=20)
chat_window.pack(pady=10)

# Entry box for user input
user_entry = tk.Entry(root, width=50)
user_entry.pack(pady=5)

# Button to send text input
send_button = tk.Button(root, text="Text-Me", command=handle_text_input)
send_button.pack(pady=5)

# Button to take voice input
voice_button = tk.Button(root, text="Voice Input", command=voice_input_thread, state=tk.DISABLED)
voice_button.pack(pady=5)

# Button to switch between text and voice chat
chat_mode_button = tk.Button(root, text="Switch to Voice Chat", command=toggle_chat_mode)
chat_mode_button.pack(pady=10)

# Initial chat mode is set to text
mode = "text"

# Run the Tkinter main loop
root.mainloop()
