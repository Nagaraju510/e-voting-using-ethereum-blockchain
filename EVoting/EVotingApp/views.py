from django.shortcuts import render
import pymysql
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import os
import pickle
from Blockchain import *
from Block import *
from datetime import date
import cv2
import numpy as np
import base64
from PIL import Image

global username, password, contact, email, address

# ---------------- BLOCKCHAIN ---------------- #

blockchain = Blockchain()
if os.path.exists('blockchain_contract.txt'):
    with open('blockchain_contract.txt', 'rb') as fileinput:
        blockchain = pickle.load(fileinput)

# ---------------- OPENCV ---------------- #

face_detection = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
recognizer = cv2.face.LBPHFaceRecognizer_create()

# ---------------- BASIC PAGES ---------------- #

def index(request):
    return render(request, 'index.html')

def Login(request):
    return render(request, 'Login.html')

def Register(request):
    return render(request, 'Register.html')

def Admin(request):
    return render(request, 'Admin.html')

def AddParty(request):
    return render(request, 'AddParty.html')

def CastVote(request):
    return render(request, 'CastVote.html')

def ViewParty(request):
    return render(request, 'ViewParty.html')

def ViewVotes(request):
    return render(request, 'ViewVotes.html')

# ---------------- WEBCAM ---------------- #

def WebCam(request):
    if request.method == 'POST':
        data = request.POST.get('image')
        format, imgstr = data.split(';base64,')
        imgdata = base64.b64decode(imgstr)

        path = "EVotingApp/static/photo/test.png"

        if os.path.exists(path):
            os.remove(path)

        with open(path, 'wb') as f:
            f.write(imgdata)

        return HttpResponse("Image saved")

# ---------------- DATABASE ---------------- #

def getConnection():
    return pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='root',
        database='evoting',
        charset='utf8'
    )

# ---------------- BLOCKCHAIN ---------------- #

def checkUser(name):
    for i in range(1, len(blockchain.chain)):
        data = blockchain.chain[i].transactions[0]
        if data.split("#")[0] == name:
            return 1
    return 0

def FinishVote(request):
    global username

    cname = request.GET.get('id')
    today = date.today()

    data = f"{username}#{cname}#{today}"

    blockchain.add_new_transaction(data)
    blockchain.mine()

    b = blockchain.chain[-1]
    blockchain.save_object(blockchain, 'blockchain_contract.txt')

    return render(request, 'UserScreen.html', {
        'data': f"Vote Accepted<br/>Block No: {b.index}<br/>Hash: {b.hash}"
    })

# ---------------- FACE RECOGNITION ---------------- #

def getUserImages():
    names, ids, faces = [], [], []
    dataset = "EVotingApp/static/profiles"

    if not os.path.exists(dataset):
        return names, ids, faces

    files = os.listdir(dataset)
    unique_names = {}
    current_id = 0

    for file in files:
        path = os.path.join(dataset, file)

        try:
            image = Image.open(path).convert('L')
            imageNp = np.array(image, 'uint8')

            if imageNp is None or imageNp.size == 0:
                continue

            name = os.path.splitext(file)[0].split("_")[0]

            if name not in unique_names:
                unique_names[name] = current_id
                current_id += 1

            ids.append(unique_names[name])
            names.append(name)
            faces.append(imageNp)

        except:
            continue

    return names, ids, faces


def getName(predict, ids, names):
    for i in range(len(ids)):
        if ids[i] == predict:
            return names[i]
    return "Unknown"

# ---------------- VALIDATE USER ---------------- #

def ValidateUser(request):
    global username

    img = cv2.imread('EVotingApp/static/photo/test.png')

    if img is None:
        return render(request, 'UserScreen.html', {'data': 'No image found'})

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_detection.detectMultiScale(gray, 1.3, 5)

    if len(faces) == 0:
        return render(request, 'UserScreen.html', {'data': 'Face not detected'})

    (x, y, w, h) = faces[0]
    face_component = gray[y:y+h, x:x+w]

    names, ids, training_faces = getUserImages()

    if len(training_faces) < 2:
        return render(request, 'UserScreen.html', {
            'data': 'Not enough training data'
        })

    recognizer.train(training_faces, np.array(ids))

    try:
        predict, conf = recognizer.predict(face_component)
    except:
        return render(request, 'UserScreen.html', {'data': 'Prediction failed'})

    if conf < 80:
        detected_name = getName(predict, ids, names)

        if detected_name == username:

            if checkUser(username) == 1:
                return render(request, 'UserScreen.html', {'data': "Already voted"})

            # ✅ LOAD CANDIDATES FOR VOTING PAGE
            con = getConnection()
            cur = con.cursor()

            cur.execute("SELECT candidatename, partyname, areaname FROM addparty")
            rows = cur.fetchall()

            candidates = []
            for row in rows:
                candidates.append({
                    'cname': row[0],
                    'pname': row[1],
                    'area': row[2],
                    'image': f"/static/parties/{row[0]}.png"
                })

            return render(request, 'VotePage.html', {'candidates': candidates})

    return render(request, 'UserScreen.html', {'data': 'Face mismatch'})

# ---------------- USER AUTH ---------------- #

def Signup(request):
    global username, password, contact, email, address

    username = request.POST.get('username')
    password = request.POST.get('password')
    contact = request.POST.get('contact')
    email = request.POST.get('email')
    address = request.POST.get('address')

    return render(request, 'CaptureFace.html')


def saveSignup(request):
    global username, password, contact, email, address

    img = cv2.imread('EVotingApp/static/photo/test.png')

    if img is None:
        return render(request, 'Register.html', {'data': 'No image captured'})

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_detection.detectMultiScale(gray, 1.3, 5)

    if len(faces) == 0:
        return render(request, 'Register.html', {'data': 'Face not detected'})

    (x, y, w, h) = faces[0]
    face = gray[y:y+h, x:x+w]

    dataset_path = "EVotingApp/static/profiles"

    if not os.path.exists(dataset_path):
        os.makedirs(dataset_path)

    # ✅ SAVE MULTIPLE IMAGES
    for i in range(5):
        cv2.imwrite(f"{dataset_path}/{username}_{i}.png", face)

    con = getConnection()
    cur = con.cursor()

    cur.execute(
        "INSERT INTO register VALUES (%s,%s,%s,%s,%s)",
        (username, password, contact, email, address)
    )

    con.commit()

    return render(request, 'Register.html', {'data': 'Signup Successful'})


def UserLogin(request):
    global username

    username = request.POST.get('username')
    password = request.POST.get('password')

    con = getConnection()
    cur = con.cursor()

    cur.execute("SELECT * FROM register WHERE username=%s AND password=%s", (username, password))

    if cur.fetchone():
        return render(request, 'UserScreen.html', {'data': f'Welcome {username}'})
    else:
        return render(request, 'Login.html', {'data': 'Invalid login'})

def AddPartyAction(request):
    cname = request.POST.get('t1')
    pname = request.POST.get('t2')
    area = request.POST.get('t3')
    file = request.FILES['t4']

    fs = FileSystemStorage()
    fs.save(f'EVotingApp/static/parties/{cname}.png', file)

    con = getConnection()
    cur = con.cursor()

    cur.execute(
        "INSERT INTO addparty VALUES (%s,%s,%s,%s)",
        (cname, pname, area, cname)
    )

    con.commit()

    return render(request, 'AddParty.html', {'data': 'Party Added'})

def AdminLogin(request):
    username = request.POST.get('username')
    password = request.POST.get('password')

    if username == 'admin' and password == 'admin':
        return render(request, 'AdminScreen.html', {'data': 'Welcome Admin'})
    else:
        return render(request, 'Admin.html', {'data': 'Invalid login'})


def ViewParty(request):
    con = getConnection()
    cur = con.cursor()

    cur.execute("SELECT candidatename, partyname, areaname FROM addparty")
    rows = cur.fetchall()

    candidates = []
    for row in rows:
        candidates.append({
            'cname': row[0],
            'pname': row[1],
            'area': row[2],
            'image': f"/static/parties/{row[0]}.png"
        })

    return render(request, 'ViewParty.html', {'candidates': candidates})