from flask import Blueprint, jsonify, render_template, request, flash, redirect, url_for


views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
def home():

    return render_template("home.html")


