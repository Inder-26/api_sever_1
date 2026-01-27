import streamlit as st
import requests
from PIL import Image
import pandas as pd
import os
# FastAPI URL
GENERATE_CAPTION_URL = "https://python-intern.onrender.com/generate_caption"

# Create the Streamlit interface
st.set_page_config(page_title="Generate jwellery descriptions", layout="wide")
st.title("Generate jwellery descriptions")
# Allow user to upload multiple images
uploaded_files = st.file_uploader("Upload images", type=['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff'], accept_multiple_files=True)

# Initialize a session state to keep track of uploaded images
if 'images' not in st.session_state:
    st.session_state.images = []

# Add newly uploaded images to the session state
if uploaded_files:
    for uploaded_file in uploaded_files:
        # Avoid adding duplicates
        if uploaded_file not in st.session_state.images:
            st.session_state.images.append(uploaded_file)

# Show uploaded images with the option to remove them
if st.session_state.images:
    cols = st.columns(5)  # Create a column for each image
    for i, img in enumerate(st.session_state.images):
        with cols[i%5]:
            st.image(img, caption=img.name, width=150)
            

# Button to generate captions
if st.button("Generate Captions"):
    if st.session_state.images:
        all_results = []
        progress_bar = st.progress(0)
        
        for idx, img in enumerate(st.session_state.images):
            # Reset pointer to ensured read from start if needed, though streamlit uploads are handled differently
            # img.seek(0) 
            
            # Prepare payload for single image
            files = {'file': (img.name, img, img.type)}
            data = {'type': jewellery_type}
            
            try:
                response = requests.post(GENERATE_CAPTION_URL, files=files, data=data)
                
                if response.status_code == 200:
                    result = response.json()
                    all_results.append(result)
                else:
                    st.error(f"Error processing {img.name}: {response.text}")
            except Exception as e:
                st.error(f"Failed to connect for {img.name}: {str(e)}")
            
            progress_bar.progress((idx + 1) / len(st.session_state.images))

        if all_results:
            output_file = "output.csv"
            df = pd.DataFrame(all_results)
            df.to_csv(output_file, index=False)

            # Store response and DataFrame in session state
            st.session_state.df = df
            st.table(st.session_state.df)

            # Provide a download button for the user to download the CSV
            with open(output_file, "rb") as f:
                st.download_button("Download CSV", f, file_name="gemini_output.csv", mime="text/csv")
            
            # Optionally clean up the file after download
            if os.path.exists(output_file):
                os.remove(output_file)
    else:
        st.error("Please upload images.")



