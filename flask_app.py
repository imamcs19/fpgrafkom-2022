from flask import Flask,render_template,flash, Response, redirect,url_for,session,logging,request,jsonify
from flask import make_response, json
# from flask_ngrok import run_with_ngrok # Alternatif Ngrok => Heroku / PythonAnywhere / https://labs.play-with-docker.com / AWS / GCP / Azure/ eval_js dari Colab (agak terbatas) / etc
import sqlite3
from flask_cors import CORS

from requests.packages.urllib3.exceptions import ProtocolError
from collections import OrderedDict
from operator import itemgetter
from textblob import TextBlob

# from tweepy import OAuthHandler, API, Stream
from tweepy.streaming import StreamListener

import tweepy
import re
import string
import datetime
import json


import joblib


from flask import send_file
from io import BytesIO

from flask_wtf.file import FileField
from wtforms import SubmitField
# from flask_wtf import Form
from flask_wtf import FlaskForm

# untuk game sekak
from flask_socketio  import SocketIO, emit, join_room, close_room
import chess
import uuid
import secrets
# import json
import os

# => terkendala socket.io tdk jalan di PythonAnywhere => alternatif deploy di heroku atau di local komputer
SOCKET_URL = os.environ.get('SOCKET_URL')
if SOCKET_URL is None:
    SOCKET_URL = "http://localhost:5000/"
    # SOCKET_URL = "https://grafkomku.pythonanywhere.com/"

print("Socket URL: " + SOCKET_URL)


# untuk game tic tac toe
from pusher import pusher

pusher = pusher_client = pusher.Pusher(
  app_id='1438025',
  key='6cbaada072aee9628f09',
  secret='eb0a40a10746305b4b40',
  cluster='ap1',
  ssl=True
)

# pusher = pusher_client = pusher.Pusher(
#   app_id='PUSHER_APP_ID',
#   key='PUSHER_APP_KEY',
#   secret='PUSHER_APP_SECRET',
#   cluster='PUSHER_APP_CLUSTER',
#   ssl=True
# )

name = ''



app = Flask(__name__, static_folder='static')
# run_with_ngrok(app)  # Start ngrok when app is run
# CORS(app)
CORS(app, resources=r'/api/*')
# CORS(app, resources=r'/*')
# CORS(app)

# app.debug = False
app.secret_key = 'graf^&&*(&^(BJH#BJH#G#VB#Bey89nkGBGUY_ap938255bnkerfuyfsdfbsdmnfsdfpkom'

# app.secret_key = secrets.token_bytes(32) # used to cryptographically sign session cookies

# socket = SocketIO(app, cors_allowed_origins="*")
# Single entry in rooms:
#
# <room key> : {
#   'world': <name of world>,
#   'board': <chess.Board>,
#   'users': {
#       <name>: <position ([x, y, z])>,
#       ...
#   },
#   'info': {
#       'white': <name of white player>,
#       'black': <name of black player>,
#       'num_users': <number of users in room>
#   }
# }
class State:
    rooms = {}

############ start Flask routes tic tac toe: ############
@app.route('/')
def ttt_index():
  return render_template('ttt_index.html')

@app.route('/play')
def play():
  global name
  name = request.args.get('username')
  return render_template('ttt_play.html')

@app.route("/pusher/auth", methods=['POST'])
def pusher_authentication():
  auth = pusher.authenticate(
    channel=request.form['channel_name'],
    socket_id=request.form['socket_id'],
    custom_data={
      u'user_id': name,
      u'user_info': {
        u'role': u'player'
      }
    }
  )
  return json.dumps(auth)


############ end Flask routes tic tac toe: ############

############ start Flask routes sekak: ############

# @app.route('/catur')
# @app.route('/')
@app.route('/catur_index')
def catur_index():
    return render_template('catur_index.html')

# contoh game sekak atau catur
@app.route('/gim')
def draw_catur():
    return SOCKET_URL

@app.route('/<room_key>')
def game(room_key):
    if room_key in State.rooms:
        session['room_key'] = room_key
        world = State.rooms[room_key]['world']
        return render_template('catur_game.html', room_key=room_key, world=world, socket_url=SOCKET_URL)
    else:
        return 'Game does not exist', 404

@app.route('/get_room', methods=['GET'])
def get_room():
    room_key = request.values.get("roomKey")
    if room_key in State.rooms:
        return 'success'
    else:
        return ''

@app.route('/create_room', methods=['POST'])
def create_room():
    world = request.values.get("world")

    # delete any rooms with no users
    for key in list(State.rooms.keys()):
        if State.rooms[key]['info']['num_users'] == 0:
            del State.rooms[key]
            print('Room {} closed!'.format(key))

    # create new room
    room_key = uuid.uuid1().hex[:6].upper()
    session['room_key'] = room_key
    State.rooms[room_key] = { 'world': world, 'board': chess.Board(), 'users': {}, 'info': { 'white': '', 'black': '', 'num_users': 0 } }
    print('Room {} added!'.format(room_key))
    return room_key

@app.route('/validate_name', methods=['POST'])
def validate_name():
    room_key = request.values.get("roomKey")
    name = request.values.get("name")
    if name in State.rooms[room_key]['users']:
        return ''
    return 'success'


############ SocketIO handlers: ############

# # sent everytime board updates
# def send_board(room_key):
#     board_fen = State.rooms[room_key]['board'].fen()
#     emit('board', board_fen, room=room_key)

# # sent when game is drawn (3 fold repetition, 50 move rule)
# def send_draw(room_key):
#     if (State.rooms[room_key]['board'].can_claim_draw()):
#         emit('draw', room=room_key)

# # sent once when page loads, and everytime a user joins room
# def send_info(room_key):
#     emit('info', State.rooms[room_key]['info'], room=room_key)

# # sent everytime a user moves
# def send_users(room_key):
#     emit('users', State.rooms[room_key]['users'], room=room_key)

# @socket.on('join_room')
# def on_join(data):
#     name = data['name']
#     session['name'] = name
#     room_key = data['roomKey']
#     join_room(room_key)

#     room = State.rooms[room_key]
#     room['users'][name] = (0, 0, 0)

#     info = room['info']
#     info['num_users'] += 1
#     if info['white'] == '':
#         info['white'] = name
#     elif info['black'] == '':
#         info['black'] = name

#     send_info(room_key)

#     # send board only to user who joined
#     client = request.sid
#     board_fen = State.rooms[room_key]['board'].fen()
#     emit('init_board', board_fen, room=client)

#     send_draw(room_key)
#     emit('user_joined', {'username': name, 'numUsers': info['num_users']}, room=room_key)

# # user automatically leaves room when disconnecting
# @socket.on('disconnect')
# def on_disconnect():
#     room_key = session['room_key']
#     room = State.rooms[room_key]
#     info = room['info']
#     if 'name' in session:
#         name = session['name']
#         info['num_users'] -= 1
#         if info['white'] == name:
#             info['white'] = ''
#         elif info['black'] == name:
#             info['black'] = ''

#         del room['users'][name]

#         send_info(room_key)
#         emit('user_left', {'username': name, 'numUsers': info['num_users']}, room=room_key)

#     # empty session globals
#     if 'name' in session:
#         session['name'] = ''
#     if 'room_key' in session:
#         session['room_key'] = ''

#     # if no clients in room, close room
#     if info['num_users'] == 0:
#         close_room(room_key)
#         del State.rooms[room_key]
#         print('Room {} closed!'.format(room_key))

# @socket.on('update_board')
# def on_update_board(data):
#     room_key = data['roomKey']
#     move = chess.Move.from_uci(data['move'])
#     State.rooms[room_key]['board'].push(move)
#     # send move (to move 3D piece)
#     emit('move', data['move'], room=room_key)

#     send_board(room_key)
#     send_draw(room_key)

# @socket.on('users_init')
# def on_users_init(room_key):
#     client = request.sid
#     emit('users_init', State.rooms[room_key]['users'], room=client) # send to only client who just joined

# @socket.on('update_position')
# def on_update_position(data):
#     room_key = data['roomKey']
#     name = data['name']
#     position = data['position']
#     State.rooms[room_key]['users'][name] = position
#     send_users(room_key)

# @socket.on('message_in')
# def on_new_message(data):
#     name = data['name']
#     room_key = data['roomKey']
#     msg = data['message']
#     emit('message_out', {'username': name, 'message': msg}, room=room_key)


############ end Flask routes sekak: ############


############ Flask routes general: ############

# @app.route("/")
# def index():
#     return render_template("index.html")
#     return 'Hello MK Grafika Komputer Filkom UB 2022 :D'

@app.route("/loginQ")
def index():
    return redirect(url_for("login"))

# contoh membuat render teks
@app.route('/fphome')
def fphome():
    return render_template('text_render.html')

# @app.route('/kincirangin')

# contoh membuat titik-titik untuk membentuk garis
@app.route('/titik')
def draw_titik():
    return render_template('draw_titik.html')

@app.route('/titik2')
def draw_titik2():
    return render_template('titik2.html')

# contoh membuat titik-titik untuk membentuk lingkaran
@app.route('/titik3')
def draw_titik3():
    return render_template('draw_titik3.html')

# contoh membuat objek garis
@app.route('/garis')
def draw_garis():
    return render_template('draw_garis.html')

# contoh membuat objek segitiga
@app.route('/segitiga')
def draw_segitiga():
    return render_template('draw_segitiga.html')

# contoh membuat objek segiempat
@app.route('/segiempat')
def draw_segiempat():
    return render_template('draw_segiempat.html')

# contoh membuat objek segiempat berwarna
@app.route('/quadcolor')
def draw_quadcolor():
    return render_template('draw_quadcolor.html')

# contoh membuat objek segitiga berotasi
@app.route('/rotasi')
def draw_rotasisegitiga():
    return render_template('draw_rotasisegitiga.html')

# contoh membuat objek kubus berotasi, mode color tiap face
@app.route('/rotasicube')
def draw_rotasicube():
    return render_template('draw_rotasicube.html')

# contoh membuat objek kubus mode color tiap vertex
@app.route('/rotasicube2')
def draw_rotasicube2():
    return render_template('draw_rotasicube2.html')

# contoh membuat multi objek
@app.route('/multiobjek')
def draw_multiobjek():
    return render_template('draw_multiobjek.html')

# contoh membuat multi objek
@app.route('/multiobjek2')
def draw_multiobjek2():
    return render_template('draw_multiobjek2.html')

# contoh membuat multi objek untuk contoh membuat kincir angin sederhana
@app.route('/multiobjek3')
def draw_multiobjek3():
    return render_template('draw_multiobjek3.html')

# contoh membuat viewing dengan perspektif
@app.route('/view')
def draw_view():
    return render_template('frustum_sbg_Perspective_viewing.html')


# contoh membuat viewing dengan LookAt sebagai camera
@app.route('/camera')
def draw_camera():
    return render_template('LookAt_sbg_camera.html')

# contoh membuat texture mapping
@app.route('/map')
def draw_map():
    return render_template('draw_texturemap.html')

# contoh membuat texture mapping dan pencerminan
@app.route('/map2')
def draw_map2():
    return render_template('draw_texturemap_n_reflection.html')

# contoh membuat texture mapping dan pencerminan
@app.route('/map4')
def draw_map4():
    return render_template('draw_texturemap_from_bufferObject.html')

# contoh membuat blending
@app.route('/blending')
def draw_blending():
    return render_template('draw_blending.html')

# contoh membuat blending stamper
@app.route('/blending2')
def draw_blending2():
    return render_template('draw_blending_stamper.html')

# contoh membuat blending untuk antialiasing
@app.route('/antialiasing')
def draw_antialiasing():
    return render_template('draw_antialiasing.html')

# contoh membuat draw_segiempat_bergaris_titik
@app.route('/quadpoint')
def draw_quadpoint():
    return render_template('draw_segiempat_bergaris_titik.html')

# contoh membuat efek pencahayaan
@app.route('/cahaya')
def draw_cahaya():
    return render_template('draw_lighting.html')

# contoh membuat efek pencahayaan dan bayangan
@app.route('/cahaya2')
def draw_cahaya2():
    return render_template('draw_lighting_n_shading.html')

# contoh membuat animasi optimasi dengan algoritma PSO
@app.route('/anim_pso')
def draw_anim_pso():
    return render_template('draw_animasi_optimasi.html')

# contoh membuat model loading & Curve part 1
@app.route('/3d')
def draw_model_loading():
    return render_template('draw_model_loading_n_curve.html')

# contoh membuat model loading & Curve part 2
@app.route('/fractal')
def draw_fractal():
    return render_template('draw_fractal2.html')


# contoh membuat dashboard smart infografis
@app.route('/ui')
def draw_ui():
    return render_template('draw_dashboard1.html')

# contoh membuat dashboard smart infografis
@app.route('/ui2')
def draw_ui2():
    return render_template('draw_dashboard2.html')

# contoh membuat dashboard smart infografis
@app.route('/ui3')
def draw_ui3():
    return render_template('draw_dashboard3.html')



# contoh membuat plot sequence dna sample
@app.route('/plot_dna')
def draw_dna():
    # (Visualiasasi Grafis DNA virus) => 2D/3D,
    # =============================================

    import os.path

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # contoh load MERS:
    # ---------------
    # # Load data Sequence & Pre-Processing
    # # Virus ke-2, Middle East Respiratory Syndrome (MERS)
    # # Sumber: https://www.ncbi.nlm.nih.gov/nuccore/NC_019843.3?report=fasta
    # #         https://www.ncbi.nlm.nih.gov/nuccore/NC_019843.3?report=genbank
    # with open('dataset-ncbi/seq MERS.txt') as f:
    #   my_list = [''.join(x.strip().split(" ")[1:]) for x in f]
    #   seq_mers__ = ''.join(my_list)
    # print(my_list)
    # print(seq_mers__)
    # print(len(seq_mers__))

    # #get unik kode atau simbol IUPAC utk nucleotides
    # print(set(seq_mers__))

    # # konversi setiap char kodenya menjadi angka, misal a = 1, c = 2, g = 3, t = 4
    # val_seq_mers__ = seq_mers__.replace("a","1").replace("c","2").replace("g","3").replace("t","4")
    # print(val_seq_mers__)

    # # upper() sequence
    # up_seq_mers__ = seq_mers__.upper()
    # print(up_seq_mers__)
    # ---------------------------------------------------------------------------------------------------------

    # contoh load SARS-CoV-1:
    # ---------------
    # # Load data Sequence & Pre-Processing
    # # Virus ke-3, Severe Scute Respiratory Syndrome Coronavirus 1 (SARS-CoV-1)
    # # Sumber: https://www.ncbi.nlm.nih.gov/nuccore/MT649402.1?report=fasta
    # #         https://www.ncbi.nlm.nih.gov/nuccore/MT649402.1?report=genbank
    # with open('dataset-ncbi/seq SARS-CoV-1.txt') as f:
    #   my_list = [''.join(x.strip().split(" ")[1:]) for x in f]
    #   seq_sars_cov_1__ = ''.join(my_list)
    # print(my_list)
    # print(seq_sars_cov_1__)
    # print(len(seq_sars_cov_1__))

    # #get unik kode atau simbol IUPAC utk nucleotides
    # print(set(seq_sars_cov_1__))

    # # konversi setiap char kodenya menjadi angka, misal a = 1, c = 2, g = 3, t = 4
    # val_seq_sars_cov_1__ = seq_sars_cov_1__.replace("a","1").replace("c","2").replace("g","3").replace("t","4")
    # print(val_seq_sars_cov_1__)

    # # upper() sequence
    # up_seq_sars_cov_1__ = seq_sars_cov_1__.upper()
    # print(up_seq_sars_cov_1__)
    # ---------------------------------------------------------------------------------------------------------

    # contoh load SARS-CoV-2:
    # ---------------
    # # Load data Sequence & Pre-Processing
    # # Virus ke-1, Severe Scute Respiratory Syndrome Coronavirus 2 (SARS-CoV-2)
    # # sumber: https://www.ncbi.nlm.nih.gov/nuccore/NC_045512.2?report=fasta
    # #         https://www.ncbi.nlm.nih.gov/nuccore/NC_045512.2?report=genbank
    # with open('dataset-ncbi/seq SARS-CoV-2.txt') as f:
    #   my_list = [''.join(x.strip().split(" ")[1:]) for x in f]
    #   seq_sars_cov_2__ = ''.join(my_list)
    # print(my_list)
    # print(seq_sars_cov_2__)
    # print(len(seq_sars_cov_2__))

    # #get unik kode atau simbol IUPAC utk nucleotides
    # print(set(seq_sars_cov_2__))

    # # konversi setiap char kodenya menjadi angka, misal a = 1, c = 2, g = 3, t = 4
    # val_seq_sars_cov_2__ = seq_sars_cov_2__.replace("a","1").replace("c","2").replace("g","3").replace("t","4")
    # print(val_seq_sars_cov_2__)

    # # upper() sequence
    # up_seq_sars_cov_2__ = seq_sars_cov_2__.upper()
    # print(up_seq_sars_cov_2__)
    # ---------------------------------------------------------------------------------------------------------


    # contoh load Human Genome yang terpapar coronavirus 229:
    # # ---------------
    # # Sumber: https://www.ncbi.nlm.nih.gov/nuccore/NC_002645.1?report=fasta
    # #         https://www.ncbi.nlm.nih.gov/nuccore/NC_002645.1?report=genbank

    # print('name: ', 'Human coronavirus 229E, complete genome')

    # # with open('dataset-ncbi/seq Human coronavirus 229E complete genome.txt') as f:
    # with open(file_path) as f:
    #   my_list = [''.join(x.strip().split(" ")[1:]) for x in f]
    #   seq_coronavirus_229e__ = ''.join(my_list)
    # # print(my_list)
    # print('seq: ', seq_coronavirus_229e__)
    # print('len: ', len(seq_coronavirus_229e__))

    # #get unik kode atau simbol IUPAC utk nucleotides
    # get_unik_kode = set(seq_coronavirus_229e__)
    # print('get unik kode: ', get_unik_kode, ' => ', [ord(x)-97 for x in list(get_unik_kode)], end="\n\n")

    # # konversi setiap char kodenya menjadi angka array, misal dgn a-z => 1-26
    # val_a_z_seq_coronavirus_229e__ = seq2val_space_plus_arr_a_z(seq_coronavirus_229e__)
    # print('Val seq: ', val_a_z_seq_coronavirus_229e__)
    # ---------------------------------------------------------------------------------------------------------

    # contoh load SARS-CoV-1:
    # ---------------
    # Load data Sequence & Pre-Processing
    # Virus ke-3, Severe Scute Respiratory Syndrome Coronavirus 1 (SARS-CoV-1)
    # Sumber: https://www.ncbi.nlm.nih.gov/nuccore/MT649402.1?report=fasta
    #         https://www.ncbi.nlm.nih.gov/nuccore/MT649402.1?report=genbank

    file_path = os.path.join(BASE_DIR, "static/data/sequence DNA sample.txt")
    # " " => 0, "a" => 1, "c" => 2, "g" => 3, "t" => 4
    # 1 at ga aa => (0,1,0), (1,4,0), (2,0,0), (3,3,0), (4,1,0), (5,0,0), (6,1,0), (7,1,0)
    # 7 tg gg tc
    # 13 ga

    # file_path = os.path.join(BASE_DIR, "static/data/sequence DNA MERS.txt")
    # file_path = os.path.join(BASE_DIR, "static/data/sequence DNA SARS-CoV-1.txt")
    # file_path = os.path.join(BASE_DIR, "static/data/sequence DNA SARS-CoV-2.txt")

    with open(file_path) as f:
      # tanpa disisipkan spasi
      # my_list = [''.join(x.strip().split(" ")[1:]) for x in f]
      # seq_sars_cov_1__ = ''.join(my_list)

      # dengan disisipkan spasi, tanpa memperhatikan new_line
      my_list = [' '.join(x.strip().split(" ")[1:]) for x in f]
      seq_sars_cov_1__ = ''.join(my_list)
    print(my_list)
    print(seq_sars_cov_1__)
    length_seq_sars_cov_1__ = len(seq_sars_cov_1__)
    print(length_seq_sars_cov_1__)

    #get unik kode atau simbol IUPAC utk nucleotides
    print(set(seq_sars_cov_1__))

    # konversi setiap char kodenya menjadi angka, misal a = 1, c = 2, g = 3, t = 4
    # val_seq_sars_cov_1__ = seq_sars_cov_1__.replace("a","1").replace("c","2").replace("g","3").replace("t","4")
    val_seq_sars_cov_1__ = seq_sars_cov_1__.replace(" ","0").replace("a","1").replace("c","2").replace("g","3").replace("t","4")
    print(val_seq_sars_cov_1__)

    # upper() sequence
    up_seq_sars_cov_1__ = seq_sars_cov_1__.upper()
    print(up_seq_sars_cov_1__)

    # kode acgt dengan disisipkan spasi
    string_seq_dna = "\n".join(my_list)

    # tranformasi dari val_seq_sars_cov_1__ menjadi titik koordinat 2D/3d
    # untuk dibuat visualisasi grafis dengan WebGL
    # loop_counter_utk_new_line = 0
    # loop_counter_utk_pembatas_spasi = 0
    set_jeda_tiap_level_counter_utk_new_line = 0
    # increment_i_stlh_pembatas_spasi = 0
    byk_spasi_tiap_baris = 2
    byk_char_per_selain_spasi = 6


    # koordinat_x_y_z = ''
    # for i in range(length_seq_sars_cov_1__):
    #     # looping per barisnya, misal dari data diketahui per byk_char_per_selain_spasi

    #     if(i%(byk_char_per_selain_spasi+byk_spasi_tiap_baris)==0 and i>0):
    #         set_jeda_tiap_level_counter_utk_new_line += 7

    #     # koordinat_x = str(i)
    #     koordinat_x = str(i%(byk_char_per_selain_spasi+byk_spasi_tiap_baris))
    #     # koordinat_y = str(int(val_seq_sars_cov_1__[i]))
    #     koordinat_y = str(int(val_seq_sars_cov_1__[i]) + set_jeda_tiap_level_counter_utk_new_line)
    #     koordinat_z = str(0)

    #     if(i==0):
    #         koordinat_x_y_z += '('+ koordinat_x + ',' + koordinat_y + ',' + koordinat_z + ')'
    #     else:
    #         koordinat_x_y_z += ',('+ koordinat_x + ',' + koordinat_y + ',' + koordinat_z + ')'

    koordinat_x_y_z = ''
    for i in range(length_seq_sars_cov_1__):
        # looping per barisnya, misal dari data diketahui per byk_char_per_selain_spasi

        if(i%(byk_char_per_selain_spasi+byk_spasi_tiap_baris)==0 and i>0):
            set_jeda_tiap_level_counter_utk_new_line += 7

        # koordinat_x = str(i)
        koordinat_x = str(i%(byk_char_per_selain_spasi+byk_spasi_tiap_baris))
        # koordinat_y = str(int(val_seq_sars_cov_1__[i]))
        koordinat_y = str(int(val_seq_sars_cov_1__[i]) + set_jeda_tiap_level_counter_utk_new_line)
        koordinat_z = str(0)

        if(i==0):
            koordinat_x_y_z += koordinat_x + ',' + koordinat_y + ',' + koordinat_z
        else:
            koordinat_x_y_z += ','+ koordinat_x + ',' + koordinat_y + ',' + koordinat_z




    # ---------------------------------------------------------------------------------------------------------

    # cek panjang seq dna
    # return str(length_seq_sars_cov_1__);

    # menampilkan hasil konversi ke x,y,z
    # return koordinat_x_y_z;

    # menampilkan hasil konversi dalam bentuk angka
    # return val_seq_sars_cov_1__;

    # menampilkan kode acgt dengan disisipkan spasi
    # return seq_sars_cov_1__;
    # atau
    # return string_seq_dna;

    mylist_koordinat_x_y_z = koordinat_x_y_z.replace(' ','').split(',')

    # return render_template('draw_dna.html', coords_xyz = list(koordinat_x_y_z))
    return render_template('draw_dna.html', coords_xyz = mylist_koordinat_x_y_z)


# contoh membuat plot sequence dna sequence DNA SARS-CoV-1
@app.route('/plot_dna2')
def draw_dna2():
    # (Visualiasasi Grafis DNA virus) => 2D/3D,
    # =============================================

    import os.path

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # contoh load MERS:
    # ---------------
    # # Load data Sequence & Pre-Processing
    # # Virus ke-2, Middle East Respiratory Syndrome (MERS)
    # # Sumber: https://www.ncbi.nlm.nih.gov/nuccore/NC_019843.3?report=fasta
    # #         https://www.ncbi.nlm.nih.gov/nuccore/NC_019843.3?report=genbank
    # with open('dataset-ncbi/seq MERS.txt') as f:
    #   my_list = [''.join(x.strip().split(" ")[1:]) for x in f]
    #   seq_mers__ = ''.join(my_list)
    # print(my_list)
    # print(seq_mers__)
    # print(len(seq_mers__))

    # #get unik kode atau simbol IUPAC utk nucleotides
    # print(set(seq_mers__))

    # # konversi setiap char kodenya menjadi angka, misal a = 1, c = 2, g = 3, t = 4
    # val_seq_mers__ = seq_mers__.replace("a","1").replace("c","2").replace("g","3").replace("t","4")
    # print(val_seq_mers__)

    # # upper() sequence
    # up_seq_mers__ = seq_mers__.upper()
    # print(up_seq_mers__)
    # ---------------------------------------------------------------------------------------------------------

    # contoh load SARS-CoV-1:
    # ---------------
    # # Load data Sequence & Pre-Processing
    # # Virus ke-3, Severe Scute Respiratory Syndrome Coronavirus 1 (SARS-CoV-1)
    # # Sumber: https://www.ncbi.nlm.nih.gov/nuccore/MT649402.1?report=fasta
    # #         https://www.ncbi.nlm.nih.gov/nuccore/MT649402.1?report=genbank
    # with open('dataset-ncbi/seq SARS-CoV-1.txt') as f:
    #   my_list = [''.join(x.strip().split(" ")[1:]) for x in f]
    #   seq_sars_cov_1__ = ''.join(my_list)
    # print(my_list)
    # print(seq_sars_cov_1__)
    # print(len(seq_sars_cov_1__))

    # #get unik kode atau simbol IUPAC utk nucleotides
    # print(set(seq_sars_cov_1__))

    # # konversi setiap char kodenya menjadi angka, misal a = 1, c = 2, g = 3, t = 4
    # val_seq_sars_cov_1__ = seq_sars_cov_1__.replace("a","1").replace("c","2").replace("g","3").replace("t","4")
    # print(val_seq_sars_cov_1__)

    # # upper() sequence
    # up_seq_sars_cov_1__ = seq_sars_cov_1__.upper()
    # print(up_seq_sars_cov_1__)
    # ---------------------------------------------------------------------------------------------------------

    # contoh load SARS-CoV-2:
    # ---------------
    # # Load data Sequence & Pre-Processing
    # # Virus ke-1, Severe Scute Respiratory Syndrome Coronavirus 2 (SARS-CoV-2)
    # # sumber: https://www.ncbi.nlm.nih.gov/nuccore/NC_045512.2?report=fasta
    # #         https://www.ncbi.nlm.nih.gov/nuccore/NC_045512.2?report=genbank
    # with open('dataset-ncbi/seq SARS-CoV-2.txt') as f:
    #   my_list = [''.join(x.strip().split(" ")[1:]) for x in f]
    #   seq_sars_cov_2__ = ''.join(my_list)
    # print(my_list)
    # print(seq_sars_cov_2__)
    # print(len(seq_sars_cov_2__))

    # #get unik kode atau simbol IUPAC utk nucleotides
    # print(set(seq_sars_cov_2__))

    # # konversi setiap char kodenya menjadi angka, misal a = 1, c = 2, g = 3, t = 4
    # val_seq_sars_cov_2__ = seq_sars_cov_2__.replace("a","1").replace("c","2").replace("g","3").replace("t","4")
    # print(val_seq_sars_cov_2__)

    # # upper() sequence
    # up_seq_sars_cov_2__ = seq_sars_cov_2__.upper()
    # print(up_seq_sars_cov_2__)
    # ---------------------------------------------------------------------------------------------------------


    # contoh load Human Genome yang terpapar coronavirus 229:
    # # ---------------
    # # Sumber: https://www.ncbi.nlm.nih.gov/nuccore/NC_002645.1?report=fasta
    # #         https://www.ncbi.nlm.nih.gov/nuccore/NC_002645.1?report=genbank

    # print('name: ', 'Human coronavirus 229E, complete genome')

    # # with open('dataset-ncbi/seq Human coronavirus 229E complete genome.txt') as f:
    # with open(file_path) as f:
    #   my_list = [''.join(x.strip().split(" ")[1:]) for x in f]
    #   seq_coronavirus_229e__ = ''.join(my_list)
    # # print(my_list)
    # print('seq: ', seq_coronavirus_229e__)
    # print('len: ', len(seq_coronavirus_229e__))

    # #get unik kode atau simbol IUPAC utk nucleotides
    # get_unik_kode = set(seq_coronavirus_229e__)
    # print('get unik kode: ', get_unik_kode, ' => ', [ord(x)-97 for x in list(get_unik_kode)], end="\n\n")

    # # konversi setiap char kodenya menjadi angka array, misal dgn a-z => 1-26
    # val_a_z_seq_coronavirus_229e__ = seq2val_space_plus_arr_a_z(seq_coronavirus_229e__)
    # print('Val seq: ', val_a_z_seq_coronavirus_229e__)
    # ---------------------------------------------------------------------------------------------------------

    # contoh load SARS-CoV-1:
    # ---------------
    # Load data Sequence & Pre-Processing
    # Virus ke-3, Severe Scute Respiratory Syndrome Coronavirus 1 (SARS-CoV-1)
    # Sumber: https://www.ncbi.nlm.nih.gov/nuccore/MT649402.1?report=fasta
    #         https://www.ncbi.nlm.nih.gov/nuccore/MT649402.1?report=genbank

    # file_path = os.path.join(BASE_DIR, "static/data/sequence DNA sample.txt")
    # " " => 0, "a" => 1, "c" => 2, "g" => 3, "t" => 4
    # 1 at ga aa => (0,1,0), (1,4,0), (2,0,0), (3,3,0), (4,1,0), (5,0,0), (6,1,0), (7,1,0)
    # 7 tg gg tc
    # 13 ga

    # file_path = os.path.join(BASE_DIR, "static/data/sequence DNA MERS.txt")
    file_path = os.path.join(BASE_DIR, "static/data/sequence DNA SARS-CoV-1.txt")
    # file_path = os.path.join(BASE_DIR, "static/data/sequence DNA SARS-CoV-2.txt")

    with open(file_path) as f:
      # tanpa disisipkan spasi
      # my_list = [''.join(x.strip().split(" ")[1:]) for x in f]
      # seq_sars_cov_1__ = ''.join(my_list)

      # dengan disisipkan spasi, tanpa memperhatikan new_line
      my_list = [' '.join(x.strip().split(" ")[1:]) for x in f]
      seq_sars_cov_1__ = ''.join(my_list)
    print(my_list)
    print(seq_sars_cov_1__)
    length_seq_sars_cov_1__ = len(seq_sars_cov_1__)
    print(length_seq_sars_cov_1__)

    #get unik kode atau simbol IUPAC utk nucleotides
    print(set(seq_sars_cov_1__))

    # konversi setiap char kodenya menjadi angka, misal a = 1, c = 2, g = 3, t = 4
    # val_seq_sars_cov_1__ = seq_sars_cov_1__.replace("a","1").replace("c","2").replace("g","3").replace("t","4")
    val_seq_sars_cov_1__ = seq_sars_cov_1__.replace(" ","0").replace("a","1").replace("c","2").replace("g","3").replace("t","4")
    print(val_seq_sars_cov_1__)

    # upper() sequence
    up_seq_sars_cov_1__ = seq_sars_cov_1__.upper()
    print(up_seq_sars_cov_1__)

    # kode acgt dengan disisipkan spasi
    string_seq_dna = "\n".join(my_list)

    # tranformasi dari val_seq_sars_cov_1__ menjadi titik koordinat 2D/3d
    # untuk dibuat visualisasi grafis dengan WebGL
    # loop_counter_utk_new_line = 0
    # loop_counter_utk_pembatas_spasi = 0
    set_jeda_tiap_level_counter_utk_new_line = 0
    # increment_i_stlh_pembatas_spasi = 0
    byk_spasi_tiap_baris = 5
    byk_char_per_selain_spasi = 60


    # koordinat_x_y_z = ''
    # for i in range(length_seq_sars_cov_1__):
    #     # looping per barisnya, misal dari data diketahui per byk_char_per_selain_spasi

    #     if(i%(byk_char_per_selain_spasi+byk_spasi_tiap_baris)==0 and i>0):
    #         set_jeda_tiap_level_counter_utk_new_line += 7

    #     # koordinat_x = str(i)
    #     koordinat_x = str(i%(byk_char_per_selain_spasi+byk_spasi_tiap_baris))
    #     # koordinat_y = str(int(val_seq_sars_cov_1__[i]))
    #     koordinat_y = str(int(val_seq_sars_cov_1__[i]) + set_jeda_tiap_level_counter_utk_new_line)
    #     koordinat_z = str(0)

    #     if(i==0):
    #         koordinat_x_y_z += '('+ koordinat_x + ',' + koordinat_y + ',' + koordinat_z + ')'
    #     else:
    #         koordinat_x_y_z += ',('+ koordinat_x + ',' + koordinat_y + ',' + koordinat_z + ')'

    koordinat_x_y_z = ''
    for i in range(length_seq_sars_cov_1__):
        # looping per barisnya, misal dari data diketahui per byk_char_per_selain_spasi

        if(i%(byk_char_per_selain_spasi+byk_spasi_tiap_baris)==0 and i>0):
            set_jeda_tiap_level_counter_utk_new_line += 7

        # koordinat_x = str(i)
        koordinat_x = str(i%(byk_char_per_selain_spasi+byk_spasi_tiap_baris))
        # koordinat_y = str(int(val_seq_sars_cov_1__[i]))
        koordinat_y = str(int(val_seq_sars_cov_1__[i]) + set_jeda_tiap_level_counter_utk_new_line)
        koordinat_z = str(0)

        if(i==0):
            koordinat_x_y_z += koordinat_x + ',' + koordinat_y + ',' + koordinat_z
        else:
            koordinat_x_y_z += ','+ koordinat_x + ',' + koordinat_y + ',' + koordinat_z




    # ---------------------------------------------------------------------------------------------------------

    # cek panjang seq dna
    # return str(length_seq_sars_cov_1__);

    # menampilkan hasil konversi ke x,y,z
    # return koordinat_x_y_z;

    # menampilkan hasil konversi dalam bentuk angka
    # return val_seq_sars_cov_1__;

    # menampilkan kode acgt dengan disisipkan spasi
    # return seq_sars_cov_1__;
    # atau
    # return string_seq_dna;

    mylist_koordinat_x_y_z = koordinat_x_y_z.replace(' ','').split(',')

    # return render_template('draw_dna.html', coords_xyz = list(koordinat_x_y_z))
    return render_template('draw_dna_cov1.html', coords_xyz = mylist_koordinat_x_y_z)

# contoh membuat konversi sequence dna menjadi numeric
@app.route('/dna')
def convert_dna():
    # (Konversi DNA virus) => 2D/3D,
    # =============================================

    import os.path

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # contoh load MERS:
    # ---------------
    # # Load data Sequence & Pre-Processing
    # # Virus ke-2, Middle East Respiratory Syndrome (MERS)
    # # Sumber: https://www.ncbi.nlm.nih.gov/nuccore/NC_019843.3?report=fasta
    # #         https://www.ncbi.nlm.nih.gov/nuccore/NC_019843.3?report=genbank
    # with open('dataset-ncbi/seq MERS.txt') as f:
    #   my_list = [''.join(x.strip().split(" ")[1:]) for x in f]
    #   seq_mers__ = ''.join(my_list)
    # print(my_list)
    # print(seq_mers__)
    # print(len(seq_mers__))

    # #get unik kode atau simbol IUPAC utk nucleotides
    # print(set(seq_mers__))

    # # konversi setiap char kodenya menjadi angka, misal a = 1, c = 2, g = 3, t = 4
    # val_seq_mers__ = seq_mers__.replace("a","1").replace("c","2").replace("g","3").replace("t","4")
    # print(val_seq_mers__)

    # # upper() sequence
    # up_seq_mers__ = seq_mers__.upper()
    # print(up_seq_mers__)
    # ---------------------------------------------------------------------------------------------------------

    # contoh load SARS-CoV-1:
    # ---------------
    # # Load data Sequence & Pre-Processing
    # # Virus ke-3, Severe Scute Respiratory Syndrome Coronavirus 1 (SARS-CoV-1)
    # # Sumber: https://www.ncbi.nlm.nih.gov/nuccore/MT649402.1?report=fasta
    # #         https://www.ncbi.nlm.nih.gov/nuccore/MT649402.1?report=genbank
    # with open('dataset-ncbi/seq SARS-CoV-1.txt') as f:
    #   my_list = [''.join(x.strip().split(" ")[1:]) for x in f]
    #   seq_sars_cov_1__ = ''.join(my_list)
    # print(my_list)
    # print(seq_sars_cov_1__)
    # print(len(seq_sars_cov_1__))

    # #get unik kode atau simbol IUPAC utk nucleotides
    # print(set(seq_sars_cov_1__))

    # # konversi setiap char kodenya menjadi angka, misal a = 1, c = 2, g = 3, t = 4
    # val_seq_sars_cov_1__ = seq_sars_cov_1__.replace("a","1").replace("c","2").replace("g","3").replace("t","4")
    # print(val_seq_sars_cov_1__)

    # # upper() sequence
    # up_seq_sars_cov_1__ = seq_sars_cov_1__.upper()
    # print(up_seq_sars_cov_1__)
    # ---------------------------------------------------------------------------------------------------------

    # contoh load SARS-CoV-2:
    # ---------------
    # # Load data Sequence & Pre-Processing
    # # Virus ke-1, Severe Scute Respiratory Syndrome Coronavirus 2 (SARS-CoV-2)
    # # sumber: https://www.ncbi.nlm.nih.gov/nuccore/NC_045512.2?report=fasta
    # #         https://www.ncbi.nlm.nih.gov/nuccore/NC_045512.2?report=genbank
    # with open('dataset-ncbi/seq SARS-CoV-2.txt') as f:
    #   my_list = [''.join(x.strip().split(" ")[1:]) for x in f]
    #   seq_sars_cov_2__ = ''.join(my_list)
    # print(my_list)
    # print(seq_sars_cov_2__)
    # print(len(seq_sars_cov_2__))

    # #get unik kode atau simbol IUPAC utk nucleotides
    # print(set(seq_sars_cov_2__))

    # # konversi setiap char kodenya menjadi angka, misal a = 1, c = 2, g = 3, t = 4
    # val_seq_sars_cov_2__ = seq_sars_cov_2__.replace("a","1").replace("c","2").replace("g","3").replace("t","4")
    # print(val_seq_sars_cov_2__)

    # # upper() sequence
    # up_seq_sars_cov_2__ = seq_sars_cov_2__.upper()
    # print(up_seq_sars_cov_2__)
    # ---------------------------------------------------------------------------------------------------------


    # contoh load Human Genome yang terpapar coronavirus 229:
    # # ---------------
    # # Sumber: https://www.ncbi.nlm.nih.gov/nuccore/NC_002645.1?report=fasta
    # #         https://www.ncbi.nlm.nih.gov/nuccore/NC_002645.1?report=genbank

    # print('name: ', 'Human coronavirus 229E, complete genome')

    # # with open('dataset-ncbi/seq Human coronavirus 229E complete genome.txt') as f:
    # with open(file_path) as f:
    #   my_list = [''.join(x.strip().split(" ")[1:]) for x in f]
    #   seq_coronavirus_229e__ = ''.join(my_list)
    # # print(my_list)
    # print('seq: ', seq_coronavirus_229e__)
    # print('len: ', len(seq_coronavirus_229e__))

    # #get unik kode atau simbol IUPAC utk nucleotides
    # get_unik_kode = set(seq_coronavirus_229e__)
    # print('get unik kode: ', get_unik_kode, ' => ', [ord(x)-97 for x in list(get_unik_kode)], end="\n\n")

    # # konversi setiap char kodenya menjadi angka array, misal dgn a-z => 1-26
    # val_a_z_seq_coronavirus_229e__ = seq2val_space_plus_arr_a_z(seq_coronavirus_229e__)
    # print('Val seq: ', val_a_z_seq_coronavirus_229e__)
    # ---------------------------------------------------------------------------------------------------------

    # contoh load SARS-CoV-1:
    # ---------------
    # Load data Sequence & Pre-Processing
    # Virus ke-3, Severe Scute Respiratory Syndrome Coronavirus 1 (SARS-CoV-1)
    # Sumber: https://www.ncbi.nlm.nih.gov/nuccore/MT649402.1?report=fasta
    #         https://www.ncbi.nlm.nih.gov/nuccore/MT649402.1?report=genbank

    file_path = os.path.join(BASE_DIR, "static/data/sequence DNA sample.txt")
    # " " => 0, "a" => 1, "c" => 2, "g" => 3, "t" => 4
    # 1 at ga aa => (0,1,0), (1,4,0), (2,0,0), (3,3,0), (4,1,0), (5,0,0), (6,1,0), (7,1,0)
    # 7 tg gg tc
    # 13 ga

    # file_path = os.path.join(BASE_DIR, "static/data/sequence DNA MERS.txt")
    # file_path = os.path.join(BASE_DIR, "static/data/sequence DNA SARS-CoV-1.txt")
    # file_path = os.path.join(BASE_DIR, "static/data/sequence DNA SARS-CoV-2.txt")

    with open(file_path) as f:
      # tanpa disisipkan spasi
      # my_list = [''.join(x.strip().split(" ")[1:]) for x in f]
      # seq_sars_cov_1__ = ''.join(my_list)

      # dengan disisipkan spasi, tanpa memperhatikan new_line
      my_list = [' '.join(x.strip().split(" ")[1:]) for x in f]
      seq_sars_cov_1__ = ''.join(my_list)
    print(my_list)
    print(seq_sars_cov_1__)
    length_seq_sars_cov_1__ = len(seq_sars_cov_1__)
    print(length_seq_sars_cov_1__)

    #get unik kode atau simbol IUPAC utk nucleotides
    print(set(seq_sars_cov_1__))

    # konversi setiap char kodenya menjadi angka, misal a = 1, c = 2, g = 3, t = 4
    # val_seq_sars_cov_1__ = seq_sars_cov_1__.replace("a","1").replace("c","2").replace("g","3").replace("t","4")
    val_seq_sars_cov_1__ = seq_sars_cov_1__.replace(" ","0").replace("a","1").replace("c","2").replace("g","3").replace("t","4")
    print(val_seq_sars_cov_1__)

    # upper() sequence
    up_seq_sars_cov_1__ = seq_sars_cov_1__.upper()
    print(up_seq_sars_cov_1__)

    # kode acgt dengan disisipkan spasi
    string_seq_dna = "\n".join(my_list)

    # tranformasi dari val_seq_sars_cov_1__ menjadi titik koordinat 2D/3d
    # untuk dibuat visualisasi grafis dengan WebGL
    # loop_counter_utk_new_line = 0
    # loop_counter_utk_pembatas_spasi = 0
    set_jeda_tiap_level_counter_utk_new_line = 0
    # increment_i_stlh_pembatas_spasi = 0
    byk_spasi_tiap_baris = 2
    byk_char_per_selain_spasi = 6


    koordinat_x_y_z = ''
    for i in range(length_seq_sars_cov_1__):
        # looping per barisnya, misal dari data diketahui per byk_char_per_selain_spasi

        if(i%(byk_char_per_selain_spasi+byk_spasi_tiap_baris)==0 and i>0):
            set_jeda_tiap_level_counter_utk_new_line += 7

        # koordinat_x = str(i)
        koordinat_x = str(i%(byk_char_per_selain_spasi+byk_spasi_tiap_baris))
        # koordinat_y = str(int(val_seq_sars_cov_1__[i]))
        koordinat_y = str(int(val_seq_sars_cov_1__[i]) + set_jeda_tiap_level_counter_utk_new_line)
        koordinat_z = str(0)

        if(i==0):
            koordinat_x_y_z += '('+ koordinat_x + ',' + koordinat_y + ',' + koordinat_z + ')'
        else:
            koordinat_x_y_z += ',('+ koordinat_x + ',' + koordinat_y + ',' + koordinat_z + ')'




    # ---------------------------------------------------------------------------------------------------------

    # cek panjang seq dna
    # return str(length_seq_sars_cov_1__);

    # menampilkan hasil konversi ke x,y,z
    return koordinat_x_y_z;

    # menampilkan hasil konversi dalam bentuk angka
    # return val_seq_sars_cov_1__;

    # menampilkan kode acgt dengan disisipkan spasi
    # return seq_sars_cov_1__;
    # atau
    # return string_seq_dna;

# Ref:
# [0] https://learnopengl.com/Getting-started/Shaders
# [1] https://webglfundamentals.org/webgl/lessons/webgl-shaders-and-glsl.html
#
# Jika memang WebGL Anda menggunakan Shader,
# maka dibutuhkan 2 shader (semacam variabel dan fungsi untuk manipulasi) yaitu vertex shader dan fragment shader yang membentuk 1 pasang shader,
# dan aplikasi yang dibuat dapat memiliki lebih dari 1 pasang shader.
#
# Tentang Vertex Shader:
# Vertex shader digunakan untuk memanipulasi per vertex untuk variabel global tertentu, misal gl_Position ke beberapa koordinat clip space.
# void main() {
#   gl_Position = buatkodingbasedMathUtkDikirimkanHasilManipulasinyaKeClipspaceCoordinates
# }
#
#
# Vertex shader mendapatkan data dengan 3 cara, yaitu:
# 1. Atribut (data yang diambil dari hasil buffer).
#    > pertama buat data buffer, dengan var buf = gl.createBuffer();
#    > lalu masukkan data Anda pada buffer tersebut, misal dengan
#        gl.bindBuffer(gl.ARRAY_BUFFER, buf);
#        gl.bufferData(gl.ARRAY_BUFFER, someData, gl.STATIC_DRAW);
#    > set variabel program Shader untuk mencari lokasi attributes saat proses inisialisasi, misal dengan
#        var positionLoc = gl.getAttribLocation(someShaderProgram, "a_position");
#    > memberi tahu WebGL untuk cara mengirimkan data (data out) dari buffer ke dalam attribute pada Shader, misal dengan
#       // mengaktifkan pengiriman data buffer dari local WebGL env ke attribute pada env Shader
#       gl.enableVertexAttribArray(positionLoc);
#       var numComponents = 3;  // (x, y, z)
#       var type = gl.FLOAT;    // 32bit floating point values
#       var normalize = false;  // dilakukan normalisasi atau nilai digunakan apa adanya
#       var offset = 0;         // nilai start untuk awal buffer
#       var stride = 0;         // berapa banyak bytes untuk berpidah ke next vertex
#                               // 0 = gunakan nilai yang benar pada stride berdasarkan type dan numComponents
#       gl.vertexAttribPointer(positionLoc, numComponents, type, normalize, stride, offset);
#    > menangkap hasil data buffer pada Shader dan membuat koding matematika di shader sesuai kebutuhan atau
#      misal dalam contoh ini hanya meneruskan data buffer saja, misal dengan
#       // attribute dapat menggunakan tipe float, vec2, vec3, vec4, mat2, mat3, dan mat4.
#       attribute vec4 a_position;
#       void main() {
#         gl_Position = a_position;
#       }
#
#
#
# 2. Uniforms (nilai yang tetap sama untuk semua titik data (vertek) dari satu panggilan proses draw atau draw call)
#    shader uniform merupakan nilai yang diteruskan ke shader yang nilainya tetap sama untuk semua vertex dalam draw call.
#    Contohnya,  menambahkan variabel offset (nilai awal data buffer atau variabel utk mengimbangi setiap simpul dengan jumlah tertentu)
#    ke code vertex shader attribute dari contoh sebelumnya, misal dengan
#    ////////////////////////////////////
#       attribute vec4 a_position;
#       void main() {
#         gl_Position = a_position;
#       }
#    ////////////////////////////////////
#    menjadi

#       attribute vec4 a_position;
#       uniform vec4 u_offset;
#       void main() {
#         gl_Position = a_position + u_offset;
#       }
#    > pertama, set variabel program Shader untuk mencari lokasi Uniforms saat proses inisialisasi, misal dengan
#       var offsetLoc = gl.getUniformLocation(someProgram, "u_offset");
#    > lalu sebelum proses draw, dapat terlebih dahulu diset nilai uniform-nya, misal dengan
#       gl.uniform4fv(offsetLoc, [1, 0, 0, 0]); // offset ke bagian kanan layar
#      Uniforms memiliki beberapa macan tipe data, gunakan sesuai kebutuhan Anda, berikut detailnya:
#       gl.uniform1f (floatUniformLoc, v); // untuk nilai skalar float
#       gl.uniform1fv(floatUniformLoc, [v]); // untuk array float atau float
#       gl.uniform2f (vec2UniformLoc, v0, v1); // untuk vec2
#       gl.uniform2fv(vec2UniformLoc, [v0, v1]); // untuk array vec2 atau vec2
#       gl.uniform3f (vec3UniformLoc, v0, v1, v2); // untuk vec3
#       gl.uniform3fv(vec3UniformLoc, [v0, v1, v2]); // untuk array vec3 atau vec3
#       gl.uniform4f (vec4UniformLoc, v0, v1, v2, v4); // untuk vec4
#       gl.uniform4fv(vec4UniformLoc, [v0, v1, v2, v4]); // untuk array vec4 atau vec4

#       gl.uniformMatrix2fv(mat2UniformLoc, false, [ array elemen 4x ]) // untuk array mat2 atau mat2
#       gl.uniformMatrix3fv(mat3UniformLoc, false, [ array elemen 9x ]) // untuk array mat3 atau mat3
#       gl.uniformMatrix4fv(mat4UniformLoc, false, [ 16x elemen larik ]) // untuk larik mat4 atau mat4

#       gl.uniform1i (intUniformLoc, v); // untuk nilai skalar int
#       gl.uniform1iv(intUniformLoc, [v]); // untuk int atau int array
#       gl.uniform2i (ivec2UniformLoc, v0, v1); // untuk ivec2
#       gl.uniform2iv(ivec2UniformLoc, [v0, v1]); // untuk array ivec2 atau ivec2
#       gl.uniform3i (ivec3UniformLoc, v0, v1, v2); // untuk ivec3
#       gl.uniform3iv(ivec3UniformLoc, [v0, v1, v2]); // untuk array ivec3 atau ivec3
#       gl.uniform4i (ivec4UniformLoc, v0, v1, v2, v4); // untuk ivec4
#       gl.uniform4iv(ivec4UniformLoc, [v0, v1, v2, v4]); // untuk array ivec4 atau ivec4
#
#       gl.uniform1i (sampler2DUniformLoc, v); // untuk sampler2D (tekstur)
#       gl.uniform1iv(sampler2DUniformLoc, [v]); // untuk array sampler2D atau sampler2D
#
#       gl.uniform1i (samplerCubeUniformLoc, v); // untuk samplerCube (tekstur)
#       gl.uniform1iv(samplerCubeUniformLoc, [v]); // untuk array samplerCube atau samplerCube
#
#    > pada shader uniform, ada juga tipe bool, bvec2, bvec3, and bvec4 yang menggunakan fungsi gl.uniform?f? atau gl.uniform?i?
#      contoh pengaturan "semua uniform array".
#      // in shader
#      uniform vec2 u_someVec2[3];
#
#      // in JavaScript at init time
#      var someVec2Loc = gl.getUniformLocation(someProgram, "u_someVec2");
#
#      // at render time
#      gl.uniform2fv(someVec2Loc, [1, 2, 3, 4, 5, 6]);  // set the entire array of u_someVec2
#
#    > Dapat diatur juga untuk "tiap elemen individual dari array", satu per satu sesuai lokasinya, seperti berikut:
#
#      // in JavaScript at init time
#      var someVec2Element0Loc = gl.getUniformLocation(someProgram, "u_someVec2[0]");
#      var someVec2Element1Loc = gl.getUniformLocation(someProgram, "u_someVec2[1]");
#      var someVec2Element2Loc = gl.getUniformLocation(someProgram, "u_someVec2[2]");

#      // at render time
#      gl.uniform2fv(someVec2Element0Loc, [1, 2]);  // set element 0
#      gl.uniform2fv(someVec2Element1Loc, [3, 4]);  // set element 1
#      gl.uniform2fv(someVec2Element2Loc, [5, 6]);  // set element 2
#
#      >> berikut contoh jika dibuat dengan struct,
#         struct SomeStruct {
#           bool active;
#           vec2 someVec2;
#         };
#
#         uniform SomeStruct u_someThing;
#
#      >> maka untuk setiap individu dicari sesuai field-nya, misal dengan
#         var someThingActiveLoc = gl.getUniformLocation(someProgram, "u_someThing.active");
#         var someThingSomeVec2Loc = gl.getUniformLocation(someProgram, "u_someThing.someVec2");
#
# 3. Textures (data yang diambil dari piksel/texel), berhubungan dengan Fragment Shader
#
# Tentang Fragment Shader
# Pengaturan tekstur di Vertex Shaders menggunakan Fragment Shader.
# Intinya Fragment Shader bertugas memberikan warna untuk piksel saat ini yang sedang diraster,
# di mana piksel ini bisa merupakan kumpulan dari beberapa vertex, misal dengan
#
# ///////////////////////
# precision mediump float;
# void main() {
#    gl_FragColor = buatkodingbasedMathUtkMakeAColor;
# }
# ///////////////////////
#
# Shader fragmen dipanggil sekali per piksel.
# Setiap dipanggil, maka diminta set variabel global khusus, misal dengan gl_FragColor untuk set tekstur warna.
#
# Fragment shader mendapatkan data dengan 3 cara, yaitu:
#
# 1. Uniforms (nilai yang tetap sama untuk setiap piksel data (kumpulan vertek) dari satu panggilan proses draw atau draw call)
#    > Uniforms di Fragment Shaders, penjelasannya sama dengan Uniforms  di Vertex Shader sebelumnya.
# 2. Textures (data yang diambil dari piksel/texel)
#    Textures  dalam Shader Fragmen, cara get nilai tekstur di shader, yaitu misal dengan membuat sampler2D uniform
#    dan menggunakan fungsi texture2D dari GLSL untuk mengekstrak nilainya. Berikut conthnya
#    ///////////////////////////
#    precision mediump float;
#    uniform sampler2D u_texture;
#    void main() {
#      vec2 texcoord = vec2(0.5, 0.5)  // mendapatkan nilai dari nilai tengah tekstur
#      gl_FragColor = texture2D(u_texture, texcoord);
#    }
#    ///////////////////////////
#
#   Hasil keluaran data texture bergantung banyak pengaturan. Minimal telah dibuat dan diletakkan nilai texture di variabel data, misal
#   ///////////////////////////
#   var tex = gl.createTexture();
#   gl.bindTexture(gl.TEXTURE_2D, tex);
#   var level = 0;
#   var width = 2;
#   var height = 1;
#   // set untuk informasi data warna dgn interval [0;255]
#   var data = new Uint8Array([
#       255, 0, 0, 255,   // a red pixel
#       0, 255, 0, 255,   // a green pixel
#   ]);
#   gl.texImage2D(gl.TEXTURE_2D, level, gl.RGBA, width, height, 0, gl.RGBA, gl.UNSIGNED_BYTE, data);
#   ///////////////////////////
#
#   Contoh melakukan filtering pada tekstur:
#   gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
#
#   Contoh saat inisialisasi, search nama variabel "uniform location" pada program shader:
#   var someSamplerLoc = gl.getUniformLocation(someProgram, "u_texture");
#
#   Saat proses render, ikat texture (bind the texture) ke unit texture:
#   var unit = 5; // Pilih beberapa unit tekstur
#   gl.activeTexture(gl.TEXTURE0 + unit);
#   gl.bindTexture(gl.TEXTURE_2D, tex);
#
#   Lalu informasikan kepada shader, variabel unit mana yang telah Anda ikat texture-nya:
#   gl.uniform1i(someSamplerLoc, unit);
#
# 3. Varyings (data dilewatkan dari vertex shader lalu dilakukan proses interpolasi)
#    Varyings adalah cara mengirimkan nilai variabel dari vertex shader ke fragment shader, yang keduanya telah dibahas sebelumnya.
#    Untuk menggunakan Varyings, butuh dideklarasikan pencocokan nama variabel (matching varyings) pada vertex shader maupun fragment shader.
#    Pada dapat dikonfigursi untuk set suatu nilai Varyings pada vertex shader dengan banyak nilai per vertex.
#    Saat WebGL draw piksel,  maka dilakukan interpolasi antara nilai-nilai tersebut dan meneruskannya ke varying yang sesuai pada fragment shader.
#    Berikut contoh rangkaian kodenya:
#
#    Contoh isi Vertex shader
#    ///////////////////////////
#    attribute vec4 a_position;
#    uniform vec4 u_offset;
#    varying vec4 v_positionWithOffset;
#    void main() {
#      gl_Position = a_position + u_offset;
#      v_positionWithOffset = a_position + u_offset;
#    }
#    ///////////////////////////
#
#    Contoh isi Fragment shader
#    ///////////////////////////
#    precision mediump float;
#    varying vec4 v_positionWithOffset;
#    void main() {
#      // convert from clip space (-1 <-> +1) to color space (0 -> 1).
#      vec4 color = v_positionWithOffset * 0.5 + 0.5
#      gl_FragColor = color;
#    }
#    ///////////////////////////
#
#    Contoh di atas merupakan contoh yang sederhana, karena secara langsung menyalin nilai clip space ke fragmen shader dan menggunakannya sebagai warna.
#    Namun kode tersebut akan tetap berjalan menghasilkan warna sesuai logika yang dibangun.
#
# 3. Textures (data yang diambil dari piksel/texel), berhubungan dengan Fragment Shader

#
# OpenGL Shading Language atau Graphics Library Shader Language (GLSL) merupakan bahasa shading tingkat tinggi atau bagian dari Shader
# yang memiliki fitur khusus seperti variabel input dan output, set variabel uniform dan fungsi utama lainnya
# sehingga mampu memanfaatkan GPU dengan sintaks bahasa C untuk mengolah data grafis berbasis vektor dan matriks.
# Sifatnya seperti terisolir, karena komunikasi input dan outputnya seolah secara tidak langsung ke kode program utama,
# misal pada WebGL yang menggunakan Js.
#
# Selain itu, GLSL merupakan bahasa shader yang dapat ditulis langsung dalam program shader, yang memiliki beberapa fitur unik karena tidak umum seperti di JavaScript.
# Fitur tersebut dirancang untuk membangun logika koding atau matematika untuk rasterisasi grafik atau general purpose,
# misal untuk implementasi algoritma Artificial Intelligent (AI), Machine Learning (ML) dan Deep Learning.
# GLSL memiliki tipe data seperti vec2, vec3, dan vec4 yang masing-masing mewakili vektor 2 nilai, 3 nilai, dan 4 nilai.
# Dan juga tipe data mat2, mat3 dan mat4 yang mewakili matriks 2x2, 3x3, dan 4x4.
# Serta developerpun dapat melakukan operasi komputasi seperti mengalikan vec dengan skalar, dll.
# > Contoh Perkalian vec dgn skalar
#   ///////////////////////////////////
#   vec4 a = vec4(1, 2, 3, 4);
#   vec4 b = a * 2.0;
#   // b is now vec4(2, 4, 6, 8);
#   ///////////////////////////////////
#
# > Contoh Perkalian antar matrik dan vec
#   ///////////////////////////////////
#   mat4 a = ???
#   mat4 b = ???
#   mat4 c = a * b;
#   vec4 v = ???
#   vec4 y = c * v;
#   ///////////////////////////////////
#
# > Contoh sintaks singkat,
#   ///////////////////////////////////
#   vec4 v;
#   yang memiliki arti sama dengan
#   v.x sama dengan v.s dan v.r dan v[0].
#   v.y sama dengan v.t dan v.g dan v[1].
#   v.z sama dengan v.p dan v.b dan v[2].
#   v.w sama dengan v.q dan v.a dan v[3].
#   ///////////////////////////////////
#
# > Contoh sintaks untuk memutar / menukar / mengulang nilai elemen vec
#   ///////////////////////////////////
#   menyambung dari vec4 v;
#   v.yyyy
#   sama dengan
#   vec4(v.y, v.y, v.y, v.y)
#
#   Demikian pula
#   v.bgra
#   sama dengan
#   vec4(v.b, v.g, v.r, v.a)
#   ///////////////////////////////////
#
# > Contoh dalam mendeklarasikan vec atau mat, dapat disediakan beberapa bagian sekaligus
#   ///////////////////////////////////
#   vec4(v.rgb, 1)
#   sama dengan
#   vec4(v.r, v.g, v.b, 1)
#
#   Demikian pula
#   vec4(1)
#   sama dengan
#   vec4(1, 1, 1, 1)
#   ///////////////////////////////////
#
# Karena GLSL sangat strict atau ketat, misal dalam menyusun tipe data, maka harus sangat diperhatikan, berikut
# > Contoh yang salah.
#   ///////////////////////////////////
#   float f = 1;  // ERROR 1, karena int.harus diganti atau di-casting ke float
#   ///////////////////////////////////
#
# > Contoh yang benar,
#   ///////////////////////////////////
#   float f = 1.0; // gunakan tipe float
#   float f = float(1) // int di-casting ke float
#   ///////////////////////////////////
#
# Contoh di atas dari vec4(v.rgb, 1) tidak ada error terkait nilai 1,
# karena vec4 secara otomatis telah melakukan casting seperti float(1).
# > Contoh banyak fungsi bawaan dari GLSL yang sekaligus dapat beroperasi pada beberapa komponen.
#   ///////////////////////////////////
#   T sin(T angle)
#   T bisa berupa float, vec2, vec3 atau vec4. Di mana jika T adalah vec4, maka v adalah vec4, misal
#   vec4 s = sin(v);
#   sama dengan
#   vec4 s = vec4(sin(v.x), sin(v.y), sin(v.z), sin(v.w));
#   ///////////////////////////////////
#
# > Contoh ada satu argumen float dan lainnya T, ini maknanya float akan diterapkan sesuai letak argumennya ke semua komponen. Misal v1 dan v2 adalah vec4 dan f adalah float maka
#   ///////////////////////////////////
#   vec4 m = mix(v1, v2, f);
#   sama dengan
#   vec4 m = vec4(
#   mix(v1.x, v2.x, f),
#   mix(v1.y, v2.y, f),
#   mix(v1.z, v2.z, f),
#   mix(v1.w, v2.w, f));
#   ///////////////////////////////////
#
# ============================================================================
#
# contoh memanfaatkan glsl pada webgl untuk membuat hasil garis persamaan
# dengan algoritma regresi linear (reglin)
# di mana Verteks diproses menggunakan OpenGL Shading Language (GLSL) atau disebut dengan vertex shader,
# menggunakan skrip dengan tipe x-shader/x-vertex.
@app.route('/plotreglin_dgn_glsl')
def draw_plotreglin_dgn_glsl():

    import os.path
    import pandas as pd
    # import numpy as np

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # contoh load data yang akan dibuat regresi linier:
    # ---------------
    # Load data Dataset Usia dan Rating Efektifitas Vaksin dll.csv
    #
    # Sumber: bahan ajar P. Imam
    #

    # misal dari sekian banyak fitur, hanya diambil 2 fitur
    # x = usia, dan y = rating_efektifitas_hasil_vaksinasi
    file_path = os.path.join(BASE_DIR, "static/data_regresi/Dataset Usia dan Rating Efektifitas Vaksin dll.csv")
    dataset = pd.read_csv(file_path)

    x = dataset['usia'].values
    y = dataset['rating_efektifitas_hasil_vaksinasi'].values


    koordinat_x_y_z = ''
    len_loop = 0
    for in_x,in_y in zip(x,y):
        koordinat_x = str(in_x)
        koordinat_y = str(in_y)
        koordinat_z = str(0)

        # if(len_loop==0):
        #     koordinat_x_y_z += '('+ koordinat_x + ',' + koordinat_y + ',' + koordinat_z + ')'
        # else:
        #     koordinat_x_y_z += ',('+ koordinat_x + ',' + koordinat_y + ',' + koordinat_z + ')'
        # len_loop += 1

        if(len_loop==0):
            koordinat_x_y_z += koordinat_x + ',' + koordinat_y + ',' + koordinat_z
        else:
            koordinat_x_y_z += ','+ koordinat_x + ',' + koordinat_y + ',' + koordinat_z

        len_loop += 1




    # ---------------------------------------------------------------------------------------------------------

    # x_str = ','.join(str(in_x) for in_x in x) # '0,3,5'
    # y_str = ','.join(str(in_y) for in_y in y) # '0,3,5'

    # return x_str + ' || ' + y_str;


    # menampilkan hasil konversi ke x,y,z
    # return koordinat_x_y_z;


    mylist_koordinat_x_y_z = koordinat_x_y_z.replace(' ','').split(',')
    return render_template('draw_regresi_linier_dgn_glsl.html', coords_xyz = mylist_koordinat_x_y_z)

@app.route('/plotreglin_non_glsl')
def draw_plotreglin_non_glsl():

    import os.path
    import pandas as pd
    # import numpy as np

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # contoh load data yang akan dibuat regresi linier:
    # ---------------
    # Load data Dataset Usia dan Rating Efektifitas Vaksin dll.csv
    #
    # Sumber: bahan ajar P. Imam
    #

    # misal dari sekian banyak fitur, hanya diambil 2 fitur
    # x = usia, dan y = rating_efektifitas_hasil_vaksinasi
    file_path = os.path.join(BASE_DIR, "static/data_regresi/Dataset Usia dan Rating Efektifitas Vaksin dll.csv")
    dataset = pd.read_csv(file_path)

    x = dataset['usia'].values
    y = dataset['rating_efektifitas_hasil_vaksinasi'].values


    koordinat_x_y_z = ''
    len_loop = 0
    for in_x,in_y in zip(x,y):
        koordinat_x = str(in_x)
        koordinat_y = str(in_y)
        koordinat_z = str(0)

        # if(len_loop==0):
        #     koordinat_x_y_z += '('+ koordinat_x + ',' + koordinat_y + ',' + koordinat_z + ')'
        # else:
        #     koordinat_x_y_z += ',('+ koordinat_x + ',' + koordinat_y + ',' + koordinat_z + ')'
        # len_loop += 1

        if(len_loop==0):
            koordinat_x_y_z += koordinat_x + ',' + koordinat_y + ',' + koordinat_z
        else:
            koordinat_x_y_z += ','+ koordinat_x + ',' + koordinat_y + ',' + koordinat_z

        len_loop += 1




    # ---------------------------------------------------------------------------------------------------------

    # x_str = ','.join(str(in_x) for in_x in x) # '0,3,5'
    # y_str = ','.join(str(in_y) for in_y in y) # '0,3,5'

    # return x_str + ' || ' + y_str;


    # menampilkan hasil konversi ke x,y,z
    # return koordinat_x_y_z;


    mylist_koordinat_x_y_z = koordinat_x_y_z.replace(' ','').split(',')
    return render_template('draw_regresi_linier_dgn_non_glsl.html', coords_xyz = mylist_koordinat_x_y_z)


@app.route('/reglin')
def draw_reglin():

    import os.path
    import pandas as pd
    # import numpy as np

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # contoh load data yang akan dibuat regresi linier:
    # ---------------
    # Load data Dataset Usia dan Rating Efektifitas Vaksin dll.csv
    #
    # Sumber: bahan ajar P. Imam
    #

    # misal dari sekian banyak fitur, hanya diambil 2 fitur
    # x = usia, dan y = rating_efektifitas_hasil_vaksinasi
    file_path = os.path.join(BASE_DIR, "static/data_regresi/Dataset Usia dan Rating Efektifitas Vaksin dll.csv")
    dataset = pd.read_csv(file_path)

    x = dataset['usia'].values
    y = dataset['rating_efektifitas_hasil_vaksinasi'].values


    koordinat_x_y_z = ''
    len_loop = 0
    for in_x,in_y in zip(x,y):
        koordinat_x = str(in_x)
        koordinat_y = str(in_y)
        koordinat_z = str(0)

        if(len_loop==0):
            koordinat_x_y_z += '('+ koordinat_x + ',' + koordinat_y + ',' + koordinat_z + ')'
        else:
            koordinat_x_y_z += ',('+ koordinat_x + ',' + koordinat_y + ',' + koordinat_z + ')'
        len_loop += 1

        # if(len_loop==0):
        #     koordinat_x_y_z += koordinat_x + ',' + koordinat_y + ',' + koordinat_z
        # else:
        #     koordinat_x_y_z += ','+ koordinat_x + ',' + koordinat_y + ',' + koordinat_z




    # ---------------------------------------------------------------------------------------------------------

    # x_str = ','.join(str(in_x) for in_x in x) # '0,3,5'
    # y_str = ','.join(str(in_y) for in_y in y) # '0,3,5'

    # return x_str + ' || ' + y_str;


    # menampilkan hasil konversi ke x,y,z
    return koordinat_x_y_z;


    # mylist_koordinat_x_y_z = koordinat_x_y_z.replace(' ','').split(',')
    # return render_template('draw_regresi_linier_dgn_glsl.html', coords_xyz = mylist_koordinat_x_y_z)

@app.route('/quadshader')
def draw_quadshader():
    return render_template('draw_quad_shadertoy.html')

@app.route('/menu')
def menugrafkom():
    return render_template('launchpad_grafkom.html')


@app.route("/login",methods=["GET", "POST"])
def login():
  conn = connect_db()
  db = conn.cursor()
  msg = ""
  if request.method == "POST":
      mail = request.form["mail"]
      passw = request.form["passw"]

      rs = db.execute("SELECT * FROM user WHERE Mail=\'"+ mail +"\'"+" AND Password=\'"+ passw+"\'" + " LIMIT 1")

      conn.commit()

      hasil = []
      for v_login in rs:
          hasil.append(v_login)

      if hasil:
          session['name'] = v_login[3]
          return redirect(url_for("fphome"))
      else:
          msg = "Masukkan Username (Email) dan Password dgn Benar!"

  return render_template("login.html", msg = msg)

@app.route("/register", methods=["GET", "POST"])
def register():
  conn = connect_db()
  db = conn.cursor()
  #conn = sqlite3.connect('fga_big_data_rev2.db')
  #db = conn.cursor()
  if request.method == "POST":
      mail = request.form['mail']
      uname = request.form['uname']
      passw = request.form['passw']

      cmd = "insert into user(Mail, Password,Name,Level) values('{}','{}','{}','{}')".format(mail,passw,uname,'1')
      conn.execute(cmd)
      conn.commit()

      # conn = db

      return redirect(url_for("login"))
  return render_template("register.html")

@app.route("/bli", methods=["GET", "POST"])
def bli():
  conn = connect_db()
  db = conn.cursor()
  #conn = sqlite3.connect('fga_big_data_rev2.db')
  #db = conn.cursor()

      # conn = db

    #   return redirect(url_for("biz"))
  return render_template("bli.html")

@app.route("/biz", methods=["GET", "POST"])
def biz():
  conn = connect_db()
  db = conn.cursor()
  #conn = sqlite3.connect('fga_big_data_rev2.db')
  #db = conn.cursor()

      # conn = db

    #   return redirect(url_for("biz"))
  return render_template("biz.html")


@app.route("/contohfp2_nonspark", methods=["GET", "POST"])
def contohfp2_nonspark():
  # Simple Linear Regression / Klasifikasi / Clustering
  # Importing the libraries
  import numpy as np
  # import matplotlib.pyplot as plt
  import pandas as pd
  import os.path

  BASE_DIR = os.path.dirname(os.path.abspath(__file__))
  url = os.path.join(BASE_DIR, "Salary_Data.csv")

  # Importing the dataset => ganti sesuai dengan case yg anda usulkan
  # a. Min. 30 Data dari case data simulasi dari yg Anda usulkan
  # b. Min. 30 Data dari real case, sesuai dgn yg Anda usulkan dari tugas minggu ke-3 (dari Kaggle/UCI Repository)
  # url = "./Salary_Data.csv"
  dataset = pd.read_csv(url)
  X = dataset.iloc[:, :-1].values
  y = dataset.iloc[:, 1].values

  # Splitting the dataset into the Training set and Test set
  # Lib-nya selain sklearn/ Tensorflow/ Keras/ PyTorch/ etc
  from sklearn.model_selection import train_test_split
  X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 1/3, random_state = 0)

  # Hitung Mape
  # from sklearn.metrics import mean_absolute_percentage_error

  # Feature Scaling
  """from sklearn.preprocessing import StandardScaler
  sc_X = StandardScaler()
  X_train = sc_X.fit_transform(X_train)
  X_test = sc_X.transform(X_test)
  sc_y = StandardScaler()
  y_train = sc_y.fit_transform(y_train)"""

  # Fitting Simple Linear Regression to the Training set
  from sklearn.linear_model import LinearRegression
  regressor = LinearRegression()
  myModelReg = regressor.fit(X_train, y_train)

  # Simpan hasil model fit
  with open(os.path.join(BASE_DIR, "myModelReg.joblib.pkl"), 'wb') as f:
    joblib.dump(myModelReg, f, compress=9)

  # Load hasil model fit
  with open(os.path.join(BASE_DIR, "myModelReg.joblib.pkl"), 'rb') as f:
    myModelReg_load = joblib.load(f)

  # Predicting the Test set results
  #y_pred = regressor.predict(X_test)
  #y_pred2 = regressor.predict(X_train)

  y_pred = myModelReg_load.predict(X_test)
  y_pred2 = myModelReg_load.predict(X_train)

  # Visualising the Training set results
  # plt.scatter(X_train, y_train, color = 'red')
  # plt.plot(X_train, regressor.predict(X_train), color = 'blue')


  # Visualising the Test set results
  # plt.scatter(X_test, y_test, color = 'red')
  # plt.plot(X_train, regressor.predict(X_train), color = 'blue')
  # plt.title('Salary vs Experience (Test set)')
  # plt.xlabel('Years of Experience')
  # plt.ylabel('Salary')
  # plt.show()

  aktual, predict = y_train, y_pred2
  mape = np.sum(np.abs(((aktual - predict)/aktual)*100))/len(predict)

  # return render_template('MybigdataApps.html', y_aktual = list(y_train), y_prediksi = list(y_pred2), mape = mape)
  return render_template('MybigdataAppsNonPySpark.html', y_aktual = list(y_train), y_prediksi = list(y_pred2), mape = mape)

@app.route("/contohfp2_spark", methods=["GET", "POST"])
def contohfp2_spark():
  # MLLIB dari Pyspark Simple Linear Regression /Klasifikasi / Clustering
  # Importing the libraries
  import numpy as np
  import matplotlib.pyplot as plt
  import pandas as pd
  import os

  BASE_DIR = os.path.dirname(os.path.abspath(__file__))
  url = os.path.join(BASE_DIR, "Salary_Data.csv")

  import findspark
  findspark.init()
#   import findspark
#   findspark.init("/home/imamcs/spark-3.1.2-bin-hadoop3.2")

  #os.environ["SPARK_HOME"] ="/home/imamcs/mysite/FGA-Big-Data-Using-Python-Filkom-x-Mipa-UB-2021/spark-2.0.0-bin-hadoop2.7"
  #os.environ["PYTHONPATH"] ="/home/imamcs/mysite/FGA-Big-Data-Using-Python-Filkom-x-Mipa-UB-2021/spark-2.0.0-bin-hadoop2.7/python/"
  #os.environ["PYTHONPATH"] +=":/home/imamcs/mysite/FGA-Big-Data-Using-Python-Filkom-x-Mipa-UB-2021/spark-2.0.0-bin-hadoop2.7/python/lib/py4j-0.10.1-src.zip"

  #os.environ["PYTHONPATH"] = "/spark-2.4.1-bin-hadoop2.7/python/"
  #os.environ["PYTHONPATH"] += ":/spark-2.4.1-bin-hadoop2.7/python/lib/py4j-0.10.7-src.zip"

#   print(os.environ["SPARK_HOME"])

#   print(os.environ["PYTHONPATH"])

#   !echo $PYTHONPATH

  from pyspark.sql import SparkSession
  spark = SparkSession.builder.appName("Linear Regression").config("spark.executor.memory", "512m").getOrCreate()

  from pyspark.ml.regression import LinearRegression
  from pyspark.ml.linalg import Vectors
  from pyspark.ml.feature import VectorAssembler
  from pyspark.ml.feature import IndexToString, StringIndexer
  from pyspark.ml import Pipeline, PipelineModel

  from pyspark import SQLContext, SparkConf, SparkContext
  from pyspark.sql import SparkSession
  #sc = SparkContext.getOrCreate()
  sc = spark.sparkContext
  if (sc is None):
      #sc = SparkContext(master="local[*]", appName="Linear Regression")

      spark = SparkSession.\
        builder.\
        appName("Linear Regression").\
        master("local[*]").\
        config("spark.executor.memory", "512m").\
        getOrCreate()

      sc = spark.sparkContext

      # ------------------
  spark = SparkSession(sparkContext=sc)
  # sqlcontext = SQLContext(sc)

  # Importing the dataset => ganti sesuai dengan case yg anda usulkan
  # a. Min. 30 Data dari case data simulasi dari yg Anda usulkan
  # b. Min. 30 Data dari real case, sesuai dgn yg Anda usulkan dari tugas minggu ke-3 (dari Kaggle/UCI Repository)
  # url = "./Salary_Data.csv"

  sqlcontext = SQLContext(sc)
  data = sqlcontext.read.csv(url, header = True, inferSchema = True)

  #from pyspark.ml.feature import VectorAssembler
  # mendifinisikan Salary sebagai variabel label/predictor
  dataset = data.select(data.YearsExperience, data.Salary.alias('label'))
  # split data menjadi 70% training and 30% testing
  training, test = dataset.randomSplit([0.7, 0.3], seed = 100)
  # mengubah fitur menjadi vektor
  assembler = VectorAssembler().setInputCols(['YearsExperience',]).setOutputCol('features')
  trainingSet = assembler.transform(training)
  # memilih kolom yang akan di vektorisasi
  trainingSet = trainingSet.select("features","label")

  #from pyspark.ml.regression import LinearRegression
  # fit data training ke model
  lr = LinearRegression()
  lr_Model = lr.fit(trainingSet)

  # Simpan hasil model fit
  #import tempfile
  #path = tempfile.mkdtemp()
  #path = os.path.join(BASE_DIR, "myModel_Spark")
  path_myModel_Spark = os.path.join(BASE_DIR, "myModel_Spark")
  #lr_Model.write.save(os.path.join(BASE_DIR, "myModelReg_Spark"))
  #lr_Model.save(spark, path_myModel_Spark)
  #lr_Model.save(path_myModel_Spark)
  lr_Model.write().overwrite().save(path_myModel_Spark)
  #write().overwrite().save(path_myModel_Spark)

  #save(sc, path)

  # Load hasil model fit
  #myModelReg_Spark_load = PipelineModel.load(os.path.join(BASE_DIR, "myModelReg_Spark"))
  #myModelReg_Spark_load = lr.load(spark, path_myModel_Spark)
  myModelReg_Spark_load = lr.load(path_myModel_Spark)


  # assembler : fitur menjadi vektor
  testSet = assembler.transform(test)
  # memilih kolom fitur dan label
  testSet = testSet.select("features", "label")

  # fit testing data ke model linear regression
  #testSet = lr_Model.transform(testSet)
  testSet = myModelReg_Spark_load.transform(testSet)

  # testSet.show(truncate=False)

  from pyspark.ml.evaluation import RegressionEvaluator
  evaluator = RegressionEvaluator()
  # print(evaluator.evaluate(testSet, {evaluator.metricName: "r2"}))

  y_pred2 = testSet.select("prediction")
  # y_pred2.show()


  return render_template('MybigdataAppsPySpark.html', y_aktual = y_pred2.rdd.flatMap(lambda x: x).collect(), y_prediksi = y_pred2.rdd.flatMap(lambda x: x).collect(), mape = evaluator.evaluate(testSet, {evaluator.metricName: "r2"}))

@app.route("/bigdataApps", methods=["GET", "POST"])
def bigdataApps():
  if request.method == 'POST':
    import pandas as pd
    import numpy as np
    import os.path

    #BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    #url = os.path.join(BASE_DIR, "dataset_dump.csv")

    dataset = request.files['inputDataset']
    # url = "./dataset_dump.csv"

    persentase_data_training = 90
    banyak_fitur = int(request.form['banyakFitur'])
    banyak_hidden_neuron = int(request.form['banyakHiddenNeuron'])
    dataset = pd.read_csv(dataset, delimiter=';', names = ['Tanggal', 'Harga'], usecols=['Harga'])
    # dataset = pd.read_csv(url, delimiter=';', names = ['Tanggal', 'Harga'], usecols=['Harga'])
    # dataset = dataset.fillna(method='ffill')
    minimum = int(dataset.min()-10000)
    maksimum = int(dataset.max()+10000)
    new_banyak_fitur = banyak_fitur + 1
    hasil_fitur = []
    for i in range((len(dataset)-new_banyak_fitur)+1):
      kolom = []
      j = i
      while j < (i+new_banyak_fitur):
        kolom.append(dataset.values[j][0])
        j += 1
      hasil_fitur.append(kolom)
    hasil_fitur = np.array(hasil_fitur)
    data_normalisasi = (hasil_fitur - minimum)/(maksimum - minimum)
    data_training = data_normalisasi[:int(persentase_data_training*len(data_normalisasi)/100)]
    data_testing = data_normalisasi[int(persentase_data_training*len(data_normalisasi)/100):]

    #Training
    bobot = np.random.rand(banyak_hidden_neuron, banyak_fitur)
    bias = np.random.rand(banyak_hidden_neuron)
    h = 1/(1 + np.exp(-(np.dot(data_training[:, :banyak_fitur], np.transpose(bobot)) + bias)))
    h_plus = np.dot(np.linalg.inv(np.dot(np.transpose(h),h)),np.transpose(h))
    output_weight = np.dot(h_plus, data_training[:, banyak_fitur])

    #Testing
    h = 1/(1 + np.exp(-(np.dot(data_testing[:, :banyak_fitur], np.transpose(bobot)) + bias)))
    predict = np.dot(h, output_weight)
    predict = predict * (maksimum - minimum) + minimum

    #MAPE
    aktual = np.array(hasil_fitur[int(persentase_data_training*len(data_normalisasi)/100):, banyak_fitur])
    mape = np.sum(np.abs(((aktual - predict)/aktual)*100))/len(predict)

    print("predict = ", predict)
    print("aktual =", aktual)
    print("mape = ", mape)

    # return render_template('bigdataApps.html', data = {'y_aktual' : list(aktual),'y_prediksi' : list(predict),'mape' : mape})
    return render_template('bigdataApps.html', y_aktual = list(aktual), y_prediksi = list(predict), mape = mape)


    # return "Big Data Apps " + str(persentase_data_training) + " banyak_fitur = " + str(banyak_fitur) + " banyak_hidden_neuron = " + str(banyak_hidden_neuron) + " :D"
  else:
    return render_template('bigdataApps.html')

def connect_db():
    import os.path

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "data.db")
    # with sqlite3.connect(db_path) as db:

    return sqlite3.connect(db_path)

#konversi Seq object menjadi array int [a-z], misal menjadi [1-26] => next untuk bahan optimasi penskalaan
def seq2val_space_plus_arr_a_z(seq_):
    #get unik kode atau simbol IUPAC utk nucleotides
    # print(set(seq_.lower()))
    # {'N', 'G', 't', 'M', 'C', 'A', 'g', 'T', 'c', 'R', 'a'}
    # ['n', 'g', 't', 'm', 'c', 'a', 'g', 't', 'c', 'r', 'a']
    # {'a', 'c', 'g', 'm', 'n', 'r', 't'}

    # konversi setiap char kodenya menjadi angka, misal a = 1, c = 2, g = 3, t = 4
    # Di mana konversi ini nantinya dapat juga dicari nilai yang optimal
    seq_ = str(seq_).lower()

    for idx_letter in range(26):
        seq_= seq_.replace(chr(idx_letter+97),str(idx_letter)+" ")

    val_seq_ = seq_.rstrip()
    # print(val_seq_)

    # upper() sequence
    # up_seq_ = seq_.upper()
    # print(up_seq_)

    arr_val_seq_ = np.fromstring(val_seq_,dtype=int,sep=' ')

    return arr_val_seq_

## untuk trendTwit
## mencoba streaming
class StreamListener(tweepy.StreamListener):
    def __init__(self, start_time):
        """
        Initalizes a StreamListener object.
        start_time: the time the stream was connected
        tweets: a dictionary to store processed tweets and their polarity
        """
        tweepy.StreamListener.__init__(self)
        self.start_time = start_time
        self.tweets = {}

    def on_status(self, status):
        """
        Function called when the stream gets connected. Filters the tweets by user and language.
        If 30 seconds have passed since the stream was connected, returns False so stream can disconnect.
        """
        if filter_users.add_user(status) and status.lang == "en":
            self.process_tweet(status)

        #we want to collect tweets every 30 seconds so we set an internal timer inside the class
        if datetime.datetime.now() <= self.start_time + datetime.timedelta(seconds=30):
            return True

        return False

    def process_tweet(self, status):
        """
        Links, mentions, "RT"s, emojis, and stopwords are removed from the tweet. Sentiment anlaysis is performed and
        the clean tweet (sans stopwords) and analysis result is stored in the tweets dict.

        status: a status object

        """
        #remove links, mentions, "RT"s, emojis, non-ascii chars from the tweet
        clean_tweet = re.sub(r"([^\w]?:\@|https?\://)\S+", "", status.text)
        clean_tweet = re.sub(r'[^\x00-\x7F]+'," ", clean_tweet)

        clean_tweet = clean_tweet.replace("RT ", "")

        #remove numbers and punctuation
        translator = str.maketrans("", "", string.punctuation + string.digits)
        clean_tweet = clean_tweet.translate(translator)


        clean_tweet = clean_tweet.lower()

        #https://stackoverflow.com/questions/2400504/easiest-way-to-replace-a-string-using-a-dictionary-of-replacements/2400577#2400577
        slang = re.compile(r'\b(' + '|'.join(settings.SLANG_DICT.keys()) + r')\b')
        clean_tweet = slang.sub(lambda x: settings.SLANG_DICT[x.group()], clean_tweet)
        ####

        polarity = StreamListener.get_polarity(clean_tweet)

        #remove stopwords(using the custom stopwords list in settings.py) to get most important words
        important_words = " ".join([word for word in clean_tweet.split() if word not in settings.STOPWORDS_SET])

        #add the processed tweet into the tweets list
        self.tweets[important_words] = polarity

    @staticmethod
    def get_polarity(tweet):
        """
        Determines the polarity of the tweet using TextBlob.

        tweet: a partially processed tweet (still has stopwords)
        return: int polarity -> 1 if positive, 0 if neutral, -1 if negative

        """

        text_blob = TextBlob(tweet)

        tweet_polarity_float = text_blob.sentiment.polarity

        #greater than 0.05 ->  positive, less than -0.05 -> negative, else neutral
        if tweet_polarity_float >= 0.05:
            polarity = 1
        elif tweet_polarity_float <= -0.05:
            polarity = -1
        else:
            polarity = 0

        return polarity


    def get_tweets(self):
        """
        Returns a copy of the tweets dictionary.
        """
        return self.tweets.copy()

    def on_error(self, status_code):
        """
        Handles errors coming from the Twitter API. If being rate limited,
        Twitter will send a 420 status code and we will disconnect.

        """
        if status_code == 420:
            return False


class SortData(object):
    data = {}

    def __init__(self, tweets):
        """
        Initializes a SortData object.
        tweets: a dictionary of processed tweets and their polarity
        """
        self.tweets = tweets

    def calculate_frequencies(self):
        """
        Calculates the frequencies of the words in processed tweets
        and creates the data dictionary. A key value pair for the dictionary
        will have the word as the key and a list as its value. The list will include
        the number of times the word has occurred in all the tweets seen so far and
        another list including the number of positive, neutral, and negative tweets
        containing that word.

        """
        #key value pair for the data dictionary -> word:[count, [numPositiveTweets, numNeutralTweets, numNegativeTweets]]

        for tweet, polarity in self.tweets.items():
            for word in tweet.split():
                if word not in self.data:

                    self.data[word] = [0, [0, 0, 0]]

                    self.data[word][0] = 1

                    self.update_polarity_frequency(word, polarity)

                else:
                    self.data[word][0] += 1

                    self.update_polarity_frequency(word, polarity)


    def update_polarity_frequency(self, word, polarity):
        """
        Determines what polarity (positive, neutral, negative) the tweet has
        according to the tweets dictionary and updates the value in the data dictionary.

        """
        if polarity == 1:
            self.data[word][1][0] += 1
        elif polarity == 0:
            self.data[word][1][1] += 1
        else:
            self.data[word][1][2] += 1


    def get_most_common_words(self):
        """
        Removes all the words in the data dictionary that have occurred
        less than two times in all the tweets seen so far. Sorts the data
        dictionary by frequency of the words in descending order.

        return: a JSON object version of the sorted dictionary

        """
        self.calculate_frequencies()

        data_copy = self.data.copy()

        for word in data_copy:
             if self.data[word][0] <= 2:
                 del self.data[word]

        sorted_words = OrderedDict(sorted(self.data.items(), key = itemgetter(1), reverse = True))

        #make sure the dictionary is less than or equal to 15 words so ajax request in javascript
        #doesn't slow down
        while len(sorted_words) >= 15:
            sorted_words.popitem()
        return json.dumps(sorted_words)

def event_stream():
    """
    Connects the stream, sorts and processes the data, and creates
    a dictionary of the most common words found.

    return: a JSON object containing the most common words found in the tweets sample
            and their frequencies and polarity data

    """
    try:
        stream_listener = StreamListener(datetime.datetime.now())
        # stream = tweepy.Stream(auth = api.auth, listener = stream_listener)
        stream = tweepy.Stream(auth, listener = stream_listener)

        # # receive tweets on assigned tracks,
        # # filter them by assigned conditions and send them to port
        # twitter_stream = Stream(auth, Listener(c_socket, api))
        # # twitter_stream.filter(lang=["en"],track=tracks)
        # twitter_stream.filter(track=tracks,languages=["id","en"])

        #we want a lot of tweets so we filter with most used words
        stream.filter(track = settings.COMMON_WORDS, locations = settings.LOCATIONS)
        stream.disconnect()
        sortData = SortData(stream_listener.get_tweets())
        return sortData.get_most_common_words()
    except ProtocolError:
        print("There was an error. Restarting stream...")
    except ConnectionError:
        print("There was an error. Restarting stream...")

@app.route('/twit')
def twit():
    #clear the data dictionary when page is refreshed
    SortData.data.clear()
    # return render_template("twit.html")
    return render_template("twity.html")

@app.route('/stream')
def stream():
    return Response(event_stream(), mimetype="application/json")

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html")

@app.errorhandler(500)
def internal_server_error(error):
    return render_template("500.html")

# labels_trendTwit = []
# values_trendTwit = []
# @app.route("/trendTwit")
# def chart_trendTwit():
#     global labels_trendTwit,values_trendTwit
#     labels = []
#     values = []
#     return render_template('chart.html', values=values_trendTwit, labels=labels_trendTwit)


# @app.route('/refreshData_trendTwit')
# def refresh_graph_data_trendTwit():
#     global labels_trendTwit, values_trendTwit
#     print("labels now: " + str(labels_trendTwit))
#     print("data now: " + str(values_trendTwit))
#     return jsonify(sLabel=labels_trendTwit, sData=values_trendTwit)


# @app.route('/updateData_trendTwit', methods=['POST'])
# def update_data_post_trendTwit():
#     global labels_trendTwit, values_trendTwit
#     if not request.form or 'data' not in request.form:
#         return "error",400
#     labels_trendTwit = ast.literal_eval(request.form['label'])
#     values_trendTwit = ast.literal_eval(request.form['data'])
#     print("labels received: " + str(labels_trendTwit))
#     print("data received: " + str(values_trendTwit))
#     return "success",201


# cara akses, misal: http://imamcs.pythonanywhere.com/api/fp/3.0/?a=70&b=3&c=2
@app.route("/api/fp/3.0/", methods=["GET"])
def api():
    import os.path
    import sys

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    url = os.path.join(BASE_DIR, "dataset_dump_tiny.csv")

    # url = "../GGRM.JK.csv"
    # dataset=pd.read_csv(url)

    import pandas as pd
    import numpy as np
    import json
    # from django.http import HttpResponse
    from flask import Response


    a, b, c = request.args.get('a'), request.args.get('b'),request.args.get('c')
    # print(a,' ',b,' ',c)
    # bar = request.args.to_dict()
    # print(bar)

    # dataset = request.FILES['inputDataset']#'E:/Pak Imam/Digitalent/dataset_dump.csv'
    persentase_data_training = int(a)
    banyak_fitur = int(b)
    banyak_hidden_neuron = int(c)
    # print(persentase_data_training,banyak_fitur,banyak_hidden_neuron)

    dataset = pd.read_csv(url, delimiter=';', names = ['Tanggal', 'Harga'], usecols=['Harga'])
    #dataset = pd.read_csv(url, usecols=['Close'])
    dataset = dataset.fillna(method='ffill')

    # print("missing value", dataset.isna().sum())

    minimum = int(dataset.min())
    maksimum = int(dataset.max())
     # print(minimum,maksimum)
    new_banyak_fitur = banyak_fitur + 1
    hasil_fitur = []
    for i in range((len(dataset)-new_banyak_fitur)+1):
        kolom = []
        j = i
        while j < (i+new_banyak_fitur):
            kolom.append(dataset.values[j][0])
            j += 1
        hasil_fitur.append(kolom)
    hasil_fitur = np.array(hasil_fitur)
        # print(hasil_fitur)
    data_normalisasi = (hasil_fitur - minimum)/(maksimum - minimum)

    data_training = data_normalisasi[:int(
        persentase_data_training*len(data_normalisasi)/100)]
    data_testing = data_normalisasi[int(
        persentase_data_training*len(data_normalisasi)/100):]

    # print(data_training)
    # Training
    is_singular_matrix = True
    while(is_singular_matrix):
        bobot = np.random.rand(banyak_hidden_neuron, banyak_fitur)
        #print("bobot", bobot)
        bias = np.random.rand(banyak_hidden_neuron)
        h = 1 / \
            (1 + np.exp(-(np.dot(data_training[:, :banyak_fitur], np.transpose(bobot)) + bias)))

        #print("h", h)
        #print("h_transpose", np.transpose(h))
        #print("transpose dot h", np.dot(np.transpose(h), h))

        # cek matrik singular
        cek_matrik = np.dot(np.transpose(h), h)
        det_cek_matrik = np.linalg.det(cek_matrik)
        if det_cek_matrik != 0:
            #proceed

        #if np.linalg.cond(cek_matrik) < 1/sys.float_info.epsilon:
            # i = np.linalg.inv(cek_matrik)
            is_singular_matrix = False
        else:
            is_singular_matrix = True


    h_plus = np.dot(np.linalg.inv(cek_matrik), np.transpose(h))

    # print("h_plus", h_plus)
    output_weight = np.dot(h_plus, data_training[:, banyak_fitur])

        # print(output_weight)
        # [none,none,...]

    # Testing
    h = 1 / \
        (1 + np.exp(-(np.dot(data_testing[:, :banyak_fitur], np.transpose(bobot)) + bias)))
    predict = np.dot(h, output_weight)
    predict = (predict * (maksimum - minimum) + minimum)

    # MAPE
    aktual = np.array(hasil_fitur[int(
        persentase_data_training*len(data_normalisasi)/100):, banyak_fitur]).tolist()
    mape = np.sum(np.abs(((aktual - predict)/aktual)*100))/len(predict)
    prediksi = predict.tolist()
    # print(prediksi, 'vs', aktual)
    # response = json.dumps({'y_aktual': aktual, 'y_prediksi': prediksi, 'mape': mape})

    # return Response(response, content_type='text/json')
    # return Response(response, content_type='application/json')
    #return Response(response, content_type='text/xml')


    response = jsonify({'y_aktual': aktual, 'y_prediksi': prediksi, 'mape': mape})


    # Enable Access-Control-Allow-Origin
    response.headers.add("Access-Control-Allow-Origin", "*")
    # response.headers.add("access-control-allow-credentials","false")
    # response.headers.add("access-control-allow-methods","GET, POST")


    # r = Response(response, status=200, mimetype="application/json")
    # r.headers["Content-Type"] = "application/json; charset=utf-8"
    return response



# get json data from a url using flask in python
@app.route('/baca_api', methods=["GET"])
def baca_api():
    import requests
    import json
    # uri = "https://api.stackexchange.com/2.0/users?order=desc&sort=reputation&inname=fuchida&site=stackoverflow"
    uri = "http://enterumum.pythonanywhere.com/api/fp/3.0/?a=50&b=3&c=2"
    try:
        uResponse = requests.get(uri)
    except requests.ConnectionError:
        return "Terdapat Error Pada Koneksi Anda"
    Jresponse = uResponse.text
    data = json.loads(Jresponse)

    # json.loads(response.get_data().decode("utf-8"))
    # data = json.loads(requests.get(uri).decode("utf-8"))
    # data = json.loads(response.get(uri).get_data().decode("utf-8"))

    # import urllib.request
    # with urllib.request.urlopen("http://imamcs.pythonanywhere.com/api/fp/3.0/?a=90&b=3&c=2") as url:
    #     data = json.loads(url.read().decode())
    #     #print(data)

    # from urllib.request import urlopen

    # import json
    # import json
    # store the URL in url as
    # parameter for urlopen
    # url = "https://api.github.com"

    # store the response of URL
    # response = urlopen(url)

    # storing the JSON response
    # from url in data
    # data_json = json.loads(response.read())

    # print the json response
    # print(data_json)

    # data = \
    #     {
    #   "items": [
    #     {
    #       "badge_counts": {
    #         "bronze": 16,
    #         "silver": 4,
    #         "gold": 0
    #       },
    #       "account_id": 258084,
    #       "is_employee": false,
    #       "last_modified_date": 1573684556,
    #       "last_access_date": 1628710576,
    #       "reputation_change_year": 0,
    #       "reputation_change_quarter": 0,
    #       "reputation_change_month": 0,
    #       "reputation_change_week": 0,
    #       "reputation_change_day": 0,
    #       "reputation": 420,
    #       "creation_date": 1292207782,
    #       "user_type": "registered",
    #       "user_id": 540028,
    #       "accept_rate": 100,
    #       "location": "Minneapolis, MN, United States",
    #       "website_url": "http://fuchida.me",
    #       "link": "https://stackoverflow.com/users/540028/fuchida",
    #       "profile_image": "https://i.stack.imgur.com/kP5GW.png?s=128&g=1",
    #       "display_name": "Fuchida"
    #     }
    #   ],
    #   "has_more": false,
    #   "quota_max": 300,
    #   "quota_remaining": 299
    # }

    # displayName = data['items'][0]['display_name']# <-- The display name
    # reputation = data['items'][0]['reputation']# <-- The reputation

    # y_train = data['y_aktual']
    # y_pred = data['y_prediksi']
    # mape = data['mape']

    return data
    # return str(mape)
    # return render_template('MybigdataAppsNonPySpark.html', y_aktual = list(y_train), y_prediksi = list(y_pred), mape = mape)


@app.route('/upload', methods=["GET", "POST"])
def upload():

    form = UploadForm()
    if request.method == "POST":

        if form.validate_on_submit():
            file_name = form.file.data
            database(name=file_name.filename, data=file_name.read() )
            # return render_template("upload.html", form=form)
            return redirect(url_for("dashboard"))

    return render_template("upload.html", form=form)


@app.route('/hapus/file/', methods=["GET"])
def hapus():
    name = request.args.get('name')
    conn = connect_db()
    db = conn.cursor()

    db.execute("DELETE FROM  upload WHERE name =\'"+ name +"\'")
    # mydata
    # for x in c.fetchall():
    #     name_v=x[0]
    #     data_v=x[1]
    #     break

    conn.commit()
    db.close()
    conn.close()

    return redirect(url_for("dashboard"))

@app.route('/unduh/file/', methods=["GET"])
def unduh():
    name = request.args.get('name')
    conn = connect_db()
    db = conn.cursor()

    # c = db.execute(""" SELECT * FROM  upload WHERE name ="""+ name)
    c = db.execute("SELECT * FROM  upload WHERE name =\'"+ name +"\'")
    # mydata
    for x in c.fetchall():
        name_v=x[0]
        data_v=x[1]
        break

    conn.commit()
    db.close()
    conn.close()

    # return render_template('dashboard.html', header = mydata)


    return send_file(BytesIO(data_v), attachment_filename=name_v, as_attachment=True)


@app.route('/download', methods=["GET", "POST"])
def download():

    form = UploadForm()

    if request.method == "POST":
        conn = connect_db()
        db = conn.cursor()

        # conn= sqlite3.connect("fga_big_data_rev2.db")
        # cursor = conn.cursor()
        print("IN DATABASE FUNCTION ")
        c = db.execute(""" SELECT * FROM  upload """)

        for x in c.fetchall():
            name_v=x[0]
            data_v=x[1]
            break

        conn.commit()
        db.close()
        conn.close()

        return send_file(BytesIO(data_v), attachment_filename='flask.pdf', as_attachment=True)


    return render_template("upload.html", form=form)



# class LoginForm(FlaskForm):
class UploadForm(FlaskForm):
    file = FileField()
    submit = SubmitField("submit")
    download = SubmitField("download")

def database(name, data):
    conn = connect_db()
    db = conn.cursor()

    # conn= sqlite3.connect("fga_big_data_rev2.db")
    # cursor = conn.cursor()

    db.execute("""CREATE TABLE IF NOT EXISTS upload (name TEXT,data BLOP) """)
    db.execute("""INSERT INTO upload (name, data) VALUES (?,?) """,(name,data))

    conn.commit()
    db.close()
    conn.close()

def query():
    # conn= sqlite3.connect("fga_big_data_rev2.db")
    # cursor = conn.cursor()

    conn = connect_db()
    db = conn.cursor()

    print("IN DATABASE FUNCTION ")
    c = db.execute(""" SELECT * FROM  upload """)

    for x in c.fetchall():
        name_v=x[0]
        data_v=x[1]
        break



    conn.commit()
    db.close()
    conn.close()

    return send_file(BytesIO(data_v), attachment_filename='flask.pdf', as_attachment=True)

@app.route('/dashboard')
def dashboard():
    # cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # cur.execute('SELECT * FROM header')
    # data = cur.fetchall()
    # cur.close()

    conn = connect_db()
    db = conn.cursor()

    # conn= sqlite3.connect("fga_big_data_rev2.db")
    # cursor = conn.cursor()
    print("IN DATABASE FUNCTION ")
    c = db.execute(""" SELECT * FROM  upload """)

    mydata = c.fetchall()
    for x in c.fetchall():
        name_v=x[0]
        data_v=x[1]
        break

    hasil = []
    for v_login in c:
        hasil.append(v_login)

    conn.commit()
    db.close()
    conn.close()

    #return send_file(BytesIO(data_v), attachment_filename='flask.pdf', as_attachment=True)

    return render_template('dashboard.html', header = mydata)

@app.route('/logout')
def logout():
   # remove the name from the session if it is there
   session.pop('name', None)
   return redirect(url_for('index'))

if __name__ == '__main__':
    #import os
    #os.environ["JAVA_HOME"] ="/usr/lib/jvm/java-8-openjdk-amd64"
    #print(os.environ["JAVA_HOME"])
    #print(os.environ["SPARK_HOME"])
    #print(os.environ["PYTHONPATH"])
    # db.create_all()
    app.run()  # If address is in use, may need to terminate other sessions:
             # Runtime > Manage Sessions > Terminate Other Sessions
  # app.run(host='0.0.0.0', port=5004)  # If address is in use, may need to terminate other sessions:
             # Runtime > Manage Sessions > Terminate Other Sessions
    # socket.run(app, debug=True)

name = ''