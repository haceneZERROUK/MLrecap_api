from sqlmodel import Session, SQLModel
from faker import Faker
import random
from datetime import date, datetime, timedelta
from app.utils import bcrypt_context
from app.database import engine
from app.modeles import Users, Film, Prediction, Salle

def populate_db():
    """
    Remplit la base de données avec des données de test pour le projet de cinéma.

    Crée:
        - Un administrateur (email: 'admin', mot de passe: 'admin')
        - Quelques utilisateurs fictifs
        - Des films avec leurs caractéristiques
        - Des prédictions pour ces films
        - Les salles du cinéma

    Note:
        - Les mots de passe sont automatiquement hashés

    Raises:
        SQLAlchemyError: En cas d'erreur de base de données
    """
    fake = Faker('fr_FR')  # Utiliser la locale française

    # Créer les tables dans la base de données
    SQLModel.metadata.create_all(engine)

    # Ouvrir une session SQLModel
    with Session(engine) as session:

        # Ajouter un utilisateur admin
        admin_user = Users(
            nom="Admin",
            email="admin@cinema.fr",
            hashed_password=bcrypt_context.hash("admin"),  # Mot de passe hashé
            role="admin",
            is_active=True
        )
        session.add(admin_user)

        # Ajouter un utilisateur gérant
        manager_user = Users(
            nom="Gérant",
            email="gerant@cinema.fr",
            hashed_password=bcrypt_context.hash("gerant"),  # Mot de passe hashé
            role="manager",
            is_active=True
        )
        session.add(manager_user)

        # Générer des utilisateurs fictifs
        for _ in range(3):
            user = Users(
                nom=fake.name(),
                email=fake.unique.email(),
                hashed_password=bcrypt_context.hash(fake.password(length=12)),
                role="user",
                is_active=True
            )
            session.add(user)

        # Créer les salles du cinéma
        salle1 = Salle(
            id=1,
            nom="Grande Salle",
            capacite=120
        )

        salle2 = Salle(
            id=2,
            nom="Petite Salle",
            capacite=80
        )

        session.add(salle1)
        session.add(salle2)

        # Liste de genres de films
        genres = ["Action", "Comédie", "Drame", "Science-Fiction", "Horreur",
                  "Aventure", "Animation", "Thriller", "Romance", "Fantastique"]

        # Liste de pays
        pays = ["France", "États-Unis", "Royaume-Uni", "Japon", "Corée du Sud",
                "Allemagne", "Espagne", "Italie", "Canada", "Australie"]

        # Liste de classifications
        classifications = ["Tous publics", "-12 ans", "-16 ans", "-18 ans"]

        # Générer des films fictifs
        films = []
        for i in range(20):
            # Générer une date de sortie entre aujourd'hui et 3 mois dans le futur
            release_date = fake.date_between(start_date='today', end_date='+90d')

            # Sélectionner aléatoirement 1 à 3 genres
            film_genres = ", ".join(random.sample(genres, random.randint(1, 3)))

            # Générer une durée entre 80 et 180 minutes
            duration = f"{random.randint(80, 180)} min"

            film = Film(
                fr_title=fake.catch_phrase(),
                original_title=fake.catch_phrase() if random.random() > 0.7 else None,  # 30% de chance d'avoir un titre original différent
                released_date=release_date,
                casting=", ".join([fake.name() for _ in range(random.randint(3, 8))]),
                director=fake.name(),
                writer=fake.name(),
                distribution=fake.company(),
                country=random.choice(pays),
                classification=random.choice(classifications),
                duration=duration,
                categories=film_genres,
                synopsis=fake.paragraph(nb_sentences=5),
                programmed=False,
                programmation_start_date=None,
                programmation_end_date=None,
                allocine_url=f"https://www.allocine.fr/film/fichefilm_gen_cfilm={i+1000}.html",
                image_url=f"https://picsum.photos/id/{i+100}/300/450"  # Images aléatoires
            )
            session.add(film)
            films.append(film)

        # S'assurer que les films sont bien enregistrés avant de créer les prédictions
        session.flush()

        # Générer des prédictions pour les films
        for film in films:
            # Prédire entre 10,000 et 2,000,000 entrées nationales
            weekly_entrances = random.randint(10000, 2000000)

            prediction = Prediction(
                film_id=film.id,
                weekly_entrances_pred=weekly_entrances,
                date_prediction=datetime.now() - timedelta(days=random.randint(1, 30)),
                semaine=film.released_date
            )
            session.add(prediction)

            # Pour certains films, ajouter des entrées réelles (films déjà sortis)
            if film.released_date < date.today() and random.random() > 0.5:
                # Variation de ±20% par rapport à la prédiction
                variation = random.uniform(0.8, 1.2)
                prediction.entrees_reelles = int(weekly_entrances * variation)

            # Programmer certains films dans les salles
            if not film.programmed and film.released_date.weekday() == 2:  # Si le film sort un mercredi
                if random.random() > 0.7:  # 30% de chance d'être programmé
                    film.programmed = True
                    film.programmation_start_date = film.released_date
                    film.programmation_end_date = film.released_date + timedelta(days=6)  # Une semaine de programmation

        session.commit()  # Enregistrer toutes les modifications

    print("Base de données remplie avec succès !")

if __name__ == "__main__":
    """
    Point d'entrée du script.

    Exécute le remplissage de la base de données avec des données de test.
    """
    # Remplir la BDD avec faker
    populate_db()