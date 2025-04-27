

# from sqlmodel import Session
# from app.utils import bcrypt_context
# from sqlmodel import SQLModel
# from app.database import engine
# from app.modeles import Users


# def populate_db():

#     with Session(engine) as session:
        
#         # Ajouter un utilisateur admin
#         admin_user = Users(
#             username="admin",
#             email="admin",
#             hashed_password=bcrypt_context.hash("admin"),
#             is_admin=1
#             )
#         session.add(admin_user)
#         session.commit()
#         print("✅ Utilisateur admin ajouté avec succès")
    
# if __name__ == "__main__" :
    
#     SQLModel.metadata.create_all(engine)
#     populate_db()

from app.database import Session, SQLModel
from app.utils import bcrypt_context
from app.modeles import Users
from app.database import engine

def populate_db():
    with Session(engine) as session:
        # Ajouter un utilisateur admin
        admin_user = Users(
            username="admin",
            email="admin",
            hashed_password=bcrypt_context.hash("admin"),  # Exemple de mot de passe hashé
            is_admin=True
        )
        session.add(admin_user)
        session.commit()
        print("✅ Utilisateur admin ajouté avec succès")

if __name__ == "__main__":
    SQLModel.metadata.create_all(engine)
    populate_db()
