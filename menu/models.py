from flask_sqlalchemy import SQLAlchemy

#pylint: disable=invalid-name
db = SQLAlchemy()

class SageMenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    menu_id = db.Column(db.Integer, nullable=False)
    recipe_id = db.Column(db.Integer, nullable=False)
    day = db.Column(db.Integer, nullable=False)
    week = db.Column(db.Integer, nullable=False)
    meal = db.Column(db.Integer, nullable=False)
    station = db.Column(db.Integer, nullable=False)
    name = db.Column(db.Text, nullable=False)
    # Allergens is a JSON list of allergen data
    allergens = db.Column(db.Text)
    date = db.Column(db.Date, nullable=False)
    # A JSON dict of the rest of the other misc properties that aren't
    # planned to be used soon. Keeping them around in case they become useful
    misc = db.Column(db.Text)
