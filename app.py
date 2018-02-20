from flask import Flask, request
import pystache, os

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def config():
    """
    get config info from user input, populate yml template
    """

    if request.method == 'POST':
        cfg = request.form.get('cfg')

        template = \
            open(
                '{}/cfg_template.tmpl'
                    .format(os.path.dirname(os.path.realpath(__file__)))
            )

        data = {
            'PID': cfg['pid'],
            'NAME': cfg['name'],
            'DELIM': cfg['delimiter'],
            'CODE_PATH': cfg['code_path'],
            'INPUT_PATH': cfg['input_path'],
            'OUTPUT_PATH': cfg['output_path'],
            'NODE_NAME': cfg['node_name'],
            'HOST_ONE': cfg['host_one'],
            'PORT_ONE': cfg['port_one'],
            'HOST_TWO': cfg['host_two'],
            'PORT_TWO': cfg['port_two'],
            'HOST_THREE': cfg['host_three'],
            'PORT_THREE': cfg['port_three']
        }

        conf = pystache.render(template, data)

        protocol = request.files['protocol']

        return conf, protocol
    else:
        return "Hello"


if __name__ == "__main__":
    app.run()
