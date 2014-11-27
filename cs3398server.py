import flask
import rest
import model.base

app = flask.Flask(__name__)
app.register_blueprint(rest.api, url_prefix='/api')

if __name__ == "__main__":
    #model.base.create_engine('sqlite:///test.db?check_same_thread=False', echo=True)
    model.base.create_engine('mysql+pymysql://admin:7NgM6Tx2JhaaJe@cs3398.coa3qiflo7sn.us-west-2.rds.amazonaws.com/cs3398', echo=True)
    app.run(debug=True)
