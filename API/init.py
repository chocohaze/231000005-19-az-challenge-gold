import pandas as pd
import re

from flask import Flask, jsonify #Memanggil library Flask

app = Flask(__name__) #Untuk menjelaskan nama modul yang digunakan, sehingga ketika folder lain memanggil folder app akan otomatis teridentifikasi.

from flask import request
from flasgger import Swagger, LazyJSONEncoder, LazyString
from flasgger import swag_from
from app import routes #Memanggil file routes (akan segera dibuat)

app.json_encoder = LazyJSONEncoder

swagger_template = {
    'info' : {
        'title': 'API Documentation for Data Processing and Modeling',
        'version': '1.0.0',
        'description': 'Dokumentasi API untuk Data Processing dan Modeling',
        },
    'host' : '127.0.0.1:5000'
}
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'docs',
            "route": '/docs.json',
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}
swagger = Swagger(app, template=swagger_template,             
                  config=swagger_config)
