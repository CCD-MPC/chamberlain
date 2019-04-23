from src.demo_hacks import Handler
import pystache


class MeanHandler(Handler):

    def __init__(self, json_data, app):

        super(Handler, self).__init__(json_data, app)

        self.domain = \
            ['35', '34', '33', '18', '9',
             '11', '7', '16', '42', '6',
             '1', '10', '8', '21', '44',
             '38', '30', '37', '55', '24',
             '23', '4', '3', '12', '40',
             '2', '13', '5', '22', '25']

    def _generate_workflows(self, d):

        template = open("{}/mean.tmpl".format(self.template_directory), 'r').read()

        data = {
            "PROTOCOL": self.protocol_config["protocol"]["data"],
            "COMPUTE_ID": "{0}-{1}".format(self.protocol_config["config"]["ID"], d),
            "CONTAINER_ONE": "{}-one".format(d),
            "CONTAINER_TWO": "{}-two".format(d)
        }

        return pystache.render(template, data)

    def generate_workflows(self):

        ret = []

        for d in self.domain:
            ret.append(self._generate_workflows(d))

        return ret