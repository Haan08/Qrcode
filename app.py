from flask import Flask, request, render_template_string, redirect, send_file
import qrcode
import io
import json
import os
import uuid

app = Flask(__name__)
DATA_FILE = "data.json"

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
        target_url = request.form['target_url']
        scan_limit = int(request.form['scan_limit'])
        qr_id = str(uuid.uuid4())  # Unique QR code ID

        # Save QR code info and limits
        data = load_data()
        data[qr_id] = {"count": 0, "limit": scan_limit, "target_url": target_url}
        save_data(data)

        # Generate QR code image in memory
        qr_url = f"http://localhost:5000/scan/{qr_id}"
        img = qrcode.make(qr_url)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)

        # Render the QR code image on the page
        qr_img_data = buf.getvalue()
        import base64
        qr_img_base64 = base64.b64encode(qr_img_data).decode('utf-8')

        return render_template_string('''
            <h2>Your QR Code (Scan Limit: {{scan_limit}})</h2>
            <img src="data:image/png;base64,{{qr_img_base64}}" />
            <p>Share this QR code. Each scan will be counted.</p>
            <a href="/">Generate another</a>
        ''', qr_img_base64=qr_img_base64, scan_limit=scan_limit)

    # Show form
    return '''
        <h2>Generate a QR Code with Scan Limit</h2>
        <form method="post">
            Destination URL: <input type="text" name="target_url" required><br>
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
    return redirect(record["target_url"])

if __name__ == '__main__':
    app.run(debug=True)
