from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from unidecode import unidecode
from datetime import datetime
from googleapiclient.discovery import build 
from google_auth_oauthlib.flow import InstalledAppFlow 
from google.auth.transport.requests import Request 
import pickle 
import os.path 
import sqlite3
from telegram import Bot
from telegram.constants import ParseMode
from prettytable import PrettyTable
import asyncio
from threading import Thread
import pyautogui

tab_index = {
    "1xbetcom" : -1,
    "bodog" : -1,
    "pinnacle" : -1,
    "megapari" : -1,
    "marathon" : -1,
    "vbet" : -1
}

min_amount = {
    "1xbetcom" : 1.0,
    "bodog" : 1.0,
    "pinnacle" : 1.0,
    "megapari" : 1.0,
    "marathon" : 1.0,
    "vbet" : 1.0
}

response = ''
new_amount = 0

service = Service(executable_path="C:\chrome\chromedriver.exe")
options = Options()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9050")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.217 Safari/537.36")
driver_bookmaker = webdriver.Chrome(service=service, options=options)
window_handles = driver_bookmaker.window_handles

async def send_message_to_channel(message):
    bot_token = '6581940771:AAHyD3cBhfuLbCZApXeIOMIFr8k9fgj-LzE'
    try:
        bot = Bot(token=bot_token)
        async with bot:
            await bot.send_message(chat_id='1089950711', text=message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
            await bot.send_message(chat_id='6578526417', text=message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    except:
        pass

def player_exists(winner_loser, players):
    home_1 = winner_loser[0].lower().split(' ')
    away_1 = winner_loser[1].lower().split(' ')
    home_2 = players[0].lower().split(' ')
    away_2 = players[1].lower().split(' ')
    result = 2
    if any(word in home_1 for word in home_2) and any(word in away_1 for word in away_2):
        result = 0
    if any(word in away_1 for word in home_2) and any(word in home_1 for word in away_2):
        result = 1
    return result

def Find_elements(driver: webdriver.Chrome, by, value):
    while True:
        try:
            elements = driver.find_elements(by, value)
            if len(elements) > 0:
                return elements
        except:
            pass
        sleep(0.1)

def Find_element(driver: webdriver.Chrome, by, value):
    while True:
        try:
            element = driver.find_element(by, value)
            return element
        except:
            pass
        sleep(0.1)
    
def _1xbet(event):
    global response
    global new_amount

    winner = event['winner']
    loser = event['loser']
    origin_quota = event['origin_quota']
    min_quota = event['min_quota']
    amount = event['amount']

    username_1xbet = 'josemiguelsatine@gmail.com' # +58 41262309 10
    password_1xbet = 'Nina1711.'
    try:
        driver_bookmaker.find_element(By.ID, 'curLoginForm').click()
        ping("1xbet logged out")
        username = Find_element(driver_bookmaker, By.ID, 'auth_id_email')
        username.send_keys(username_1xbet)
        sleep(0.5)
        password = Find_element(driver_bookmaker, By.ID, 'auth-form-password')
        password.send_keys(password_1xbet)
        sleep(0.5)
        Find_element(driver_bookmaker, By.CLASS_NAME, 'auth-button').click()
        # Find_element(driver_bookmaker, By.ID, 'phone_middle').send_keys('41262309')
        Find_element(driver_bookmaker, By.ID, 'user-money')
        print('[1xbet], logged in successfully')
        sleep(1)
    except:
        pass
    driver_bookmaker.get("https://1xbet.com/en/live/tennis")
    search_input = Find_element(driver_bookmaker, By.CLASS_NAME, 'sport-search__input')
    search_input.clear()
    search_input.send_keys(winner)
    driver_bookmaker.find_element(By.CLASS_NAME, 'sport-search__btn').click()

    while True:
        try:
            content = driver_bookmaker.find_element(By.CLASS_NAME, 'search-popup__nothing-find').text
            print(f'{datetime.now().strftime("%H:%M:%S")}, Not found')
            response = 'Not found'
            break
        except:
            pass
        try:
            results = driver_bookmaker.find_elements(By.CLASS_NAME, 'search-popup-events__item')
            if len(results) > 0:
                selected_quota = None
                selected_quota_value = 0
                for item in results:
                    content = item.text.lower() 

                    if 'tennis' in content and  winner.lower() in content and loser.lower() in content:      
                        quotas = item.find_elements(By.CLASS_NAME, 'search-popup-coefs__item')
                        if content.find(winner.lower()) > content.find(loser.lower()):
                            index = 1
                        else:
                            index = 0
                        selected_quota = quotas[index]
                        selected_quota_value = float(selected_quota.text.split('\n')[1])               
                        break
                if selected_quota_value > 0:
                    user_money = Find_element(driver_bookmaker, By.ID, 'user-money')
                    bank = float(user_money.find_element(By.CLASS_NAME, 'top-b-acc__amount').text)
                    if bank >= amount:
                        if selected_quota_value >= min_quota:
                            if selected_quota_value != origin_quota:
                                response = f"quota@{selected_quota_value}"
                                print(f'{datetime.now().strftime("%H:%M:%S")}, updated quota "{selected_quota_value}" sent to scanner')
                                new_amount = -1
                                while new_amount == -1:
                                    sleep(0.1)
                                amount = new_amount                                
                                print(f'{datetime.now().strftime("%H:%M:%S")}, updated amount "${new_amount }" received from scanner')                            
                            stake_input = Find_element(driver_bookmaker, By.CLASS_NAME, 'cpn-value-controls__input')
                            stake_input.clear()
                            stake_input.send_keys(amount)
                            print(f'{datetime.now().strftime("%H:%M:%S")}, ${amount} was typed to stake input')

                            selected_quota.click()
                            print(f'{datetime.now().strftime("%H:%M:%S")}, quota button was clicked')
                            
                            content = Find_element(driver_bookmaker, By.CLASS_NAME, 'c-coupon-modal__header').text.lower()
                            for item in content.split('\n'):
                                if 'bet slip' in item:
                                    bet_id = item.split(': ')[1]
                            benefit = round(((selected_quota_value - 1) * amount), 3)

                            success_button = Find_element(driver_bookmaker, By.CLASS_NAME, 'o-btn-group__item').find_element(By.TAG_NAME, 'button')
                            driver_bookmaker.execute_script("arguments[0].click();", success_button)

                            close_button = Find_element(driver_bookmaker, By.CLASS_NAME, 'search-popup__close')
                            driver_bookmaker.execute_script("arguments[0].click();", close_button)

                            print(f'{datetime.now().strftime("%H:%M:%S")}, bet place button was clicked')                    

                            response = "success"
                            # print(f'{datetime.now().strftime("%H:%M:%S")}, "benefit: ${benefit}, bet id: {bet_id}" sent to scanner')  
                        else:
                            print(f'{datetime.now().strftime("%H:%M:%S")}, quota is less than minimum')
                            response = "quota is less than minimum"
                    else:
                        print(f'{datetime.now().strftime("%H:%M:%S")}, bank is not enough')
                        response = "bank is not enough"
                        ping("1xbet's bank is not enough")                   
                else:
                    print(f'{datetime.now().strftime("%H:%M:%S")}, Not matched ---')
                    response = "Not found"
                    ping("1xbet not found")
                break
        except Exception as e:
            print(e)
        sleep(0.1)
    print(f'{datetime.now().strftime("%H:%M:%S")}, closed thread-1xbet')

def bodog(event):
    global response

    global new_amount

    winner = event['winner']
    loser = event['loser']
    origin_quota = event['origin_quota']
    min_quota = event['min_quota']
    amount = event['amount']

    username_bodog = 'davidabadi23@gmail.com'
    password_bodog = 'Messi2312.' 
    try:
        driver_bookmaker.find_element(By.ID, 'headerUnloggedLogin').click()
        ping("bodog logged out")
        username = Find_element(driver_bookmaker, By.ID, 'email')
        username.clear()
        username.send_keys(username_bodog)
        sleep(0.5)
        password = Find_element(driver_bookmaker, By.ID, 'login-password')
        password.clear()
        password.send_keys(password_bodog)
        sleep(0.5)
        driver_bookmaker.find_element(By.ID, 'login-submit').click()
        sleep(1)
        Find_element(driver_bookmaker, By.ID, 'balance')
        print('[bodog], logged in successfully')
    except:
        pass

    driver_bookmaker.get('https://www.bodog.com/en/sports/tennis')
    search_input = Find_element(driver_bookmaker, By.ID, 'gio-sports-search')
    search_input.clear()
    search_input.send_keys(winner)
    results = Find_elements(driver_bookmaker, By.CLASS_NAME, "result-item")
    index = 2
    for result in results:
        name = result.text.replace("\n", " ").lower()
        if winner.lower() in name and loser.lower() in name:
            if name.find(winner.lower()) > name.find(loser.lower()):
                index = 1
            else:
                index = 0
            result.click()
            break
    if index != 2:
        quotas = Find_element(driver_bookmaker, By.TAG_NAME, 'sp-two-way').find_elements(By.TAG_NAME, 'button')
        selected_quota = quotas[index]
        selected_quota_value = float(selected_quota.text)
        bank = float(driver_bookmaker.find_element(By.ID, 'balance').text.split(' ')[1])
        if bank >= amount:
            if selected_quota_value >= min_quota:
                if selected_quota_value != origin_quota:
                    print(f'{datetime.now().strftime("%H:%M:%S")}, updated quota: {selected_quota_value}')
                    response = f"quota@{selected_quota_value}"
                    print(f'{datetime.now().strftime("%H:%M:%S")}, updated quota "{selected_quota_value}" sent to scanner')
                    new_amount = -1
                    while new_amount == -1:
                        sleep(0.1)
                    amount = new_amount
                    print(f'{datetime.now().strftime("%H:%M:%S")}, updated amount "${new_amount }" received from scanner')
                driver_bookmaker.execute_script("arguments[0].click();", selected_quota)
                print(f'{datetime.now().strftime("%H:%M:%S")}, quota button was clicked')
                
                stake_input = Find_element(driver_bookmaker, By.ID, 'default-input--risk')
                stake_input.clear()
                stake_input.send_keys(amount)
                print(f'{datetime.now().strftime("%H:%M:%S")}, ${amount} was typed to stake input')

                bet_button = Find_element(driver_bookmaker, By.CLASS_NAME, 'place-bets')
                driver_bookmaker.execute_script("arguments[0].click();", bet_button)
                print(f'{datetime.now().strftime("%H:%M:%S")}, bet place button was clicked')
                success_button = Find_element(driver_bookmaker, By.CLASS_NAME, 'coupon-success-modal-controls__item')
                driver_bookmaker.execute_script("arguments[0].click();", success_button)
                sleep(1)

                # driver_bookmaker.get('https://www.bodog.com/es/cuenta/transacciones')
                # print(f'{datetime.now().strftime("%H:%M:%S")}, visited histroy page to get bet id')
                # sports_tab = Find_element(driver_bookmaker, By.CLASS_NAME, 'tx-tab-sports')
                # driver_bookmaker.execute_script("arguments[0].click();", sports_tab)
                # frame = Find_element(driver_bookmaker, By.CLASS_NAME, 'bets-history-coupon-row--size-m')
                # bet_id = frame.find_element(By.CLASS_NAME, 'bets-history-table-row-value__value').text
                # bet_id = "12345"
                # benefit = round(((selected_quota_value - 1) * amount), 3)
                # print(f'{datetime.now().strftime("%H:%M:%S")}, "benefit: ${benefit}, bet id: {bet_id}" sent to scanner')  
                response = "success"
            else:
                print(f'{datetime.now().strftime("%H:%M:%S")}, quota is less than minimum')
                response = "quota is less than minimum"
        else:
            print(f'{datetime.now().strftime("%H:%M:%S")}, bank is not enough')
            response = "bank is not enough"
            ping("bodog's bank is not enough")
    else:
        print(f'{datetime.now().strftime("%H:%M:%S")}, Not matched')
        response = "Not found"
        ping("bodog not found")
    print(f'{datetime.now().strftime("%H:%M:%S")}, closed thread-bodog')

def marathon(event):
    global response
    global new_amount

    winner = event['winner']
    loser = event['loser']
    origin_quota = event['origin_quota']
    min_quota = event['min_quota']
    amount = event['amount']

    username_MARATHON = 'cesaraguirrebet@gmail.com'  # +58 4126230910
    password_MARATHON = 'Leomessi2312.'
    try:   
        driver_bookmaker.find_element(By.CSS_SELECTOR, 'button[data-test="headerAuthLogin"]').click()
        ping("marathon logged out")
        # sleep(5)
        # username = Find_element(driver_bookmaker, By.CSS_SELECTOR, 'input[data-test="authDialogLogin"]')
        # username.clear()
        # sleep(5)
        # username.send_keys(username_MARATHON)
        # print(1)
        # password = driver_bookmaker.find_element(By.CSS_SELECTOR, 'input[data-test="authDialogPassword"]')
        # password.clear()
        # sleep(5)
        # password.send_keys(password_MARATHON)
        # print(2)

        submit = Find_element(driver_bookmaker, By.CLASS_NAME, 'login-form__submit')
        pyautogui.moveTo(720, 650)
        sleep(3)
        pyautogui.click(720, 650)
        # driver_bookmaker.execute_script("arguments[0].click();", submit)
        sleep(1)
        Find_element(driver_bookmaker, By.CSS_SELECTOR, 'div[data-test="headerLoggedBalanceValue"]')
        print('[marathon], logged in successfully')
    except:
        pass

    search_key = ''
    for split in winner.split(' '):
        if len(split) >= 3:
            search_key = split
            break

    driver_bookmaker.get(f'https://www.marathonbet.com/en/search.htm?searchText={search_key}')
    Find_element(driver_bookmaker, By.CLASS_NAME, 'search-page')

    try:
        sports_tab = driver_bookmaker.find_elements(By.CLASS_NAME, 'tab-labels')[2]
        driver_bookmaker.execute_script("arguments[0].click();", sports_tab)
    except:
        pass

    while True:
        try:
            driver_bookmaker.find_element(By.CLASS_NAME, 'v-not-found')
            print(f'{datetime.now().strftime("%H:%M:%S")}, Not found')
            response = 'Not found'
            break
        except:
            pass
        try:
            results = driver_bookmaker.find_elements(By.CLASS_NAME, 'coupon-row')
            if len(results) > 0:
                selected_quota = None
                selected_quota_value = 0
                for item in results:
                    # if 'Tennis' in item.get_attribute('data-event-path'):
                    player = item.find_elements(By.CLASS_NAME, 'member-link')
                    quotas = item.find_elements(By.CLASS_NAME, 'height-column-with-price')
                    players = []
                    for name in player:
                        player_name = unidecode(name.text)
                        players.append(player_name)
                    index = player_exists([winner, loser], players)
                    if index != 2:
                        selected_quota = quotas[index]
                        selected_quota_value = float(selected_quota.text)
                        break
                if selected_quota_value > 0:
                    bank = float(driver_bookmaker.find_element(By.CSS_SELECTOR, 'div[data-test="headerLoggedBalanceValue"]').text.replace("$", "").replace(" ", ""))
                    if bank >= amount:
                        if selected_quota_value >= min_quota:
                            if selected_quota_value != origin_quota:
                                print(f'{datetime.now().strftime("%H:%M:%S")}, updated quota: {selected_quota_value}')
                                response = f"quota@{selected_quota_value}"
                                print(f'{datetime.now().strftime("%H:%M:%S")}, updated quota "{selected_quota_value}" sent to scanner')
                                new_amount = -1
                                while new_amount == -1:
                                    sleep(0.1)
                                amount = new_amount
                                print(f'{datetime.now().strftime("%H:%M:%S")}, updated amount "${new_amount }" received from scanner')
                            driver_bookmaker.execute_script("arguments[0].click();", selected_quota)
                            print(f'{datetime.now().strftime("%H:%M:%S")}, quota button was clicked')
                            
                            stake_input = Find_element(driver_bookmaker, By.CLASS_NAME, 'stake-input')
                            stake_input.clear()
                            stake_input.send_keys(amount)
                            print(f'{datetime.now().strftime("%H:%M:%S")}, ${amount} was typed to stake input')

                            bet_place_button = Find_element(driver_bookmaker, By.CLASS_NAME, 'btn-place-bet')
                            driver_bookmaker.execute_script("arguments[0].click();", bet_place_button)   
                            ok_button = Find_element(driver_bookmaker, By.ID, 'ok-button')
                            driver_bookmaker.execute_script("arguments[0].click();", ok_button)   
                            print(f'{datetime.now().strftime("%H:%M:%S")}, bet place button was clicked')
                            sleep(1)

                            # driver_bookmaker.get('https://www.marathonbet.com/en/myaccount/bethistory.htm')
                            # frame = Find_element(driver_bookmaker, By.CLASS_NAME, 'history-result-main')
                            # bet_id = frame.find_element(By.TAG_NAME, 'input').get_attribute('data-bet-id')
                            # benefit = round(((selected_quota_value - 1) * amount), 3)
                            # print(f'{datetime.now().strftime("%H:%M:%S")}, "benefit: ${benefit}, bet id: {bet_id}" sent to scanner')  
                            response = "success"
                        else:
                            print(f'{datetime.now().strftime("%H:%M:%S")}, quota is less than minimum')
                            response = "quota is less than minimum"
                    else:
                        print(f'{datetime.now().strftime("%H:%M:%S")}, bank is not enough')
                        response = "bank is not enough"
                        ping("marathon's bank is not enough")
                else:
                    print(f'{datetime.now().strftime("%H:%M:%S")}, Not matched ---')
                    response = "Not found"
                    ping("marathon not found")
                break
        except Exception as e:
            print(e)
        sleep(0.1)
    print(f'{datetime.now().strftime("%H:%M:%S")}, closed thread-marathon')

def megapari(event):
    global response
    global new_amount

    winner = event['winner']
    loser = event['loser']
    origin_quota = event['origin_quota']
    min_quota = event['min_quota']
    amount = event['amount']

    username_MEGAPARI = '697257045'
    password_MEGAPARI = 'alicia1711'   # +58 41262309 10
    try:
        driver_bookmaker.find_element(By.CLASS_NAME, 'auth-dropdown-trigger').click()
        ping("megapari logged out")
        login_form = Find_element(driver_bookmaker, By.TAG_NAME, 'form')
        Inputs = Find_elements(login_form, By.TAG_NAME, 'input')
        Inputs[0].clear()
        Inputs[0].send_keys(username_MEGAPARI)
        sleep(0.5)
        Inputs[1].clear()
        Inputs[1].send_keys(password_MEGAPARI)
        sleep(0.5)
        login_form.find_element(By.CLASS_NAME, 'auth-form-fields__submit').click()
        sleep(1)
        Find_element(driver_bookmaker, By.CLASS_NAME, 'account-select-toggle__value')
        print('[megapari], logged in successfully')
    except:
        pass

    search_input = driver_bookmaker.find_element(By.CLASS_NAME, 'search__input')
    search_input.clear()
    search_input.send_keys(winner)
    
    search_button = Find_element(driver_bookmaker, By.CLASS_NAME, 'search-button')
    driver_bookmaker.execute_script("arguments[0].click();", search_button)

    Find_element(driver_bookmaker, By.CLASS_NAME, 'games-search-modal__results')

    while True:
        try:
            driver_bookmaker.find_element(By.CLASS_NAME, 'message-block__head')
            print(f'{datetime.now().strftime("%H:%M:%S")}, Not found')
            response = "Not found"
            break
        except:
            pass
        try:
            results = driver_bookmaker.find_elements(By.CLASS_NAME, 'games-search-modal-results-list__item')
            if len(results) > 0:
                selected_quota = None
                selected_quota_value = 0
                for item in results:
                    player = item.find_element(By.CLASS_NAME, 'games-search-modal-card-info__main')
                    quotas = item.find_element(By.CLASS_NAME, 'games-search-modal-game-card-markets').find_elements(By.CLASS_NAME, 'ui-market__value')

                    player_name = unidecode(player.text)
                    players = player_name.split(' - ')

                    index = player_exists([winner, loser], players)
                    if index != 2:
                        selected_quota = quotas[index]
                        selected_quota_value = float(selected_quota.text)
                        break
                if selected_quota_value > 0:
                    bank = float(driver_bookmaker.find_element(By.CLASS_NAME, 'account-select-toggle__value').text)
                    bank = 1
                    if bank >= amount:
                        if selected_quota_value >= min_quota:
                            if selected_quota_value != origin_quota:
                                response = f"quota@{selected_quota_value}"
                                print(f'{datetime.now().strftime("%H:%M:%S")}, updated quota "{selected_quota_value}" sent to scanner')
                                new_amount = -1
                                while new_amount == -1:
                                    sleep(0.1)
                                amount = new_amount
                                print(f'{datetime.now().strftime("%H:%M:%S")}, updated amount "${new_amount }" received from scanner')
                            driver_bookmaker.execute_script("arguments[0].click();", selected_quota)
                            print(f'{datetime.now().strftime("%H:%M:%S")}, quota button was clicked')
                            close_button = driver_bookmaker.find_element(By.CLASS_NAME, 'v--modal-box').find_element(By.TAG_NAME, 'button')
                            driver_bookmaker.execute_script("arguments[0].click();", close_button)
                            sleep(0.1)
                            stake_input = Find_element(driver_bookmaker, By.CLASS_NAME, 'ui-number-input__field')
                            stake_input.clear()
                            stake_input.send_keys(amount)
                            print(f'{datetime.now().strftime("%H:%M:%S")}, ${amount} was typed to stake input')

                            bet_button = Find_element(driver_bookmaker, By.CLASS_NAME, 'coupon-buttons').find_element(By.TAG_NAME, 'button')
                            driver_bookmaker.execute_script("arguments[0].click();", bet_button)
                            print(f'{datetime.now().strftime("%H:%M:%S")}, bet place button was clicked')
                            success_button = Find_element(driver_bookmaker, By.CLASS_NAME, 'coupon-success-modal-controls__item')
                            driver_bookmaker.execute_script("arguments[0].click();", success_button)
                            sleep(1)

                            # driver_bookmaker.get('https://megapari.com/en/office/history')
                            # print(f'{datetime.now().strftime("%H:%M:%S")}, visited histroy page to get bet id')
                            # frame = Find_element(driver_bookmaker, By.CLASS_NAME, 'bets-history-coupon-row--size-m')
                            # bet_id = frame.find_element(By.CLASS_NAME, 'bets-history-table-row-value__value').text
                            # benefit = round(((selected_quota_value - 1) * amount), 3)
                            # print(f'{datetime.now().strftime("%H:%M:%S")}, "benefit: ${benefit}, bet id: {bet_id}" sent to scanner')  
                            response = "success"
                        else:
                            print(f'{datetime.now().strftime("%H:%M:%S")}, quota is less than minimum')
                            response = "quota is less than minimum"
                    else:
                        print(f'{datetime.now().strftime("%H:%M:%S")}, bank is not enough')
                        response = "bank is not enough"
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            loop.run_until_complete(send_message_to_channel("megapari's bank is not enough"))
                        finally:
                            loop.close()    
                else:
                    print(f'{datetime.now().strftime("%H:%M:%S")}, Not matched ---')
                    response = "Not found"
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(send_message_to_channel("megapari not found"))
                    finally:
                        loop.close() 
                break
        except Exception as e:
            print(e)
        sleep(0.1)
    # driver_bookmaker.get('https://megapari.com/en/')
    print(f'{datetime.now().strftime("%H:%M:%S")}, closed thread-megapari')

def pinnacle(event):
    global response
    global new_amount

    winner = event['winner']
    loser = event['loser']
    origin_quota = event['origin_quota']
    min_quota = event['min_quota']
    amount = event['amount']

    username_PINNACLE = 'josemiguelsatine@gmail.com'
    password_PINNACLE = 'Nina1711.'
    try:
        driver_bookmaker.find_element(By.CSS_SELECTOR, 'div[data-test-id="header-login-loginButton"]').find_element(By.TAG_NAME, 'button')
        ping("pinnacle logged out")
        username = driver_bookmaker.find_element(By.CSS_SELECTOR, 'input[aria-label="Current username"]')
        username.clear()
        username.send_keys(username_PINNACLE)
        password = driver_bookmaker.find_element(By.CSS_SELECTOR, 'input[aria-label="Current password"]')
        password.clear()
        password.send_keys(password_PINNACLE)
        driver_bookmaker.find_element(By.CSS_SELECTOR, 'div[data-test-id="header-login-loginButton"]').find_element(By.TAG_NAME, 'button').click()
        sleep(1)
        Find_element(driver_bookmaker, By.CSS_SELECTOR, 'span[data-test-id="QuickCashier-BankRoll"]')
        print(f'{datetime.now().strftime("%H:%M:%S")}, logged in successfully')
    except:
        pass

    driver_bookmaker.get(f'https://www.pinnacle.com/en/search/tennis/{winner}/participant/')

    main_part = Find_element(driver_bookmaker, By.TAG_NAME, 'main')
    Find_element(main_part, By.CSS_SELECTOR, 'div[data-test-id="Browse-Header"]') 
    found = False     
    while True:
        try:
            content = main_part.find_element(By.TAG_NAME, 'h3').text
            if 'without' in content.lower():
                found = False
                break
        except:
            pass
        try:
            content = main_part.find_elements(By.TAG_NAME, 'span')[-1].text
            if content == 'This selection has no matchups available.' or content == 'Try to search again with a different league or team name.':
                found = False
                break
        except:
            pass
        try:
            results = driver_bookmaker.find_elements(By.CSS_SELECTOR, 'div[data-test-id="Event.Row"]')
            selected_quota = None
            selected_quota_value = 0
            if len(results) > 0:
                found = True
                for item in results:
                    spans = item.find_elements(By.TAG_NAME, 'span')
                    index = player_exists([winner, loser], [spans[0].text, spans[1].text])
                    if index != 2:
                        for id, span in enumerate(spans):
                            try:
                                val = float(span.text)
                                selected_quota = spans[id + index]
                                selected_quota_value = float(selected_quota.text)
                                break
                            except:
                                pass
                        if selected_quota_value > 0:
                            break
                if selected_quota_value > 0:
                    bank = float(driver_bookmaker.find_element(By.CSS_SELECTOR, 'span[data-test-id="QuickCashier-BankRoll"]').text.replace(" ", "").replace("USD", "").replace(',', ''))
                    if bank >= amount:
                        if selected_quota_value >= min_quota:
                            if selected_quota_value != origin_quota:
                                response = f"quota@{selected_quota_value}"
                                print(f'{datetime.now().strftime("%H:%M:%S")}, updated quota "{selected_quota_value}" sent to scanner')
                                new_amount = -1
                                while new_amount == -1:
                                    sleep(0.1)
                                amount = new_amount
                                print(f'{datetime.now().strftime("%H:%M:%S")}, updated amount "${new_amount }" received from scanner')
                            driver_bookmaker.execute_script("arguments[0].click();", selected_quota)
                            print(f'{datetime.now().strftime("%H:%M:%S")}, quota button was clicked')

                            container = Find_element(driver_bookmaker, By.ID, 'scroll-container')
                            stake_input = Find_element(container, By.TAG_NAME, 'input')
                            stake_input.clear()
                            stake_input.send_keys(amount)
                            print(f'{datetime.now().strftime("%H:%M:%S")}, ${amount} was typed to stake input')

                            bet_button = driver_bookmaker.find_element(By.CSS_SELECTOR, 'button[data-test-id="Betslip-ConfirmBetButton"]')
                            driver_bookmaker.execute_script("arguments[0].click();", bet_button)
                            print(f'{datetime.now().strftime("%H:%M:%S")}, bet place button was clicked')
                            sleep(1)                                            

                            # driver_bookmaker.get('https://www.pinnacle.com/en/account/bets/history')
                            # print(f'{datetime.now().strftime("%H:%M:%S")}, visited histroy page to get bet id')
                            # frame = Find_element(driver_bookmaker, By.CSS_SELECTOR, 'div[data-test-id="betCard"]')
                            # contents = frame.text.split('\n')
                            # for content in contents:
                            #     if 'Bet no.#' in content:
                            #         bet_id = content.split('#')[1]
                            # benefit = round(((selected_quota_value - 1) * amount), 3)
                            # print(f'{datetime.now().strftime("%H:%M:%S")}, "benefit: {benefit}, bet id: {bet_id}" sent to scanner')
                            response = "success"
                        else:
                            print(f'{datetime.now().strftime("%H:%M:%S")}, quota is less than minimum')
                            response = "quota is less than minimum"
                    else:
                        print(f'{datetime.now().strftime("%H:%M:%S")}, bank is not enough')
                        response = "bank is not enough"
                        ping("pinnacle's bank is not enough")
                else:
                    print(f'{datetime.now().strftime("%H:%M:%S")}, Not matched')
                    response = "Not found"
                    ping("pinnacle not found")
                break
        except Exception as e:                        
            print(e)
        sleep(0.1)
    if not found:
        print(f'{datetime.now().strftime("%H:%M:%S")}, Not found')
        response = "Not found"
        ping("pinnacle not found")
    print(f'{datetime.now().strftime("%H:%M:%S")}, closed thread-pinnacle')

def vbet(event):
    global response
    global new_amount

    winner = event['winner']
    loser = event['loser']
    origin_quota = event['origin_quota']
    min_quota = event['min_quota']
    amount = event['amount']

    username_VBET = 'josemiguelsatine@gmail.com'
    password_VBET = 'Nina1711.'
    try:
        driver_bookmaker.find_element(By.CLASS_NAME, 'sign-in').click()
        ping("vbet logged out")
        Find_element(driver_bookmaker, By.NAME, 'username').send_keys(username_VBET)
        sleep(0.5)
        driver_bookmaker.find_element(By.NAME, 'password').send_keys(password_VBET)
        sleep(0.5)
        driver_bookmaker.find_element(By.CLASS_NAME, 'entrance-form-action-item-bc').find_element(By.TAG_NAME, 'button').click()
        sleep(1)
        Find_element(driver_bookmaker, By.CLASS_NAME, 'hdr-user-info-texts-bc')
        print('[vbet], logged in successfully')
    except:
        pass

    search_input = driver_bookmaker.find_element(By.CLASS_NAME, 'ss-input-bc')
    search_input.clear()
    search_input.send_keys(winner)

    Find_element(driver_bookmaker, By.CLASS_NAME, 'sport-search-result-bc')

    while True:
        try:
            driver_bookmaker.find_element(By.CLASS_NAME, 'sport-search-result-bc').find_element(By.CLASS_NAME, 'empty-b-text-v-bc')
            print(f'{datetime.now().strftime("%H:%M:%S")}, Not found')
            response = 'Not found'
            break
        except:
            pass
        try:
            results = driver_bookmaker.find_elements(By.CLASS_NAME, 'sport-search-result-item-bc')
            if len(results) > 0:
                isMatched = False
                for item in results:
                    element = item.find_elements(By.TAG_NAME, 'p')[1]

                    player_name = unidecode(element.text).split(' - ')
                    players = []
                    players.append(player_name[0])
                    players.append(player_name[1])
                
                    index = player_exists([winner, loser], players)

                    if index != 2:
                        driver_bookmaker.execute_script("arguments[0].click();", item)
                        isMatched = True
                        break
                if isMatched:
                    try:
                        element = Find_element(driver_bookmaker, By.CSS_SELECTOR, 'div[data-index="0"]')
                        quotas = element.find_elements(By.CLASS_NAME, 'market-odd-bc')
                        selected_quota = quotas[index]
                        selected_quota_value = float(quotas[index].text)

                        bank = float(driver_bookmaker.find_element(By.CLASS_NAME, 'hdr-user-info-texts-bc').text.split(' ')[0])
                        if bank >= amount:
                            print(selected_quota_value, min_quota)
                            if selected_quota_value >= min_quota:
                                if selected_quota_value != origin_quota:
                                    response = f"quota@{selected_quota_value}"
                                    print(f'{datetime.now().strftime("%H:%M:%S")}, updated quota "{selected_quota_value}" sent to scanner')
                                    new_amount = -1
                                    while new_amount == -1:
                                        sleep(0.1)
                                    amount = new_amount                                    
                                    print(f'{datetime.now().strftime("%H:%M:%S")}, updated amount "${new_amount }" received from scanner')                                    
                                driver_bookmaker.execute_script("arguments[0].click();", selected_quota)
                                print(f'{datetime.now().strftime("%H:%M:%S")}, quota button was clicked')

                                stake_input = Find_element(driver_bookmaker, By.CLASS_NAME, 'bs-bet-i-b-s-i-bc')
                                stake_input.clear()
                                stake_input.send_keys(amount)
                                print(f'{datetime.now().strftime("%H:%M:%S")}, ${amount} was typed to stake input')

                                bet_button = driver_bookmaker.find_element(By.CLASS_NAME, 'bet-button-wrapper-bc').find_element(By.TAG_NAME, 'button')
                                driver_bookmaker.execute_script("arguments[0].click();", bet_button)     
                                print(f'{datetime.now().strftime("%H:%M:%S")}, bet place button was clicked. sleeping for 5s...')                                
                                sleep(1) #10

                                # driver_bookmaker.get('https://www.vbet.lat/en/sports/pre-match/event-view/Soccer/Brazil/1792?profile=open&account=history&page=bets')
                                # print(f'{datetime.now().strftime("%H:%M:%S")}, visited histroy page to get bet id')
                                # sleep(1)
                                # Find_element(driver_bookmaker, By.CLASS_NAME, 'u-i-p-c-filter-footer-bc').find_element(By.TAG_NAME, 'button').click()    
                                # frame = Find_element(driver_bookmaker, By.CLASS_NAME, 'betHistoryList-tbody')
                                # bet_id = frame.find_element(By.CLASS_NAME, 'betHistory-Id').text.replace("\n", " ")
                                # benefit = round(((selected_quota_value - 1) * amount), 3)
                                # print(f'{datetime.now().strftime("%H:%M:%S")}, "benefit: ${benefit}, bet id: {bet_id}" sent to scanner') 
                                response = "success"                                         
                            else:
                                print(f'{datetime.now().strftime("%H:%M:%S")}, quota is less than minimum')
                                response = "quota is less than minimum"
                        else:
                            print(f'{datetime.now().strftime("%H:%M:%S")}, bank is not enough')
                            response = "bank is not enough"
                            ping("vbet's bank is not enough")
                    except:
                        print(f'{datetime.now().strftime("%H:%M:%S")}, Not found')
                        response = "Not found"
                        ping("vbet not found")
                else:
                    print(f'{datetime.now().strftime("%H:%M:%S")}, Not matched ---')
                    response = "Not found"
                    ping("vbet not found")
                break
        except:
            pass
        sleep(0.1)
    # driver_bookmaker.get("https://www.vbet.lat/en/sports/pre-match/event-view")
    print(f'{datetime.now().strftime("%H:%M:%S")}, closed thread-vbet')

def winner(just_started):
    global response
    global new_amount

    username_WinnarOdds = 'davidodds23@gmail.com'
    password_WinnarOdds = 'Nina1711.'

    options_winner = Options()
    options_winner.add_experimental_option("debuggerAddress", "127.0.0.1:9056")
    driver_winner = webdriver.Chrome(service=service, options=options_winner)

    if driver_winner.current_url == 'https://app.winnerodds.com/login':
        inputs = Find_elements(driver_winner, By.TAG_NAME, 'input')
        username = inputs[0]
        username.send_keys(username_WinnarOdds)
        sleep(0.5)
        password = inputs[1]
        password.send_keys(password_WinnarOdds)
        driver_winner.find_element(By.TAG_NAME, 'button').click()
    else:
        driver_winner.refresh()
    matchs = []
    if just_started:
        while True:
            try:
                driver_winner.find_element(By.CLASS_NAME, 'fnt-xl2').text
                break
            except:
                pass
            try:
                matchs = driver_winner.find_elements(By.CLASS_NAME, 'match')
                if matchs:
                    break
            except:
                pass
            sleep(0.1)
    else:
        matchs = Find_elements(driver_winner, By.CLASS_NAME, 'match')
    count = len(matchs)
    print(f'{datetime.now().strftime("%H:%M:%S")}, {count} events found')
    for index in range(count):
        try:
            match = driver_winner.find_element(By.CLASS_NAME, 'match')
            country = match.find_element(By.CLASS_NAME, 'country').text
            winner = match.find_element(By.CLASS_NAME, 'player-info-name').text
            loser = match.find_element(By.CLASS_NAME, 'players-info-home').text
            if winner == loser:
                loser = match.find_element(By.CLASS_NAME, 'players-info-away').text
            min_quota = float(match.find_element(By.CLASS_NAME, 'match-cmin-quota').text)

            winner = unidecode(winner)
            loser = unidecode(loser)

            odd = match.find_element(By.CLASS_NAME, 'odd')
            bookie = odd.find_element(By.CLASS_NAME, 'bookie').text
            origin_quota = float(odd.find_element(By.CLASS_NAME, 'match-odd-quota').text)
            try:
                amount = float(odd.find_element(By.CLASS_NAME, 'amount').text.split('$')[0])     
            except:      
                match.find_element(By.CLASS_NAME,'icon-eye-open').click() 
                sleep(1)
                continue
            event = {}
            event['country'] = country
            event['winner'] = winner
            event['loser'] = loser
            event['min_quota'] = min_quota
            event['origin_quota'] = origin_quota
            event['amount'] = amount

            odd.click()                

            if bookie == '1XBETCOM':
                thread = Thread(target=(_1xbet), args=(event, ))
            if bookie == 'DOBOG':
                thread = Thread(target=(bodog), args=(event, ))
            if bookie == 'MARATHON':
                thread = Thread(target=(marathon), args=(event, ))
            if bookie == 'MEGAPARI':
                thread = Thread(target=(megapari), args=(event, ))
            if bookie == 'PINNACLE':
                thread = Thread(target=(pinnacle), args=(event, ))
            if bookie == 'VBET':
                thread = Thread(target=(vbet), args=(event, ))

            print("\n", "-"*20, bookie.center(10), "-"*20)
            print(f'{datetime.now().strftime("%H:%M:%S")}, bookie: {bookie}, winner: {winner}, lowser: {loser}, origin quota: {origin_quota}, min quota: {min_quota}, amount: {amount}')
            if tab_index[f"{bookie.lower()}"] == -1: 
                ping(f"No tab for {bookie} on Chrome browser. It's waiting for the Tab")
            
            res = input(f"{bookie} opened?(y/n) ")
            for i in range(len(window_handles)):
                driver_bookmaker.switch_to.window(window_handles[i])
                url = driver_bookmaker.current_url
                if "1xbet" in url:
                    tab_index["1xbetcom"] = i
                    driver_bookmaker.get("https://1xbet.com/en/live/tennis")
                if "bodog" in url:
                    tab_index["bodog"] = i 
                if "pinnacle" in url:
                    tab_index["pinnacle"] = i 
                if "megapari" in url:
                    tab_index["megapari"] = i 
                if "marathon" in url:
                    tab_index["marathon"] = i 
                if "vbet" in url:
                    tab_index["vbet"] = i 
                    driver_bookmaker.get("https://www.vbet.lat/en/sports/pre-match/event-view")          
                sleep(1)

            driver_bookmaker.switch_to.window(window_handles[tab_index[f"{bookie.lower()}"]])
            thread.start()
        
            response = 'none'
            while response == 'none':
                sleep(0.1)
            if 'quota' in response:
                new_quota = float(response.split('@')[1])
                print(f'{datetime.now().strftime("%H:%M:%S")}, origin quota: {origin_quota} -> updated quota: {new_quota}')

                # save_quota = driver_winner.find_element(By.NAME, 'quota')
                save_quota = Find_element(driver_winner, By.NAME, 'quota')
                save_quota.clear()
                save_quota.send_keys(new_quota) 

                temp = 0
                while True:
                    try:
                        temp = float(driver_winner.find_element(By.NAME, 'amount').get_attribute('value'))
                        break
                    except:
                        pass
                    sleep(0.1)
                print(f'{datetime.now().strftime("%H:%M:%S")}, origin amount: ${amount} -> updated amount: ${temp}')

                if temp >= min_amount[bookie.lower()]:
                    new_amount = temp
                    response = 'none'
                    print(f'{datetime.now().strftime("%H:%M:%S")}, ${temp} sent to [{bookie}]')
                    while response == 'none':
                        sleep(0.1)
                else:
                    response = "amount is less than minimum" 
            if response == "quota is less than minimum" or response == "Not found" or response == "bank is not enough" or response == "amount is less than minimum":
                print(f'{datetime.now().strftime("%H:%M:%S")}, "{response}" received from "{bookie}"')
                driver_winner.find_element(By.CLASS_NAME, 'icon-close').click() 
                print(f'{datetime.now().strftime("%H:%M:%S")}, event close button was clicked')
                match.find_element(By.CLASS_NAME,'icon-eye-open').click()
                print(f'{datetime.now().strftime("%H:%M:%S")}, event hide button was clicked')
            if response == 'success':
                driver_winner.find_element(By.CLASS_NAME, 'fnt-upper').click()  
                print(f'{datetime.now().strftime("%H:%M:%S")}, event save button was clicked\n')

                # curr_time = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
                # connection = sqlite3.connect("database.db")
                # cursor = connection.cursor()
                # cursor.execute("insert into data(date_time,bookie,country,winner,loser,quota,amount,benefit,bet_id,status) values(?,?,?,?,?,?,?,?,?,?)", (curr_time,bookie,country,winner,loser,new_quota,new_amount,benefit,bet_id,"Unsettled"))
                # connection.commit()
                # print(f'{datetime.now().strftime("%H:%M:%S")}, saved to database')

                table = PrettyTable(["Options".center(20), "Value".center(20)])
                table.add_row(["Bookie", bookie])
                table.add_row(["Sports", "Tennis"])
                table.add_row(["Winner", winner])
                table.add_row(["Loser", loser])
                table.add_row(["Quota", new_quota])
                table.add_row(["Amount", f"${new_amount}"])
                table.add_row(["Benefit", f"${round((new_quota - 1) * new_amount), 2}"])

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(send_message_to_channel(f"```{table}```"))
                finally:
                    loop.close()
            sleep(0.5) 
        except:
            pass
    
def gmail():
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly'] 
    credential = {
        "installed": {
            "client_id": "103131702885-2topln7qn007mg934o3ocvmr2r9h25jq.apps.googleusercontent.com",
            "project_id": "exemplary-works-402420",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": "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",
            "redirect_uris": [
                "http://localhost"
            ]
        }
    }

    creds = None
    if os.path.exists('token.pickle'): 
        with open('token.pickle', 'rb') as token: 
            creds = pickle.load(token) 

    if not creds or not creds.valid: 
        if creds and creds.expired and creds.refresh_token: 
            creds.refresh(Request()) 
        else: 
            # flow = InstalledAppFlow.from_client_secrets_file('_credentials.json', SCOPES) 
            flow  = InstalledAppFlow.from_client_config(credential, SCOPES)
            creds = flow.run_local_server(port=0) 

        # Save the access token in token.pickle file for the next run 
        with open('token.pickle', 'wb') as token: 
            pickle.dump(creds, token) 

    service = build('gmail', 'v1', credentials=creds) 

    last_id = None
    is_restarted = True

    while True:
        try:
            result = service.users().messages().list(userId='me').execute() 
            messages = result.get('messages') 

            compare_id = last_id
            received = False
            for index, msg in enumerate(messages):

                txt = service.users().messages().get(userId='me', id=msg['id'], ).execute() 
                id = txt['id']                
                if id == compare_id or last_id == None:
                    last_id = id
                    break
                if index == 0:
                    last_id = id
                    if is_restarted:
                        is_restarted = False
                        break
                datas = txt['payload']['headers']
                for data in datas:
                    print("Here")
                    if data['name'] == "From" and data['value'] == "Winnerodds <info@winnerodds.com>":
                        received = True
                        break
                if received:
                    break
            print(f'{datetime.now().strftime("%H:%M:%S")}, gmail received? {received}')
            if received:
                winner(just_started=False)
        except:
            pass
        sleep(10)

def ping(content):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(send_message_to_channel(content))
    finally:
        loop.close() 

if __name__ == "__main__":
    for i in range(len(window_handles)):
        driver_bookmaker.switch_to.window(window_handles[i])
        url = driver_bookmaker.current_url
        if "1xbet" in url:
            tab_index["1xbetcom"] = i
            driver_bookmaker.get("https://1xbet.com/en/live/tennis")
        if "bodog" in url:
            tab_index["bodog"] = i 
        if "pinnacle" in url:
            tab_index["pinnacle"] = i 
        if "megapari" in url:
            tab_index["megapari"] = i 
        if "marathon" in url:
            tab_index["marathon"] = i 
        if "vbet" in url:
            tab_index["vbet"] = i 
            driver_bookmaker.get("https://www.vbet.lat/en/sports/pre-match/event-view")          
        sleep(1)
    winner(just_started=True)
    gmail()
