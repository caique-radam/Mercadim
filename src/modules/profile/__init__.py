from flask import Blueprint, render_template, redirect

profile_bp = Blueprint("profile", __name__, template_folder="templates")

@profile_bp.route("/")
def profile():
    return ""