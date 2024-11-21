from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import Optional
import numpy as np
import joblib  # To load your trained models
import datetime
import ollama  # Importing the ollama package
from transformers import pipeline  # Importing the text classification pipeline for your model
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],  # React app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load your trained models
rf_model = joblib.load(r"D:\AI project\WESAD Model\random_forest_model.pkl")  # Random forest model for smartwatch data
text_model = pipeline("text-classification", model=r"D:\AI project\Datasets\Reddit Stress\stress_detector_gpt_model")

# Data model for chat input only (no smartwatch data input from frontend)
class ChatInput(BaseModel):
    message: str

# Function to check stress level from text data using your trained text model
def check_stress_from_text(text: str):
    # Use your trained model to predict stress based on text
    result = text_model(text)
    stress_label = result[0]['label']
    # Adjust the label check to your model's labels (e.g., 'LABEL_1' might represent 'stressed')
    return True if stress_label == 'LABEL_1' else False  # Adjust based on your model's labels

# Function to check stress level from smartwatch data (hardcoded or passed data)
def check_stress_from_smartwatch():
    # Predefined smartwatch data (example data)
    accX, accY, accZ = 0.02, 0.05, 0.01
    BVP, EDA, Temp = 0.35, 0.8, 36.7
    
    # Prepare feature array for the model
    features = np.array([[accX, accY, accZ, BVP, EDA, Temp]])
    stress_prediction = rf_model.predict(features)
    return bool(stress_prediction[0])  # Returns True if stressed, False if not

# Function to generate a dynamic conversational response based on stress level using Ollama's API
def generate_response(message: str, is_stressed: bool):
    # Prepare a prompt based on the stress level
    if is_stressed:
        context = "The user seems stressed. Respond with empathy and suggest relaxing activities or supportive words."
    else:
        context = "Respond naturally to the following message."

    # Use Ollama's chat function to generate a response
    try:
        ollama_response = ollama.chat(model='llama3.2', messages=[
            {
                'role': 'system',
                'content': context
            },
            {
                'role': 'user',
                'content': message
            }
        ])
        return ollama_response['message']['content']
    except Exception as e:
        return f"Error: {e}"

# Endpoint to handle chatbot interaction
@app.post("/chat")
async def chat(input_data: ChatInput = Body(...)):
    # Step 1: Detect stress from text (using your custom trained model)
    text_stress = check_stress_from_text(input_data.message)

    # Step 2: Detect stress from smartwatch data (hardcoded in this example)
    smartwatch_stress = check_stress_from_smartwatch()

    # Step 3: Combine both results (stress detected if either model detects it)
    is_stressed = text_stress or smartwatch_stress

    # Step 4: Generate response based on stress status using Ollama
    response_text = generate_response(input_data.message, is_stressed)

    # Step 5: Send response with timestamp and stress detection results
    return {
        "timestamp": datetime.datetime.now().isoformat(),
        "response": response_text,
        "stress_detected_text": text_stress,
        "stress_detected_smartwatch": smartwatch_stress,
        "overall_stress_detected": is_stressed
    }
