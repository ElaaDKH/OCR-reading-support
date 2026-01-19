from flask import Flask, request, jsonify
from PIL import Image
import easyocr
import io
import numpy as np

app = Flask(__name__)
reader = easyocr.Reader(['en'], gpu=False)

@app.route('/ocr', methods=['POST'])
def ocr():
    try:
        file = request.files['image']
        img = Image.open(io.BytesIO(file.read()))
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        img_array = np.array(img)
        result = reader.readtext(img_array, detail=0)
        text = ' '.join(result)
        
        print(f"OCR Result: {text}")  # Debug output
        return jsonify({'text': text})
        
    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({'text': f'Error: {str(e)}'})

if __name__ == '__main__':
    app.run(host='192.168.1.16', port=5000)
