import urllib.request
import json

boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
body = bytearray()
body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"patient_id\"\r\n\r\nPT-4082\r\n".encode("utf-8"))
body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"consent_for_research\"\r\n\r\ntrue\r\n".encode("utf-8"))
body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"sampling_rate\"\r\n\r\n250.0\r\n".encode("utf-8"))
body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"normal_sinus_rhythm_sample.csv\"\r\nContent-Type: text/csv\r\n\r\n".encode("utf-8"))
with open("data/sample/normal_sinus_rhythm_sample.csv", "rb") as f:
    body.extend(f.read())
body.extend(f"\r\n--{boundary}--\r\n".encode("utf-8"))

req = urllib.request.Request(
    "http://127.0.0.1:8000/api/v1/ecg/upload",
    data=bytes(body),
    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
)

with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode())
    print("HTTP Status Code:", resp.status)
    print("Upload Result:", data["success"])
    print("Created Analysis ID:", data["data"]["analysis_id"])
    print("R-Peaks Detected:", data["data"]["preprocessing"]["cardiac_metrics"]["r_peak_count"])

