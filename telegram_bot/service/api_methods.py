import aiohttp
import json
import csv


############################################################################################################
##                                                                                                        ##
##                                          POST METHODS                                                  ##
##                                                                                                        ##
############################################################################################################


async def send_to_api(endpoint, data=None, method='POST'):
    url = f'http://djangoapp:8000/api/{endpoint}'
    headers = {'Content-Type': 'application/json'}

    async with aiohttp.ClientSession() as session:
        if method == 'POST':
            print(f"Attempting to connect to: {url}")
            async with session.post(url=url, data=json.dumps(data), headers=headers) as response:
                if response.status != 200:
                    # Handle error
                    response_data = await response.text()
                    print(f"Error: {response.status}. {response_data}")
                else:
                    return await response.json()
        elif method == 'DELETE':
            async with session.delete(url=url, headers=headers) as response:
                if response.status != 200:
                    # Handle error
                    response_data = await response.text()
                    print(f"Error: {response.status}. {response_data}")
                else:
                    return await response.json()


async def create_applicant(telegram_name, user_id, urls, name_from_user, telephone_number, request):
    endpoint = 'applicant/'
    data = {
        'telegram_name': telegram_name,
        'user_id': user_id,
        'name_from_user': name_from_user,
        'telephone_number': telephone_number,
        'urls': urls,
        'request': request
    }

    data = {key: value for key, value in data.items() if value is not None}

    return await send_to_api(endpoint, data)


############################################################################################################
##                                                                                                        ##
##                                          PUT METHODS                                                   ##
##                                                                                                        ##
############################################################################################################


async def update_applicant_data(user_id, urls, name_from_user=None, telephone_number=None, request=None):
    endpoint = f'urls/{user_id}/'

    data = {
        'name_from_user': name_from_user,
        'telephone_number': telephone_number,
        'urls': urls,
        'request': request
    }
    clean_data = {k: v for k, v in data.items() if v is not None}
    print ("FINISHED")
    return await send_to_api(endpoint, clean_data, method='POST')



############################################################################################################
##                                                                                                        ##
##                                          GET METHODS                                                   ##
##                                                                                                        ##
############################################################################################################


async def get_from_api(endpoint, params=None):
    url = f'http://djangoapp:8000/api/{endpoint}'

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Failed to fetch data from API. Status: {response.status}")
                return None

async def get_all_applicants():
    endpoint = ('applicants/')
    return await get_from_api(endpoint)

async def get_applicant(user_id):
    endpoint = f'get_applicant/{user_id}/'
    return await get_from_api(endpoint)