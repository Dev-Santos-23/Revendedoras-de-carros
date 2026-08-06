from pydantic import BaseModel, EmailStr, field_validator

DOMINIOS_BLOQUEADOS = {
    "mailinator.com",
    "10minutemail.com",
    "tempmail.com",
}

class UsuarioSchema(BaseModel):
    nome: str
    telefone: str
    email: EmailStr
    senha: str

    @field_validator("nome")
    @classmethod
    def validar_nome(cls, value: str):

        # Remove espaços do início e fim
        value = value.strip()

        # Nome vazio
        if not value:
            raise ValueError("Nome não pode ser vazio.")

        # Nome muito curto
        if len(value) < 3:
            raise ValueError(
                "Nome inválido! O nome deve possuir pelo menos 3 caracteres."
            )

        # Nome contendo números
        if any(char.isdigit() for char in value):
            raise ValueError("O nome não pode conter números.")

        return value.title()

    @field_validator("telefone")
    @classmethod
    def validar_telefone(cls, value: str):

        # Mantém apenas os números
        numero = "".join(filter(str.isdigit, value))

        # Verifica quantidade de dígitos
        if len(numero) not in (10, 11):
            raise ValueError(
                "Telefone deve possuir 10 ou 11 dígitos."
            )

        # DDD não pode começar com zero
        if numero[0] == "0":
            raise ValueError("DDD inválido.")

        # Celular
        if len(numero) == 11 and numero[2] != "9":
            raise ValueError(
                "Celular inválido. Após o DDD deve começar com 9."
            )

        # Telefone fixo
        if len(numero) == 10 and numero[2] not in "2345":
            raise ValueError(
                "Telefone fixo inválido."
            )

        return numero

    @field_validator("email")
    @classmethod
    def validar_email(cls, value: EmailStr):

        dominio = value.split("@")[1].lower()

        if dominio in DOMINIOS_BLOQUEADOS:
            raise ValueError(
                "E-mails temporários não são permitidos."
            )

        return value.lower()

    @field_validator("senha")
    @classmethod
    def validar_senha(cls, value: str):

        if not value.strip():
            raise ValueError("Senha não pode ser vazia.")

        if len(value) < 8:
            raise ValueError("A senha deve conter no mínimo 8 caracteres.")

        if not any(char.isdigit() for char in value):
            raise ValueError("A senha deve conter pelo menos um número.")

        if not any(char.isupper() for char in value):
            raise ValueError("A senha deve conter pelo menos uma letra maiúscula.")

        if not any(char.islower() for char in value):
            raise ValueError("A senha deve conter pelo menos uma letra minúscula.")

        caracteres_especiais = "!@#$%^&*()-_=+[]{}|;:,.<>?/"

        if not any(char in caracteres_especiais for char in value):
            raise ValueError("A senha deve conter pelo menos um caractere especial.")

        return value
        
    class Config:
        from_attributes = True


class LoginSchema(BaseModel):
    email : EmailStr
    senha : str

    class Config:
        from_attributes = True
