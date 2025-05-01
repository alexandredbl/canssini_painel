from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flaskwebgui import FlaskUI
import numpy as np
import time
import serial
from APC220 import USB_Radio, RF_DataRate, UART_Rate

app = Flask(__name__)
socketio = SocketIO(app)
try:
    port = serial.Serial('COM8', baudrate=9600, timeout=1)
except:
    port = serial.Serial('COM9', baudrate=9600, timeout=1)
port.rts = False
port.dtr = False

dados = []
response = ""

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/config")
def config():
    return render_template("config.html")

@socketio.on("temperature_request")
def handle_request():
    emit(
        "temperature",
        [{"x":dados[i][0]-dados[0][0],"y":dados[i][2]} for i in range(len(dados))]
    )

@socketio.on("pressure_request")
def handle_request():
    emit(
        "pressure",
        [{"x":dados[i][0]-dados[0][0],"y":dados[i][3]} for i in range(len(dados))]
    )

@socketio.on("altitude_request")
def handle_request():
    emit(
        "altitude",
        {
            "h1":[{"x":dados[i][0]-dados[0][0],"y":dados[i][5]} for i in range(len(dados))],
            "h2":[{"x":dados[i][0]-dados[0][0],"y":dados[i][6]} for i in range(len(dados))]
        }
    )

@socketio.on("serial_request")
def handle_request():
    global response, dados, port, table
    while True:
        try:
            l=port.readline().decode("utf-8",errors="ignore")
            break
        except:
            continue
    if l=="": return
    emit("serial_read", "← "+l)
    a=l[1:-2].split(",")
    a, cs = a[0:-1], a[-1]
    if len(a)>=1:
        if a[0]=="DATA":
            a = a[1:]
            for i in range(len(a)):
                try:
                    a[i] = float(a[i])
                except:
                    a[i] = 0
            if len(a)==11:
                dados.append(a)
                with open("dados.csv","a") as table:
                    table.write("{},{},{},{},{},{},{},{},{},{},{}\n".format(*a))
        elif a[0]=="RSP":
            response = l[:-1]

@socketio.on("reboot")
def handle_request():
    global response
    msg=r'{reboot}'
    port.write(msg.encode("utf-8"))
    emit("serial_written","→ "+msg)
    time.sleep(0.1)
    if response=="{RSP,reboot,131}":
        print(response)
        response=""
    else:
        print("No response")

@socketio.on("ping")
def handle_request():
    global response
    msg = r'{ping}'
    port.write(msg.encode("utf-8"))
    emit("serial_written","→ "+msg)
    time.sleep(0.1)
    if response=="{RSP,ping,251}":
        response=""
    else:
        print("No response")

@socketio.on("mode0")
def handle_request():
    global response
    msg = r'{mode,0}'
    port.write(msg.encode("utf-8"))
    emit("serial_written","→ "+msg)
@socketio.on("mode1")
def handle_request():
    global response
    msg = r'{mode,1}'
    port.write(msg.encode("utf-8"))
    emit("serial_written","→ "+msg)
@socketio.on("mode2")
def handle_request():
    global response
    msg = r'{mode,2}'
    port.write(msg.encode("utf-8"))
    emit("serial_written","→ "+msg)

if __name__ == "__main__":

    try:
        
        radio = USB_Radio(port)

        # Read configuration
        radio.enterConfigMode()
        (freq, drate, power, brate, par) = radio.getConfiguration()
        print(f'{freq} kHz; {drate.name}; {power}; {brate.name}; {par}')
        radio.exitConfigMode()
        time.sleep(1)

        if freq != 433550:

            # Configure
            radio.enterConfigMode()
            res = radio.configureRadio(433550, RF_DataRate.RATE_9600, 9, UART_Rate.UART_9600, False)
            print(f'Result: {res}')
            radio.exitConfigMode()
            time.sleep(1)

            # Check config
            radio.enterConfigMode()
            (freq, drate, power, brate, par) = radio.getConfiguration()
            print(f'{freq} kHz; {drate.name}; {power}; {brate.name}; {par}')
            radio.exitConfigMode()
            time.sleep(1)

        FlaskUI(
            app=app,
            socketio=socketio,
            server="flask_socketio",
            width=800,
            height=600,
        ).run()

    finally:
        print("Closing")
        port.close()