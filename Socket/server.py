from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase

app = Flask(__name__)
app.config["SECRET_KEY"] = "faeaggd"
socketio = SocketIO(app)

rooms = {}

def criar_sala(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
            
        if code not in rooms:
            break
        
    return code

@app.route("/", methods=["POST", "GET"])
def principal():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)
        
        if not name:
            return render_template("index.html", error="Insira um nome.", code=code, name=name)
        
        if join != False and not code:
            return render_template("index.html", error="Entre em um chat.", code=code, name=name)
        
        room = code
        if create != False:
            room = criar_sala(4)
            rooms[room] = {"members":0, "messages":[]}
        elif code not in rooms:
            return render_template("index.html", error="A sala não existe.", code=code, name=name)
        
        session["room"] = room
        session["name"] = name
        return redirect(url_for("sala"))
            
    return render_template("index.html")

@app.route("/sala")
def sala():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("principal"))

    return render_template("room.html", code=room, messages=rooms[room]["messages"])

@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return
    
    content = {
        "name": session.get("name"),
        "message" : data["data"]    
    }
    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{session.get('name')} disse: {data['data']}")

@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    
    join_room(room)
    send({"name": name, "message": "entrou no chat"}, to=room)
    rooms[room]["members"] += 1
    print(f"{name} entrou na sala {room}")
    
@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)
    
    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]

    send({"name": name, "message": "saiu do chat"}, to=room)
    print(f"{name} saiu da sala")

if __name__ == "__main__":
    socketio.run(app, debug=True)
    
