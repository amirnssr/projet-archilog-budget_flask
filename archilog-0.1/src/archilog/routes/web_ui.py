from flask import Blueprint, render_template

web_ui = Blueprint("web_ui", __name__, url_prefix="/")

@web_ui.route("/<page>")
def show(page):
    return render_template(f"pages/{page}.html")
