# #!/usr/bin/env python

# #-----------------------------------------------------------------------
# # tigerengage.py
# # Author: Wangari Karani, Roshaan Khalid
# #-----------------------------------------------------------------------

# # import html # html_code.escape() is used to thwart XSS attacks
# import flask

# #-----------------------------------------------------------------------

# app = flask.Flask(__name__)

# #-----------------------------------------------------------------------

# @app.route('/', methods=['GET'])
# @app.route('/home', methods=['GET'])
# def home():

#     html_code = flask.render_template('home.html')
    
#     response = flask.make_response(html_code)
#     return response

# #-----------------------------------------------------------------------
