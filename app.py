from groq import Groq
import os
import base64
from dotenv import load_dotenv
import streamlit as st
import cv2
import psycopg2
from psycopg2 import sql
import json

load_dotenv()

api_key=os.getenv('GROQ_API_KEY')
client = Groq()

# Function to encode the image
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# Database connection setup
def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    return conn

def insert_data(systole, diastole, pulse):
    conn = get_db_connection()
    cursor = conn.cursor()
    insert_query = sql.SQL("""
        INSERT INTO blood_pressure_readings (systole, diastole, pulse) 
        VALUES (%s, %s, %s)
    """)
    cursor.execute(insert_query, (systole, diastole, pulse))
    conn.commit()
    cursor.close()
    conn.close()

def analyze_image(base64_image):
   
    chat_completion = client.chat.completions.create(
        model="llama-3.2-11b-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": SYSTEM_PROMPT
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )

    result = chat_completion.choices[0].message.content
    st.write("Raw response:", result)

    # Parse the JSON result
    try:
        data = json.loads(result)
        if 'error' not in data:
            systole = data.get('systole')
            diastole = data.get('diastole')
            pulse = data.get('pulse')

            st.subheader("Extracted Blood Pressure Data")
            st.write(f"Systolic Pressure: {systole}")
            st.write(f"Diastolic Pressure: {diastole}")
            st.write(f"Pulse Rate: {pulse}")

            if st.button("Save to Database"):
                insert_data(systole, diastole, pulse)
                st.success("Data saved to the database successfully!")
        else:
            st.error("Error in the response: " + data.get('error', 'Unknown error'))
    except json.JSONDecodeError:
        st.error("Failed to decode JSON response.")


SYSTEM_PROMPT = """
Act as an OCR assistant specializing in extracting specific numerical readings from images of blood pressure measuring devices. Analyze the provided image and:  

1. **Focus on Targeted Values Only:** Identify and extract the numerical values representing:
   - **Systolic pressure (systole):** The higher numerical value.
   - **Diastolic pressure (diastole):** The lower numerical value.
   - **Pulse rate:** Typically displayed as a separate numerical value labeled as pulse or heart rate.

2. **Ignore Non-Relevant Data:** Disregard any text, symbols, units (e.g., mmHg, bpm), or other extraneous information. Only extract the three numerical values of interest.

3. **Format Output:** Return the results as a JSON object in the following structure:
   ```json
   {
     "systole": <systole_value>,
     "diastole": <diastole_value>,
     "pulse": <pulse_value>
   }
   ```
   Replace `<systole_value>`, `<diastole_value>`, and `<pulse_value>` with the extracted integers.

4. **Error Handling:** If no clear numerical values for systole, diastole, or pulse can be extracted, respond with:
   ```json
   {
     "error": "Unable to extract values from the image. The display may be unreadable or unclear."
   }
   ```

5. **Accuracy and Efficiency:** Prioritize accurate recognition of the specified values while processing the image efficiently.  

Provide only the JSON output without any additional comments or explanations.
"""

st.title("Blood Pressure OCR Assistant")

uploaded_file = st.file_uploader("Upload an image of a blood pressure device", type=["jpg", "jpeg"])

if uploaded_file is not None: 
  # Encode the uploaded image 
  base64_image = encode_image(uploaded_file)
  analyze_image(base64_image)

ctx = st.camera_input("Take a photo of the blood pressure device")

if ctx: # Capture the image 
    img_array = ctx.get_image_data() 
    image_bytes = cv2.imencode('.jpg', img_array) 
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    analyze_image(base64_image)

client = Groq(api_key=api_key)

