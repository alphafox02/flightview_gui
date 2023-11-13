import asyncio
import aiohttp
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import errors
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from copy import deepcopy
import logging, logging.handlers
from os.path import join
from config import config

messages = {}

def log_setup():
    logger = logging.getLogger(__name__)
    logger.setLevel(config['logging']['log_level'])
    if config['logging']['enabled']:
        log_file = join(config['logging']['log_dir'], config['logging']['log_file_name'])
        logging_file_handler = logging.handlers.TimedRotatingFileHandler(
                                                        filename=log_file,
                                                        when='midnight',
                                                        backupCount=config['logging']['log_file_hist_count']
                                                        )
        logging_file_handler.setLevel(config['logging']['log_level'])
        logging_file_handler.setFormatter(logging.Formatter(config['logging']['log_format']))
        logger.addHandler(logging_file_handler)
    if config['pushover']['enabled']:
        from LogPushoverHandler import LogPushoverHandler
        pushover_handler = LogPushoverHandler(
                                                token=config['pushover']['token'],
                                                user=config['pushover']['user']
                                                )
        pushover_handler.setLevel(config['pushover']['log_level'])
        pushover_handler.setFormatter(logging.Formatter(config['pushover']['log_format']))
        logger.addHandler(pushover_handler)
    return logger

async def cleanup(db, logger):
    '''
    Trims the messages dict that grows over time
    based on max age defined in config dict
    '''
    while True:
        logger.info('Cleanup: starting')
        now = datetime.now()
        cutoff_time = now - relativedelta(seconds=config['messages_max_age'])
        logger.info(f'Cleanup: Cut-off time: {cutoff_time}')
        del_list = []
        for key, value in messages.items():
                if value['time'] < cutoff_time:
                    del_list.append(key)
        logger.info(f'Cleanup: {len(del_list)} being removed')
        for key in del_list:
            del messages[key]
        logger.info(f'Cleanup: Messages dict size is now {len(messages)}')
        logger.info(f"Cleanup: Deleting status docs older than {config['max_status_age_days']} days")
        res = await db.aircraft.delete_many({'time':{
            '$lt': now - relativedelta(days=config['max_status_age_days'])}
        })
        if res.acknowledged:
            logger.info(f'Cleanup: Deleted {res.deleted_count} status docs')
        else:
            logger.error(f'Cleanup: Error in status docs deletion')
            raise errors.InvalidOperation
        logger.info('Cleanup: complete')
        await asyncio.sleep(config['cleanup_run_interval'])

async def process_dataset(db, logger, dataset):
    '''
    Processes the dump1090 JSON dataset, process each record/message into messages dict
    and call process_message(message) for each
    '''
    # Loop through each item of the aircraft list - we call them messages
    logger.info('Processing dataset')
    tasks = []
    for message in dataset['aircraft']:
        aircraft = message['hex']
        if aircraft not in messages:
            # Add to the list as skeleton dict if not existing
            messages[aircraft] = {'status':{}, 'first_flight_message':False, 'processed':False}
        # Keep a copy of the old status for comparison
        old_status = deepcopy(messages[aircraft]['status'])
        # Fill/replace each attribute below
        for key, value in message.items():
            if key not in config['excluded_fields'] and value != None:
                if type(value) == str:
                    value = value.strip()
                # Set flag if flight ID is received for the first time
                if (key == 'flight' and len(value) > 0
                    and (
                            'flight' not in messages[aircraft]['status']
                            or len(messages[aircraft]['status']['flight']) == 0
                        )
                    ):
                    messages[aircraft]['first_flight_message'] = True
                messages[message['hex']]['status'][key] = value
                # In future consider skipping and unsetting zero/empty values
        # Set the processed flag and time if status is changed from earlier
        if messages[aircraft]['status'] != old_status:
            messages[aircraft]['processed'] = False
            messages[aircraft]['time'] = datetime.fromtimestamp(dataset['now'])
        tasks.append(asyncio.create_task(process_message(db, logger, messages[aircraft])))
    await asyncio.gather(*tasks)
    logger.info('Completed processing dataset')

async def process_message(db, logger, message):
    '''Process given message into DB records as needed'''
    if not message['processed']:
        status = deepcopy(message['status'])
        status['time'] = message['time']
        # Insert aircraft into DB if not already existing or update 'last seen'
        db_aircraft = await db.aircraft.find_one({'hex':status['hex']})
        if  db_aircraft == None:
            res = await db.aircraft.insert_one({  'hex':          status['hex'],
                                            'first seen':   status['time'],
                                            'last seen':    status['time']
                                        })
            if res.acknowledged:
                logger.info(f"Inserted new aircraft: {status['hex']}")
            else:
                logger.error(f"Aircraft document insertion for {status['hex']} was not acknowledged")
                raise errors.InvalidOperation
        else:
            res = await db.aircraft.update_one({'hex':status['hex']}, {'$set':{'last seen':status['time']}})
            if res.acknowledged:
                logger.info(f"Updated 'last seen' for aircraft {status['hex']}")
            else:
                logger.error(f"Aircraft document updation for {status['hex']} was not acknowledged")
                raise errors.InvalidOperation
        # If flight available
        if (
            'flight' in status
            and len(status['flight']) > 0
            ):
            # Insert flight into DB if not erxisting or update 'last seen'
            db_flight = await db.flights.find_one({ 'flight':status['flight'], 'hex':status['hex']})
            if  db_flight == None:
                res = await db.flights.insert_one({   'flight':       status['flight'],
                                                'hex':          status['hex'],
                                                'first seen':   status['time'],
                                                'last seen':    status['time'],
                                                'seen on':      [datetime.combine(status['time'].date(), time.fromisoformat('00:00'))]
                                            })
                if res.acknowledged:
                    logger.info(f"Inserted new flight: {status['flight']} - {status['hex']}")
                else:
                    logger.error(f"Flight document insertion for {status['flight']} - {status['hex']} was not acknowledged")
                    raise errors.InvalidOperation
            else:
                res = await db.flights.update_one({'flight':status['flight'], 'hex':status['hex']},
                                                {'$set':{
                                                        'last seen':status['time']
                                                        },
                                                '$addToSet':{
                                                        'seen on':datetime.combine(status['time'].date(), time.fromisoformat('00:00'))
                                                        }
                                                }
                                            )
                if res.acknowledged:
                    logger.info(f"Updated 'last seen' for flight {status['flight']} - {status['hex']}")
                else:
                    logger.error(f"Flight document updation for {status['flight']} - {status['hex']} was not acknowledged")
                    raise errors.InvalidOperation
        # Create status record if some basic location fields are available
        if ('lat' in status and 'lon' in status) or 'alt_baro' in status or 'alt_geom' in status:
            # Build GeoJSON object for position (lat-lon) if available
            if 'lat' in status and 'lon' in status:
                status['position'] = {
                                        'type': 'Point',
                                        'coordinates': [status['lon'], status['lat']]
                                    }
                del status['lat']
                del status['lon']
            # Cleanup status if limited status is requested
            if config['limited_status']:
                status_del_list = []
                for key in status:
                    if key not in config['limited_status_allowed_list'] and key not in ['hex', 'flight', 'time']:
                        status_del_list.append(key)
                for key in status_del_list:
                    del status[key]
            res = await db.status.insert_one(status)
            if res.acknowledged:
                logger.info(f"Inserted 'status' document for {status['hex']}")
            else:
                logger.error(f"Status document insertion for {status['hex']} was not acknowledged")
                raise errors.InvalidOperation
        # If flight ID received for the first time
        if message['first_flight_message']:
            # Retroactively update older status records (which don't have the flight ID yet)
            res = await db.status.update_many(  {
                                        'hex':status['hex'],
                                        'time':{'$gte':status['time']-relativedelta(seconds=config['orphan_status_update_max_age'])}
                                    },
                                    {'$set':{'flight':status['flight']}}
                                )
            if res.modified_count > 0:
                logger.info(f"Rectroactively updated flight ID for {res.modified_count} status documents")
            messages[status['hex']]['first_flight_message'] = False
        messages[status['hex']]['processed'] = True
        # Debug timing messages
        #print(f'Status for {status["hex"]} from {status["time"].time()} submitted at {datetime.now().time()}')

async def main():
    '''The driver function - will get the JSON from the URL and call process_dataset'''
    try:
        max_consecutive_http_errors = config['max_consecutive_http_errors']

        # Set up logging
        logger = log_setup()
        logger.info('Program starting')

        # Initialize DB connection
        logger.info('Initializing database connection')
        mdb = AsyncIOMotorClient(config['db']['mongodb_conn_str'])
        db = mdb[config['db']['database_name']]

        # Create and start a separate task for the cleanup function
        asyncio.create_task(cleanup(db, logger))

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=config['http_timeout'])) as http_session:
            while True:
                logger.info('Getting latest dataset from dump1090')
                try:
                    async with http_session.get(config['dump1090_url']) as response:
                        dataset = await response.json()
                    max_consecutive_http_errors = config['max_consecutive_http_errors']
                except Exception as exc:
                    logger.debug(f"HTTP error, remaining allowance: {max_consecutive_http_errors}")
                    logger.exception('Something went wrong while fetching data from dump1090')
                    if max_consecutive_http_errors == 0:
                        logger.critical('Maximum consecutive errors exceeded')
                        raise exc
                    max_consecutive_http_errors -= 1
                    await asyncio.sleep(config['source_poll_interval'])
                    continue
                logger.debug(f'Dataset received from dump1090:\n{dataset}')
                logger.info(f"Got {len(dataset['aircraft'])} aircraft detail messages from dump1090")
                try:
                    await process_dataset(db, logger, dataset)
                    max_consecutive_http_errors = config['max_consecutive_http_errors']
                except Exception as exc:
                    logger.debug(f"Possible MongoDB error, remaining allowance: {max_consecutive_http_errors}")
                    logger.exception('Something went wrong while processing dataset')
                    if max_consecutive_http_errors == 0:
                        logger.critical('Maximum consecutive errors exceeded')
                        raise exc
                    max_consecutive_http_errors -= 1
                    
                await asyncio.sleep(config['source_poll_interval'])
    except Exception as exc:
        logger.exception('Something went wrong')
        logger.critical('This is a fatal error. Exiting.')

if __name__ == '__main__':
    asyncio.run(main())
