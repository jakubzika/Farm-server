from flask import Blueprint, request
from werkzeug.utils import secure_filename
import os
import inspect
from lib.utils import loadConfig, translatePrinterNamesToPrinterObjects, loadFromFile
from lib.requests import makeRequest
import json
import actions


PRINTERS_CONFIG_PATH = 'config/printers.yml'
SHUTDOWN_SCRIPT_PATH = 'shutdown.sh'

def getSelectedPrinters():
    return request.form['selectedPrinters'].split(',')

def add_blueprint(app=None):
    api = Blueprint('Printer API',__name__, url_prefix='/api')

    @api.route('/pause', methods=['POST'])
    def pause():
        response = makeRequest(actions.COMMAND_PAUSE,translatePrinterNamesToPrinterObjects(getSelectedPrinters(), loadConfig(PRINTERS_CONFIG_PATH)))

        return json.dumps(response)

    @api.route('/resume', methods=['POST'])
    def resume():
        print(getSelectedPrinters())
        response = makeRequest(actions.COMMAND_RESUME,
                    translatePrinterNamesToPrinterObjects(getSelectedPrinters(), loadConfig(PRINTERS_CONFIG_PATH)))

        return json.dumps(response)

    @api.route('/print', methods=['POST'])
    def printer():
        response = makeRequest(actions.COMMAND_PRINT,
                    translatePrinterNamesToPrinterObjects(getSelectedPrinters(), loadConfig(PRINTERS_CONFIG_PATH)))

        return json.dumps(response)

    @api.route('/load', methods=['POST'])
    def load():
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join('data','file.gco'))
        response = makeRequest(actions.COMMAND_LOAD,
                    translatePrinterNamesToPrinterObjects(getSelectedPrinters(), loadConfig(PRINTERS_CONFIG_PATH)),filename)
        return json.dumps(response)

    @api.route('/load/<string:fileName>', methods=['POST'])
    def loadFile(fileName):
        response = makeRequest(actions.COMMAND_LOAD_FILE,
                    translatePrinterNamesToPrinterObjects(getSelectedPrinters(), loadConfig(PRINTERS_CONFIG_PATH)),
                    fileName)
        return json.dumps(response)

    @api.route('/cancel', methods=['POST'])
    def cancel():
        response = makeRequest(actions.COMMAND_CANCEL,
                    translatePrinterNamesToPrinterObjects(getSelectedPrinters(), loadConfig(PRINTERS_CONFIG_PATH)))

        return json.dumps(response)

    @api.route('/preheat', methods=['POST'])
    def preheat():
        print(request.form['tool'])
        print(request.form['bed'])
        print(request.form['selectedPrinters'])

        response = makeRequest(actions.COMMAND_PREHEAT,
                    translatePrinterNamesToPrinterObjects(getSelectedPrinters(), loadConfig(PRINTERS_CONFIG_PATH)),toolTemperature=request.form['tool'], bedTemperature=request.form['bed'])
        return json.dumps(response)

    @api.route('/system/shutdown/<string:target>', methods=['POST'])
    def shutdown(target):
        printers = []
        if(target == 'farm'):
            printers = loadConfig(PRINTERS_CONFIG_PATH)['printers'].keys()
        elif(target == 'printers'):
            printers = getSelectedPrinters()

        response = makeRequest(actions.COMMAND_SHUTDOWN,
                    translatePrinterNamesToPrinterObjects(printers, loadConfig(PRINTERS_CONFIG_PATH)))

        if(target == 'farm'):
            shutdownCommand = loadFromFile(SHUTDOWN_SCRIPT_PATH)
            shutdownCommand = shutdownCommand.splitlines()
            for command in shutdownCommand:
                os.system(command)

        return json.dumps(response)

    @api.route('/finish', methods=['POST'])
    def finish():
        response = makeRequest(actions.COMMAND_FINISH,
                    translatePrinterNamesToPrinterObjects(getSelectedPrinters(), loadConfig(PRINTERS_CONFIG_PATH)))

        return json.dumps(response)

    app.register_blueprint(api)