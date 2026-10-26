
import os
import requests
import streamlit as st
from dotenv import load_dotenv

from local_engine import LocalSymptomEngine
from safety import emergency_screen, SAFETY_NOTICE

# --------------------------------------------------
# 1. Application configuration
# --------------------------------------------------

load_dotenv()

st.set_page_config(
    page_title="AI Healthcare Chatbot",
    page_icon="🩺",
    layout="wide",
)

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000",
)

LOCAL_DB_PATH = os.getenv(
    "LOCAL_DB_PATH",
    "data/healthcare.db",
)

engine = LocalSymptomEngine(LOCAL_DB_PATH)


# --------------------------------------------------
# 2. Check whether the online API is available
# --------------------------------------------------

def api_is_healthy():
    try:
        response = requests.get(
            f"{API_BASE_URL}/health",
            timeout=2,
        )
        return response.ok

    except requests.RequestException:
        return False


# --------------------------------------------------
# 3. Send symptoms to the online backend
# --------------------------------------------------

def online_assessment(symptoms, age, duration, notes):
    payload = {
        "symptoms": symptoms,
        "age": age,
        "duration": duration,
        "notes": notes,
    }

    response = requests.post(
        f"{API_BASE_URL}/assess",
        json=payload,
        timeout=8,
    )

    response.raise_for_status()
    return response.json()


# --------------------------------------------------
# 4. Application heading
# --------------------------------------------------

st.title("🩺 AI Healthcare Chatbot")

st.subheader(
    "Symptom Analysis and Healthcare Guidance"
)

st.caption(
    "An educational chatbot providing general symptom "
    "information using online and offline resources."
)


# --------------------------------------------------
# 5. Determine application mode
# --------------------------------------------------

online = api_is_healthy()

if online:
    st.success(
        "Online service available. "
        "The chatbot can use the backend API."
    )
else:
    st.warning(
        "Offline mode active. "
        "The chatbot will use the local SQLite database. "
        "Online AI/NLP services are unavailable."
    )


# --------------------------------------------------
# 6. Sidebar information
# --------------------------------------------------

with st.sidebar:
    st.header("About this chatbot")

    st.write(
        "This project provides general health information "
        "based on symptoms entered by the user."
    )

    st.write("**How it works**")

    st.write("1. Enter your symptoms.")
    st.write("2. The app checks for emergency warning signs.")
    st.write("3. The app checks online service availability.")
    st.write("4. It retrieves relevant healthcare information.")
    st.write("5. It displays general guidance and care warnings.")

    st.divider()

    st.caption(
        "This educational project does not diagnose diseases "
        "or replace a qualified healthcare professional."
    )


# --------------------------------------------------
# 7. Safety notice
# --------------------------------------------------

st.info(SAFETY_NOTICE)


# --------------------------------------------------
# 8. Symptom input form
# --------------------------------------------------

with st.form("symptom_form"):

    symptoms_text = st.text_area(
        "Describe your symptoms",
        placeholder=(
            "Example: I have a runny nose, "
            "sneezing, and a mild cough."
        ),
        help=(
            "Describe your symptoms in everyday language. "
            "Avoid entering your name, address, or other "
            "identifying information."
        ),
    )

    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input(
            "Age (optional)",
            min_value=0,
            max_value=120,
            value=0,
            help="Enter 0 if you prefer not to provide your age.",
        )

    with col2:
        duration = st.selectbox(
            "How long have symptoms been present?",
            [
                "Not specified",
                "Less than 24 hours",
                "1–3 days",
                "4–7 days",
                "More than 7 days",
            ],
        )

    notes = st.text_input(
        "Additional context (optional)",
        placeholder="Example: symptoms are getting worse",
    )

    submitted = st.form_submit_button(
        "Get Healthcare Guidance",
        type="primary",
    )


# --------------------------------------------------
# 9. Process the submitted symptoms
# --------------------------------------------------

if submitted:

    if not symptoms_text.strip():

        st.error(
            "Please enter at least one symptom."
        )

    else:

        # Screen for potential emergencies first.
        urgent, urgent_messages = emergency_screen(
            symptoms_text
        )

        if urgent:

            st.error(
                "🚨 Potential Emergency Warning"
            )

            for item in urgent_messages:
                st.write(f"• {item}")

            st.markdown(
                "**Please seek emergency medical care now.** "
                "If you are in India, call 112 for emergency "
                "assistance. Do not wait for chatbot results."
            )

            # Stop before running the ordinary assessment.
            st.stop()

        # --------------------------------------------------
        # 10. Run online assessment or offline fallback
        # --------------------------------------------------

        try:

            if api_is_healthy():

                try:

                    symptoms_list = [
                        item.strip()
                        for item in symptoms_text.replace(
                            ";", ","
                        ).split(",")
                        if item.strip()
                    ]

                    result = online_assessment(
                        symptoms=symptoms_list,
                        age=int(age) if age else None,
                        duration=duration,
                        notes=notes.strip(),
                    )

                    source = "Online API"

                except requests.RequestException:

                    result = engine.assess(
                        symptoms_text,
                        duration=duration,
                    )

                    source = (
                        "Local SQLite fallback "
                        "(online request failed)"
                    )

            else:

                result = engine.assess(
                    symptoms_text,
                    duration=duration,
                )

                source = "Local SQLite database"

        except Exception as exc:

            st.error(
                "The assessment could not be completed. "
                "Please try again or contact a healthcare "
                "professional for guidance."
            )

            st.caption(
                f"Technical detail: {type(exc).__name__}"
            )

            st.stop()

        # --------------------------------------------------
        # 11. Display healthcare guidance
        # --------------------------------------------------

        st.divider()

        st.subheader("Healthcare Guidance")

        st.caption(f"Information source: {source}")

        matched_topics = result.get(
            "matched_topics", []
        )

        if matched_topics:

            st.write(
                "**Relevant symptom topics:** "
                + ", ".join(matched_topics)
            )

        st.markdown("### What this may mean")

        st.write(
            result.get(
                "summary",
                "No matching information was found "
                "in the available database.",
            )
        )

        # General self-care information
        self_care = result.get("self_care", [])

        if self_care:

            st.markdown("### General self-care information")

            for item in self_care:
                st.write(f"• {item}")

        # When to seek medical care
        seek_care = result.get("seek_care", [])

        if seek_care:

            st.markdown("### When to seek medical care")

            for item in seek_care:
                st.write(f"• {item}")

        # Project limitations
        limitations = result.get("limitations")

        if limitations:
            st.caption(limitations)

        st.warning(
            "This chatbot provides general educational "
            "information, not a diagnosis. Seek professional "
            "medical advice if symptoms persist, worsen, "
            "or cause concern."
        )


# --------------------------------------------------
# 12. Footer
# --------------------------------------------------

st.divider()

st.caption(
    "Privacy: this starter app does not intentionally "
    "save symptom submissions. Review your backend and "
    "hosting configuration before using real patient data."
)
