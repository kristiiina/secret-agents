from app import app, db
from datetime import datetime
import re
from random import randint


class AgentsDb(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(11), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    access_level = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'Agent {self.nickname}'


@app.context_processor
def get_current_year():
    return dict(current_year=datetime.now().year)


adjectives = [
    "brave", "wise", "ancient", "shining", "mighty", "fierce", "gentle", "mysterious", "bold", "daring",
    "silent", "wild", "swift", "eternal", "radiant", "serene", "luminous", "mystic", "fearless", "boundless",
    "fiery", "glorious", "infinite", "precious", "shadowy", "noble", "restless", "sacred", "distant", "timeless",
    "resilient", "vibrant", "enigmatic", "majestic", "pure", "vivid", "harmonious", "golden", "ruthless", "elegant",
    "devoted", "silent", "unyielding", "cosmic", "graceful", "heroic", "playful", "fabled", "bold", "radiant"
]

nouns = [
    "adventure", "journey", "dream", "shadow", "flame", "whisper", "thunder", "horizon", "river", "forest",
    "mountain", "storm", "phoenix", "breeze", "star", "light", "moon", "ocean", "crystal", "flame",
    "spirit", "wings", "echo", "stone", "wolf", "soul", "sky", "ash", "feather", "dawn",
    "twilight", "fire", "rain", "ice", "dust", "wild", "bloom", "leaf", "flame", "compass",
    "path", "heart", "mist", "cliff", "temple", "cave", "thunderbolt", "blade", "pearl", "lantern"
]


def get_nickname():
    attempts = 0
    while True:
        num1 = randint(0, len(adjectives)-1)
        num2 = randint(0, len(nouns)-1)
        adj = adjectives[num1]
        noun = nouns[num2]
        nickname = f'{adj} {noun}'
        attempts += 1
        if verify_nickname(nickname):
            return nickname
        elif attempts == len(nouns):
            return None


def verify_nickname(nickname):
    find_nickname = AgentsDb.query.filter_by(nickname=nickname).first()
    if find_nickname:
        return False
    for char in nickname:
        if char != ' ' and not char.isalpha():
            return False
    return True


def verify_phone(phone):
    return bool(re.match(r'^(\+7|8)\d{10}$', phone))


def verify_email(email):
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))


def get_agent_by_id(agent_id):
    return AgentsDb.query.get(agent_id)







