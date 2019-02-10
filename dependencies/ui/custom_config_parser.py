# Written by Timothy Bergström

class custom_config_parser():

    def __init__(self):
        pass

    def load(self, file):
        self.settings_file = file

    def read_lines(self):
        settings = []
        for line in open(self.settings_file, 'r'):
            settings.append(line)
        return settings

    def get(self, parameter):
        settings = self.read_lines()
        index = [settings.index(i) for i in settings if i.startswith(parameter)][0]
        # syntax:  <parameter>=<input>
        value = settings[index].split('=')
        if len(value) != 2:  # Check for blank spaces in parameter file
            value = settings[index].split(' = ')[-1]
        else:
            value = value[-1]
        value = value.replace('"', '')
        return value

    def write(self, parameter, value, isString=True):
        settings = self.read_lines()
        value = str(value)
        index = [settings.index(i) for i in settings if i.startswith(parameter)][0]
        if isString:  # Need "
            value = '"' + value + '"'
        settings[index] = f'{parameter}={value}\n'  # Need to add \n here
        with open(self.settings_file, 'w') as file:
            for line in settings:
                file.write(line)
        return True

    def get_params():
        settings = self.read_lines()
        params = []
        for line in settings:
            if not line.startswith('#') and '=' in line:
                params.append(line.split('=')[0])
        return params

    def get_values():
        settings = self.read_lines()
        values = []
        for line in settings:
            if not line.startswith('#') and '=' in line:
                values.append(line.split('=')[0])
        return values
