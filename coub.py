"""
Copyright (C) 2018-2020 HelpSeeker <AlmostSerious@protonmail.ch>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
import sys
import time
import requests
import random
import json
import traceback
import logging
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.remote_connection import LOGGER
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from fake_useragent import UserAgent
from slugify import slugify
from bs4 import BeautifulSoup
import requests
import subprocess
import argparse
import ffmpeg

FILENAME = '1.mp3'
URL_BOOKMARKS = 'https://coub.com/bookmarks'
URL_LIKES = 'https://coub.com/likes'
GOOGLEIBMLINK = 'https://speech-to-text-demo.ng.bluemix.net/'
DELAYTIME = 2
AUDIOTOTEXTDEALY = 10
script_path = os.path.dirname(sys.argv[0])

def audioToText(mp3Path, driver):
    print('Start ReCaptcha audio to text.')
    driver.execute_script('''window.open("","_blank");''')
    driver.switch_to.window(driver.window_handles[1])
    driver.get(GOOGLEIBMLINK)
    delayTime = 10
    time.sleep(2)
    btn = driver.find_element(By.XPATH, '//*[@id="root"]/div/input')
    btn.send_keys(mp3Path)
    time.sleep(delayTime)
    time.sleep(AUDIOTOTEXTDEALY)
    text = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[7]/div/div/div').find_elements(By.TAG_NAME, 'span')
    result = " ".join( [ each.text for each in text ] )
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    print('Almost done')
    return result
def saveFile(content, filename):
    with open(filename, "wb") as handle:
        for data in content.iter_content():
            handle.write(data)

def download_coub(coub_url):
    ua = UserAgent()
    headers = {'User-Agent': ua.random}
    response = requests.get(coub_url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    coubPageCoubJson = soup.find(id = "coubPageCoubJson")
    coubPageCoubJson = str(coubPageCoubJson).split('>')[1]
    coubPageCoubJson = coubPageCoubJson.split('<')[0]
    json_ = json.loads(coubPageCoubJson)
    title = json_['title']
    title = slugify(title)
    if title is None or title == '':
        title = 'no_title'
    path = os.path.join(script_path, 'video', f'{title}.mp4')
    video_url = json_["file_versions"]["share"]['default']
    if video_url is None:
        video_url = json_["file_versions"]["html5"]['video']['med']['url']
        audio_url = json_["file_versions"]["html5"]['audio']['med']['url']
        video = requests.get(video_url, headers=headers)
        audio = requests.get(audio_url, headers=headers)
        path_video = os.path.join(script_path, 'temp', f'{title}.mp4')
        path_audio = os.path.join(script_path, 'temp', f'{title}.mp3') 
        with open (path_video, "wb") as f:
                f.write(video.content)
        with open (path_audio, "wb") as f:
                f.write(audio.content)   
        cmd = f"ffmpeg  -stream_loop -1 -i {path_video} -i {path_audio} -shortest -map 0:v:0 -map 1:a:0 -y {path} -nostats -loglevel 0"
        subprocess.call(cmd, shell=True) 
        os.remove(path_video)
        os.remove(path_audio)
    else:
        tmp = requests.get(video_url, headers=headers)    
        with open (path, "wb") as f:
            f.write(tmp.content)

def pass_urls_to_download(list):
    errors = {}
    count = 0
    for c_url in list:
        print(f"Trying to download: {c_url}")
        try:
            download_coub(c_url)
            count+=1
            print(f"{count} coubs downloaded.")            
        except Exception:
            errors[c_url] = str(traceback.format_exc())
            print('Not able to download coub.')
    with open(os.path.join(script_path, 'json_lists', 'error_coubs_list.json'), 'w') as f:
            json.dump(errors, f)
    return count, errors

def scrape_coub_list(url, email, password):
    options = webdriver.ChromeOptions() 
    options.add_argument("--headless")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("start-maximized")
    options.add_argument('disable-infobars')
    options.add_argument('--disable-gpu')
    options.add_argument("--disable-extensions")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--mute-audio")
    options.add_argument("--log-level=3")
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36")

    LOGGER.setLevel(logging.ERROR)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager(log_level=0).install()), options=options)
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    time_to_sleep = random.uniform(3, 5)
    time.sleep(time_to_sleep)

    try:
        log = wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div[3]/div/div/div[2]/button[1]")))
        log.click()
        print('Log in button clicked.')
        time_to_sleep = random.uniform(1, 3)
        time.sleep(time_to_sleep)
    except Exception as e:
        print('Log in button not found.')
        print(e)

    try:
        email_box = wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[3]/div[2]/div/div[2]/div/div[2]/div[1]/div/form/div[1]/input[1]")))
        email_box.send_keys(email)        
        print('Email box filled.')
        time_to_sleep = random.uniform(1, 3)        
        time.sleep(time_to_sleep)   
        email_box.send_keys(Keys.ENTER)         
    except Exception as e:
        print('Email box not found.')
        print(e)     

    try:
        password_box = wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[3]/div[2]/div/div[2]/div/div[2]/div[1]/div/form/div[1]/input[2]")))
        password_box.send_keys(password) 
        password_box.send_keys(Keys.ENTER)       
        print('Password box filled.')
        time_to_sleep = random.uniform(1, 2)        
        time.sleep(time_to_sleep)             
    except Exception as e:
        print('Email box not found.')
        print(e)

    allIframesLen = driver.find_elements(By.TAG_NAME, 'iframe')
    time.sleep(1)
    audioBtnFound = False
    audioBtnIndex = -1
    for index in range(len(allIframesLen)):
        driver.switch_to.default_content()
        iframe = driver.find_elements(By.TAG_NAME, 'iframe')[index]
        time.sleep(1)
        try:
            driver.switch_to.frame(iframe)
            driver.implicitly_wait(DELAYTIME)
            try:
                audioBtn = driver.find_element(By.ID, 'recaptcha-audio-button') or driver.find_element(By.ID, 'recaptcha-anchor')            
                audioBtn.click()
                time.sleep(1)
                audioBtnFound = True
                audioBtnIndex = index
                break
            except Exception as e:
                pass
        except:
            break

    if audioBtnFound:
        try:
            while True:
                href = driver.find_element(By.ID,'audio-source').get_attribute('src')
                response = requests.get(href, stream=True)
                saveFile(response, os.path.join(script_path,'temp', FILENAME))
                response = audioToText(os.path.join(script_path,'temp', FILENAME), driver)
                print(f"ReCaptcha auto text: {response}")            
                driver.switch_to.default_content()
                iframe = driver.find_elements(By.TAG_NAME, 'iframe')[audioBtnIndex]
                driver.switch_to.frame(iframe)
                inputbtn = driver.find_element(By.ID, 'audio-response')
                inputbtn.send_keys(response)
                inputbtn.send_keys(Keys.ENTER)
                time.sleep(2)
                try:
                    errorMsg = driver.find_elements(By.CLASS_NAME, 'rc-audiochallenge-error-message')[0]
                    if errorMsg.text == "" or errorMsg.value_of_css_property('display') == 'none':
                        print("Success")
                        os.remove(os.path.join(script_path,'temp', FILENAME))
                        break
                except:
                    print("Success")
                    os.remove(os.path.join(script_path,'temp', FILENAME))
                    break
        except Exception as e:
                print(e)
                print('Caught. Need to change proxy now. ReCaptcha found that we are a bot.')
                sys.exit()
    else:
        print('ReCaptcha button not found. This should not happen or there is no ReCaptcha and everything is ok.')

    driver.switch_to.default_content() 
    time_to_sleep = random.uniform(1, 2)        
    time.sleep(time_to_sleep)   

    print('Scrolling webpage. It can take a while.')

    counter = 0
    pageHeight = 0
    loop = False
    while not loop == True:
        try:
            previous_page_height = pageHeight             
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            pageHeight = driver.execute_script("return document.body.scrollHeight")
            driver.execute_script("return window.pageYOffset + window.innerHeight")             
            counter += 1        
            if previous_page_height != pageHeight:
                counter = 0
            time_to_sleep = random.uniform(0.9, 1.3)
            time.sleep(time_to_sleep) 
            if(counter > 30):
                loop = True 
                print("End of page")
                time.sleep(2)             
                break  
        except Exception as e:
            print(e)  

    page_coub_list = driver.find_element(By.CSS_SELECTOR, 'body > div.body-container > div.logged.page-container > div > div > div.coubs-list > div.coubs-list__inner').find_element(By.CLASS_NAME, 'page').find_elements(By.XPATH, '//div[@data-permalink]')

    title_list = []
    for i in range(len(page_coub_list)):
        coub = 'https://coub.com/view/' + page_coub_list[i].get_attribute("data-permalink")
        title_list.append(coub)
        print(coub)

    driver.close()

    coubs_list = list(set(title_list))
    print(f"Number of cubes: {len(coubs_list)}")

    with open(os.path.join(script_path, 'json_lists', 'coubs_list.json'), 'w') as f:
        json.dump(coubs_list, f)

    return coubs_list


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--password", type=str, help='Your password to your coub.com account')
    parser.add_argument("-e", "--email", type=str, help='Your email to your coub.com account')
    parser.add_argument("-t", "--type", type=str, help="Type [likes] to download coubs form My likes page and [bookmarks] for Bookmarks.")

    args = parser.parse_args()
    password = args.password
    email = args.email
    type = args.type

    if password == None:
        print('No password argument. -> python coub.py --help | for help')
        sys.exit()
    if email == None:
        print('No email argument. -> python coub.py --help | for help')
        sys.exit()
    if type not in ['bookmarks', 'likes']:
        print('Wrong type argument. -> python coub.py --help | for help')
        sys.exit()

    if type == 'bookmarks':
        url = URL_BOOKMARKS
    elif type == 'likes':
        url = URL_LIKES

    coub_list = scrape_coub_list(url, email, password)

    counter_one, error_list = pass_urls_to_download(coub_list)
    print(f'{len(error_list)} coubs have not been downloaded.')
    
    if len(error_list) > 0 :
        print('Try again.')
        counter_two, error_list = pass_urls_to_download(error_list)
        print(f'{len(error_list)} coubs have not been downloaded. Check them and errors in /json_lists/error_coubs_list.json')

    print(f'\nFinaly, {counter_two + counter_one} have been downloaded.')
