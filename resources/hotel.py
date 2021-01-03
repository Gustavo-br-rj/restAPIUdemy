from flask_restful import Resource, reqparse
from models.hotel import HotelModel

hoteis = [
{
'hotel_id':'alpha',
'nome':'Alpha Hotel',
'estrelas':4.3,
'diaria':420.34,
'cidade':'Rio de Janeiro'
},
{
'hotel_id':'bravo',
'nome':'Bravo Hotel',
'estrelas':4.4,
'diaria':380.90,
'cidade':'Santa Catarina'
},
{
'hotel_id':'charlie',
'nome':'Charlie Hotel',
'estrelas':3.9,
'diaria':320.20,
'cidade':'Santa Catarina'
}
]

class Hoteis(Resource):
    def get(self):
        return {'hoteis':hoteis}

class Hotel(Resource):
    argumentos = reqparse.RequestParser()
    argumentos.add_argument('nome')
    argumentos.add_argument('estrelas')
    argumentos.add_argument('diaria')
    argumentos.add_argument('cidade')

    def find_hotel(hotel_id):
        for hotel in hoteis:
            if hotel['hotel_id'] == hotel_id:
                return hotel
        return None

    def get(self, hotel_id):
        hotel = Hotel.find_hotel(hotel_id)
        if hotel: #similar if hotel is not None
            return hotel
        return {'message': 'Hotel not found'}, 404 #not found

    def post(self, hotel_id):
        dados = Hotel.argumentos.parse_args()
        obj_hotel = HotelModel(hotel_id, **dados)
        novo_hotel = obj_hotel.json()

        hoteis.append(novo_hotel)

        return novo_hotel, 200 #success

    def put(self, hotel_id):
        dados = Hotel.argumentos.parse_args()

        obj_hotel = HotelModel(hotel_id, **dados)
        novo_hotel = obj_hotel.json()

        hotel = Hotel.find_hotel(hotel_id)

        if hotel:
            hotel.update(novo_hotel)
            return novo_hotel, 200 #Success

        hoteis.append(novo_hotel)
        return novo_hotel, 201 #Created

    def delete(self, hotel_id):
        global hoteis
        size_before = len(hoteis)
        hoteis = [hotel for hotel in hoteis if hotel['hotel_id'] != hotel_id]

        if len(hoteis) == size_before:
            return {'message': 'Hotel not found'}, 404 #Not found

        return {'message': 'Hotel deleted.'}, 200 #Success
