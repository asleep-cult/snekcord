from os import path


def setup(app):
    app.add_html_theme('snakecord_theme', path.abspath(path.dirname(__file__)))
