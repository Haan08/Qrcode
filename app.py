from flask import Flask, request, render_template_string, redirect, jsonify
import qrcode
import io
import json
import os
import uuid
import base64
import math

app = Flask(__name__)
DATA_FILE = "data.json"

DEFAULT_DESTINATION_URL = "https://haan08.github.io/website/"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    meters = R * c
    return meters

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        scan_limit = int(request.form['scan_limit'])
        lat = request.form.get('lat')
        lon = request.form.get('lon')

        if lat is None or lon is None or lat.strip() == '' or lon.strip() == '':
            return render_template_string('''
                <main class="max-w-xl mx-auto bg-white p-8 rounded-xl shadow-lg mt-20 text-center">
                    <h2 class="text-3xl font-extrabold text-gray-900 mb-6">Error: Location is required to generate QR code.</h2>
                    <a href="/" class="inline-block mt-4 text-blue-600 hover:text-blue-800 font-semibold">Go back</a>
                </main>            
            ''')

        try:
            lat = float(lat)
            lon = float(lon)
        except ValueError:
            return render_template_string('''
                <main class="max-w-xl mx-auto bg-white p-8 rounded-xl shadow-lg mt-20 text-center">
                  <h2 class="text-3xl font-extrabold text-gray-900 mb-6">Error: Invalid latitude or longitude values.</h2>
                  <a href="/" class="inline-block mt-4 text-blue-600 hover:text-blue-800 font-semibold">Go back</a>
                </main>
            ''')

        qr_id = str(uuid.uuid4())

        data = load_data()
        data[qr_id] = {
            "count": 0,
            "limit": scan_limit,
            "origin_lat": lat,
            "origin_lon": lon,
            "target_url": DEFAULT_DESTINATION_URL
        }
        save_data(data)

        qr_url = f"{request.host_url}scan/{qr_id}"
        img = qrcode.make(qr_url)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)

        qr_img_data = buf.getvalue()
        qr_img_base64 = base64.b64encode(qr_img_data).decode('utf-8')

        return render_template_string('''
          <main class="max-w-xl mx-auto bg-white p-8 rounded-xl shadow-lg mt-20 text-center">
            <h2 class="text-3xl font-extrabold text-gray-900 mb-6">Your QR Code (Scan Limit: {{scan_limit}})</h2>
            <img src="data:image/png;base64,{{qr_img_base64}}" alt="QR Code" class="mx-auto mb-6" />
            <p class="text-gray-700 mb-4">
              Share this QR code. Each scan will be counted and user must be near the original QR location to be redirected.
            </p>
            <p class="mb-6">
              Redirect destination:<br>
              <a href="{{target_url}}" target="_blank" class="text-blue-600 hover:text-blue-800 font-semibold break-words">{{target_url}}</a>
            </p>
            <a href="/" class="inline-block px-6 py-3 bg-black text-white font-bold rounded-lg hover:bg-gray-800 transition">Generate another</a>
          </main>
        ''', qr_img_base64=qr_img_base64, scan_limit=scan_limit, target_url=DEFAULT_DESTINATION_URL)

    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Generate QR Code with Location</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body {
      background-color: #fff;
      font-family: 'Inter', sans-serif;
      color: #6b7280;
      margin: 0;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 2rem;
    }
    main {
      max-width: 400px;
      width: 100%;
      background: #fff;
      padding: 2rem;
      border-radius: 0.75rem;
      box-shadow: 0 10px 15px rgba(0,0,0,0.1);
      text-align: center;
    }
    h2 {
      font-weight: 800;
      font-size: 2.5rem;
      color: #111827;
      margin-bottom: 1.5rem;
    }
    label {
      display: block;
      font-weight: 600;
      color: #374151;
      margin-bottom: 0.5rem;
      text-align: left;
    }
    input[type="number"],
    input[type="text"] {
      width: 100%;
      padding: 0.5rem 0.75rem;
      font-size: 1rem;
      border: 1px solid #d1d5db;
      border-radius: 0.5rem;
      margin-bottom: 1rem;
      transition: border-color 0.3s ease;
    }
    input[type="number"]:focus,
    input[type="text"]:focus {
      outline: none;
      border-color: #2563eb;
    }
    button[type="submit"] {
      margin-top: 1rem;
      width: 100%;
      background-color: #111827;
      color: white;
      font-weight: 700;
      font-size: 1.125rem;
      padding: 0.75rem;
      border: none;
      border-radius: 0.75rem;
      cursor: pointer;
      transition: background-color 0.3s ease;
    }
    button[type="submit"]:hover {
      background-color: #1e40af;
    }
    .info-text {
      font-size: 0.9rem;
      color: #4b5563;
      margin-bottom: 1rem;
    }
  </style>
</head>
<body>
  <main>
    <h2>Generate a QR Code with Scan Limit & Location</h2>
    <form method="post" id="qrForm" novalidate>
      <label for="scan_limit">Scan Limit</label>
      <input type="number" id="scan_limit" name="scan_limit" min="1" required />

      <label for="lat">Your Latitude (auto-filled if allowed)</label>
      <input type="text" id="lat" name="lat" required readonly placeholder="Allow location access..." />

      <label for="lon">Your Longitude (auto-filled if allowed)</label>
      <input type="text" id="lon" name="lon" required readonly placeholder="Allow location access..." />

      <p class="info-text">Please allow location access, or enter your coordinates manually if denied.</p>

      <button type="submit">Generate QR Code</button>
    </form>
  </main>

  <script>
    function fillLocation(position) {
      document.getElementById('lat').value = position.coords.latitude.toFixed(6);
      document.getElementById('lon').value = position.coords.longitude.toFixed(6);
    }
    function errorLocation(error) {
      alert('Geolocation needed for precise scan validation: ' + error.message);
      // Fallback: allow manual input by making fields editable
      var latInput = document.getElementById('lat');
      var lonInput = document.getElementById('lon');
      latInput.removeAttribute('readonly');
      lonInput.removeAttribute('readonly');
      latInput.placeholder = "Enter latitude";
      lonInput.placeholder = "Enter longitude";
    }
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(fillLocation, errorLocation);
    } else {
      alert('Geolocation is not supported by your browser. Please input location manually.');
      var latInput = document.getElementById('lat');
      var lonInput = document.getElementById('lon');
      latInput.removeAttribute('readonly');
      lonInput.removeAttribute('readonly');
      latInput.placeholder = "Enter latitude";
      lonInput.placeholder = "Enter longitude";
    }
  </script>
</body>
</html>
''')

@app.route('/scan/<qr_id>')
def scan(qr_id):
    data = load_data()
    if qr_id not in data:
        return "Invalid QR code.", 404

    record = data[qr_id]
    if record["count"] >= record["limit"]:
        return "Scan limit reached.", 403

    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Validate QR Scan Location</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body {
      background-color: #fff;
      font-family: 'Inter', sans-serif;
      color: #6b7280;
      margin: 0;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 2rem;
      text-align: center;
    }
    main {
      max-width: 400px;
      width: 100%;
      background: white;
      padding: 2rem;
      border-radius: 0.75rem;
      box-shadow: 0 10px 15px rgba(0,0,0,0.1);
    }
    h2 {
      font-weight: 800;
      font-size: 2.5rem;
      color: #111827;
      margin-bottom: 1rem;
    }
    #message {
      margin-top: 1rem;
      font-size: 1rem;
      font-weight: 600;
    }
  </style>
</head>
<body>
  <main>
    <h2>Validating your location to continue...</h2>
    <p>Please allow location access to proceed.</p>
    <div id="message"></div>
  </main>

  <script>
    function showMessage(msg, isError) {
      let el = document.getElementById('message');
      el.textContent = msg;
      el.style.color = isError ? 'red' : 'green';
    }

    function sendLocation(lat, lon) {
      fetch('/validate_scan/{{qr_id}}', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({latitude: lat, longitude: lon})
      }).then(res => res.json())
        .then(data => {
          if(data.success) {
            window.location.href = data.redirect_url;
          } else {
            showMessage(data.message || 'Access denied', true);
          }
        }).catch(err => {
          showMessage('Validation error: ' + err.message, true);
        });
    }

    function errorLocation(err) {
      showMessage('Location access denied or unavailable: ' + err.message, true);
    }

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(function(pos) {
        sendLocation(pos.coords.latitude, pos.coords.longitude);
      }, errorLocation);
    } else {
      showMessage('Geolocation is not supported by your browser.', true);
    }
  </script>
</body>
</html>
    ''', qr_id=qr_id)



@app.route('/validate_scan/<qr_id>', methods=['POST'])
def validate_scan(qr_id):
    data = load_data()
    if qr_id not in data:
        return jsonify(success=False, message="Invalid QR code."), 404
    record = data[qr_id]
    if record["count"] >= record["limit"]:
        return jsonify(success=False, message="Scan limit reached."), 403

    req_data = request.get_json()
    if not req_data or "latitude" not in req_data or "longitude" not in req_data:
        return jsonify(success=False, message="Location not provided."), 400

    try:
        lat = float(req_data["latitude"])
        lon = float(req_data["longitude"])
    except ValueError:
        return jsonify(success=False, message="Invalid location data."), 400

    origin_lat = record.get("origin_lat")
    origin_lon = record.get("origin_lon")
    if origin_lat is None or origin_lon is None:
        return jsonify(success=False, message="QR code location not set."), 400

    distance = haversine(origin_lat, origin_lon, lat, lon)
    allowed_distance_meters = 300

    if distance > allowed_distance_meters:
        return jsonify(success=False, message=f"You are too far from the origin location ({int(distance)}m away)."), 403

    record["count"] += 1
    save_data(data)
    target_url = record.get("target_url", DEFAULT_DESTINATION_URL)
    return jsonify(success=True, redirect_url=target_url)

if __name__ == '__main__':
    app.run(debug=True)

