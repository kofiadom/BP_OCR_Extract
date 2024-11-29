from groq import Groq
import os
from dotenv import load_dotenv
import streamlit as st
import sqlite3
import json
from datetime import datetime, timedelta

load_dotenv()

api_key=os.getenv('GROQ_API_KEY')
client = Groq(api_key=api_key)

# Database connection setup
def get_db_connection():
    conn = sqlite3.connect("patient_app.db")  # Connect to SQLite database
    conn.row_factory = sqlite3.Row
    return conn

def insert_data(systolic, diastolic, pulse):
    conn = get_db_connection()
    cursor = conn.cursor()
    risk_score = 0.5 * systolic + 0.3 * diastolic
    measurement_time = datetime.now()
    insert_query = """
        INSERT INTO bp_records (systolic, diastolic, pulse, risk_score, measurement_time)
        VALUES (?, ?, ?, ?, ?)
    """
    cursor.execute(insert_query, (systolic, diastolic, pulse, risk_score, measurement_time))
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
            systolic = data.get('systole')
            diastolic = data.get('diastole')
            pulse = data.get('pulse')

            st.subheader("Extracted Blood Pressure Data")
            st.write(f"Systolic Pressure: {systolic}")
            st.write(f"Diastolic Pressure: {diastolic}")
            st.write(f"Pulse Rate: {pulse}")

            if st.button("Save to Database"):
                insert_data(systolic, diastolic, pulse)
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

