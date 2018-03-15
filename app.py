from flask import Flask, request, render_template
# import pystache
import os

application = Flask(__name__)


@application.route('/', methods=['GET', 'POST'])
def config():
    """
    get config info from user input, populate yml template
    
    """
    return render_template('hello.html')
    # if request.method == 'POST':
    #     print 'This is flask'
    #     # cfg = request.form.get('cfg')
    #
    #     template = open( '{}/cfg_template.tmpl' .format(os.path.dirname(os.path.realpath(__file__))))
    #
    #     data = {
    #         'PID': cfg['pid'],
    #         'NAME': cfg['name'],
    #         'DELIM': cfg['delimiter'],
    #         'CODE_PATH': cfg['code_path'],
    #         'INPUT_PATH': cfg['input_path'],
    #         'OUTPUT_PATH': cfg['output_path'],
    #         'NODE_NAME': cfg['node_name'],
    #         'HOST_ONE': cfg['host_one'],
    #         'PORT_ONE': cfg['port_one'],
    #         'HOST_TWO': cfg['host_two'],
    #         'PORT_TWO': cfg['port_two'],
    #         'HOST_THREE': cfg['host_three'],
    #         'PORT_THREE': cfg['port_three']
    #     }
    #
    #     # conf = pystache.render(template, data)
    #
    #     # protocol = request.files['protocol']
    #
    #     return render_template('submit.html')
    # else:
    #     return render_template('hello.html')


if __name__ == "__main__":
    application.run()
