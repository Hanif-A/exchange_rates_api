# This python module comes with no warranty.
#
# Rates API
# Source: https://ratesapi.io/
# This module has affiliation with the Rates API provided
#
# Foreign currency exchange rates api with currency conversion
# Rates API is a free service for current and historical foreign exchange rates built on top of data published by European Central Bank.
# Rates API is compatible with any application and programming languages.
#
# Full documentation: https://ratesapi.io/documentation/
#
# Rates are quoted against the Euro by default.
# Quote against a different currency by setting the base parameter in your request.
# 
# Please cache results whenever possible this will allow Rates API to keep the service without any rate limits or api key requirements.
# The API comes with no warranty.
#
# The reference rates are usually updated around 16:00 CET on every working day, except on TARGET closing days.
# They are based on a regular daily concertation procedure between central banks across Europe, which normally takes place at 14:15 CET.
# https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html
#
# Full Terms & Conditions from Rates API
# https://ratesapi.io/terms-and-conditions/
# 

import os
import re
import json
import ntpath
import requests
import datetime as dt

# TODO: Change caching to daily files
# TODO: Place all files into a cached folder
# TODO: Convert from_when into date at start of process, and add /latest as comment


def get_rates(from_when='latest', base_currency=None, dict_proxy=None, use_cache = True, cache_json_path = 'RatesAPI.json'):

    # Always ensure the cache file exists so we can store it
    cache_full_path, directory, file_name, cached_rates = initiate_cache(cache_json_path=cache_json_path)

    # Check if whatever date we need is already cached
    get_from_cache = check_data_cached(cached_rates=cached_rates, from_when=from_when)

    # If we are not using the cache, define the url using the parameters provided
    if not get_from_cache:

        # Define the url we need to use
        url_rates = define_url(from_when, base_currency)

        # If an url is returned
        if url_rates:

            # Confirmation message
            print_base_currency = '' if not base_currency else f' in {base_currency}' + '...'
            if from_when == 'latest':
                print('Getting latest rates data from API' + print_base_currency )
            else:
                print(f'Getting rates data for {from_when}' + print_base_currency)

            # Submt the request to get the rates
            new_rates = request_rates(url_rates, dict_proxy)

        # If data was returned
        if new_rates:
            # Cache the rates
            cache_new_rates(new_rates=new_rates, cache_full_path=cache_full_path, cached_rates=cached_rates)

        if cache_new_rates:
            print(f'Rates data retreieved and cachced! ({from_when})')
            return new_rates

    else:

        # Convert to date
        if from_when in ['latest']:

            # Convert text into actual date
            from_when = dt.datetime.now().strftime('%Y-%m-%d')

        for rates in cached_rates:

            if rates['date'] == from_when:

                # Once you've found the rates, send it back
                return rates
                


def initiate_cache(cache_json_path):

    # If it doesn't end with .json, then add it on
    cache_json_path += '.json' if not cache_json_path.lower().endswith('.json') else ''

    # Split the file name from the file path
    directory, file_name = ntpath.split(cache_json_path)

    # If no directory is specified, use the same folder the script is in
    directory = os.path.dirname(os.path.abspath(__file__)) if directory == '' else directory

    # Recombine the directory and the filename
    cache_full_path = os.path.join(directory, file_name)

    # If it doesn't exist
    if not os.path.exists(cache_full_path):        

        # Create an empty JSON file
        with open(cache_full_path, 'w'):
            pass

        # Use an empty dictionary
        json_rates = {}
    else:
        # Read the JSON file
        try:
            with open(cache_full_path) as json_file:
                json_rates = json.load(json_file)

            # If the contents are not in JSON, start an empty JSON object
            if not json_rates:
                print('\t# Invalid contents - reseting cache file (sorry!)')
                json_rates = {}

        except json.JSONDecodeError:

            # If the file is blank, then delete it
            if os.path.getsize(cache_full_path) == 0:
                os.remove(cache_full_path)

                # Start with an empty file
                json_rates = {}
            else:
                raise

    return cache_full_path, directory, file_name, json_rates



def check_data_cached(cached_rates, from_when):

    if from_when in ['latest']:

        # Convert text into actual date
        from_when = dt.datetime.now().strftime('%Y-%m-%d')

    already_cached = False

    # If it finds a list, then it's a dictionary of lists
    if isinstance(cached_rates, list):

        # Loop through each dictionary
        for record in cached_rates:

            try:
                # Check the date key in the dictionary
                if record['date'] == from_when:
                    
                    # Confirm already cached
                    already_cached = True
                    break
            except KeyError:
                print(f'check_data_cached (1) - ''date'' not found in cache for {from_when} - resetting cache...')
                return False
            except Exception as e:
                print(f'\t## ERROR - check_data_cached (1F) -  resetting cache - {e}')

    elif isinstance(cached_rates, dict):
        
        # Check the date key in the dictionary
        try:
            if cached_rates['date'] == from_when:
                
                # Confirm already cached
                already_cached = True
        except KeyError:
            print(f'check_data_cached (2) - ''date'' not found in cache for {from_when} - resetting cache...')
            return False
        except Exception as e:
            print(f'\t## ERROR - check_data_cached (2F) - resetting cache -  {e}')

    else:
        # Unknown format presented
        print(f'\t## Error - check_data_cached (3) - resetting cache -  {e}')
        return False

    # Switch to True if not already cached
    use_cache = False if not already_cached else True

    return use_cache


def request_rates(url_rates, dict_proxy=None):

    # Send the request
    r = requests.get(url_rates, proxies=dict_proxy)

    # If it succesfully returns data
    if r.status_code == requests.codes.ok:

        returned_rates = json.loads(r.text)

        return returned_rates

    else:
        print(f'\t# Error returning data from API - {r.status_code}')



def accepted_rates(show_me=True):
    
    # As at 2021-04-15
    
    rates = ('EUR', 'GBP', 'HKD', 'IDR', 'ILS', 'DKK',
            'INR', 'CHF', 'MXN', 'CZK', 'SGD', 'THB',
            'HRK', 'MYR', 'NOK', 'CNY', 'BGN', 'PHP',
            'SEK', 'PLN', 'ZAR', 'CAD', 'ISK', 'BRL',
            'RON', 'NZD', 'TRY', 'JPY', 'RUB', 'KRW',
            'USD', 'HUF', 'AUD')

    if show_me:
        print('The following rates are accepted:')
        
        for rate in rates:
            print(f'\t{rate}')
        
    else:
        return rates
    


def define_url(from_when, base_currency):

    url_rates_now = 'https://api.ratesapi.io/api/latest'
    url_rates_date = 'https://api.ratesapi.io/{0}' 
    param_base_currency = '?base={0}'

    if base_currency:
        if base_currency not in accepted_rates(show_me=False):
            print(f'# Error - {base_currency} is not a supported currency!')
            return False

    # Ensure date is in format YYYY-MM-DD
    rgx_date = r'20\d{2}-[0-1]\d-[0-3]\d'
    
    # Determine what time period they are interested in
    if from_when == 'latest':
        
        url_rates = url_rates_now
        
    elif isinstance(from_when, str):
        
        # If a string was entered            
        if len(from_when) == 10:
        
            # 10 characters is the right length for a date
            # But is it a date we recognise

            # Compare against regex
            matched_dates = re.search(rgx_date, from_when)

            # If it matches
            if matched_dates:

                # Grab the first date group
                matched_date = matched_dates.group(0)
                
                try:
                    # Ensure it's a real date
                    dt.datetime.strptime(matched_date, '%Y-%m-%d')
                    url_rates = url_rates_date.format(from_when)                    
                except:
                    print('\t # An invalid date was entered!')
                    return False
                
            else:
                # Regex failed
                print('\t # No valid date was found!')                
                    
        else:
            # String, but not 10 chars
            print('\t # An date in the correct format was not entered!')            
            return False
    else:
        # Not latest, or a date
        print('\t # A valid date entry was not provided!')
        return False
    
    
    # If a base currency was provided
    if base_currency:

        # Append the url to the end with the currency
        url_rates += param_base_currency.format(base_currency)
        
    return url_rates



def cache_new_rates(new_rates, cache_full_path, cached_rates):

    if isinstance(cached_rates, list):
        cached_rates.append(new_rates)
        export_rates = cached_rates      

    elif isinstance(cached_rates, dict):
        export_rates = [new_rates]

    # Dump the contents to overwrite the existing file
    with open(cache_full_path, 'w', encoding='utf-8') as f:
        json.dump(export_rates, f, ensure_ascii=False, indent=4)

    return export_rates

if __name__ == '__main__':

    #rates = get_rates(from_when='2021-04-13', use_cache=False)
    rates = get_rates()

    print(rates)
