from flask_restful import Resource, reqparse
from models.usuario import UserModel

class User(Resource):

    #/usuarios/{user_id}
    def get(self, user_id):
        user = UserModel.find_user(user_id)
        if user:
            return user.json()
        return {'message': 'User not found'}, 404 #not found

    def delete(self, user_id):
        user = UserModel.find_user(user_id)
        if user:
            try:
                user.delete_user()
            except:
                return {'message':'An internal error ocurred trying to delete user.'}, 500 #Internal server error
            return {'message': 'User deleted'}, 200 #Success
        return {'message': 'User not found.'}, 404 #Not found

class UserRegister(Resource):
    def post(self):
        atributos = reqparse.RequestParser()
        atributos.add_argument( 'login', type=str, required=True, help="The field 'login' cannot be left blank.")
        atributos.add_argument( 'password', type=str, required=True, help="The field 'password' cannot be left blank.")
        dados = atributos.parse_args()

        if UserModel.find_by_login(dados['login']):
            return {"message": "The login '{}' already exists.".format(dados['login'])}

        user = UserModel(**dados)

        try:
            user.save_user()
            return {'message':'User created successfully.'}, 201 #Created
        except:
            return {'message':'An internal error ocurred trying to save user.'}, 500 #Internal server error
