from flask_restful import Resource, reqparse
from models.hotel import HotelModel
from models.site import SiteModel
from resources.filtros import normalize_path_params, consulta_com_cidade, consulta_sem_cidade
from flask_jwt_extended import jwt_required
import sqlite3

def normalize_path_params(cidade=None,
                            estrelas_min=0,
                            estrelas_max=5,
                            diaria_min=0,
                            diaria_max=10000,
                            limit=50,
                            offset=0, **dados):
    if cidade:
        return {
            'estrelas_min': estrelas_min,
            'estrelas_max': estrelas_max,
            'diaria_min':diaria_min,
            'diaria_max':diaria_max,
            'cidade':cidade,
            'limit':limit,
            'offset':offset
        }

    return {
            'estrelas_min': estrelas_min,
            'estrelas_max': estrelas_max,
            'diaria_min':diaria_min,
            'diaria_max':diaria_max,
            'limit':limit,
            'offset':offset
    }

#path /hoteis?cidade=Rio de Janeiro&estrelas_min=4&diaria_max=400
path_params = reqparse.RequestParser()
path_params.add_argument('cidade', type=str)
path_params.add_argument('estrelas_min', type=float)
path_params.add_argument('estrelas_max', type=float)
path_params.add_argument('diaria_min', type=float)
path_params.add_argument('diaria_max', type=float)
path_params.add_argument('limit', type=float)
path_params.add_argument('offset', type=float)

class Hoteis(Resource):
    def get(self):
        connection = sqlite3.connect('hotel.db')
        cursor = connection.cursor()

        dados = path_params.parse_args()
        dados_validos = {chave:dados[chave] for chave in dados if dados[chave] is not None}
        parametros = normalize_path_params(**dados_validos)

        if not parametros.get('cidade'):
            tupla = tuple([parametros[chave] for chave in parametros])
            result = cursor.execute(consulta_sem_cidade,tupla)
        else:
            tupla = tuple([parametros[chave] for chave in parametros])
            result = cursor.execute(consulta_com_cidade,tupla)

        hoteis = []
        for linha in result:
            hoteis.append({'hotel_id': linha[0],
                          'nome': linha[1],
                          'estrelas': linha[2],
                          'diaria': linha[3],
                          'cidade': linha[4],
                          'site_id': linha[5]})
        return  {"hoteis":hoteis}, 200


class Hotel(Resource):
    argumentos = reqparse.RequestParser()
    argumentos.add_argument('nome', type=str, required=True, help="The field 'nome' cannot be blank")
    argumentos.add_argument('estrelas', type=float, required=True, help="The field 'estrelas' cannot be blank")
    argumentos.add_argument('diaria')
    argumentos.add_argument('cidade')
    argumentos.add_argument('site_id', type=int, required=True, help="The field 'site_id' cannot be blank.")

    def get(self, hotel_id):
        hotel = HotelModel.find_hotel(hotel_id)
        if hotel: #similar if hotel is not None
            return hotel.json(), 200
        return {'message': 'Hotel not found'}, 404 #not found

    @jwt_required
    def post(self, hotel_id):
        if HotelModel.find_hotel(hotel_id):
            return {"message": "Hotel id '{}' already exists.".format(hotel_id)}, 400 #Bad request

        dados = Hotel.argumentos.parse_args()
        hotel = HotelModel(hotel_id, **dados)

        if not SiteModel.find_by_id(dados.get('site_id')):
            return {'message':'The hotel must be associated with a valid site id.'}, 400

        try:
            hotel.save_hotel()
        except:
            return {'message':'An internal error ocurred trying to save hotel.'}, 500 #Internal server error

        return hotel.json(), 201

    @jwt_required
    def put(self, hotel_id):
        dados = Hotel.argumentos.parse_args()

        finded_hotel = HotelModel.find_hotel(hotel_id)

        if finded_hotel:
            finded_hotel.update_hotel(**dados)
            try:
                finded_hotel.save_hotel()
            except:
                return {'message':'An internal error ocurred trying to save hotel.'}, 500 #Internal server error
            return finded_hotel.json(), 200 #Success

        hotel = HotelModel(hotel_id, **dados)
        try:
            hotel.save_hotel()
        except:
            return {'message':'An internal error ocurred trying to save hotel.'}, 500 #Internal server error

        return hotel.json(), 201 #Created

    @jwt_required
    def delete(self, hotel_id):
        hotel = HotelModel.find_hotel(hotel_id)
        if hotel:
            try:
                hotel.delete_hotel()
            except:
                return {'message':'An internal error ocurred trying to delete hotel.'}, 500 #Internal server error
            return {'message': 'Hotel deleted'}, 200 #Success
        return {'message': 'Hotel not found.'}, 404 #Not found
