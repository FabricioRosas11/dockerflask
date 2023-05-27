from flask import Flask, request, jsonify
import os
import json
from azure.cosmos import CosmosClient
from azure.cosmos import PartitionKey
from azure.identity import DefaultAzureCredential
from datetime import datetime

# endpoint = os.environ["COSMOS_ENDPOINT"]

# ENDPOINT = os.environ["COSMOS_ENDPOINT"]
# KEY = os.environ["COSMOS_KEY"]
ENDPOINT = "https://ticketdb.documents.azure.com:443/"
KEY = "vsJ9xZem0Q6mZ49CWPKr4JEZ9ySkaekDNVgkHkdnNqk33yyUsvcqlIoFF2VQoeu7KUlzsfrA2G50ACDbDPfsNg=="

client = CosmosClient(url=ENDPOINT, credential=KEY)

database = client.get_database_client("ticket_UNMSM")
container = database.get_container_client("ticket")


app = Flask(__name__)


@app.route('/hola')
def getHola():
    return "Hola Mundo"


@app.route('/consultar-disponibilidad', methods=["GET"])
def disponibilidad():
    id_menu = request.args.get('id_menu')
    fecha = request.args.get('fecha')
    # print(id_menu)
    reservas = ultimo_nro_ticket(id_menu, fecha)
    # query_nro_ticket = container.query_items(query="SELECT t.nro_ticket FROM ticket t WHERE t.id_menu=@id_menu AND t.fecha=@fecha", parameters=[
    #     {"name": "@id_menu", "value": id_menu}, {"name": "@fecha", "value": fecha}],  enable_cross_partition_query=True)

    # for item2 in query_nro_ticket:
    #     print(item2)
    #     reservas = item2

    mensaje = "No hay tickets disponibles"
    if (reservas and 300 > reservas):
        mensaje = 300-reservas

    respuesta = {"Disponibilidad": mensaje}
    return jsonify(respuesta)


@app.route('/consultar', methods=["GET"])
# Consultamos el ultimo ticekt reservado por un alumno
def consultar():
    ticket = {}
    fecha_Actual = datetime.now()
    fecha_formateada = fecha_Actual.strftime("%d/%m/%Y")
    ticket_reservado = container.query_items(query="SELECT * FROM ticket t WHERE t.codigo_alumno=@codigo", parameters=[
                                             {"name": "@codigo", "value": request.args.get('codigo')}],  enable_cross_partition_query=True)
    for item in ticket_reservado:
        if (item["fecha"] == fecha_formateada):
            ticket = item
            break
    return jsonify(ticket)


@app.route('/reservar-ticket', methods=['POST'])
# Reservamos el ticekt guardandolo en la bd
def reservar_ticket():

    nuevo_ticket = {}
    # Pasamos los datos al diccionario
    fecha_formateada = request.form['fecha'].replace("/", "")
    id_nuevo = request.form['codigo_alumno'] + \
        request.form['id_menu']+fecha_formateada
    nroticket = ultimo_nro_ticket(
        request.form['id_menu'], request.form['fecha']) + 1
    nuevo_ticket["id"] = id_nuevo
    nuevo_ticket["id_menu"] = request.form['id_menu']
    nuevo_ticket["nro_ticket"] = nroticket
    nuevo_ticket["fecha"] = request.form['fecha']
    nuevo_ticket["codigo_alumno"] = request.form['codigo_alumno']
    nuevo_ticket["codigo_menu"] = int(request.form['codigo_menu'])

    # Aniadimos el item al contenedor
    container.create_item(nuevo_ticket)
    # Devolver la respuesta
    respuesta = {
        'codigo': 200,
        'mensaje': 'Ticket reservado',
        'id': nuevo_ticket['id']
    }
    return jsonify(respuesta)


def ultimo_nro_ticket(idmenu, fecha):
    query_nro_ticket = container.query_items(query="SELECT t.nro_ticket FROM ticket t WHERE t.id_menu=@id_menu AND t.fecha=@fecha", parameters=[
        {"name": "@id_menu", "value": idmenu}, {"name": "@fecha", "value": fecha}],  enable_cross_partition_query=True)
    for item2 in query_nro_ticket:
        ultimo = item2
    return int(ultimo['nro_ticket'])
