from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import pymysql
import bcrypt
import os
from flasgger import Swagger

app = Flask(__name__)
CORS(app)
swagger = Swagger(app)

# Conexión a la base de datos — SIN CONTRASEÑA (XAMPP)
def conectar(vhost, vuser, vpass, vdb):
    conn = pymysql.connect(host=vhost, user=vuser, passwd=vpass, db=vdb, charset='utf8mb4')
    return conn

# Servir los archivos del frontend
@app.route('/<nombre>')
def servir_frontend(nombre):
    ruta_frontend = os.path.join(os.path.dirname(__file__), '../frontend')
    return send_from_directory(ruta_frontend, nombre)

# Ruta para consulta general
@app.route("/", methods=['GET'])
def consulta_general():
    """
    Consulta general del baúl de contraseñas
    ---
    responses:
      200:
        description: Lista de registros
    """
    try:
        conn = conectar('localhost', 'root', '', 'gestor_contrasena')
        cur = conn.cursor()
        cur.execute("SELECT * FROM baul")
        datos = cur.fetchall()
        data = []
        for row in datos:
            dato = {'id_baul': row[0], 'Plataforma': row[1], 'usuario': row[2], 'clave': row[3]}
            data.append(dato)
        cur.close()
        conn.close()
        return jsonify({'baul': data, 'mensaje': 'Baúl de contraseñas'})
    except Exception as ex:
        print(ex)
        return jsonify({'mensaje': 'Error'})

# Ruta para consulta individual
@app.route("/consulta_individual/<codigo>", methods=['GET'])
def consulta_individual(codigo):
    try:
        conn = conectar('localhost', 'root', '', 'gestor_contrasena')
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM baul WHERE id_baul = '{codigo}'")
        datos = cur.fetchone()
        cur.close()
        conn.close()
        if datos:
            dato = {'id_baul': datos[0], 'Plataforma': datos[1], 'usuario': datos[2], 'clave': datos[3]}
            return jsonify({'baul': dato, 'mensaje': 'Registro encontrado'})
        else:
            return jsonify({'mensaje': 'Registro no encontrado'})
    except Exception as ex:
        print(ex)
        return jsonify({'mensaje': 'Error'})

# Ruta para registro
@app.route("/registro/", methods=['POST'])
def registro():
    try:
        data = request.get_json()
        plataforma = data['plataforma']
        usuario = data['usuario']
        clave = bcrypt.hashpw(data['clave'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        conn = conectar('localhost', 'root', '', 'gestor_contrasena')
        cur = conn.cursor()
        cur.execute("INSERT INTO baul (Plataforma, usuario, clave) VALUES (%s, %s, %s)",
                    (plataforma, usuario, clave))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'mensaje': 'Registro agregado'})
    except Exception as ex:
        print(ex)
        return jsonify({'mensaje': 'Error'})

# Ruta para eliminar registro
@app.route("/eliminar/<codigo>", methods=['DELETE'])
def eliminar(codigo):
    try:
        conn = conectar('localhost', 'root', '', 'gestor_contrasena')
        cur = conn.cursor()
        cur.execute("DELETE FROM baul WHERE id_baul = %s", (codigo,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'mensaje': 'Eliminado'})
    except Exception as ex:
        print(ex)
        return jsonify({'mensaje': 'Error'})

# Ruta para actualizar registro
@app.route("/actualizar/<codigo>", methods=['PUT'])
def actualizar(codigo):
    try:
        data = request.get_json()
        plataforma = data['plataforma']
        usuario = data['usuario']
        clave = bcrypt.hashpw(data['clave'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        conn = conectar('localhost', 'root', '', 'gestor_contrasena')
        cur = conn.cursor()
        cur.execute("UPDATE baul SET Plataforma = %s, usuario = %s, clave = %s WHERE id_baul = %s",
                    (plataforma, usuario, clave, codigo))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'mensaje': 'Registro actualizado'})
    except Exception as ex:
        print(ex)
        return jsonify({'mensaje': 'Error'})

if __name__ == '__main__':
    app.run(debug=True)