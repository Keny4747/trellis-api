from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS, cross_origin
import os
from process import process_image
from initialize import initialize_models
import uuid
import logging
import zipfile

app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(level=logging.INFO)

INPUT_DIR = "/workspace/TRELLIS/input"
OUTPUT_DIR = "/workspace/TRELLIS/output"

@app.route('/output/<request_id>/<filename>')
@cross_origin()
def serve_file(request_id, filename):
    """Serve files from the output directory"""
    return send_from_directory(os.path.join(OUTPUT_DIR, request_id), filename)

@app.route('/initialize', methods=['POST'])
@cross_origin()
def initialize():
    app.logger.info("Received request")   
    
    request_id = str(uuid.uuid4())
    
    try:
        app.logger.info("Starting initialization process")
        # Process the image
        initialize_models()

        result = {
            'status': 'success',
            'request_id': request_id,
        }
        app.logger.info(f"Initialization complete: {result}")
        return jsonify(result)
    except Exception as e:
        app.logger.error(f"Error during initialization: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/process', methods=['POST'])
@cross_origin()
def process():
    app.logger.info("Received request")
    
    # Check if we received a file or a path
    if 'image' in request.files:
        file = request.files['image']
        app.logger.info(f"Received file: {file.filename}")
        
        if file.filename == '':
            app.logger.error("Empty filename")
            return jsonify({'error': 'No selected file'}), 400
            
        # Create unique ID for this request
        request_id = str(uuid.uuid4())
        request_output_dir = os.path.join(OUTPUT_DIR, request_id)
        os.makedirs(request_output_dir, exist_ok=True)
        app.logger.info(f"Created output directory: {request_output_dir}")
        
        # Save uploaded file
        input_path = os.path.join(INPUT_DIR, f"{request_id}.webp")
        app.logger.info(f"Saving file to: {input_path}")
        file.save(input_path)
        
    elif 'image' in request.form:
        # Handle the case where we receive a path instead of a file
        input_path = request.form['image']
        app.logger.info(f"Received image path: {input_path}")
        
        if not os.path.exists(input_path):
            app.logger.error(f"File not found: {input_path}")
            return jsonify({'error': 'File not found'}), 400
            
        request_id = str(uuid.uuid4())
        request_output_dir = os.path.join(OUTPUT_DIR, request_id)
        os.makedirs(request_output_dir, exist_ok=True)
        
    else:
        app.logger.error("No image in request")
        return jsonify({'error': 'No image provided'}), 400
    
    try:
        app.logger.info("Starting image processing")
        # Process the image
        output_files = process_image(input_path, request_output_dir)
        
        zip_path = os.path.join(OUTPUT_DIR, request_id, "outputs.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for filename in output_files.values():
                zipf.write(os.path.join(request_output_dir, filename), arcname=filename)

        result = {
            'status': 'success',
            'request_id': request_id,
            'output_files': output_files,
            'zip_file': f'{request_id}/outputs.zip',
            'base_url': f'http://localhost:5000/output/{request_id}'  # Add base URL for files
        }
        app.logger.info(f"Processing complete: {result}")
        return jsonify(result)
    except Exception as e:
        app.logger.error(f"Error during processing: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500
    finally:
        # Only clean up the input file if we created it
        if 'file' in locals() and os.path.exists(input_path):
            os.remove(input_path)
            app.logger.info(f"Cleaned up input file: {input_path}")
            
if __name__ == '__main__':
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("Starting TRELLIS service on port 5000...")
    # Increase timeout and enable debug mode
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)