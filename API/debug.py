import pandas as pd
import re
import sqlite3
import string

connection = sqlite3.connect('database/db_debug.db', check_same_thread=False)
connection.execute('''CREATE TABLE IF NOT EXISTS file_process (original varchar(255), after_regex varchar(255));''')


kamus_abusive = pd.read_csv('abusive.csv', encoding = 'latin-1')
kamus_alay = pd.read_csv('new_kamusalay.csv', encoding = 'latin-1', header= None)
kamus_alay = kamus_alay.rename(columns={0: 'tulisan awal', 1: 'pengganti'})

def lowercase(text): # Mengubah teks menjadi lowercase
    return text.lower()

def remove(text):
    pattern = "[" + re.escape(string.punctuation) + "]"
    text = re.sub(pattern, '', text)
    return text

def remove_unnecessary_char(text):
    text = re.sub('\n',' ',text) # Menghilangkan '\n'
    text = re.sub('\t',' ',text) # Menghilangkan '\n'
    text = re.sub('rt',' ',text) # Menghilangkan simbol retweet 'rt'
    text = re.sub('user',' ',text) # Menghilangkan username 'user'
    text = re.sub('[^\w+\w+$]', ' ', text)
    # text = re.sub("""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~""", ' ', text)
    text = re.sub('((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))',' ',text) # Menghilangkan URL dan simbol-simbol yang mungkin terdapat dalam URL
    text = re.sub('  +', ' ', text) # Menghilangkan space berlebih
    # text = re.sub(r'[^a-zA-Z0-9]',' ',text)
    return text

def remove_nonaplhanumeric(text): # Menghilangkan seluruh objek selain angka 0-9, huruf a-z, huruf A-Z
    text = re.sub('[^0-9a-zA-Z]+', ' ', text) 
    return text

new_kamus_alay = dict(zip(kamus_alay['tulisan awal'], kamus_alay['pengganti']))
def normalisasi_alay(text):
    return ' '.join([new_kamus_alay[word] if word in new_kamus_alay else word for word in text.split(' ')])

def preprocess(text): # Menggabungkan seluruh fungsi yang telah dibuat ke dalam satu fungsi, agar dapat dipanggil dalam satu kali proses
    text = lowercase(text)
    text = remove(text)
    text = remove_nonaplhanumeric(text)
    text = remove_unnecessary_char(text)
    text = normalisasi_alay(text)
    return text

df = pd.read_csv('data.csv', encoding='latin-1')
# print(df)

texts = df['Tweet'].to_list()
# print(texts)

# cleaned_text = []
for text_input in texts:
    # print(text_input)
    file_after_regex = preprocess(text_input)
    print(file_after_regex)
    connection.execute("INSERT INTO file_process (original, after_regex) VALUES ('" + text_input + "', '" + file_after_regex + "')")
    connection.commit()
# cleaned_text.append(file_after_regex)

# print(cleaned_text)
