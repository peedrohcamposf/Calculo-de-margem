from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import SubmitField


class LogoutForm(FlaskForm):
    submit = SubmitField("Sair")
