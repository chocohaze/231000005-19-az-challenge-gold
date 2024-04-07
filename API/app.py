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
connection.execute('''CREATE TABLE IF NOT EXISTS processed_text (process_1 varchar(255), process_2 varchar(255));''')


# Read CSV untuk membantu proses cleaning
kamus_abusive = pd.read_csv('abusive.csv', encoding = 'latin-1')
kamus_alay = pd.read_csv('new_kamusalay.csv', encoding = 'latin-1', header= None)
kamus_alay = kamus_alay.rename(columns={0: 'tulisan awal', 1: 'pengganti'})


# Membuat fungsi untuk text cleaning
def lowercase(text): # Mengubah teks menjadi lowercase
    return text.lower()
    
def remove_unnecessary_char(text):
    text = re.sub('\n',' ',text) # Menghilangkan newline
    text = re.sub('\t',' ',text) # Menghilangkan tab
    text = re.sub('rt',' ',text) # Menghilangkan simbol retweet 'rt'
    text = re.sub('user',' ',text) # Menghilangkan username 'user'
    text = re.sub('((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))',' ',text) # Menghilangkan URL dan simbol-simbol yang mungkin terdapat dalam URL
    text = re.sub('  +', ' ', text) # Menghilangkan space berlebih
    return text

def remove_nonaplhanumeric(text): # Menghilangkan seluruh objek selain angka 0-9, huruf a-z, huruf A-Z
    text = re.sub('[^0-9a-zA-Z]+', ' ', text) 
    return text

new_kamus_alay = dict(zip(kamus_alay['tulisan awal'], kamus_alay['pengganti'])) # Mengganti nama kolom pada kamus alay
def normalisasi_alay(text): #Mengganti kata tidak baku dengan kata baku sesuai data pada kamus alay
    return ' '.join([new_kamus_alay[word] if word in new_kamus_alay else word for word in text.split(' ')])

def preprocess(text): # Menggabungkan seluruh fungsi yang telah dibuat ke dalam satu fungsi, agar dapat dipanggil dalam satu kali proses
    text = lowercase(text)
    text = remove_nonaplhanumeric(text)
    text = remove_unnecessary_char(text)
    text = normalisasi_alay(text)
    return text

# @swag_from("docs/hello_world.yml")
# @app.route('/')
# def hello_world():

#     json_response = {
#         'status_code': 200,
#         'description': "Ini adalah API untuk text-processing menggunakan RegEx",
#         'data': 'API telah berhasil dibuka',
#     }

#     response_data = jsonify(json_response)
#     return response_data


# Membuat endpoint untuk swagger
@swag_from("docs/text_processing.yml", methods=['POST']) # Swagger membaca spec yang telah dibuat pada file yaml
@app.route('/text-processing', methods=['POST']) # Routing endpoint
def text_processing():

    text = request.form.get('text')

    text_after_regex = preprocess(text)
    
    # Input hasil ke database
    connection.execute("INSERT INTO processed_text (process_1) VALUES ('" + text_after_regex + "')")
    connection.commit()

    json_response = {
        'status_code': 200,
        'description': "Teks yang sudah diproses",
        'data': text_after_regex,
    }
    response_data = jsonify(json_response)
    return response_data

# try:
    
# except Exception as E:
#     print(E)
# finally:
#     pass

@swag_from("docs/text_processing_file.yml", methods=['POST'])
@app.route('/text-processing-file', methods=['POST'])
def text_processing_file():

    # Upload file menggunakan file = request.file.getlist('file')[0]
    file = request.files.getlist('file')[0]

    # Import file csv ke dalam bentuk pandas dataframe
    df = pd.read_csv(file, encoding='latin-1')

    # Mengambil data pada kolom yang dibutuhkan, data series diubah menjadi list
    texts = df['Tweet'].to_list()

    # Looping list
    cleaned_text = []
    
    for text_input in texts:
        
        # Data cleansing
        file_after_regex =  preprocess(text_input)

        # Input hasil ke database
        connection.execute ("INSERT INTO processed_text (process_2)  VALUES ('"+ file_after_regex +"')")
        connection.commit()

        # Menambahkan list ke dalam kolom file_process
        cleaned_text.append(file_after_regex)
        
    json_response = {
        'status_code': 200,
        'description': "Teks yang sudah diproses",
        'data': cleaned_text,
        }
    response_data = jsonify(json_response)
    return response_data

# try:
#     text_processing_file
# except Exception as E:
#     print(E)
# finally:
#     pass

if __name__ == '__main__':
    app.run()
