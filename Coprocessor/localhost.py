from flask import Flask, Response, render_template_string
import cv2

app = Flask(__name__)

# HTML template for the webpage
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Live Video Feed</title>
</head>
<body>
    <h1>Live Video Feed</h1>
    <img src="{{ url_for('video_feed') }}" alt="Video Feed">
</body>
</html>
"""

# Initialize the video capture (0 for default camera)
camera = cv2.VideoCapture(0)

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Encode the frame in JPEG format
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            # Yield the frame as part of a multipart response
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)