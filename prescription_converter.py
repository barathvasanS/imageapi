from flask import Flask, request, jsonify
from pathlib import Path
import google.generativeai as genai

app = Flask(__name__)

# Configure the API key
genai.configure(api_key="AIzaSyBCMezv0Z4EHJn401DHiycKGvRP7Yr6t-4")

# Set up the model
generation_config = {
  "temperature": 0.4,
  "top_p": 1,
  "top_k": 32,
  "max_output_tokens": 4096,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
]

model = genai.GenerativeModel(model_name="gemini-1.0-pro-vision-latest",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

@app.route('/convert_prescription', methods=['POST'])
def convert_prescription():
    # Get the prescription image file from the request
    prescription_image = request.files['prescription_image']

    if not prescription_image:
        return jsonify({"error": "No prescription image provided"}), 400

    # Save the prescription image temporarily
    img_path = Path("temp_image.png")
    prescription_image.save(img_path)

    # Prepare prompt parts
    image_part = {
        "mime_type": "image/png",
        "data": img_path.read_bytes()
    }

    prompt_parts = [
        image_part,
        "\n\nbased on the prescription provided by [Doctor's Name] from [Hospital Name], the prescribed medication is [Medicine Name] with a dosage of [Dosage]. It should be taken [Timing Instructions]\n\n\n For prescription 1:\nThe patient's name is Armando Coquia. He is 29 years old and male. The medication prescribed for him is Amoxicillin 500mg, and he is to take 1 capsule 3 times a day for seven days.\n\nFor prescription 2:\nThe patient's name is Lolita Alvarez. She is 39 years old and female. The medication prescribed for her is Ferrous Sulfate 325mg, and she is to take 1 tablet twice a day for 30 days. She is also prescribed Ascorbic Acid 500mg, and she is to take 1 tablet once a day for 30 days.",
    ]

    # Generate content
    response = model.generate_content(prompt_parts)
    
    # Delete the temporary image file
    img_path.unlink()

    return jsonify({"prescription_text": response.text})

if __name__ == '__main__':
    app.run(debug=True)
