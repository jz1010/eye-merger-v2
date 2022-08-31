#!/usr/bin/env python

import os
import sys
import datetime
import json

cur_path = os.path.dirname(__file__)
settings_dir="..\\settings\\"

class json_db_t:
    def __init__(self, settings_dir, fname_json_temp='/home/pi/temp.json'):
        self.settings_dir = settings_dir
        self.fname_json_temp = fname_json_temp
	self.temp_file_path='/home/pi/temp.json'
        self.settings_file_path = '/home/pi/settings_template.json'
        
        # Sanity checks
        if not os.path.exists(self.fname_json_temp):
            print('** ERROR: temp JSON file {} does not exist, exiting **'.format(self.fname_json_temp))
            sys.exit(1)

        if not os.path.exists(self.settings_file_path):
            print('** ERROR: settings JSON file {} does not exist, exiting **'.format(self.settings_dir))
            sys.exit(1)


        self.poll_cnt = 0
        self.json_last_changed = self.get_json_last_changed()
        
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

    def get_json_last_changed(self):
        stat_result = os.stat(self.fname_json_temp)
        last_changed = stat_result.st_mtime
        
        return last_changed
        
    def poll_json_changed(self):
        changed = False
        print ('** poll[{}]: JSON file {} datestamp **'.format(self.poll_cnt,
                                                               self.fname_json_temp))
        self.poll_cnt += 1
        json_last_changed = self.get_json_last_changed()
        if self.json_last_changed != json_last_changed:
            self.json_last_changed = json_last_changed
            self.poll_cnt = 0
            changed = True
            print ('Change detected to {}'.format(self.fname_json_temp))
        
        return changed

    def read_json_db(self,cfg_db):
        with open(self.fname_json_temp) as f:
            data = json.load(f)
            print ('*** Loading new JSON contents as follows ***')
            print (data)
            for control in data:
                print ('loading controls')
                new_db = {}
                pair_db = data[control][0]
                for pair in pair_db.items():
                    #print ('pair: {}'.format(pair))
                    key = str(pair[0])
                    value = str(pair[1])
                    new_db[key] = value
                    print ('key: {} value: {}'.format(key,value))

                print ('*** END NEW JSON CONTENTS ***')
            
                # Merge dictionaries
                for (key,value) in new_db.items():
                    if key in cfg_db:
                        print ('Updating cfg_db[{}] = {}'.format(key,value))
                        cfg_db[key] = value
                    elif key in cfg_db['hack']:
                            print ('Updating cfg_db[hack][{}] = {}'.format(key,value))
                            cfg_db['hack'][key] = value
                    else:
                        print ('No match in cfg_db for {}={}'.format(key,value))
            
        return cfg_db

if __name__ == "__main__":
    cur_path = os.path.dirname(__file__)
    file_path = os.path.join(cur_path, '{}temp.json'.format(settings_dir))
    json_db = json_db_t(settings_dir)
    json_db.merge_json_db()
