# Reconhecimento Facial

Para fazer a substituição do modelo de reconhecimento facial com python, é necessário trocar a função `identify_face` dentro da file `identify_face.py`. 
Essa função recebe:
- file: UploadFile = File(...)
- modelName: str

Atualmente, `modelName` indica o modelo utilizado pela biblioteca `deepface`, que permite o usuário utilizar diferentes modelos de reconhecimento sem substituir o backend manualmente. Os modelos são: VGG-Face, Facenet, OpenFace, DeepFace, DeepID, ArcFace e Dlib.

O `file` é a imagem com os rostos a serem reconhecidos. 

Essa função retorna um dicionario com 3 chaves contendo listas:
- faces: [File(...)]
- names: [str]
- backups: [[str]]

As linhas de codigo abaixo deverão ser mantidas, para acesso a database de rostos e salvamento da imagem no disco:

``` python
async def identify_face(
    file: UploadFile = File(...),
    modelName: str = Form("VGG-Face") 
):

    contents = await file.read()
    with open("/app/app/api/temp/face_recognized.jpeg", "wb") as f:
        f.write(contents)

    db_path = "/app/app/api/facesDatabase"
    imgPath = "/app/app/api/temp/face_recognized.jpeg"

    # outra funcionalidade/modelo entraria aqui

    return JSONResponse(content={
        "faces": faces,
        "names": names,
        "backups": backupNames
    })
```

Caso seja necessário usar outra lingua de preogramação ou backend completo, a rota utilizada é `/face/facial-recognition/`. Os argumentos recebidos por essa rota (vindos do front-end) são os mesmo que o acima. 



