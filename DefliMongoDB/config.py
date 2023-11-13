# Make a copy of this file as config.py and update the required values below.
# The MongoDB connection details and the dump1090 URL are the ones you really need to look at.
# The rest can be left at the defaults to start with.

import logging # Ignore this line

config = {} # Ignore this line

# MongoDB connection details (don't miss the username and password):
config['db'] = {
                'mongodb_conn_str':
                    'mongodb+srv://team:kaPAIYJz1EhpWtTO@defli1.snqvy.mongodb.net/?retryWrites=true&w=majority',
                'database_name': 'defli1'
                } #Include username and password in mongodb_conn_str

# Dump1090 URL for the aircraft.json file
config['dump1090_url'] = 'http://172.17.0.1:8078/data/aircraft.json'

# Once a flight ID is received for the first time,
# status records already inserted to the DB can be updated with the flight ID.
# Records only up to these many seconds will be updated.
config['orphan_status_update_max_age'] = 600 # seconds

# The source (dump1090 JSON URL) will be checked every:
# This affects how often the script checks dump1090 for updated status
# Increasing this interval is a way to reduce amount of data going into the DB.
config['source_poll_interval'] = 1 # seconds

# The timeout for the HTTP request to get the JSON file from dump1090
# If a response if not received within this period, the request will be aborted.
# This will not fail the script and it will try the next request after the source_poll_interval.
# If your dump1090 is running locally, a short timeout is fine.
# If your source_poll_interval is short, better to keep the timeout short.
config['http_timeout'] = 3 # seconds

# A dictionary is used to maintain a local of copy of the ADS-B status messages
# so that new messages can be distinhuished from those already processed.
# A cleanup function periodically trims this dictionary to keep it from growing too much.
# The following 2 options control how often the cleanup runs
config['cleanup_run_interval'] = 3600 # seconds
# and how old the messages can be before they are removed.
config['messages_max_age'] = 1800 # seconds

# The following parameter determines how many days worth of "status" documents
# are kept in your status collection. As status documents form the majority of the data,
# adjusting this parameter would help you manage the size of your DB.
# If you are not concerned with the size of your DB growing, you may set this to a higher number.
config['max_status_age_days'] = 60 # days

# The following fields are excluded from the status documents.
# This is primarily done to prevent new status documents from being created
# when there is no change in the actual data but just change in the
# age or cumulative fields. Add or remove fields here as per your preferences.
config['excluded_fields'] = ['messages', 'seen', 'seen_pos',]

# The maximum number of consecutive errors that will be allowed for the
# HTTP fetch process that get the data from dump1090.
# The process will fail if consecutive errors exceed this threshold.
# A successful operation will reset the counter.
config['max_consecutive_http_errors'] = 10

# If the following is set to True, only a limited set of data will be kep in the
# status documents. This is to save space on MongoDB.
# Only the data points listed in limited_status_allowed_list will be saved.
config['limited_status'] = True
config['limited_status_allowed_list'] = ['position', 'alt_baro', 'gs', 'track', 'squawk', 'track_rate', 'roll_rate', 'baro_rate', 'mach', 'ias']

# Configure the following parameters for logging.
# The process can write to log files in the directory speified below.
# A new log file will be created at midnight every day and the old file will be
# renamed with the date. The maximum number of old files that will be kept can
# be specified below.
# The log levels are the standard Python logging module levels. To log only errors,
# set it to logging.ERROR (case sensitive).
config['logging'] =     {
                        # To enable, set to True (with capitlized T)
                        'enabled':              False,
                        # Directory/folder where log files will be created
                        'log_dir':              '',
                        # Log file name
                        'log_file_name':        'adsb_data_collector_mongodb.log',
                        # Log level
                        'log_level':            logging.INFO,
                        # Log format
                        'log_format':           '%(asctime)s - %(levelname)s - %(message)s',
                        # Max number of old logs that will be kept
                        'log_file_hist_count':  7
                        }

# This set of parameters are to be used if you want to configure Pushover notifcations.
# If not , just leave 'enabled' as False.
config['pushover'] =    {
                        # To enable, set to True (with capitlized T)
                        'enabled':      False,
                        # Your Pushover user
                        'user':         'your Pushover user string',
                        # Your Pushover app token
                        'token':        'your Pushover app token',
                        # Log level
                        'log_level':    logging.CRITICAL,
                        # Log format
                        'log_format':   'ADS-B MongoDB feeder had an error\n%(message)s'
                        }
