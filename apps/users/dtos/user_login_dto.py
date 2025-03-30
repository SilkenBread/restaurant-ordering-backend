from dataclasses import dataclass

@dataclass
class UserLoginDTO:
    email: str
    password: str
    
    def validate(self):
        errors = {}
        if not self.email:
            errors['email'] = 'El correo electrónico es obligatorio'
        if not self.password:
            errors['password'] = 'La contraseña es obligatoria'
        return errors
