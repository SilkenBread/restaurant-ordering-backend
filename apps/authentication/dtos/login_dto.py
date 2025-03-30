from dataclasses import dataclass


@dataclass
class LoginDTO:
    """
    DTO para representar los datos de inicio de sesión.

    Attributes:
        email (str): Correo electrónico del usuario.
        password (str): Contraseña del usuario.
    """
    email: str
    password: str

    def validate(self):
        errors = {}
        if not self.email:
            errors['email'] = 'El correo electrónico es obligatorio'
        if not self.password:
            errors['password'] = 'La contraseña es obligatoria'
        return errors
