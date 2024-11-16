 
import os
import threading
import subprocess
from flask import Flask, request, redirect, url_for, flash

from pyngrok import ngrok
from werkzeug.utils import secure_filename

ngrok.kill()

app = Flask(__name__)
port = "6989"
app.config['UPLOAD_FOLDER'] = '/content/uploads'  # Folder where videos will be saved
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # Max file size (100MB)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Open a ngrok tunnel to the HTTP server
public_url = ngrok.connect(port).public_url
print(public_url)

# Update any base URLs to use the public ngrok URL
app.config["BASE_URL"] = public_url

# Allowed file extensions for uploads
ALLOWED_EXTENSIONS = {'webm', 'mp4', 'avi', 'mov'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Define Flask routes
@app.route("/")
def index():
    return '''
    <html>
    <head>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f9;
                color: #333;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .container {
                background-color: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
                text-align: center;
            }
            h1 {
                color: #4CAF50;
            }
            button {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 16px;
                border-radius: 5px;
                cursor: pointer;
                transition: background-color 0.3s ease;
            }
            button:hover {
                background-color: #45a049;
            }
            .button-container {
                display: flex;
                justify-content: center;
                gap: 10px;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Welcome to the Video Processor</h1>
            <div class="button-container">
                <a href="/llm_correction"><button>LLM Correction</button></a>
                <a href="/"><button>Go Back</button></a>
            </div>
        </div>
    </body>
    </html>
    '''





# Define a route to handle the button click and run the command
@app.route("/run_command", methods=["POST"])
def run_command():
    # Check if the file is in the request
    if 'file' not in request.files:
        return '''
        <html>
        <head><style>h1 {color: red;}</style></head>
        <body><h1>No file part</h1></body></html>
        '''

    file = request.files['file']

    # If no file is selected
    if file.filename == '':
        return '''
        <html>
        <head><style>h1 {color: red;}</style></head>
        <body><h1>No selected file</h1></body></html>
        '''

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)  # Save the uploaded file

        # Update command to use the uploaded file
        command = f"python demo.py data.modality=video pretrained_model_path=/content/auto_avsr/vsr_trlrwlrs2lrs3vox2avsp_base.pth file_path={file_path}"

        try:
            # Run the command using subprocess
            result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = result.stdout.decode("utf-8")
            return f'''
                <html>
                <head>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            background-color: #f4f4f9;
                            color: #333;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            height: 100vh;
                            margin: 0;
                        }}
                        .container {{
                            background-color: white;
                            padding: 20px;
                            border-radius: 10px;
                            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
                            text-align: center;
                        }}
                        h1 {{
                            color: #4CAF50;
                        }}
                        pre {{
                            text-align: left;
                            background-color: #f4f4f4;
                            padding: 10px;
                            border-radius: 5px;
                            white-space: pre-wrap;
                            word-wrap: break-word;
                            border: 1px solid #ddd;
                        }}
                        button {{
                            background-color: #4CAF50;
                            color: white;
                            border: none;
                            padding: 10px 20px;
                            font-size: 16px;
                            border-radius: 5px;
                            cursor: pointer;
                            transition: background-color 0.3s ease;
                        }}
                        button:hover {{
                            background-color: #45a049;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>Command executed successfully!</h1>
                        <pre>{output}</pre>

                        <a href="/"><button>Go Back</button></a>
                    </div>
                </body>
                </html>
            '''
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode("utf-8")
            return f'''
                <html>
                <head><style>h1 {{color: red;}}</style></head>
                <body><h1>Error while running the command</h1><pre>{error_msg}</pre></body>
                </html>
            '''
    else:
        return "<h1>Invalid file type</h1>"


@app.route("/llm_correction")
def llm_correction():
    return '''
        <html>
        <head><style>h1 {color: blue;}</style></head>
        <body>
            <h1>LLM Correction Page Under Construction</h1>
            <a href="/"><button>Go Back</button></a>
        </body>
        </html>
    '''



# Start the Flask server in a new thread, explicitly specifying port 6969
threading.Thread(target=app.run, kwargs={"use_reloader": False, "port": 6989}).start()