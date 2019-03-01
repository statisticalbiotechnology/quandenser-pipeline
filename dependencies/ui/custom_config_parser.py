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

    def get_index(self, parameter, settings, additional_information=''):
        index = [settings.index(i) for i in settings if i.lstrip().startswith(parameter)]
        if len(index) == 0:
            print("ERROR, no such parameter found")
            return None
        elif len(index) == 1:
            index = index[0]
        else:  # If multiple, will use additional information to get correct
            start_search_index = [settings.index(i) for i in settings if additional_information in i][0]
            settings_slice = settings[start_search_index:]
            # This caused REALLY wierd bugs. DO NOT USE
            #index = [settings.index(i) for i in settings_slice if i.lstrip().startswith(parameter)]
            for i, line in enumerate(settings):
                if i < start_search_index:
                    continue
                if line.lstrip().startswith(parameter):
                    index = i
                    break
        return index

    def get(self, parameter, additional_information=''):
        settings = self.read_lines()
        index = self.get_index(parameter, settings, additional_information=additional_information)
        # syntax:  <parameter>=<input>
        value = settings[index].split('=')
        if len(value) != 2:  # Check for blank spaces in parameter file
            value = settings[index].split(' = ')[-1]
        else:
            value = value[-1]
        value = value.replace('"', '').replace('\n', '').replace('\r', '')
        return value

    def write(self, parameter, value, isString=True, additional_information=''):
        settings = self.read_lines()
        value = str(value)
        index = self.get_index(parameter, settings, additional_information=additional_information)
        intendation = 0
        for char in settings[index]:
            if char == ' ':
                intendation += 1
            else:
                break
        intendation = intendation * ' '

        if isString:  # Need "
            value = '"' + value + '"'
        settings[index] = f'{intendation}{parameter}={value}\n'  # Need to add \n here
        with open(self.settings_file, 'w') as file:
            for line in settings:
                file.write(line)
        return True

    def get_params(self):
        settings = self.read_lines()
        params = []
        for line in settings:
            if not line.startswith('#') and '=' in line:
                params.append(line.split('=')[0])
        return params

    def get_values(self):
        settings = self.read_lines()
        values = []
        for line in settings:
            if not line.startswith('#') and '=' in line:
                values.append(line.split('=')[0])
        return values
