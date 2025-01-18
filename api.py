import sqlite3
from flask import Flask, jsonify, request
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

# Configuração do Swagger UI
SWAGGER_URL = '/docs'
API_URL = '/static/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "API Roletas"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Configurações do banco de dados
DATABASE_PATH = 'roletas.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = sqlite3.connect('roletas.db')
    c = conn.cursor()
    
    # Cria a tabela se não existir
    c.execute('''CREATE TABLE IF NOT EXISTS resultados
                 (gametoken TEXT PRIMARY KEY,
                  arialabel TEXT,
                  initialresults TEXT,
                  data TEXT)''')
    
    conn.commit()
    return conn

# Inicializa o banco de dados ao iniciar
init_db()

@app.route('/api/roletas', methods=['GET'])
def get_all_roletas():
    """
    Retorna todas as roletas do banco de dados
    ---
    tags:
      - Roletas
    responses:
      200:
        description: Lista de todas as roletas
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/Roleta'
    """
    with get_db_connection() as conn:
        cursor = conn.execute('SELECT * FROM resultados')
        roletas = [dict(row) for row in cursor.fetchall()]
    return jsonify(roletas), 200

@app.route('/api/roletas/<game_token>', methods=['GET'])
def get_roleta_by_token(game_token):
    """
    Retorna uma roleta específica pelo token
    ---
    tags:
      - Roletas
    parameters:
      - name: game_token
        in: path
        required: true
        schema:
          type: string
    responses:
      200:
        description: Dados da roleta
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Roleta'
      404:
        description: Roleta não encontrada
    """
    with get_db_connection() as conn:
        cursor = conn.execute('SELECT * FROM resultados WHERE gametoken = ?', (game_token,))
        roleta = cursor.fetchone()
        
    if roleta:
        return jsonify(dict(roleta)), 200
    else:
        return jsonify({"error": "Roleta not found"}), 404

@app.route('/static/swagger.json', methods=['GET'])
def swagger_spec():
    """Endpoint que retorna a especificação OpenAPI"""
    return jsonify({
        "openapi": "3.0.0",
        "info": {
            "title": "API Roletas",
            "version": "1.0.0",
            "description": "API para gerenciamento de dados de roletas"
        },
        "paths": {
            "/api/roletas": {
                "get": {
                    "summary": "Lista todas as roletas",
                    "responses": {
                        "200": {
                            "description": "Lista de roletas",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {
                                            "$ref": "#/components/schemas/Roleta"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/roletas/{game_token}": {
                "get": {
                    "summary": "Obtém uma roleta específica",
                    "parameters": [
                        {
                            "name": "game_token",
                            "in": "path",
                            "required": True,
                            "schema": {
                                "type": "string"
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Dados da roleta",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/Roleta"
                                    }
                                }
                            }
                        },
                        "404": {
                            "description": "Roleta não encontrada"
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "Roleta": {
                    "type": "object",
                    "properties": {
                        "gametoken": {
                            "type": "string"
                        },
                        "arialabel": {
                            "type": "string"
                        },
                        "initialresults": {
                            "type": "string"
                        },
                        "data": {
                            "type": "string"
                        }    
                    }
                }
            }
        }
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
