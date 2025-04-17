
from fastapi.responses import JSONResponse
from deepface import DeepFace
import os
import cv2
import base64
import time
from fastapi import File, UploadFile, Form

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

def calculate_iou(box1, box2):
    '''Calculates the Intersection over Union (IoU) of two bounding boxes.
    Args:
        box1 (list): The first bounding box, containing the x, y, width, and height.
        box2 (list): The second bounding box, containing the x, y, width, and height.
    Returns:
        float: The IoU value.
    '''
    
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2
    x_inter1 = max(x1, x2)
    y_inter1 = max(y1, y2)
    x_inter2 = min(x1 + w1, x2 + w2)
    y_inter2 = min(y1 + h1, y2 + h2)
    inter_width = max(0, x_inter2 - x_inter1)
    inter_height = max(0, y_inter2 - y_inter1)
    intersection_area = inter_width * inter_height
    box1_area = w1 * h1
    box2_area = w2 * h2

    union_area = box1_area + box2_area - intersection_area

    if union_area == 0:
        return 0  
    
    iou = intersection_area / union_area
    return iou

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

async def identify_face(
    file: UploadFile = File(...),
    modelName: str = Form("VGG-Face") 
):

    contents = await file.read()
    with open("/app/app/api/temp/face_recognized.jpeg", "wb") as f:
        f.write(contents)

    db_path = "/app/app/api/facesDatabase"
    imgPath = "/app/app/api/temp/face_recognized.jpeg"

    # ---------------------------------------------------------- #
    
    faces = []
    names = []
    backupNames = []
    recognized_faces_coords = []  
    try:
        result_list = DeepFace.find(img_path=imgPath, db_path=db_path, model_name=modelName)
        
        if result_list:
            for idx, result_df in enumerate(result_list):
                
                # ---------------------------------------------------------- #

                # Check if a match was found
                if not result_df.empty:
                    matchPath = result_df.iloc[0].identity
                    match = matchPath.split("/")[-2]
                    coords = [result_df.iloc[0].source_x, result_df.iloc[0].source_y, result_df.iloc[0].source_w, result_df.iloc[0].source_h]

                    # gets the next most likely matches in the list (aka backup names)
                    i = 1
                    backups = []
                    prevNames = [match]
                    
                    while len(result_df) > i and len(prevNames) < 4:
                        if i >= len(result_df):
                            break  # Prevent accessing out of range
                        extraMatchPath = result_df.iloc[i].identity
                        extraMatch = extraMatchPath.split("/")[-2]
                        if extraMatch in prevNames:
                            i += 1
                            continue
                        else:
                            confidence = result_df.iloc[i].distance * 100
                            confidence = round(confidence, 2)
                            backups.append({"name": extraMatch, "confidence": confidence})
                            prevNames.append(extraMatch)
                            i += 1

                    # Process the face and extract the sub-image
                    print(coords, "\n", match, "\n")
                    face_image = cv2.imread(imgPath)
                    face_image = face_image[coords[1]:coords[1]+coords[3], coords[0]:coords[0]+coords[2]]
                    # cv2.imwrite(f"/app/app/api/temp/{match}.jpeg", face_image)
                    _, buffer = cv2.imencode('.jpg', face_image)

                    # Encode the image as base64 so it can be returned in JSON
                    encoded_image = base64.b64encode(buffer).decode('utf-8')
                    faces.append(encoded_image)
                    names.append(match)
                    backupNames.append(backups)

                    recognized_faces_coords.append(coords)
                
                # ---------------------------------------------------------- #                
        
        else:
            print("No faces detected")

    except Exception as e:
        if "Face could not be detected" in str(e):
            print("No faces detected")
        else:
            print(f"Error: {str(e)}")

    # ---------------------------------------------------------- #

    # Handles unrecognized faces
    detected_faces = DeepFace.extract_faces(img_path=imgPath, detector_backend='retinaface')
    if detected_faces:
        i = 0
        for face in detected_faces:
            i += 1
            # Get the coordinates for each detected face
            coords = [face["facial_area"]["x"], face["facial_area"]["y"], face["facial_area"]["w"], face["facial_area"]["h"]]
            name = f"No Match {i}"

            # Check if the detected face is already recognized
            start_time = time.time()
            is_recognized = False
            for other_coord in recognized_faces_coords:
                iou = calculate_iou(coords, other_coord)
                print(f"IoU: {iou}")
                if iou >= 0.35:
                    is_recognized = True
            if is_recognized:
                continue  # Skip if the face is already recognized
            print(f"Time elapsed (IoU): {time.time() - start_time} \nis_recognized: {is_recognized}")

            # Process the face and extract the sub-image
            print(coords, "\n")
            face_image = cv2.imread(imgPath)
            face_image = face_image[coords[1]:coords[1]+coords[3], coords[0]:coords[0]+coords[2]]
            # cv2.imwrite(f"/app/app/api/temp/{name}.jpeg", face_image)
            _, buffer = cv2.imencode('.jpg', face_image)

            # Encode the image as base64 so it can be returned in JSON
            encoded_image = base64.b64encode(buffer).decode('utf-8')
            faces.append(encoded_image)
            names.append(name)
            backupNames.append([{"name": "No Match", "confidence": 0}])

    else:
        print("\n", "No faces detected", "\n")

    # --------------------------------------- #

    return JSONResponse(content={
        "faces": faces,
        "names": names,
        "backups": backupNames
    })
