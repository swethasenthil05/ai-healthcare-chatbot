import json
import os
import re
import sqlite3
from pathlib import Path

DEFAULT_DB = Path(os.getenv("LOCAL_DB_PATH", "data/healthcare.db"))

def normalize(text):
    return re.sub(r"[^a-z0-9\s]", " ", (text or "").lower()).split()

class LocalSymptomEngine:
    def __init__(self, db_path=None):
        self.db_path = Path(db_path or DEFAULT_DB)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.db_path.exists():
            self.initialize_db()

    def connect(self):
        return sqlite3.connect(str(self.db_path))

    def initialize_db(self):
        with self.connect() as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS topics (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    keywords TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    self_care TEXT NOT NULL,
                    seek_care TEXT NOT NULL
                )
            """)
            count = con.execute("SELECT COUNT(*) FROM topics").fetchone()[0]
            if count == 0:
                seed = [
                    ("Common cold", ["runny nose", "sneezing", "congestion", "sore throat", "mild cough"],
                     "These symptoms can occur with a common respiratory infection, but other causes are possible.",
                     ["Rest and drink fluids.", "Consider saline nasal spray for congestion.", "Follow medicine labels and ask a pharmacist if unsure."],
                     ["Seek care for breathing difficulty, dehydration, persistent high fever, or symptoms that worsen or do not improve."]),
                    ("Fever", ["fever", "high temperature", "chills", "temperature"],
                     "Fever can have many causes, including infections. Symptoms alone cannot identify the cause.",
                     ["Drink fluids and rest.", "Monitor your temperature.", "Use fever medicines only according to the label and check with a clinician/pharmacist if you have medical conditions or take other medicines."],
                     ["Seek urgent care for confusion, difficulty breathing, stiff neck, severe dehydration, or a fever in a very young infant. Contact a clinician for persistent or worsening fever."]),
                    ("Headache", ["headache", "head pain", "migraine"],
                     "Headaches have many possible causes, including tension, migraine, dehydration, and illness.",
                     ["Rest in a quiet place and drink water.", "Consider whether missed meals, sleep changes, or dehydration may contribute."],
                     ["Get emergency help for a sudden extremely severe headache, weakness, fainting, confusion, new vision/speech problems, or headache after a serious head injury."]),
                    ("Cough", ["cough", "dry cough", "wet cough", "phlegm"],
                     "A cough can result from respiratory infections, allergies, asthma, or other causes.",
                     ["Drink fluids and avoid smoke or other irritants.", "Warm drinks may soothe throat irritation."],
                     ["Seek urgent care for difficulty breathing, blue/grey lips, chest pain, or coughing up significant blood. Contact a clinician if persistent or worsening."]),
                    ("Stomach discomfort", ["stomach pain", "abdominal pain", "nausea", "vomiting", "diarrhea"],
                     "Digestive symptoms can have many causes; the location, severity, and duration matter.",
                     ["Take small sips of fluids if tolerated.", "Avoid foods that worsen symptoms and monitor for dehydration."],
                     ["Seek urgent care for severe or worsening abdominal pain, blood in vomit/stool, fainting, or inability to keep fluids down."]),
                    ("Sore throat", ["sore throat", "throat pain", "painful swallowing"],
                     "A sore throat may be caused by a viral infection, irritation, or other conditions.",
                     ["Drink fluids and rest.", "Warm drinks or salt-water gargles may help if appropriate for your age."],
                     ["Seek urgent care for trouble breathing or swallowing saliva, drooling, or rapidly increasing throat/neck swelling."]),
                ]
                for name, keywords, summary, self_care, seek_care in seed:
                    con.execute(
                        "INSERT INTO topics(name, keywords, summary, self_care, seek_care) VALUES (?, ?, ?, ?, ?)",
                        (name, json.dumps(keywords), summary, json.dumps(self_care), json.dumps(seek_care)),
                    )

    def assess(self, text, duration="Not specified"):
        query = normalize(text)
        query_text = " ".join(query)
        matches = []
        with self.connect() as con:
            rows = con.execute("SELECT name, keywords, summary, self_care, seek_care FROM topics").fetchall()
        for name, keywords_json, summary, self_care_json, seek_care_json in rows:
            keywords = json.loads(keywords_json)
            score = 0
            for keyword in keywords:
                k = " ".join(normalize(keyword))
                if k and k in query_text:
                    score += 2 if " " in k else 1
            if score:
                matches.append((score, name, summary, json.loads(self_care_json), json.loads(seek_care_json)))
        matches.sort(key=lambda x: x[0], reverse=True)
        if not matches:
            return {
                "matched_topics": [],
                "summary": "No close match was found in the offline reference database. This does not mean the symptoms are harmless. Please consult a healthcare professional, especially if symptoms are severe, persistent, or worsening.",
                "self_care": ["Rest and maintain hydration if you can do so safely."],
                "seek_care": ["Seek urgent medical care for severe or rapidly worsening symptoms."],
                "limitations": "Offline mode uses a small, curated demo dataset and simple keyword matching; it is not a diagnostic system."
            }
        best = matches[:3]
        return {
            "matched_topics": [m[1] for m in best],
            "summary": " ".join(m[2] for m in best),
            "self_care": list(dict.fromkeys(x for m in best for x in m[3])),
            "seek_care": list(dict.fromkeys(x for m in best for x in m[4])),
            "limitations": "Offline mode uses a small, curated demo dataset and simple keyword matching; it is not a diagnostic system."
        }
