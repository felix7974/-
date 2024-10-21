import re
import asyncio
from telethon import TelegramClient, events
import pyautogui
import time
from concurrent.futures import ThreadPoolExecutor
import datetime
import clipboard
import requests
import json

# 텔레그램 API 설정
api_id = ''          # 자신의 API ID로 교체
api_hash = ''      # 자신의 API Hash로 교체
channel_id = int('')  # 모니터링할 채널의 고유 ID로 교체

#텔레그램 봇이랑 알림 채널 설정
bot_token = ''
notification_channel_id = ''

#url 설정
url = f'https://api.telegram.org/bot{bot_token}/sendMessage'

# 투자 금액 정하기
a = '20'

# 텔레그램 클라이언트 초기화
client = TelegramClient('session_name', api_id, api_hash)

# 스레드 풀 생성 (pyautogui 작업을 별도의 스레드에서 실행하기 위함)
executor = ThreadPoolExecutor(max_workers=5)

# API 호출 제한 관리
last_api_call = None
api_call_interval = datetime.timedelta(seconds=3)  # 개인 채팅의 경우 1초 간격 적용
last_group_call = None
group_call_interval = datetime.timedelta(seconds=5)  # 그룹의 경우 분당 20회이므로 3초 간격 적용

# 메시지에서 필요한 정보를 추출하는 함수
def extract_info(message_text):
    iteration = None
    target_price = None
    stop_loss = None
    entry_price = None
    position = None
    action = None

    # 정규 표현식을 사용하여 회차, 목표가, 손절가, 진입가, 포지션 추출
    iteration_match = re.search(r'(\d+)회차', message_text)
    target_match = re.search(r'목표가\s*([0-9,.]+)', message_text)
    stop_loss_match = re.search(r'손절가\s*([0-9,.]+)', message_text)
    entry_match = re.search(r'진입가\s*([0-9,.]+)', message_text)
    position_match = re.search(r'\b\w+\s*/\s*(Long|Short)\s*(오픈|종료)', message_text, re.IGNORECASE)
    action_match = re.search(r'(오픈|종료)', message_text)

    if iteration_match:
        iteration = iteration_match.group(1)  # 회차 번호 추출
    if target_match:
        target_price = target_match.group(1).replace(',', '')
    if stop_loss_match:
        stop_loss = stop_loss_match.group(1).replace(',', '')
    if entry_match:
        entry_price = entry_match.group(1).replace(',', '')
    if position_match:
        position = position_match.group(1).capitalize()  # 'Long' 또는 'Short'로 표준화
    if action_match:
        action = action_match.group(1)

    return iteration, target_price, stop_loss, entry_price, position, action

# pyautogui 작업을 별도의 스레드에서 실행하는 함수
def execute_pyautogui_tasks(task_list):
    for task in task_list:
        func, args = task
        func(*args)

# 메시지 처리 함수
async def process_message(message):
    global last_api_call, last_group_call
    current_time = datetime.datetime.now()

    # 그룹 메시지일 경우
    if message.is_group:
        if last_group_call and (current_time - last_group_call) < group_call_interval:
            print("그룹 메시지 처리 제한: 호출 간격이 너무 짧습니다. 대기 중입니다.")
            await asyncio.sleep((group_call_interval - (current_time - last_group_call)).total_seconds())  # 남은 시간 대기
        last_group_call = current_time

    # 개인 채팅일 경우
    else:
        if last_api_call and (current_time - last_api_call) < api_call_interval:
            print("개인 메시지 처리 제한: 호출 간격이 너무 짧습니다. 대기 중입니다.")
            await asyncio.sleep((api_call_interval - (current_time - last_api_call)).total_seconds())  # 남은 시간 대기
        last_api_call = current_time

    iteration, target, stop, entry, position, action = extract_info(message.text)
    while True:

        # '송출' 단어 감지
        if '송출' in message.text:
            print("송출 단어 감지됨. 지정된 좌표로 이동하여 클릭합니다.")
        
            # 마우스를 특정 좌표로 이동하고 클릭 (청산하기)
            task_list = [
                (pyautogui.moveTo, (1471,758, 0.2)),
                (pyautogui.click, ()),
                (time.sleep, (0.2,)),
                (pyautogui.moveTo, (1069, 629, 0.2)),
                (pyautogui.click, ())
            ]
            await asyncio.get_running_loop().run_in_executor(executor, execute_pyautogui_tasks, task_list)
            return  # '송출' 처리 후 다른 작업을 하지 않도록 종료

        if action == '오픈':
            if iteration and target and stop and entry and position:
                print(f"{iteration}회차 포지션: {position}, 진입가: {entry}, 목표가: {target}, 손절가: {stop}")

                # 공통 작업: 거래 플랫폼 창 활성화 및 초기 클릭
                pyautogui.moveTo(1871,181,duration=0.3)
                pyautogui.click()
                time.sleep(0.1)
                pyautogui.moveTo(1908, 171, duration=0.3)
                pyautogui.click()
                time.sleep(0.2)
                pyautogui.moveTo(1662,165,duration=0.3)
                pyautogui.click()
                time.sleep(0.2)

                # 회차에 따라 다른 좌표로 이동 및 클릭
                if iteration == '1':
                    pyautogui.moveTo(1738,430-40-10, duration=0.3)
                    pyautogui.click()
                    time.sleep(0.2)
                    pyautogui.typewrite(a)
                elif iteration == '2':
                    pyautogui.moveTo(1738,430-40-10, duration=0.3)
                    pyautogui.click()
                    time.sleep(0.2)
                    pyautogui.typewrite(str(int(a)*3))
                elif iteration == '3':
                    pyautogui.moveTo(1738,430-40-10, duration=0.3)
                    pyautogui.click()
                    time.sleep(0.2)
                    pyautogui.typewrite(str(int(a)*6))
                else:
                    print(f"알 수 없는 회차: {iteration}")
                    return  # 알 수 없는 회차일 경우 작업 중단

                if position == 'Long':
                    # 롱 포지션 작업(tp/sl, 목표가, 손절가, 롱 시작)
                    pyautogui.moveTo(1624, 643 - 39-40-15, duration=0.3-0.1)
                    pyautogui.click()
                    time.sleep(0.2)

                    pyautogui.moveTo(1740, 705 - 39-40-10, duration=0.3-0.1)
                    pyautogui.click()
                    pyautogui.typewrite(target)
                    time.sleep(0.2)

                    pyautogui.moveTo(1740, 800 - 39-40-10, duration=0.3-0.1)
                    pyautogui.click()
                    pyautogui.typewrite(stop)
                    time.sleep(0.2)

                    pyautogui.moveTo(1682, 865 - 39-40-10, duration=0.3-0.1)
                    pyautogui.click()
                    time.sleep(0.2)

                    # 롱 포지션 마지막 추가 작업(팝업창 2번 클릭 후 초기 상태로 되돌리기)
                    pyautogui.moveTo(1073, 358, duration=0.3-0.1)
                    pyautogui.click()
                    time.sleep(0.2)
                    pyautogui.moveTo(1624, 643 - 39-40-15, duration=0.3-0.1)
                    pyautogui.click()
                    time.sleep(0.2-0.1)
                
                    #목표가 손절가 확인해서 비교하기
                    t=target
                    s=stop
                    pyautogui.moveTo(364, 748, duration=0.3-0.1)
                    pyautogui.click()
                    time.sleep(0.5)
                    pyautogui.moveTo(1087, 879, duration=0.3-0.1)
                    pyautogui.click(clicks=2)
                    pyautogui.hotkey('ctrl','c')
                    time.sleep(0.5)
                    t1=str(clipboard.paste())
                    t1=t1.replace(',','')
                    pyautogui.moveTo(1087, 900, duration=0.2)
                    time.sleep(0.5)
                    pyautogui.click(clicks=2)
                    time.sleep(0.5)
                    pyautogui.hotkey('ctrl','c')
                    s1=str(clipboard.paste())
                    s1=s1.replace(',','')
                    pyautogui.moveTo(51, 752, duration=0.3-0.1)
                    pyautogui.click()
                    time.sleep(0.5)

                    #거래가 체결되었는지 출력
                    if t==t1 and s==s1:
                        trade_message1 = '회차: ' + iteration
                        trade_message0 = '포지션: ' + position
                        trade_message2 = '진입가: ' + entry
                        trade_message3 = '목표가: ' + target
                        trade_message4 = '손절가: ' + stop
                        trade_message = f'''
{trade_message1}
{trade_message0}
{trade_message2}
{trade_message3}
{trade_message4}
거래가 체결되었습니다'''
                        data = {'chat_id': notification_channel_id, 'text': trade_message}
                        res = requests.get(url, data=data)
                        if res.status_code == 200:
                            print(json.loads(res.text))
                        return
                        break
                    else:
                         #거래가 체결되었는지 출력
                        trade_message1 = '회차:'+ iteration
                        trade_message0 = '포지션: ' + position
                        trade_message2 = '진입가:'+ entry
                        trade_message3 = '목표가:'+ target
                        trade_message4 = '손절가:'+ stop
                        trade_message = f'''
{trade_message1}
{trade_message0}
{trade_message2}
{trade_message3}
{trade_message4}
거래가 미체결되었습니다. 다시 시도하겠습니다. 미체결되었으므로 확인 한번 해야 합니다'''
                        data = {'chat_id': notification_channel_id, 'text': trade_message}
                        res = requests.get(url, data=data)
                        if res.status_code == 200:
                            print(json.loads(res.text))
                        print('거래가 미체결되었습니다. 다시 시도하겠습니다.')
                    
                elif position == 'Short':
                    # 숏 포지션 작업(tp/sl, 목표가, 손절가, 숏 시작)
                    pyautogui.moveTo(1825, 645 - 39-40-15, duration=0.3-0.1)
                    pyautogui.click()
                    time.sleep(0.2)

                    pyautogui.moveTo(1740, 705 - 39-40-10, duration=0.3-0.1)
                    pyautogui.click()
                    pyautogui.typewrite(target)
                    time.sleep(0.2)

                    pyautogui.moveTo(1740, 800 - 39-40-10, duration=0.3-0.1)
                    pyautogui.click()
                    pyautogui.typewrite(stop)
                    time.sleep(0.2)

                    pyautogui.moveTo(1807, 860 - 39-40-10, duration=0.3-0.1)
                    pyautogui.click()
                    time.sleep(0.2)

                    # 숏 포지션 마지막 추가 작업(팝업창 클릭 2번하고 초기 상태로 되돌리기)
                    pyautogui.moveTo(1073, 358, duration=0.3-0.1)
                    pyautogui.click()
                    time.sleep(0.2)
                    pyautogui.moveTo(1825, 645 - 39-40-15, duration=0.3-0.1)
                    pyautogui.click()
                    time.sleep(0.2)

                    #목표가 손절가 확인해서 비교하기
                    t=target
                    s=stop
                    pyautogui.moveTo(364, 748, duration=0.3-0.1)
                    pyautogui.click()
                    time.sleep(0.5)
                    pyautogui.moveTo(1087, 879, duration=0.3-0.1)
                    pyautogui.click(clicks=2)
                    pyautogui.hotkey('ctrl','c')
                    time.sleep(0.5)
                    t1=str(clipboard.paste())
                    t1=t1.replace(',','')
                    pyautogui.moveTo(1087, 900, duration=0.2)
                    time.sleep(0.5)
                    pyautogui.click(clicks=2)
                    time.sleep(0.5)
                    pyautogui.hotkey('ctrl','c')
                    s1=str(clipboard.paste())
                    s1=s1.replace(',','')
                    pyautogui.moveTo(51, 752, duration=0.3-0.1)
                    pyautogui.click()
                    time.sleep(0.5)
                    
                    #거래가 체결되었는지 출력
                    if t==t1 and s==s1:
                        trade_message1 = '회차: ' + iteration
                        trade_message0 = '포지션: ' + position
                        trade_message2 = '진입가: ' + entry
                        trade_message3 = '목표가: ' + target
                        trade_message4 = '손절가: ' + stop
                        trade_message = f'''
{trade_message1}
{trade_message0}
{trade_message2}
{trade_message3}
{trade_message4}
거래가 체결되었습니다'''
                        data = {'chat_id': notification_channel_id, 'text': trade_message}
                        res = requests.get(url, data=data)
                        if res.status_code == 200:
                            print(json.loads(res.text))
                        print('거래가 체결되었습니다')
                        return
                        break
                    else:
                         #거래가 체결되었는지 출력
                        trade_message1 = '회차:'+ iteration
                        trade_message0 = '포지션: ' + position
                        trade_message2 = '진입가:'+ entry
                        trade_message3 = '목표가:'+ target
                        trade_message4 = '손절가:'+ stop
                        trade_message = f'''
{trade_message1}
{trade_message0}
{trade_message2}
{trade_message3}
{trade_message4}
거래가 미체결되었습니다. 다시 시도하겠습니다. 미체결되었으므로 확인 한번 해야 합니다'''
                        data = {'chat_id': notification_channel_id, 'text': trade_message}
                        res = requests.get(url, data=data)
                        if res.status_code == 200:
                            print(json.loads(res.text))
                        print('거래가 미체결되었습니다. 다시 시도하겠습니다.')
                else:
                    print("알 수 없는 포지션입니다.")
            else:
                print("회차, 포지션, 진입가, 목표가 또는 손절가를 찾을 수 없습니다.")
        elif action == '종료':
            if iteration and position and entry:
                #거래가 체결되었는지 출력
                        trade_message1 = '회차:'+ iteration
                        trade_message0 = '포지션: ' + position
                        trade_message2 = '진입가:'+ entry
                        trade_message = f'''
{trade_message1}
{trade_message0}
{trade_message2}
해당 회차에서의 수익을 실현하였습니다! 축하합니다!'''
                        return
                        break

# 클라이언트 시작 시 최신 메시지 처리
@client.on(events.NewMessage(chats=channel_id))
async def handler(event):
    asyncio.create_task(process_message(event.message))

async def main():
    await client.start()

    # 시작 시 최신 메시지 가져오기
    async for message in client.iter_messages(channel_id, limit=1):
        await process_message(message)

    print("실시간으로 메시지를 대기 중입니다...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
