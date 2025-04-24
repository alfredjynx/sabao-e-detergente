import os
import base64

def get_faces(img_id):
    try:
        dir_path = f'/app/app/api/facesDatabase/{img_id}'
        
        if not os.path.exists(dir_path):
            return {"error": f"Directory for ID '{img_id}' not found."}

        imgs = os.listdir(dir_path)
        imgs = [img for img in imgs if img.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]

        encoded_imgs = []
        for img in imgs:
            img_path = os.path.join(dir_path, img)
            with open(img_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
                encoded_imgs.append(encoded_string)

        return {"imgs": encoded_imgs}
    
    except Exception as e:
        return {"error": str(e)}
