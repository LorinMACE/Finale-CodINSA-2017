from flask import Flask,request,render_template,send_from_directory
import mmap,json,os,time
from telemetry import telemetry

app = Flask(__name__,static_url_path='')

filename = "kb.txt"
sharememFile= "ManiaPlanet_Telemetry"
command = ""

def writeCommand(command):
    f = open(filename,'wb')
    f.write(command)
    f.close()

@app.route('/datas')
def datas():
    shm = mmap.mmap(0, 4096, sharememFile)
    if not shm:
        return "No data"
    else:
        t = telemetry(shm)
        shm.close()
        content,code = t.makeResponse()
        return content,code

@app.route('/')
def main():
    return render_template('mainpage.html')

@app.route('/map')
def map():
    return render_template('map.html')

@app.route('/TilesApi/<path:path>')
def send_static_tiles(path):
    return send_from_directory('TilesApi', path)

@app.route('/command')
def command():
    if 'c' in request.args:
        command = request.args.get("c")
        command = int("U" in command) + 2*int("D" in command) + 4*int("L" in command)+ 8*int("R" in command)
    else:
        command = 0
    writeCommand(str(command))
    return 'ok',200


@app.route('/exit')
def exit():
    writeCommand('q')
    return 'ok',200

@app.route('/reset')
def treset():
    writeCommand("r")
    time.sleep(0.005)
    writeCommand(str(1)) # Up apres restart
    return 'ok',200

@app.route('/track')
def track():
    if 't' in request.args:
        elem = request.args.get("t")
        filena = elem+".txt"
        path = "tracks/"+filena
        if filena in os.listdir("tracks"):
            contents = open(path).read().split('\n')
            blocs = []
            for bloc in contents:
                try:
                    x,y,z,name,rot = bloc.split(";")
                    bloc = {
                        "Type":name,
                        "X":int(x),
                        "Y":int(y),
                        "Z":int(z),
                        "Rot":int(rot)
                    }
                    blocs.append(bloc)
                except:
                    pass
            return json.dumps(blocs),200
        else:
            return "Not Found",404
    return 'no arg "t"',401

if __name__ == '__main__':
    app.run(port=8087)
