from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
import pymysql
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import os
from Blockchain import *
from Block import *
from datetime import date
import cv2
import numpy as np
import base64
import random
from datetime import datetime
from PIL import Image



global username, password, contact, email, address

blockchain = Blockchain()
if os.path.exists('blockchain_contract.txt'):
    with open('blockchain_contract.txt', 'rb') as fileinput:
        blockchain = pickle.load(fileinput)
    fileinput.close()

face_detection = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
recognizer = cv2.face_LBPHFaceRecognizer.create()

def AddParty(request):
    if request.method == 'GET':
       return render(request, 'AddParty.html', {})

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

def Login(request):
    if request.method == 'GET':
       return render(request, 'Login.html', {})

def CastVote(request):
    if request.method == 'GET':
       return render(request, 'CastVote.html', {})
    

def Register(request):
    if request.method == 'GET':
       return render(request, 'Register.html', {})

def Admin(request):
    if request.method == 'GET':
       return render(request, 'Admin.html', {})
    
def WebCam(request):
    if request.method == 'POST':
        imgstr = request.POST.get('image')

        format, imgstr = imgstr.split(';base64,')
        data = base64.b64decode(imgstr)

        file_path = "EVotingApp/static/photo/test.png"

        if os.path.exists(file_path):
            os.remove(file_path)

        with open(file_path, 'wb') as f:
            f.write(data)

        return HttpResponse("Image saved successfully")    

def checkUser(name):
    flag = 0
    for i in range(len(blockchain.chain)):
          if i > 0:
              b = blockchain.chain[i]
              data = b.transactions[0]
              print(data)
              arr = data.split("#")
              if arr[0] == name:
                  flag = 1
                  break
    return flag            

def getOutput(status):
    output = '<h3><br/>'+status+'<br/><table border=1 align=center>'
    output+='<tr><th><font size=3 color=black>Candidate Name</font></th>'
    output+='<th><font size=3 color=black>Party Name</font></th>'
    output+='<th><font size=3 color=black>Area Name</font></th>'
    output+='<th><font size=3 color=black>Image</font></th>'
    output+='<th><font size=3 color=black>Cast Vote Here</font></th></tr>'
    con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'evoting',charset='utf8')
    with con:
        cur = con.cursor()
        cur.execute("select * FROM addparty")
        rows = cur.fetchall()
        for row in rows:
            cname = row[0]
            pname = str(row[1])
            area = row[2]
            image = row[3]
            output+='<tr><td><font size=3 color=black>'+cname+'</font></td>'
            output+='<td><font size=3 color=black>'+pname+'</font></td>'
            output+='<td><font size=3 color=black>'+area+'</font></td>'
            output+='<td><img src="/static/parties/'+cname+'.png" width=200 height=200></img></td>'
            output+='<td><a href="FinishVote?id='+cname+'"><font size=3 color=black>Click Here</font></a></td></tr>'
    output+="</table><br/><br/><br/><br/><br/><br/>"        
    return output      
    

def FinishVote(request):
    if request.method == 'GET':
        global username
        cname = request.GET.get('id', False)
        voter = ''
        today = date.today()
        data = str(username)+"#"+str(cname)+"#"+str(today)
        blockchain.add_new_transaction(data)
        hash = blockchain.mine()
        b = blockchain.chain[len(blockchain.chain)-1]
        print("Previous Hash : "+str(b.previous_hash)+" Block No : "+str(b.index)+" Current Hash : "+str(b.hash))
        bc = "Previous Hash : "+str(b.previous_hash)+"<br/>Block No : "+str(b.index)+"<br/>Current Hash : "+str(b.hash)
        blockchain.save_object(blockchain,'blockchain_contract.txt')
        context= {'data':'<font size=3 color=black>Your Vote Accepted<br/>'+bc}
        return render(request, 'UserScreen.html', context)
    
def getUserImages():
    names = []
    ids = []
    faces = []
    
    dataset = "EVotingApp/static/profiles"

    if not os.path.exists(dataset):
        print("Dataset folder not found")
        return names, ids, faces

    count = 0

    for file in os.listdir(dataset):
        file_path = os.path.join(dataset, file)

        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
            try:
                pilImage = Image.open(file_path).convert('L')
                imageNp = np.array(pilImage, 'uint8')

                name = os.path.splitext(file)[0]

                names.append(name)
                faces.append(imageNp)
                ids.append(count)

                count += 1

            except Exception as e:
                print("Error loading image:", file, e)

    print("Loaded:", names, ids)
    return names, ids, faces       


def getName(predict, ids, names):
    name = "Unable to get name"
    for i in range(len(ids)):
        if ids[i] == predict:
            name = names[i]
            break
    return name    

def ValidateUser(request):
    if request.method == 'POST':
        global username

        img_path = 'EVotingApp/static/photo/test.png'

        if not os.path.exists(img_path):
            return render(request, 'UserScreen.html', {'data': 'No image captured'})

        img = cv2.imread(img_path)

        if img is None:
            return render(request, 'UserScreen.html', {'data': 'Image not readable'})

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        detected_faces = face_detection.detectMultiScale(
            gray, scaleFactor=1.3, minNeighbors=5
        )

        if len(detected_faces) == 0:
            return render(request, 'UserScreen.html', {'data': 'No face detected'})

        # Take largest face
        (x, y, w, h) = sorted(
            detected_faces,
            key=lambda f: f[2] * f[3],
            reverse=True
        )[0]

        face_component = gray[y:y+h, x:x+w]

        # Load dataset
        names, ids, training_faces = getUserImages()

        if len(training_faces) == 0:
            return render(request, 'UserScreen.html', {'data': 'No training data found. Please register users first.'})

        # Train model safely
        recognizer.train(training_faces, np.array(ids))

        predict, conf = recognizer.predict(face_component)

        print("Prediction:", predict, "Confidence:", conf)

        if conf < 80:
            detected_name = getName(predict, ids, names)

            if detected_name == username:
                flag = checkUser(username)

                if flag == 0:
                    output = getOutput("User predicted as : " + username + "<br/><br/>")
                    return render(request, 'VotePage.html', {'data': output})
                else:
                    return render(request, 'UserScreen.html', {'data': 'You already casted your vote'})
        
        return render(request, 'UserScreen.html', {'data': 'Face not matched. Try again'})
        

def getCount(name):
    count = 0
    for i in range(len(blockchain.chain)):
          if i > 0:
              b = blockchain.chain[i]
              data = b.transactions[0]
              arr = data.split("#")
              if arr[1] == name:
                  count = count + 1
                  break
    return count

def ViewVotes(request):
    if request.method == 'GET':
        output = '<table border=1 align=center>'
        output+='<tr><th><font size=3 color=black>Candidate Name</font></th>'
        output+='<th><font size=3 color=black>Party Name</font></th>'
        output+='<th><font size=3 color=black>Area Name</font></th>'
        output+='<th><font size=3 color=black>Image</font></th>'
        output+='<th><font size=3 color=black>Vote Count</font></th>'
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'evoting',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * FROM addparty")
            rows = cur.fetchall()
            for row in rows:
                cname = row[0]
                count = getCount(cname)
                pname = str(row[1])
                area = row[2]
                image = row[3]
                output+='<tr><td><font size=3 color=black>'+cname+'</font></td>'
                output+='<td><font size=3 color=black>'+pname+'</font></td>'
                output+='<td><font size=3 color=black>'+area+'</font></td>'
                output+='<td><img src="/static/parties/'+cname+'.png" width=200 height=200></img></td>'
                output+='<td><font size=3 color=black>'+str(count)+'</font></td></tr>'
        output+="</table><br/><br/><br/><br/><br/><br/>"        
        context= {'data':output}
        return render(request, 'ViewVotes.html', context)    
            
def ViewParty(request):
    if request.method == 'GET':
        output = '<table border=1 align=center>'
        output+='<tr><th><font size=3 color=black>Candidate Name</font></th>'
        output+='<th><font size=3 color=black>Party Name</font></th>'
        output+='<th><font size=3 color=black>Area Name</font></th>'
        output+='<th><font size=3 color=black>Image</font></th>'
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'evoting',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * FROM addparty")
            rows = cur.fetchall()
            for row in rows:
                cname = row[0]
                pname = str(row[1])
                area = row[2]
                image = row[3]
                output+='<tr><td><font size=3 color=black>'+cname+'</font></td>'
                output+='<td><font size=3 color=black>'+pname+'</font></td>'
                output+='<td><font size=3 color=black>'+area+'</font></td>'
                output+='<td><img src="/static/parties/'+cname+'.png" width=200 height=200></img></td></tr>'
        output+="</table><br/><br/><br/><br/><br/><br/>"        
        context= {'data':output}
        return render(request, 'ViewParty.html', context)    

def AddPartyAction(request):
    if request.method == 'POST':
      cname = request.POST.get('t1', False)
      pname = request.POST.get('t2', False)
      area = request.POST.get('t3', False)
      myfile = request.FILES['t4']

      fs = FileSystemStorage()
      filename = fs.save('EVotingApp/static/parties/'+cname+'.png', myfile)
      
      db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'evoting',charset='utf8')
      db_cursor = db_connection.cursor()
      student_sql_query = "INSERT INTO addparty(candidatename,partyname,areaname,image) VALUES('"+cname+"','"+pname+"','"+area+"','"+cname+"')"
      db_cursor.execute(student_sql_query)
      db_connection.commit()
      print(db_cursor.rowcount, "Record Inserted")
      if db_cursor.rowcount == 1:
       context= {'data':'Party Details Added'}
       return render(request, 'AddParty.html', context)
      else:
       context= {'data':'Error in adding party details'}
       return render(request, 'AddParty.html', context)    

def saveSignup(request):
    if request.method == 'POST':
        global username, password, contact, email, address

        img = cv2.imread('EVotingApp/static/photo/test.png')

        if img is None:
            return render(request, 'Register.html', {'data': 'Image not captured properly'})

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = face_detection.detectMultiScale(gray, 1.3, 5)

        if len(faces) == 0:
            return render(request, 'Register.html', {'data': 'No face detected. Try again'})

        (x, y, w, h) = faces[0]
        face_component = gray[y:y+h, x:x+w]

        save_path = 'EVotingApp/static/profiles/' + username + '.png'
        cv2.imwrite(save_path, face_component)

        db_connection = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password='root',
            database='evoting',
            charset='utf8'
        )

        db_cursor = db_connection.cursor()

        query = "INSERT INTO register(username,password,contact,email,address) VALUES(%s,%s,%s,%s,%s)"
        db_cursor.execute(query, (username, password, contact, email, address))

        db_connection.commit()

        return render(request, 'Register.html', {'data': 'Signup Completed'})


def Signup(request):
    if request.method == 'POST':
      global username, password, contact, email, address
      username = request.POST.get('username', False)
      password = request.POST.get('password', False)
      contact = request.POST.get('contact', False)
      email = request.POST.get('email', False)
      address = request.POST.get('address', False)
      context= {'data':'Capture Your face'}
      return render(request, 'CaptureFace.html', context)
      
def AdminLogin(request):
    if request.method == 'POST':
        global username
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        if username == 'admin' and password == 'admin':
            context= {'data':'Welcome '+username}
            return render(request, 'AdminScreen.html', context)
        if status == 'none':
            context= {'data':'Invalid login details'}
            return render(request, 'Admin.html', context)

def UserLogin(request):
    if request.method == 'POST':
        global username
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        status = 'none'
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'evoting',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * FROM register")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == username and row[1] == password:
                    status = 'success'
                    break
        if status == 'success':
            context= {'data':'<center><font size="3" color="black">Welcome '+username+'<br/><br/><br/><br/><br/>'}
            return render(request, 'UserScreen.html', context)
        else:
            context= {'data':'Invalid login details'}
            return render(request, 'Login.html', context)





        
            
