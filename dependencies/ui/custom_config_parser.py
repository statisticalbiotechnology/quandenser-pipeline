# Written by Timothy Bergström

class custom_config_parser():

    def __init__(self):
        pass

    def load(self, file):
        self.settings_file = file
        self.settings = []
        for line in open(self.settings_file, 'r'):
            self.settings.append(line)

    def get(self, parameter):
        index = [self.settings.index(i) for i in self.settings if i.startswith(parameter)][0]
        # syntax:  <parameter> = <input>
        value = self.settings[index].split('=')
        if len(value) != 2:
            value = self.settings[index].split(' = ')[-1]
        else:
            value = value[-1]
        value = value.replace('"', '')
        return value

    def write(self, parameter, value, isString=True):
        value = str(value)
        index = [self.settings.index(i) for i in self.settings if i.startswith(parameter)][0]
        if isString:  # Need "
            value = '"' + value + '"'
        self.settings[index] = f'{parameter}={value}\n'  # Need to add \n here
        with open(self.settings_file, 'w') as file:
            for line in self.settings:
                file.write(line)
        return True
