import base64
from io import BytesIO
from PIL import Image
import streamlit as st
import requests
import os
from datetime import datetime
from streamlit_cropper import st_cropper
import shutil

URL = "http://localhost:8000/face/" 

st.title('Facial Recognition Testing - Bubble')

if 'param' not in st.session_state:
    st.session_state.param = {}

file_select = st.sidebar.selectbox(
    'File Options',
    ('Upload Face', 'Recognize Faces', "Get Faces")
    
)

if file_select == "Recognize Faces":
    uploaded_file = st.sidebar.file_uploader("Upload image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # Display the uploaded image
        image = Image.open(uploaded_file)
        
        resized_image = image.resize((300, 300))  # width x height

        # Display resized image
        st.image(resized_image, caption="Resized Image", use_column_width=False)

        # Sanitize timestamp for filename (replace ":" with "-")
        date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        os.makedirs("../data/", exist_ok=True)
        st.session_state.param['file_path'] = f'../data/file_{date}.png'

        # Save the uploaded image to disk
        with open(st.session_state.param['file_path'], "wb") as out_file:
            out_file.write(uploaded_file.getbuffer())
            
        

        st.success(f"Image saved to: {st.session_state.param['file_path']}")
        
        
if file_select == "Upload Face":
    uploaded_file = st.sidebar.file_uploader("Upload image", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        image = Image.open(uploaded_file)

        st.write("Draw a box to crop the image")
        cropped_image = st_cropper(
            image,
            aspect_ratio=None,       # Allow free crop
            box_color='blue',
            return_type="image",     # Return cropped PIL image
        )

        # Display original and cropped side by side
        col1, col2 = st.columns(2)

        with col1:
            st.image(image, caption="Original Image", use_column_width=True)

        with col2:
            st.image(cropped_image, caption="Cropped Image", use_column_width=True)

        # Optional: Save cropped image
        if st.button("Save Cropped Image"):
            date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            os.makedirs("../data/", exist_ok=True)
            st.session_state.param['file_path'] = f'../data/file_{date}.png'

            cropped_image.save(st.session_state.param['file_path'])
            st.success("Cropped image saved.")
        
if file_select == "Upload Face":
    name = st.sidebar.text_input("Name of Person", value="")
    
if file_select == "Get Faces":
    person_id = st.sidebar.text_input("UUID of Person", value="")


if st.button("Call API"):

    if file_select == "Recognize Faces" or file_select == "Upload Face":
    

        with open(st.session_state.param['file_path'], "rb") as image_file:
            files = {
                "file": (st.session_state.param['file_path'], image_file, "image/jpeg"),
            }
            data = {}
            
            if file_select == "Upload Face":
                data["name"] = name
            
       
            if file_select == "Upload Face":
                response = requests.post(URL+"save-face/", files=files, data=data)
                
                print("*"*80)
                print("This is the JSON response from the API Call")
                print(response.json())
                print("*"*80)
                
                response_id = response.json().get("id", "No ID returned")
                st.text_input("ID", value=response_id, disabled=True)

            if file_select == "Recognize Faces":
                
                response = requests.post(URL+"facial-recognition/", files=files, data=data)

                
                for i in range(len(response.json()["faces"])):
                    col1, col2 = st.columns([1, 2])

                    with col1:
                        # Decode base64 image and display
                        img_response = base64.b64decode(response.json()["faces"][i])
                        img = Image.open(BytesIO(img_response))
                        st.image(img, caption=f"Face {i+1}", use_column_width=True)

                    with col2:
                        st.markdown(f"**Name:** {response.json()['names'][i]}")
                        if response.json()["backups"][i]:
                            st.markdown("**Other possibilities:**")
                            for alt_name in response.json()["backups"][i]:
                                st.markdown(f"- Name - {alt_name['name']}\n- Confidence - {alt_name['confidence']}\n" + "-"*20)

                                
                        else:
                            st.markdown("_No backups available_")

    if file_select == "Get Faces":
        response = requests.post(URL+"get-faces/", files=files, data=data)
        
        for img_b64 in response.json()["imgs"]:
            img_bytes = base64.b64decode(img_b64)
            img = Image.open(BytesIO(img_bytes))
            st.image(img)
        
        
    