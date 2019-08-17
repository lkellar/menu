from flask_sqlalchemy import SQLAlchemy

#pylint: disable=invalid-name
db = SQLAlchemy()

SageMenuItem = db.Table('sage_menu_item',
                        db.Column('id', db.Integer, primary_key=True),
                        db.Column('menu_id', db.Integer, nullable=False),
                        db.Column('recipe_id', db.Integer, nullable=False),
                        db.Column('day', db.Integer, nullable=False),
                        db.Column('week', db.Integer, nullable=False),
                        db.Column('meal', db.Integer, nullable=False),
                        db.Column('station', db.Integer, nullable=False),
                        db.Column('name', db.Text, nullable=False),
                        # Allergens is a JSON list of allergen data
                        db.Column('allergens', db.Text),
                        db.Column('date', db.Date, nullable=False),
                        # A JSON dict of the rest of the other misc properties that aren't
                        # planned to be used soon. Keeping them around in case they become useful
                        db.Column('misc', db.Text)
                        )
