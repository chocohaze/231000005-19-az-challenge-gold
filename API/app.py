import pandas as pd
import re
import sqlite3

from flask import Flask, jsonify 
from flask import request

app = Flask(__name__) 

from flasgger import Swagger, LazyJSONEncoder, LazyString
from flasgger import swag_from


# Swagger Template
app.json_encoder = LazyJSONEncoder

swagger_template = {
    'info' : {
        'title': 'API Documentation for RegEx Text Cleaning',
        'version': '1.0.0',
        'description': 'Ini adalah dokumentasi API untuk melakukan text cleaning menggunakan RegEx',
        }
    # 'host' : '127.0.0.1:5000'
}
swagger_config = {
    'headers': [],
    'specs': [
        {
            'endpoint': 'docs',
            'route': '/docs.json',
        }
    ],
    'static_url_path': '/flasgger_static',
    'swagger_ui': True,
    'specs_route': "/docs/"
}
swagger = Swagger(app, template=swagger_template,             
                  config=swagger_config)

connection = sqlite3.connect('database/challenge.db', check_same_thread=False)
# connection.execute ('CREATE TABLE IF NOT EXISTS all_text (original_csv varchar(255), unprocessed_text varchar(255), text_processing(255), text_processing_file(255));')
connection.execute('''CREATE TABLE IF NOT EXISTS text_process (unprocessed_text varchar(255), text_processing varchar(255));''')
connection.execute('''CREATE TABLE IF NOT EXISTS file_process (original_csv varchar(255), text_processing_file varchar(255));''')
# connection.close()


# Routes

# @swag_from("docs/hello_world.yml", methods=['GET'])
# @app.route('/', methods=['GET'])
# def hello_world():
#     json_response = {
#         'status_code': 200,
#         'description': "Menyapa Hello World",
#         'data': 'hello_world', 
#     }

#     response_data = jsonify(json_response)
#     return response_data

# @swag_from("docs/text.yml", methods=['GET'])
# @app.route('/text', methods=['GET'])
# def text():
#     json_response = {
#         'status_code': 200,
#         'description': "Belum ada pemrosesan pada bagian ini, hanya memastikan method GET berfungsi dengan baik",
#         'data': "Ini \n adalah TEKS yang **bElum diproses", 
#     }

#     response_data = jsonify(json_response)
#     return response_data

# Read CSV untuk cleaning

# data = pd.read_csv('data.csv')
kamus_abusive = pd.read_csv('abusive.csv', encoding = 'latin-1')
kamus_alay = pd.read_csv('new_kamusalay.csv', encoding = 'latin-1', header= None)
kamus_alay = kamus_alay.rename(columns={0: 'tulisan awal', 1: 'pengganti'})

# Membuat fungsi untuk text cleaning

def lowercase(text): # Mengubah teks menjadi lowercase
    return text.lower()
# def lowercase2(str): # Mengubah teks menjadi lowercase
#     return str.lower()
    
def remove_unnecessary_char(text):
    text = re.sub('\n',' ',text) # Menghilangkan '\n'
    text = re.sub('\t',' ',text) # Menghilangkan '\n'
    text = re.sub('rt',' ',text) # Menghilangkan simbol retweet 'rt'
    text = re.sub('user',' ',text) # Menghilangkan username 'user'
    text = re.sub('((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))',' ',text) # Menghilangkan URL dan simbol-simbol yang mungkin terdapat dalam URL
    text = re.sub('  +', ' ', text) # Menghilangkan space berlebih
    text = re.sub(r'[^a-zA-Z0-9]',' ',text)
    return text

# def remove_unnecessary_char2(text):
#     text = re.sub('\n',' ',str(text)) # Menghilangkan '\n'
#     text = re.sub('rt',' ',str(text)) # Menghilangkan simbol retweet 'rt'
#     text = re.sub('user',' ',str(text)) # Menghilangkan username 'user'
#     text = re.sub('((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))',' ',str(text)) # Menghilangkan URL dan simbol-simbol yang mungkin terdapat dalam URL
#     text = re.sub('  +', ' ', str(text)) # Menghilangkan space berlebih
#     return text

def remove_nonaplhanumeric(text): # Menghilangkan seluruh objek selain angka 0-9, huruf a-z, huruf A-Z
    text = re.sub('[^0-9a-zA-Z]+', ' ', text) 
    return text

# def remove_nonaplhanumeric2(text): # Menghilangkan seluruh objek selain angka 0-9, huruf a-z, huruf A-Z
#     text = re.sub('[^0-9a-zA-Z]+', ' ', str(text)) 
#     return text

new_kamus_alay = dict(zip(kamus_alay['tulisan awal'], kamus_alay['pengganti']))
def normalisasi_alay(text):
    return ' '.join([new_kamus_alay[word] if word in new_kamus_alay else word for word in text.split(' ')])

def preprocess(text): # Menggabungkan seluruh fungsi yang telah dibuat ke dalam satu fungsi, agar dapat dipanggil dalam satu kali proses
    text = lowercase(text)
    text = remove_nonaplhanumeric(text)
    text = remove_unnecessary_char(text)
    text = normalisasi_alay(text)
    return text

# def preprocess2(text): # Menggabungkan seluruh fungsi yang telah dibuat ke dalam satu fungsi, agar dapat dipanggil dalam satu kali proses
#     text = remove_nonaplhanumeric2(text)
#     text = remove_unnecessary_char2(text)
#     # text = normalisasi_alay(text)
#     return text

# @swag_from("docs/clean_text.yml", methods=['GET'])
# @app.route('/clean-text', methods=['GET'])
# def text_clean():
#     json_response = {
#         'status_code': 200,
#         'description': "Ini adalah teks yang sudah dibersihkan",
#         'data': preprocess("Ini \n adalah TEKS yang **bElum diproses"),
#     }

#     response_data = jsonify(json_response)
#     return response_data

@swag_from("docs/text_processing.yml", methods=['POST'])
@app.route('/text-processing', methods=['POST'])
def text_processing():

    text = request.form.get('text')

    text_after_regex = preprocess(text)

# Input hasil ke database
    connection.execute("INSERT INTO text_process (unprocessed_text, text_processing) VALUES ('" + text + "', '" + text_after_regex + "')")
    connection.commit()

    json_response = {
        'status_code': 200,
        'description': "Teks yang sudah diproses",
        'data': text_after_regex,
    }

    response_data = jsonify(json_response)
    return response_data


@swag_from("docs/text_processing_file.yml", methods=['POST'])
@app.route('/text-processing-file', methods=['POST'])
def text_processing_file():

    # Upload file menggunakan file = request.file.getlist('file')[0]
    file = request.files.getlist('file')[0]

    # Import file csv ke dalam bentuk pandas dataframe
    df = pd.read_csv(file, encoding = 'latin-1')
#     # df2 = df['Tweet'].tolist()
#     # df2 = list(df['Tweet'])
#     # df = df.to_json()

    # texts = df.text.to_list()

    texts = df['Tweet'].to_list()


#     # df = df.to_json()

#     # Ambil teks yang akan diproses dalam format list
    
#     file_after_regex = preprocess2(texts)
# Lakukan cleansing pada teks
    
    cleaned_text = []
    for text_input in texts:
        file_after_regex = preprocess(text_input)
        cleaned_text.append(file_after_regex)

# Input hasil ke database
    connection.execute ("insert into file_process (original_csv, text_processing_file)  values ('" + texts + "', '"+ file_after_regex +"')")
    connection.commit()

    json_response = {
        'status_code': 200,
        'description': "Teks yang sudah diproses",
        'data': file_after_regex,
    }

    response_data = jsonify(json_response)
    return response_data


if __name__ == '__main__':
    app.run()
