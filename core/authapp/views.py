from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, LoginSerializer
from .utils import hash_password, generate_jwt
from django.db import connection

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            email = serializer.validated_data['email']
            password = hash_password(serializer.validated_data['password'])

            # Raw SQL execution
            with connection.cursor() as cursor:
                try:
                    cursor.execute("SELECT * FROM get_user_by_email(%s);", [email])
                    existing_user = cursor.fetchone()
                    if existing_user:
                        return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)

                    cursor.execute("SELECT insert_user(%s, %s, %s);", [username, email, password])
                    return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)

                except Exception as e:
                    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




# Login View


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = hash_password(serializer.validated_data['password'])

            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM get_user_by_email(%s);", [email])
                user = cursor.fetchone()
                if not user:
                    return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

                db_password = user[3]  # password column
                if password != db_password:
                    return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

                token = generate_jwt(user[0])  # id column
                return Response({"token": token}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

