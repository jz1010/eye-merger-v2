import os
import sys
import datetime
import json

cur_path = os.path.dirname(__file__)
settings_dir="..\\settings\\"

class json_db_t:
    def __init__(self, settings_dir):
        self.settings_dir = settings_dir

        # Sanity checks
        self.cur_path = os.path.dirname(__file__)
        self.temp_file_path = os.path.join(cur_path, f'{settings_dir}temp.json')
        self.settings_file_path = os.path.join(cur_path, f'{settings_dir}settings_template.json')
        if not os.path.exists(self.temp_file_path):
            print('** ERROR: temp JSON file {} does not exist, exiting **'.format(self.settings_dir))
            sys.exit(1)

        if not os.path.exists(self.settings_file_path):
            print('** ERROR: settings JSON file {} does not exist, exiting **'.format(self.settings_dir))
            sys.exit(1)

        return self.merge_json_db()
    def merge_json_db(self):
        #open temp.json and dump into a dictionary
        with open(self.temp_file_path) as json_file:
            temp_data = json.load(json_file)

        #open settings_template.json and dump into a dictionary
        with open(self.settings_file_path) as json_file:
            settings_data = json.load(json_file)

        #loop through temp_data and update settings_data
        for key, value in temp_data.items():
            settings_data[key] = value

        #write settings_data to settings_template.json
        with open(self.settings_file_path, 'w') as f:
            json.dump(settings_data, f)

        #clear temp.json
        with open(self.temp_file_path, 'w') as f:
            json.dump({}, f)

        print(settings_data)
        return settings_data


if __name__ == "__main__":
    cur_path = os.path.dirname(__file__)
    file_path = os.path.join(cur_path, f'{settings_dir}temp.json')
    json_db = json_db_t(settings_dir)
    json_db.merge_json_db()