from django.contrib.auth import get_user_model

class CustomUserAuthBackend():
    def authenticate(self, request, username=None, password=None, **kwargs):
        print(f"Intento de inicio de sesión para el usuario: {username}")
        try:
            CustomUser = get_user_model()
            user = CustomUser.objects.get(username=username)
            print("hola")
            print(f"Usuario encontrado: {user}")
        
            if user(password):
                print("Contraseña correcta. Inicio de sesión exitoso.")
                return user
            else:
                print("Contraseña incorrecta.")
                return None
        except CustomUser.DoesNotExist:
            #print("Usuario no encontrado.")
            return None