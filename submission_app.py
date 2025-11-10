import streamlit as st
import os
import zipfile
import io

# -----------------------
# Config
# -----------------------

SAVE_DIR = "Submissions"
os.makedirs(SAVE_DIR, exist_ok=True)

# Prefer secret in Streamlit Cloud; fallback to placeholder
TEACHER_PASS = st.secrets.get("TEACHER_PASS", "rl4inv")

# -----------------------
# UI: student submission
# -----------------------

st.title("RL Assignment Submission Portal")

st.write("""
Please enter your **group name** and upload your code file below.
Your file will be saved automatically with your ID.
""")

# Input for group name
student_id = st.text_input("Group name (required)")

# File uploader
uploaded_file = st.file_uploader("Upload your assignment file:", type=["py", "ipynb", "zip", "txt"])

# Submit button
if st.button("Submit"):
    if not student_id.strip():
        st.error("Please enter your group name before submitting.")
    elif uploaded_file is None:
        st.error("Please upload a file before submitting.")
    else:
        # Create unique filename: GroupName + original extension
        filename = f"{student_id.strip()}{os.path.splitext(uploaded_file.name)[1]}"
        save_path = os.path.join(SAVE_DIR, filename)

        # Save uploaded file
        with open(save_path, "wb") as f:
            f.write(uploaded_file.read())

        st.success(f"Submission saved as `{filename}` ✅")
        st.info("Thank you! You can now close this page.")

# -----------------------
# Teacher login + download (restricted)
# -----------------------

if "teacher_authenticated" not in st.session_state:
    st.session_state.teacher_authenticated = False

st.write("---")
st.subheader("Submission Access Request (instructor only)")

if not st.session_state.teacher_authenticated:
    with st.form("teacher_login_form"):
        teacher_pass = st.text_input("Enter teacher password:", type="password")
        login = st.form_submit_button("Login")
        if login:
            if teacher_pass == TEACHER_PASS:
                st.session_state.teacher_authenticated = True
                st.success("Authenticated — you can now download submissions.")
            else:
                st.error("Invalid password.")
else:
    st.success("Teacher authenticated ✅")

    if st.button("🔄 Refresh submissions"):
        st.rerun()

    files = os.listdir(SAVE_DIR)
    if not files:
        st.info("No submissions yet.")
    else:
        # Build ZIP archive in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for fname in files:
                zf.write(os.path.join(SAVE_DIR, fname), arcname=fname)
        zip_buffer.seek(0)

        st.download_button(
            label="⬇️ Download all submissions (ZIP)",
            data=zip_buffer.getvalue(),
            file_name="submissions.zip",
            mime="application/zip"
        )
