from app import db

class Tmachine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    definicia = db.Column(db.String(100), index=True, unique=True)
    tm_d_n_x = db.Column(db.String(16), index=True, unique=False)
    states = db.Column(db.String(200), index=True, unique=False)
    input_symbols = db.Column(db.String(100), index=True, unique=False)
    tape_symbols = db.Column(db.String(200), index=True, unique=False)
    left_end = db.Column(db.String(16), index=True, unique=False)
    transitions = db.Column(db.String(1000), index=True, unique=False)
    initial_state = db.Column(db.String(16), index=True, unique=False)
    blank_symbol = db.Column(db.String(16), index=True, unique=False)
    reject_state = db.Column(db.String(16), index=True, unique=False)
    final_states = db.Column(db.String(16), index=True, unique=False)

    def __repr__(self):
        return '<Tmachine {}>'.format(self.definicia)  
