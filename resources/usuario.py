from flask_restful import Resource, reqparse
from flask import make_response, render_template
from models.usuario import UserModel
from flask_jwt_extended import create_access_token, jwt_required, get_raw_jwt
from werkzeug.security import safe_str_cmp
from blacklist import BLACKLIST
import traceback

atributos = reqparse.RequestParser()
atributos.add_argument( 'login', type=str, required=True, help="The field 'login' cannot be left blank.")
atributos.add_argument( 'password', type=str, required=True, help="The field 'password' cannot be left blank.")
atributos.add_argument( 'email', type=str)
atributos.add_argument( 'ativado', type=bool)

class User(Resource):

    #/usuarios/{user_id}
    def get(self, user_id):
        user = UserModel.find_user(user_id)
        if user:
            return user.json()
        return {'message': 'User not found'}, 404 #not found

    @jwt_required
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
        dados = atributos.parse_args()
        if not dados.get('email') or dados.get('email') is None:
            return {"message":"The field 'email' cannot be left blank."}, 400

        if UserModel.find_by_email(dados['email']):
            return {"message":"The email '{}' already exists.".format(dados['email'])}, 400

        if UserModel.find_by_login(dados['login']):
            return {"message": "The login '{}' already exists.".format(dados['login'])}

        user = UserModel(**dados)
        user.ativado = False

        try:
            user.save_user()
            user.send_confirmation_email()
        except:
            user.delete_user()
            traceback.print_exc()
            return {'message':'An internal error ocurred trying to save user.'}, 500 #Internal server error
        return {'message':'User created successfully.'}, 201 #Created

class UserLogin(Resource):

    @classmethod
    def post(cls):
        dados = atributos.parse_args()
        user = UserModel.find_by_login(dados['login'])

        if user and safe_str_cmp( user.password, dados['password']):
            if user.ativado:
                token_acesso = create_access_token(identity=user.user_id)
                return {'access_token': token_acesso}, 200
            return {'message':'User not confirmed.'}, 400
        return { 'message': 'The username or password is incorrect.'}, 401 #Unauthorized

class UserLogout(Resource):

    @jwt_required
    def post(self):
        jwt_id = get_raw_jwt()['jti'] #JWT Token Identifier
        BLACKLIST.add(jwt_id)
        return {'message':'Logged out successfully.'}, 200


class UserConfirm(Resource):

    @classmethod
    def get(cls, user_id):
        user = UserModel.find_user(user_id)
        if not user:
            return {"message": "User id '{}' not found.".format(user_id)}, 404

        user.ativado = True
        user.save_user()
        # return {"message": "User id '{}' confirmed successfully.".format(user_id)}
        headers = {'Content-Type':'text/html'}
        return make_response(render_template('user_confirm.html', email=user.email, usuario=user.login),200,headers)
