from flask import Flask, request, render_template_string, redirect
import qrcode
import io
import json
import os
import uuid
import base64

app = Flask(__name__)
DATA_FILE = "data.json"
DESTINATION_URL = "https://haan08.github.io/my-qrcode-landing-page/"  # <-- Your fixed destination

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        scan_limit = int(request.form['scan_limit'])
        qr_id = str(uuid.uuid4())  # Unique QR code ID

        # Save QR code info and limits
        data = load_data()
        data[qr_id] = {"count": 0, "limit": scan_limit}
        save_data(data)

        # Generate QR code image in memory
        qr_url = f"{request.host_url}scan/{qr_id}"
        img = qrcode.make(qr_url)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)

        # Encode image to base64 for embedding in HTML
        qr_img_data = buf.getvalue()
        qr_img_base64 = base64.b64encode(qr_img_data).decode('utf-8')

        return render_template_string('''
            <h2>Your QR Code (Scan Limit: {{scan_limit}})</h2>
            <img src="data:image/png;base64,{{qr_img_base64}}" />
            <p>Share this QR code. Each scan will be counted and redirected to:<br>
            <a href="{{destination_url}}" target="_blank">{{destination_url}}</a></p>
            <a href="/">Generate another</a>
        ''', qr_img_base64=qr_img_base64, scan_limit=scan_limit, destination_url=DESTINATION_URL)

    # Show form (only scan limit)
    return '''
        <h2>Generate a QR Code with Scan Limit</h2>
        <form method="post">
            Scan Limit: <input type="number" name="scan_limit" min="1" required><br>
            <input type="submit" value="Generate QR Code">
        </form>
    '''

@app.route('/scan/<qr_id>')
def scan(qr_id):
    data = load_data()
    if qr_id not in data:
        return "Invalid QR code.", 404
    record = data[qr_id]
    if record["count"] >= record["limit"]:
        return "Scan limit reached.", 403
    record["count"] += 1
    save_data(data)
    return redirect(DESTINATION_URL)

if __name__ == '__main__':
    app.run(debug=True)
