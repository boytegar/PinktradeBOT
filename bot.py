
import random
import requests
import time
import urllib.parse
import json
import base64
import socket
from datetime import datetime

headers = {
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Origin': 'https://bot.pinktrade.fi',
    'Pragma': 'no-cache',
    'Referer': 'https://bot.pinktrade.fi/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
}


def load_credentials():

    try:
        with open('query_id.txt', 'r') as f:
            queries = [line.strip() for line in f.readlines()]
        return queries
    except FileNotFoundError:
        print("File query_id.txt tidak ditemukan.")
        return [  ]
    except Exception as e:
        print("Terjadi kesalahan saat memuat token:", str(e))
        return [  ]

def getuseragent(index):
    try:
        with open('useragent.txt', 'r') as f:
            useragent = [line.strip() for line in f.readlines()]
        if index < len(useragent):
            return useragent[index]
        else:
            return "Index out of range"
    except FileNotFoundError:
        return 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36'
    except Exception as e:
        return 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36'


def cek_balance(query):
    url = 'https://bot-api.pinktrade.fi/pinktrade/api/v1/airdrop'
    headers['Authorization'] = query
    repeat = 1
    while True:
        time.sleep(3)
        response = requests.get(url, headers=headers)
        # print(response)
        if response.status_code >= 500:
            print(f'Error 500 {response.json()}')
        elif response.status_code >= 400:
            print(f'Error 400 {response.json()}')
        elif response.status_code == 200:
            return response.json()
        
        if repeat == 5:
            print("failed to get data")
            return None
        print(f"trying {repeat}")
        repeat +=1
            

def claim_balance(query):
    url = 'https://bot-api.pinktrade.fi/pinktrade/api/v1/airdrop/claim-mint-reward'
    headers['Authorization'] = query
    for attempt in range(3):
        response = requests.post(url, headers=headers)
        # print(response.json())
        if response.status_code == 200:
            return response.json()
    return None
 

def get_tasks(query):
    url = 'https://bot-api.pinktrade.fi/pinktrade/api/v1/airdrop/tasks?type=TASK2'
    headers['Authorization'] = query
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return []


def claim_task(query, task_id):
    url = f'https://bot-api.pinktrade.fi/pinktrade/api/v1/airdrop/claim-task?task_id={task_id}'
    headers['Authorization'] = query
    response = requests.post(url, headers=headers)
    return response

def getupgrade(query):
    url = 'https://bot-api.pinktrade.fi/pinktrade/api/v1/airdrop/upgrading-list'
    headers['Authorization'] = query
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def submitupgrade(query, level):
    url = f'https://bot-api.pinktrade.fi/pinktrade/api/v1/airdrop/upgrade-option?type=astronaut&level={level}'
    headers['Authorization'] = query
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return 'Done'
    return None

def upgrade(query, balance, level):
    stop = False
    while True:
        if stop == True:
            break

        data_upgraded = getupgrade(query)
        time.sleep(2)
        if data_upgraded is not None:
            astronauts = data_upgraded.get('astronauts')
            for astro in astronauts:
                lev = astro.get('level')
                price = astro.get('price')
                if level < lev:
                    if balance > price:
                        data_submit = submitupgrade(query, lev)
                        print(f"Upgraded level to {lev} Success : {data_submit}")
                        level += 1
                        balance -= price
                        time.sleep(2)
                    else:
                        print('balance not enough')
                        stop = True
                        break


def join_squad(query, squad_id=102):
    url = f'https://bot-api.pinktrade.fi/pinktrade/api/v1/airdrop/join-squad-pool?squad_id={squad_id}'
    headers['Authorization'] = query
    response = requests.get(url, headers=headers)
    return response

def clear_tasks(query):
    tasks = get_tasks(query)
    time.sleep(2)
    for task in tasks:
        print(f"Task :  Progressing {task['title']}")
        while True:
            response = claim_task(query, task['id'])
            time.sleep(3)
            if response.status_code == 201:
                print(f"Task : {task['title']} Done!")
                break

            elif response.status_code == 400:
                print(f"Task : {task['title']} Already Done")
                break

def main():

    auto_clear_task = input("Auto clear task? (y/n): ").strip().lower()
    auto_upgraded_astro = input("Auto Upgrade Astronauts ? (y/n) : ").strip().lower()
    cap_level = input("Set Limit Max level upgrade astronauts ? (0 for set not limited) : ").strip()
    while True:
        queries = load_credentials()
        waiting_time = random.randint(3600,3700)
        start_time = time.time()
        try:
            for index, query_data in enumerate(queries):
                useragent = getuseragent(index)
                headers['User-Agent'] = useragent
                query_data = query_data.strip()
                data_balance = cek_balance(query_data)
                
                # print(data_balance)
                if data_balance is not None:
                    total_earn = data_balance['totalEarn']
                    total_reff = data_balance['totalRef']
                    next_claim = int(data_balance['nextClaimTime'])  
                    astro_level = data_balance['astronauntSize']['level']
                    astro_token = data_balance['astronauntSize']['maxToken']
                    space_shiplevel = data_balance['spaceshipSize']['level']
                    space_shiptime = data_balance['spaceshipSize']['maxTime']
                    user_name = data_balance.get('username', 'no username')
                    
                    # Check for squadPool
                    current_time = int(time.time())
                    remaining_time = next_claim - current_time
                    print(f"=== Account {index+1} | {user_name} === ")
                    time.sleep(5)
                    if remaining_time > 0:
                        hours = remaining_time // 3600
                        minutes = (remaining_time % 3600) // 60
                        seconds = remaining_time % 60
                        nextclaim_formatted = f"{hours} Hours {minutes} Mins {seconds} Seconds"
                    else:
                        nextclaim_formatted = "Need Claim"
                  
                    if auto_clear_task == 'y':
                        clear_tasks(query_data)
               
                    squad_pool = data_balance.get('squadPool', None)
                    if squad_pool:
                        squad_title = squad_pool['title']
                        squad_total_earn = squad_pool['totalEarn']
                        totalUser = squad_pool['totalUser']
                    else:
                        print("No Have Squad, joining squad...")
                        time.sleep(2)
                        join_response = join_squad(query_data)
                        if join_response.status_code == 200:
                            print("Successfully joined squad!")
                            time.sleep(2)
                        else:
                            print("Failed to join squad.")
                        squad_title = "No Squad"
                        totalUser = "0"
                        squad_total_earn = "N/A"


                    print(f"Squad     : {squad_title} | {totalUser} Member | Total Earn: {squad_total_earn}")
                    print(f"Astronaut : {astro_token} $PINK / hour | Level {astro_level}")
                    print(f"Spaceship : Claim Every {space_shiptime} hour | Level {space_shiplevel}")
                    print(f"Balance   : {int(total_earn):,}".replace(',', '.'))
                    print(f"Referral  : {int(total_reff):,} | Invited {data_balance['inviteCnt']}")
                 
                    if nextclaim_formatted == 'Need Claim':
                        print(f"Claim : Claiming...")
                        claim_balance(query_data)
                        time.sleep(5)
                        print(f"Claim : Done!!")
                    else:
                        print(f"Claim : {nextclaim_formatted}")
                    
                    if auto_upgraded_astro == 'y':
                        if int(cap_level) < astro_level:
                            upgrade(query_data, total_earn, astro_level)
                        else:
                            print("level has limited")
                else:
                    print(f"Invalid Query. Account {index} Failed")

            end_time = time.time()
            delay = waiting_time - (end_time-start_time)
            print(f"========== ALL ID DONE ==========")   
            printdelay(delay)
            time.sleep(delay)

              
        except Exception as e:
            print(f"An error occurred: {str(e)}")


def printdelay(delay):
    now = datetime.now().isoformat(" ").split(".")[0]
    hours, remainder = divmod(delay, 3600)
    minutes, sec = divmod(remainder, 60)
    print(f"{now} | Waiting Time: {hours} hours, {minutes} minutes, and {round(sec)} seconds")

if __name__ == "__main__":
    main()