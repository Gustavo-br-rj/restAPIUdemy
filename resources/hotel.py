from flask_restful import Resource, reqparse
from models.hotel import HotelModel

class Hoteis(Resource):
    def get(self):
        return {'hoteis':[hotel.json() for hotel in HotelModel.query.all()]}

class Hotel(Resource):
    argumentos = reqparse.RequestParser()
    argumentos.add_argument('nome', type=str, required=True, help="The field 'nome' cannot be blank")
    argumentos.add_argument('estrelas', type=float, required=True, help="The field 'estrelas' cannot be blank")
    argumentos.add_argument('diaria')
    argumentos.add_argument('cidade')

    def get(self, hotel_id):
        hotel = HotelModel.find_hotel(hotel_id)
        if hotel: #similar if hotel is not None
            return hotel.json()
        return {'message': 'Hotel not found'}, 404 #not found

    def post(self, hotel_id):
        if HotelModel.find_hotel(hotel_id):
            return {"message": "Hotel id '{}' already exists.".format(hotel_id)}, 400 #Bad request

        dados = Hotel.argumentos.parse_args()
        hotel = HotelModel(hotel_id, **dados)

        try:
            hotel.save_hotel()
        except:
            return {'message':'An internal error ocurred trying to save hotel.'}, 500 #Internal server error

        return hotel.json()

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

    def delete(self, hotel_id):
        hotel = HotelModel.find_hotel(hotel_id)
        if hotel:
            try:
                hotel.delete_hotel()
            except:
                return {'message':'An internal error ocurred trying to delete hotel.'}, 500 #Internal server error
            return {'message': 'Hotel deleted'}, 200 #Success
        return {'message': 'Hotel not found.'}, 404 #Not found
