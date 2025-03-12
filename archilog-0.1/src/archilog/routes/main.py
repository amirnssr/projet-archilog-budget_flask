from flask import Blueprint

main_bp = Blueprint("main", __name__, url_prefix="/api")

@main_bp.route("/status")
def status():
    return {"status": "OK"}
