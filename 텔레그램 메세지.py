import re
import asyncio
from telethon import TelegramClient, events
import pyautogui
import time

# 텔레그램 API 설정
api_id = ''          # 자신의 API ID로 교체
api_hash = ''      # 자신의 API Hash로 교체
channel_id = int('')  # 모니터링할 채널의 고유 ID로 교체

# 텔레그램 클라이언트 초기화
client = TelegramClient('session_name', api_id, api_hash)

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

# 메시지 처리 함수
async def process_message(message):
    iteration, target, stop, entry, position, action = extract_info(message.text)
    
    # '송출' 단어 감지
    if '송출' in message.text:
        print("송출 단어 감지됨. 지정된 좌표로 이동하여 클릭합니다.")
        
        # 마우스를 특정 좌표로 이동하고 클릭 (청산하기)
        pyautogui.moveTo(1213, 978 - 39, duration=0.3-0.1)  # 예시 좌표
        pyautogui.click()
        time.sleep(0.3-0.1)
        pyautogui.moveTo(1069, 686 - 39, duration=0.3-0.1)  # 예시 좌표
        pyautogui.click()
        time.sleep(0.3-0.1)
        return  # '송출' 처리 후 다른 작업을 하지 않도록 종료

    if action == '오픈':
        if iteration and target and stop and entry and position:
            print(f"{iteration}회차 포지션: {position}, 진입가: {entry}, 목표가: {target}, 손절가: {stop}")

            # 공통 작업: 거래 플랫폼 창 활성화 및 초기 클릭
            time.sleep(0.1)
            pyautogui.moveTo(1369, 530 - 39, duration=0.3-0.1)
            pyautogui.click()
            time.sleep(0.2)

            # 회차에 따라 다른 좌표로 이동 및 클릭
            if iteration == '1':
                pyautogui.moveTo(1653, 510 - 39, duration=0.3-0.1)
                pyautogui.click()
                time.sleep(0.2)
            elif iteration == '2':
                pyautogui.moveTo(1706, 510 - 39, duration=0.3-0.1) 
                pyautogui.click()
                time.sleep(0.2)
            elif iteration == '3':
                pyautogui.moveTo(1785, 510 - 39, duration=0.3-0.1)
                pyautogui.click()
                time.sleep(0.2)
            else:
                print(f"알 수 없는 회차: {iteration}")
                return  # 알 수 없는 회차일 경우 작업 중단

            if position == 'Long':
                # 롱 포지션 작업(tp/sl,목표가,손절가,롱 시작)
                pyautogui.moveTo(1624, 643 - 39, duration=0.3-0.1)
                pyautogui.click()
                time.sleep(0.2)

                pyautogui.moveTo(1740, 705 - 39, duration=0.3-0.1)
                pyautogui.click()
                pyautogui.typewrite(target)
                time.sleep(0.2)

                pyautogui.moveTo(1740, 800 - 39, duration=0.3-0.1)
                pyautogui.click()
                pyautogui.typewrite(stop)
                time.sleep(0.2)

                pyautogui.moveTo(1682, 865 - 39, duration=0.3-0.1)
                pyautogui.click()
                time.sleep(0.2)

                # 롱 포지션 마지막 추가 작업(파업창 2번클릭 후 초기상태로 되돌리기)
                pyautogui.moveTo(1073, 358, duration=0.3-0.1)
                pyautogui.click()
                time.sleep(0.2)
                pyautogui.moveTo(1624, 643 - 39, duration=0.3-0.1)
                pyautogui.click()
                time.sleep(0.2-0.1)

            elif position == 'Short':
                # 숏 포지션 작업(tp/sl,목표가,손절가,숏 시작)
                pyautogui.moveTo(1825, 645 - 39, duration=0.3-0.1)
                pyautogui.click()
                time.sleep(0.2)

                pyautogui.moveTo(1740, 705 - 39, duration=0.3-0.1)
                pyautogui.click()
                pyautogui.typewrite(target)
                time.sleep(0.2)

                pyautogui.moveTo(1740, 800 - 39, duration=0.3-0.1)
                pyautogui.click()
                pyautogui.typewrite(stop)
                time.sleep(0.2)

                pyautogui.moveTo(1807, 860 - 39, duration=0.3-0.1)
                pyautogui.click()
                time.sleep(0.2)

                # 숏 포지션 마지막 추가 작업(파업창 클릭 2번하고 초기상태로 되돌리기)
                pyautogui.moveTo(1073, 358, duration=0.3-0.1)
                pyautogui.click()
                time.sleep(0.2)
                pyautogui.moveTo(1825, 645 - 39, duration=0.3-0.1)
                pyautogui.click()
                time.sleep(0.2)
            else:
                print("알 수 없는 포지션입니다.")
        else:
            print("회차, 포지션, 진입가, 목표가 또는 손절가를 찾을 수 없습니다.")
    elif action == '종료':
        if iteration and position and entry:
            #청산 좌표 코드
            print(f"{iteration}회차 포지션 종료: {position}, 진입가: {entry}, 청산하세요.")
            

# 클라이언트 시작 시 최신 메시지 처리
@client.on(events.NewMessage(chats=channel_id))
async def handler(event):
    await process_message(event.message)

async def main():
    await client.start()

    # 시작 시 최신 메시지 가져오기
    async for message in client.iter_messages(channel_id, limit=1):
        await process_message(message)

    print("실시간으로 메시지를 대기 중입니다...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
