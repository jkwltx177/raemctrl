import math
import os
import random
import sys
import time
from datetime import datetime

import cv2 # 비디오 재생 기능 위해 추가
import numpy as np # 비디오 재생 기능 위해 추가
import pygame
import threading
import queue
import obsws_python as obs

import hashlib
import struct
import screeninfo
import socket
import json


import win32print
import win32ui
from PIL import Image, ImageDraw, ImageFont, ImageWin
import tempfile

# --- State Constants ---
STATE_LANGUAGE_SELECT = "LANGUAGE_SELECT"
STATE_NEW_TITLE = "NEW_TITLE"
STATE_INTRODUCTION_P1 = "INTRODUCTION_P1"
STATE_INTRODUCTION_P2 = "INTRODUCTION_P2"
# STATE_MAIN_MENU 제거됨
STATE_NAME_INPUT = "NAME_INPUT"
# --- Updated Psych Test Question States ---
STATE_PSYCH_TEST_Q1 = "PSYCH_TEST_Q1" # Openness 1
STATE_PSYCH_TEST_Q2 = "PSYCH_TEST_Q2" # Openness 2
STATE_PSYCH_TEST_Q3 = "PSYCH_TEST_Q3" # Conscientiousness 1
STATE_PSYCH_TEST_Q4 = "PSYCH_TEST_Q4" # Conscientiousness 2
STATE_PSYCH_TEST_Q5 = "PSYCH_TEST_Q5" # Extraversion 1
STATE_PSYCH_TEST_Q6 = "PSYCH_TEST_Q6" # Extraversion 2
STATE_PSYCH_TEST_Q7 = "PSYCH_TEST_Q7" # Agreeableness 1
STATE_PSYCH_TEST_Q8 = "PSYCH_TEST_Q8" # Agreeableness 2
STATE_PSYCH_TEST_Q9 = "PSYCH_TEST_Q9" # Neuroticism 1
# --- End Updated Psych Test Question States ---
STATE_SHOW_RESULT = "SHOW_RESULT"
STATE_PRE_FLOPPY_NOTICE = "PRE_FLOPPY_NOTICE"
STATE_FLOPPY_INSERT_GUIDE = "FLOPPY_INSERT_GUIDE"
STATE_FLOPPY_CHECK = "FLOPPY_CHECK"
STATE_WRONG_FLOPPY_ERROR = "WRONG_FLOPPY_ERROR"
STATE_VISUAL_ANALYSIS_SETUP = "VISUAL_ANALYSIS_SETUP"
STATE_VISUAL_ANALYSIS_DISPLAY = "VISUAL_ANALYSIS_DISPLAY"
STATE_COMPLETE_SCREEN = "COMPLETE_SCREEN"
#프린트
STATE_ART_FILM_NOTICE = "ART_FILM_NOTICE"
STATE_SETTINGS = "SETTINGS"
STATE_KEY_GUIDE = "KEY_GUIDE"

# --- Color Constants ---
COLOR_BLACK = (0, 0, 0)
COLOR_GREEN = (0, 255, 0) #200
COLOR_DARK_GREEN = (0, 150, 0) #100
COLOR_RED_AUTO_OFF = (200, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_GRAY = (128, 128, 128)
COLOR_LIGHT_GRAY = (200, 200, 200)
COLOR_FLOPPY_BODY = (70, 70, 70)
COLOR_FLOPPY_SHUTTER = (180, 180, 180)
COLOR_GLOW_GREEN = (0, 120, 0) # 은은한 효과를 위해 어두운 녹색 사용

# --- Font & Path Constants ---
FONT_DIR_NAME = 'fonts'
SOUND_DIR_NAME = 'sounds'
IMAGE_DIR_NAME = 'images'
SKETCH_DIR_NAME = 'sketches'
VIDEO_DIR_NAME = 'videos' # 비디오 디렉토리 경로 추가
SCREENSHOT_DIR_NAME = 'screenshots'

DEFAULT_ENG_FONT_NAME = 'VT323-Regular.ttf'
#DEFAULT_ENG_FONT_NAME = 'IBMPlexMono-Regular.ttf'
FALLBACK_ENG_FONTS = ['Fixedsys500c.ttf', 'cour.ttf', 'Courier New', 'monospace']
#DEFAULT_KO_FONT_NAME = 'DOSMyungjo.ttf'
#DEFAULT_KO_FONT_NAME = 'DungGeunMo.ttf'
#DEFAULT_KO_FONT_NAME = 'HBIOS-SYS-prop.ttf'
#DEFAULT_KO_FONT_NAME = 'neodgm.ttf'
#DEFAULT_KO_FONT_NAME = 'NeoDunggeunmoPro-Regular.ttf'
#DEFAULT_KO_FONT_NAME = 'IyagiGGC.ttf'
#DEFAULT_KO_FONT_NAME = 'Galmuri9.ttf'
#DEFAULT_KO_FONT_NAME = 'GalmuriMono9.ttf'
#DEFAULT_KO_FONT_NAME = 'GalmuriMono11.ttf'
#DEFAULT_KO_FONT_NAME = 'GalmuriMono7.ttf'
#DEFAULT_KO_FONT_NAME = 'ChosunSm.TTF'
#DEFAULT_KO_FONT_NAME = 'ChosunKm.TTF' #good
#DEFAULT_KO_FONT_NAME = 'RIDIBatang.otf'
DEFAULT_KO_FONT_NAME = 'KBIZ한마음명조 R.ttf' #good
FALLBACK_KO_FONTS = ['Malgun Gothic', 'Gulim', 'Dotum', 'sans-serif']

# --- Game Constants ---
ASPECT_RATIO = 4 / 3
CONTENT_BOX_PADDING_RATIO = 30
TYPING_SPEED_DEFAULT = 0.025
CURSOR_INTERVAL_DEFAULT = 0.4
AUTO_PROGRESS_DELAY_DEFAULT = 3.0 # 일반적인 자동 진행 시간
MAX_NAME_LENGTH = 20
MAX_ANSWER_LENGTH = 1 # Still 1 for '1' or '2'
NUM_TOP_KEYWORDS = 3 # Display top 3 traits if needed, can be adjusted

# # 영어 폰트 크기 (새로운 코드의 기준 유지)
# ENG_MAIN_FONT_SIZE = 72
# ENG_TINY_FONT_SIZE = int(ENG_MAIN_FONT_SIZE * 0.5)
# ENG_SMALL_FONT_SIZE = int(ENG_MAIN_FONT_SIZE * 0.75)
# ENG_LARGE_FONT_SIZE = int(ENG_MAIN_FONT_SIZE * 1.25)
# ENG_TITLE_FONT_SIZE = int(ENG_MAIN_FONT_SIZE * 2.2)

# # 한글 폰트 크기 (가독성을 위해 독립적 설정)
# KO_MAIN_FONT_SIZE = 60
# KO_TINY_FONT_SIZE = int(KO_MAIN_FONT_SIZE * 0.5)
# KO_SMALL_FONT_SIZE = int(KO_MAIN_FONT_SIZE * 0.75)
# KO_LARGE_FONT_SIZE = int(KO_MAIN_FONT_SIZE * 1.15)
# KO_TITLE_FONT_SIZE = int(KO_MAIN_FONT_SIZE * 2.0)

class DataLogger:
    def __init__(self, log_file="exhibition_data.log"):
        self.log_file = log_file
        
        # --- 네트워크 설정 ---
        self.server_host = '10.210.68.162' # ◀◀◀ [필수] 컴퓨터 2의 고정 IP 주소
        self.server_port = 51985          # ◀◀◀ 충돌 방지를 위해 높은 번호의 포트로 변경
        
        # --- 안정성 강화를 위한 내부 큐 ---
        self.network_queue = queue.Queue(maxsize=100) # 최대 100개 로그 임시 저장
        
        self.stop_event = threading.Event()

        # 파일 로깅 스레드 (기존과 동일)
        self.file_log_queue = queue.Queue()
        self.file_log_thread = threading.Thread(target=self._file_log_worker)
        self.file_log_thread.daemon = True
        self.file_log_thread.start()
        
        # 네트워크 전송 및 연결 관리를 전담하는 스레드
        self.network_thread = threading.Thread(target=self._network_manager)
        self.network_thread.daemon = True
        self.network_thread.start()

        self.session_counter = 0

    def _network_manager(self):
        """백그라운드에서 네트워크 연결, 재연결, 데이터 전송을 모두 처리"""
        client_socket = None
        last_retry_time = 0

        while not self.stop_event.is_set():
            # 1. 연결 시도 (연결이 안 된 경우)
            if client_socket is None:
                if time.time() - last_retry_time > 3.0: # 3초마다 재연결 시도
                    try:
                        print("Trying to connect to log server...")
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(2.0)
                        sock.connect((self.server_host, self.server_port))
                        sock.settimeout(None)
                        client_socket = sock
                        print(f"✅ Log server connected at {self.server_host}:{self.server_port}")
                    except Exception as e:
                        # print(f"⚠️ Connection failed: {e}") # 너무 자주 뜨면 지저분하므로 주석 처리 가능
                        client_socket = None
                    last_retry_time = time.time()
                
                # 연결 실패 시 잠시 대기
                if client_socket is None:
                    time.sleep(1)
                    continue

            # 2. 데이터 전송 (연결이 된 경우)
            try:
                # 큐에 쌓인 데이터가 있으면 전송
                log_lines = self.network_queue.get(timeout=1.0) # 1초간 데이터 기다림
                
                message = json.dumps(log_lines).encode('utf-8')
                msg_len_prefix = struct.pack('>I', len(message))
                client_socket.sendall(msg_len_prefix + message)
                
                self.network_queue.task_done() # 큐 작업 완료 표시

            except queue.Empty:
                # 큐가 비어있으면 그냥 루프 계속 (정상)
                continue
            except (socket.error, BrokenPipeError, ConnectionResetError) as e:
                print(f"🔴 Network error, attempting to reconnect: {e}")
                if client_socket:
                    client_socket.close()
                client_socket = None # 연결 끊김 상태로 전환하여 재연결 로직 타도록 함
            except Exception as e:
                print(f"An unexpected error occurred in network manager: {e}")
                time.sleep(1)

        if client_socket:
            client_socket.close()
        print("Network manager stopped.")

    def log_visitor_data(self, visitor_data):
        """메인 스레드에서 호출. 데이터를 큐에 넣기만 하고 바로 리턴 (빠름)"""
        self.session_counter += 1
        thread_data = self.generate_thread_data(visitor_data)

        # 화면 표시용 데이터 생성
        log_lines_for_display = []
        # (기존과 동일하게 log_lines_for_display 리스트를 채우는 코드)
        # ...
        log_lines_for_display.append(f"Thread {thread_data['thread_id']} name: {thread_data['thread_name']}")
        log_lines_for_display.append(f"Thread {thread_data['thread_id']}:")
        for i, mem_line in enumerate(thread_data['memory_dump']):
            comment = ""
            if i == 0: comment = f"// personality: {thread_data['personality_raw']}"
            elif i == 1: comment = f"// floppy_key: {thread_data['floppy_key']:03d}"
            elif i == 2: comment = f"// session_id: {self.session_counter:08x}"
            else: comment = f"// data_{i}"
            log_lines_for_display.append(f"{i}     {mem_line:<50} {comment}")
        log_lines_for_display.append(f"5     {'  '.join(thread_data['personality_hex']):<50} // trait_values")
        log_lines_for_display.append("")
        # ...

        # 생성된 데이터를 네트워크 큐에 넣음
        if not self.network_queue.full():
            self.network_queue.put(log_lines_for_display)
        else:
            print("⚠️ Network queue is full. Log data is being dropped.")

        # 파일 로깅 큐에도 넣음
        self.file_log_queue.put(thread_data)

    def generate_hex_data(self, data):
        base_addr = 0x01828a3000 + (self.session_counter * 0x1000)
        return f"0x{base_addr:012x}"

    def generate_thread_data(self, visitor_data):
        thread_id = self.session_counter % 3 + 1
        visitor_hash = hashlib.md5(f"{visitor_data['name']}{visitor_data['timestamp']}".encode()).hexdigest()
        memory_addresses = []
        for i in range(5, 9):
            addr = f"0x{random.randint(0x01000000, 0x7fffffff):08x}"
            offset = f"0x{random.randint(0x1000, 0xffff):04x}"
            value = f"0x{random.randint(0x00, 0xff):02x}"
            memory_addresses.append(f"{addr} {offset} + {value}")
        personality_hex = []
        for trait, value in [('O', visitor_data['O']), ('C', visitor_data['C']), 
                           ('E', visitor_data['E']), ('A', visitor_data['A']), 
                           ('N', visitor_data['N'])]:
            hex_val = f"0x{ord(trait):02x}{value:02x}"
            personality_hex.append(hex_val)
        thread_data = {
            "thread_id": thread_id,
            "thread_name": f"visitor_{visitor_hash[:8]}_{visitor_data['name']}",
            "personality_raw": f"O{visitor_data['O']}-C{visitor_data['C']}-E{visitor_data['E']}-A{visitor_data['A']}-N{visitor_data['N']}",
            "personality_hex": personality_hex,
            "floppy_key": visitor_data['floppy_key'],
            "memory_dump": memory_addresses,
            "timestamp": visitor_data['timestamp']
        }
        return thread_data

    def _file_log_worker(self):
        while not self.stop_event.is_set():
            try:
                data = self.file_log_queue.get(timeout=1.0)
                if data is None: break
                
                log_lines = []
                # ... (파일에 저장할 로그 라인 생성하는 기존 코드)
                log_lines.append(f"Thread {data['thread_id']} name: {data['thread_name']}")
                log_lines.append(f"Thread {data['thread_id']}:")
                for i, mem_line in enumerate(data['memory_dump']):
                    if i == 0: comment = f"// personality: {data['personality_raw']}"
                    elif i == 1: comment = f"// floppy_key: {data['floppy_key']:03d}"
                    elif i == 2: comment = f"// session_id: {self.session_counter:08x}"
                    else: comment = f"// data_{i}"
                    log_lines.append(f"{i}     {mem_line:<50} {comment}")
                log_lines.append(f"5     {'  '.join(data['personality_hex']):<50} // trait_values")
                log_lines.append("")
                # ...

                with open(self.log_file, 'a', encoding='utf-8') as f:
                    for line in log_lines:
                        f.write(line + '\n')
                self.file_log_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"File logging error: {e}")

    def stop(self):
        """모든 스레드를 안전하게 종료"""
        print("Stopping all logger threads...")
        self.stop_event.set()
        self.file_log_queue.put(None) # 파일 로거 스레드 종료 신호
        # 네트워크 큐는 더 이상 넣지 않으면 스레드가 자연스럽게 종료됨
        self.network_thread.join(timeout=1)
        self.file_log_thread.join(timeout=1)

class VideoPlayer:
    """동영상 재생을 위한 헬퍼 클래스"""

    def __init__(self, video_paths, target_width, target_height, video_scales=None):
        if isinstance(video_paths, str):
            video_paths = [video_paths]
        
        self.video_paths = video_paths
        self.video_scales = video_scales or [1.0] * len(video_paths)
        self.current_video_index = 0
        self.cap = cv2.VideoCapture(self.video_paths[self.current_video_index])
        
        self.base_target_width = target_width
        self.base_target_height = target_height
        
        current_scale = self.video_scales[self.current_video_index]
        self.target_width = int(target_width * current_scale)
        self.target_height = int(target_height * current_scale)
        
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_delay = 1000 / self.fps if self.fps > 0 else 33
        self.last_frame_time = 0
        self.last_valid_frame = None
        # 프레임 캐시 추가
        self.frame_cache = None
        self.cache_time = 0
        #self.skip_frames = False  # 프레임 스킵 플래그
        #self.frame_skip_counter = 0

    def get_current_video_index(self):
        """현재 재생 중인 비디오의 인덱스를 반환"""
        return self.current_video_index
    
    def get_current_video_scale(self):
        """현재 재생 중인 비디오의 스케일을 반환"""
        return self.video_scales[self.current_video_index]

    def get_frame(self, current_time_ms):
        """현재 시간에 맞는 프레임을 반환"""
        # # 프레임 스킵 로직 추가
        # if hasattr(self, 'skip_frames') and self.skip_frames:
        #     if not hasattr(self, 'frame_skip_counter'):
        #         self.frame_skip_counter = 0
        #     self.frame_skip_counter += 1
        #     if self.frame_skip_counter % 2 == 0:  # 2프레임당 1프레임만 처리
        #         return self.last_valid_frame if hasattr(self, 'last_valid_frame') else None
        # 같은 프레임 시간대면 캐시된 프레임 반환
        if self.frame_cache and abs(current_time_ms - self.cache_time) < self.frame_delay:
            return self.frame_cache
            
        if current_time_ms - self.last_frame_time >= self.frame_delay:
            self.last_frame_time = current_time_ms
            ret, frame = self.cap.read()
            
            if not ret:
                self.current_video_index = (self.current_video_index + 1) % len(self.video_paths)
                self.cap.release()
                self.cap = cv2.VideoCapture(self.video_paths[self.current_video_index])
                
                current_scale = self.video_scales[self.current_video_index]
                self.target_width = int(self.base_target_width * current_scale)
                self.target_height = int(self.base_target_height * current_scale)
                
                self.fps = self.cap.get(cv2.CAP_PROP_FPS)
                self.frame_delay = 1000 / self.fps if self.fps > 0 else 33
                ret, frame = self.cap.read()

            if ret:
                frame = cv2.convertScaleAbs(frame, alpha=1.0, beta=0)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # INTER_NEAREST로 변경하여 리사이즈 속도 향상
                frame = cv2.resize(frame, (self.target_width, self.target_height), 
                                 interpolation=cv2.INTER_NEAREST)
                frame = frame.swapaxes(0, 1)
                frame = pygame.surfarray.make_surface(frame)
                self.last_valid_frame = frame
                self.frame_cache = frame
                self.cache_time = current_time_ms
        return self.last_valid_frame

    def close(self):
        if self.cap:
            self.cap.release()
            
class ThermalPrinterController:
    def __init__(self, printer_name="Xprinter XP-DT108B LABEL"):
        self.printer_name = printer_name
        self.is_connected = False
        
        # Windows 프린터 확인
        try:
            printers = [printer[2] for printer in win32print.EnumPrinters(2)]
            if self.printer_name in printers:
                self.is_connected = True
                print(f"✅ Printer '{self.printer_name}' found in Windows")
            else:
                print(f"⚠️ Printer '{self.printer_name}' not found. Available printers:")
                for p in printers:
                    print(f"  - {p}")
        except Exception as e:
            print(f"⚠️ Error checking printers: {e}")

    def _draw_pil_radar_chart(self, draw, data_dict, labels_ordered_keys, chart_center_x, chart_center_y, size, color='black'):
        num_vars = len(labels_ordered_keys)
        max_val_on_chart = 2
        if num_vars == 0: return

        angle_step = 2 * math.pi / num_vars
        
        try:
            font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'KBIZ한마음명조 R.ttf')
            font = ImageFont.truetype(font_path, 30)
        except IOError:
            font = ImageFont.load_default()

        dark_gray = (100, 100, 100)
        for score_level in [0.5, 1, 1.5, 2]:
            # 전체 크기(size)를 최대 점수(max_val_on_chart) 기준으로 계산합니다.
            radius = size * (score_level / float(max_val_on_chart))
            points = []
            for j in range(num_vars):
                angle = j * angle_step - math.pi / 2
                points.append((chart_center_x + radius * math.cos(angle), chart_center_y + radius * math.sin(angle)))
            
            line_width = 3
            draw.polygon(points, outline=dark_gray, width=line_width)

        for i, trait_key in enumerate(labels_ordered_keys):
            angle = i * angle_step - math.pi / 2
            end_x = chart_center_x + size * math.cos(angle)
            end_y = chart_center_y + size * math.sin(angle)
            draw.line([(chart_center_x, chart_center_y), (end_x, end_y)], fill=dark_gray, width=5)
            
            trait_korean = {
                'Openness': '개방성',
                'Conscientiousness': '성실성', 
                'Extraversion': '외향성',
                'Agreeableness': '우호성',
                'Neuroticism': '신경성'
            }
            label_text = trait_korean.get(trait_key, trait_key)

            lx = chart_center_x + (size + 40) * math.cos(angle)
            ly = chart_center_y + (size + 40) * math.sin(angle)
            bbox = draw.textbbox((0, 0), label_text, font=font)
            lw, lh = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text((lx - lw / 2, ly - lh / 2), label_text, fill=color, font=font)

        points = []
        for i, trait_key in enumerate(labels_ordered_keys):
            angle = i * angle_step - math.pi / 2
            value = data_dict.get(trait_key, 0)
            norm_val = min(value / float(max_val_on_chart), 1.0) * size
            points.append((chart_center_x + norm_val * math.cos(angle), chart_center_y + norm_val * math.sin(angle)))

        # if len(points) > 2:
        #     # 1. 먼저 외곽선 그리기
        #     draw.polygon(points, outline=color, width=4)

        #     # 2. 폴리곤 영역의 경계 구하기
        #     x_coords = [p[0] for p in points]
        #     y_coords = [p[1] for p in points]
        #     min_x, max_x = min(x_coords), max(x_coords)
        #     min_y, max_y = min(y_coords), max(y_coords)

        #     # 3. 점이 폴리곤 내부에 있는지 확인하는 함수
        #     def point_in_polygon(x, y, poly_points):
        #         n = len(poly_points)
        #         inside = False
        #         p1x, p1y = poly_points[0]
        #         for i in range(1, n + 1):
        #             p2x, p2y = poly_points[i % n]
        #             if y > min(p1y, p2y):
        #                 if y <= max(p1y, p2y):
        #                     if x <= max(p1x, p2x):
        #                         if p1y != p2y:
        #                             xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
        #                         if p1x == p2x or x <= xinters:
        #                             inside = not inside
        #             p1x, p1y = p2x, p2y
        #         return inside
    
        #     # 4. 해칭 패턴 그리기 (대각선)
        #     spacing = 10  # 선 간격
        #     for offset in range(int(min_x - max_y), int(max_x - min_y), spacing):
        #         # 대각선 시작점과 끝점 계산
        #         line_points = []
        #         for x in range(int(min_x), int(max_x) + 1):
        #             y = x - offset
        #             if min_y <= y <= max_y and point_in_polygon(x, y, points):
        #                 line_points.append((x, y))

        #         # 연속된 점들을 선으로 연결
        #         if len(line_points) > 1:
        #             draw.line(line_points, fill=(180, 180, 180), width=1)
        # if len(points) > 2:
        #     # 1단계: 먼저 채우기만
        #     draw.polygon(points, fill=(100, 100, 100))
        #     # 2단계: 그 다음 외곽선만
        #     draw.polygon(points, outline=color, width=6)
        if len(points) > 2:
            draw.polygon(points, fill='black')
            center_point = (chart_center_x, chart_center_y)
            trait_keys = list(labels_ordered_keys)
            for i in range(num_vars):
                # 이전(왼쪽)과 다음(오른쪽) 인덱스를 순환 구조로 계산합니다.
                prev_index = (i - 1 + num_vars) % num_vars
                next_index = (i + 1) % num_vars

                # 현재, 이전, 다음 점수의 값을 가져옵니다.
                current_score = data_dict.get(trait_keys[i], 0)
                prev_score = data_dict.get(trait_keys[prev_index], 0)
                next_score = data_dict.get(trait_keys[next_index], 0)

                # 조건: 현재 점수는 0보다 크고, 양옆 점수는 모두 0일 때
                if current_score > 0 and prev_score == 0 and next_score == 0:
                    # 중심점에서 해당 데이터 포인트까지 두꺼운 선을 긋습니다.
                    target_point = points[i]
                    draw.line([center_point, target_point], fill='black', width=12) # 선 두께는 8로 설정

    def create_label_image(self, visitor_data):
        width_px = int((10 / 2.54) * 203)
        height_px = int((15 / 2.54) * 203)
        
        margin_left = 80
        margin_right = 80
        margin_top = 60
        margin_bottom = 60
        
        content_width = width_px - margin_left - margin_right
        
        base_path = os.path.dirname(__file__)
        try:
            title_font_path = os.path.join(base_path, 'fonts', 'VT323-Regular.ttf')
            body_font_path = os.path.join(base_path, 'fonts', 'KBIZ한마음명조 R.ttf')
            
            font_title = ImageFont.truetype(title_font_path, 70)
            # 요청사항 반영: 폰트 크기를 30pt로 변경
            font_unified = ImageFont.truetype(body_font_path, 30) 
            
        except IOError:
            font_title = ImageFont.load_default()
            font_unified = ImageFont.load_default()
            
        label_image = Image.new('RGB', (width_px, height_px), 'white')
        draw = ImageDraw.Draw(label_image)
        
        current_y = margin_top

        # 1. 제목
        title_text = "RAEMCTRL ANALYSIS"
        bbox = draw.textbbox((0, 0), title_text, font=font_title)
        title_w = bbox[2] - bbox[0]
        draw.text(((width_px - title_w) / 2, current_y), title_text, fill='black', font=font_title)
        current_y += (bbox[3] - bbox[1]) + 25
        
        draw.line([(margin_left, current_y), (width_px - margin_right, current_y)], fill='black', width=3)
        current_y += 35

        # 요청사항 반영: 행간(줄 간격)을 줄여서 텍스트가 모여 보이도록 수정 (e.g., 50 -> 40)
        line_spacing = 40 

        # 2. 검사자 정보
        draw.text((margin_left, current_y), f"SUBJECT: {visitor_data['name']}", fill='black', font=font_unified)
        current_y += line_spacing
        draw.text((margin_left, current_y), f"TIMESTAMP: {visitor_data['timestamp']}", fill='black', font=font_unified)
        current_y += line_spacing

        # 3. 성격 유형 코드
        personality_raw = f"O{visitor_data['O']}-C{visitor_data['C']}-E{visitor_data['E']}-A{visitor_data['A']}-N{visitor_data['N']}"
        draw.text((margin_left, current_y), f"RESULT CODE: {personality_raw}", fill='black', font=font_unified)
        current_y += line_spacing
        draw.text((margin_left, current_y), f"FLOPPY KEY: {visitor_data['floppy_key']:03d}", fill='black', font=font_unified)
        current_y += line_spacing
        
        # 4. 성격 원형 (Archetype) 키워드
        archetype_text = "ARCHETYPE:"
        if visitor_data['keywords']:
            archetype_text += f" {visitor_data['keywords'][0]}"
        draw.text((margin_left, current_y), archetype_text, fill='black', font=font_unified)
        current_y += 60 # 텍스트 블록과 그래프 사이 간격

        # 5. 방사형 그래프 (하단에 출력)
        chart_size = min(content_width, 450) # 차트 크기를 약간 키움
        chart_x = width_px / 2
        remaining_height = height_px - current_y - margin_bottom
        chart_y = current_y + remaining_height / 2
        
        radar_data = {
            'Openness': visitor_data['O'], 'Conscientiousness': visitor_data['C'],
            'Extraversion': visitor_data['E'], 'Agreeableness': visitor_data['A'],
            'Neuroticism': visitor_data['N']
        }
        self._draw_pil_radar_chart(draw, radar_data, list(radar_data.keys()), chart_x, chart_y, chart_size/2)
        
        # 6. 하단 구분선과 C) NATJAM 추가 (새로 추가할 부분)
        # 그래프 아래 여백 계산
        bottom_line_y = height_px - margin_bottom - 50  # 하단에서 50픽셀 위
        draw.line([(margin_left, bottom_line_y), (width_px - margin_right, bottom_line_y)], fill='black', width=3)
        
        # C) NATJAM 텍스트 추가
        natjam_text = "C) NATJAM"
        bbox = draw.textbbox((0, 0), natjam_text, font=font_unified)
        natjam_w = bbox[2] - bbox[0]
        draw.text(((width_px - natjam_w) / 2, bottom_line_y + 15), natjam_text, fill='black', font=font_unified)
        
        return label_image

    def print_psychology_results(self, visitor_data):
        if not self.is_connected:
            print("Cannot print, printer is not connected.")
            return

        print("Generating label image for printing...")
        
        try:
            label_image = self.create_label_image(visitor_data)
            
            temp_file = tempfile.mktemp('.bmp')
            label_image.save(temp_file, 'BMP')
            
            hDC = win32ui.CreateDC()
            hDC.CreatePrinterDC(self.printer_name)
            
            printer_width = hDC.GetDeviceCaps(110)
            printer_height = hDC.GetDeviceCaps(111)
            
            hDC.StartDoc('Psychology Test Results')
            hDC.StartPage()
            
            dib = ImageWin.Dib(label_image)
            
            dib.draw(hDC.GetHandleOutput(), (0, 0, printer_width, printer_height))
            
            hDC.EndPage()
            hDC.EndDoc()
            hDC.DeleteDC()
            
            os.unlink(temp_file)
            
            print("✅ Label printed successfully.")
            
        except Exception as e:
            print(f"⚠️ An error occurred during printing: {e}")
            import traceback
            traceback.print_exc()

class PsychologyTest:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.TYPING_SOUND_CHANNEL_ID = 0
        # --- 아래 부분을 통째로 붙여넣어 주세요 ---

        # 기준 해상도 (개발 시 사용한 해상도) - 이 값은 그대로 둡니다.
        self.BASE_RESOLUTION = (1600, 900)
        
        # 자동 해상도 감지 대신, 전시용 해상도를 직접 지정합니다.
        self.screen_width = 800
        self.screen_height = 600
        
        # 이제 scale_factor가 올바르게 계산됩니다.
        # (800/2560)과 (600/1440) 중 작은 값이 선택됩니다.
        self.scale_factor = min(
            self.screen_width / self.BASE_RESOLUTION[0],
            self.screen_height / self.BASE_RESOLUTION[1]
        )
        
       
        
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height),
                                              pygame.FULLSCREEN | pygame.DOUBLEBUF)

        self._calculate_content_box()
        self.debug_draw_content_box_border = True

        self.colors = {
            "black": COLOR_BLACK, "green": COLOR_GREEN, "dark_green": COLOR_DARK_GREEN,
            "red_auto_off": COLOR_RED_AUTO_OFF, "white": COLOR_WHITE, "gray": COLOR_GRAY,
            "light_gray": COLOR_LIGHT_GRAY,
            "floppy_body": COLOR_FLOPPY_BODY, "floppy_shutter": COLOR_FLOPPY_SHUTTER,
            "glow_green": COLOR_GLOW_GREEN
        }
        self.glow_enabled = True
        self.glow_offsets = [(x, y) for x in [-3, 0, 3] for y in [-3, 0, 3] if x != 0 or y != 0]
        self.script_dir = os.path.dirname(__file__)

        self.language = "KO" # 기본 언어
        # --- Updated Trait Keys ---
        self.all_traits_keys = ["Openness", "Conscientiousness", "Extraversion", "Agreeableness", "Neuroticism"]
        # --- End Updated Trait Keys ---
        self._init_texts() # Must be before _init_psych_questions_data
        self._init_personality_mapping()  # 추가
        self._init_floppy_keywords()
        self._init_psych_questions_data()


        self.font_dir_abs_path = os.path.join(self.script_dir, FONT_DIR_NAME)
        self.eng_font_path = self._find_font(DEFAULT_ENG_FONT_NAME, FALLBACK_ENG_FONTS, self.font_dir_abs_path)
        self.ko_font_path = self._find_font(DEFAULT_KO_FONT_NAME, FALLBACK_KO_FONTS, self.font_dir_abs_path)
        self.fallback_font_path = self._find_font('Arial', ['Segoe UI Symbol', 'Arial Unicode MS', 'DejaVu Sans', 'Malgun Gothic', 'sans-serif'], None)

        self._load_actual_fonts()

        self._load_sounds()
        self.loaded_sketches = self._load_all_sketches()
        self.current_sketch_image = None

        self.video_players = {}
        self._load_videos()

        self.screenshot_dir = os.path.join(self.script_dir, SCREENSHOT_DIR_NAME)
        os.makedirs(self.screenshot_dir, exist_ok=True)

        self.game_state = STATE_INTRODUCTION_P1
        self.previous_game_state_for_settings = STATE_INTRODUCTION_P1
        self.running = True
        self.clock = pygame.time.Clock()

        self.current_text_key = ""
        self.current_text_args = {}
        self.current_text = ""
        self.displayed_text = ""
        self.typing_index = 0
        self.typing_speed = TYPING_SPEED_DEFAULT
        self.typing_timer = 0
        self.show_cursor = True
        self.cursor_timer = 0
        self.cursor_interval = CURSOR_INTERVAL_DEFAULT
        self.user_input_active = False
        self.user_input_text = ""
        self.input_max_length = MAX_ANSWER_LENGTH
        self.needs_space_to_progress = False
        self.delay_timer = 0
        self.delay_duration = AUTO_PROGRESS_DELAY_DEFAULT

        self.floppy_anim_y_offset = 0
        self.floppy_anim_dir = 1
        self.floppy_anim_speed = 25
        self.floppy_anim_range = 6

        self.user_name = ""
        self.psych_test_answers = []
        self.psych_test_results = {trait: 0 for trait in self.all_traits_keys}
        self.current_question_index = 0
        self.current_settings_selection = 0

        self.scanline_visible_rows, self.scanline_gap_rows = 2, 1

        self.sound_enabled = True
        self.auto_mode_active = False
        self.last_activity_time = time.time()
        self.history_stack = []

        pygame.display.set_caption(self.get_text("window_title"))
        self.set_state(STATE_INTRODUCTION_P1, record_history=False)

        self.ime_composition_text = ""
        self.ime_composition_cursor = 0
        self.visual_display_prompt_timer = 0
        self.visual_display_prompt_visible = False

        # 플로피 관련 변수
        self.floppy_progress_timer = 0
        self.floppy_progress_started = False
        self.floppy_drive_path = "A:\\"
        self.floppy_detected = False
        self.floppy_data = []  # [(filename, content), ...]
        self.floppy_videos = []  # 로드된 VideoPlayer 인스턴스들
        self.current_floppy_video_index = 0
        # self.floppy_check_timer = 0
        # self.floppy_check_interval = 1  # 1초마다 체크
        # 플로피 체크용 스레드 통신
        self.floppy_check_queue = queue.Queue()
        self.floppy_check_thread = None
        self.floppy_check_running = False
        self.skip_frames = False  # 프레임 스킵 플래그
        self.frame_skip_counter = 0
        # OBS 설정 추가
        self.obs_enabled = True  # OBS 연동 기능 활성화 여부
        self.obs_host = "localhost"
        self.obs_port = 4455
        self.obs_password = "qazwsx123"
        self.obs_client = None
        # 플로피 내용과 OBS 장면 매핑
        self.floppy_to_scene_mapping = {
                "00000001": "장면 1",
                "00000002": "장면 2",
                "00000003": "장면 3",
                "00000004": "장면 4",
                "00000005": "장면 5",
                "00000006": "장면 6",
                "00000007": "장면 7",
                "00000008": "장면 8",
                "00000009": "장면 9",
                "00000010": "장면 10",
                "00000011": "장면 11",
                "00000012": "장면 12",
                "00000013": "장면 13",
                "00000014": "장면 14",
                "00000015": "장면 15",
                "00000016": "장면 16",
                "00000017": "장면 17",
                "00000018": "장면 18",
                "00000019": "장면 19",
                "00000020": "장면 20",
                "00000021": "장면 21",
                "00000022": "장면 22",
                "00000023": "장면 23",
                "00000024": "장면 24",
                "00000025": "장면 25",
                "00000026": "장면 26",
                "00000027": "장면 27",
                "00000028": "장면 28",
                "00000029": "장면 29",
                "00000030": "장면 30",
                "00000031": "장면 31",
                "00000032": "장면 32",
                "00000033": "장면 33",
                "00000034": "장면 34",
                "00000035": "장면 35",
                "00000036": "장면 36",
                "00000037": "장면 37",
                "00000038": "장면 38",
                "00000039": "장면 39",
                "00000040": "장면 40",
                "00000041": "장면 41",
                "00000042": "장면 42",
                "00000043": "장면 43",
                "00000044": "장면 44",
                "00000045": "장면 45",
                "00000046": "장면 46",
                "00000047": "장면 47",
                "00000048": "장면 48",
                "00000049": "장면 49",
                "00000050": "장면 50",
                "00000051": "장면 51",
                "00000052": "장면 52",
                "00000053": "장면 53",
                "00000054": "장면 54",
                "00000055": "장면 55",
                "00000056": "장면 56",
                "00000057": "장면 57",
                "00000058": "장면 58",
                "00000059": "장면 59",
                "00000060": "장면 60",
                "00000061": "장면 61",
                "00000062": "장면 62",
                "00000063": "장면 63",
                "00000064": "장면 64",
                "00000065": "장면 65",
                "00000066": "장면 66",
                "00000067": "장면 67",
                "00000068": "장면 68",
                "00000069": "장면 69",
                "00000070": "장면 70",
                "00000071": "장면 71",
                "00000072": "장면 72",
                "00000073": "장면 73",
                "00000074": "장면 74",
                "00000075": "장면 75",
                "00000076": "장면 76",
                "00000077": "장면 77",
                "00000078": "장면 78",
                "00000079": "장면 79",
                "00000080": "장면 80",
                "00000081": "장면 81",
                "00000082": "장면 82",
                "00000083": "장면 83",
                "00000084": "장면 84",
                "00000085": "장면 85",
                "00000086": "장면 86",
                "00000087": "장면 87",
                "00000088": "장면 88",
                "00000089": "장면 89",
                "00000090": "장면 90",
                "00000091": "장면 91",
                "00000092": "장면 92",
                "00000093": "장면 93",
                "00000094": "장면 94",
                "00000095": "장면 95",
                "00000096": "장면 96",
                "00000097": "장면 97",
                "00000098": "장면 98",
                "00000099": "장면 99",
                "00000100": "장면 100",
                "00000101": "장면 101",
                "00000102": "장면 102",
                "00000103": "장면 103",
                "00000104": "장면 104",
                "00000105": "장면 105",
                "00000106": "장면 106",
                "00000107": "장면 107",
                "00000108": "장면 108",
                "00000109": "장면 109",
                "00000110": "장면 110",
                "00000111": "장면 111",
                "00000112": "장면 112",
                "00000113": "장면 113",
                "00000114": "장면 114",
                "00000115": "장면 115",
                "00000116": "장면 116",
                "00000117": "장면 117",
                "00000118": "장면 118",
                "00000119": "장면 119",
                "00000120": "장면 120",
                "00000121": "장면 121",
                "00000122": "장면 122",
                "00000123": "장면 123",
                "00000124": "장면 124",
                "00000125": "장면 125",
                "00000126": "장면 126",
                "00000127": "장면 127",
                "00000128": "장면 128",
                "00000129": "장면 129",
                "00000130": "장면 130",
                "00000131": "장면 131",
                "00000132": "장면 132",
                "00000133": "장면 133",
                "00000134": "장면 134",
                "00000135": "장면 135",
                "00000136": "장면 136",
                "00000137": "장면 137",
                "00000138": "장면 138",
                "00000139": "장면 139",
                "00000140": "장면 140",
                "00000141": "장면 141",
                "00000142": "장면 142",
                "00000143": "장면 143",
                "00000144": "장면 144",
                "00000145": "장면 145",
                "00000146": "장면 146",
                "00000147": "장면 147",
                "00000148": "장면 148",
                "00000149": "장면 149",
                "00000150": "장면 150",
                "00000151": "장면 151",
                "00000152": "장면 152",
                "00000153": "장면 153",
                "00000154": "장면 154",
                "00000155": "장면 155",
                "00000156": "장면 156",
                "00000157": "장면 157",
                "00000158": "장면 158",
                "00000159": "장면 159",
                "00000160": "장면 160",
                "00000161": "장면 161",
                "00000162": "장면 162",
            }
        self.data_logger = DataLogger()
        self.printer_controller = ThermalPrinterController(printer_name="Xprinter XP-DT108B LABEL")
        # OBS 연결 시도
        self._connect_to_obs()
        
    def _connect_to_obs(self):
        """OBS WebSocket에 연결"""
        if not self.obs_enabled:
            return

        try:
            self.obs_client = obs.ReqClient(
                host=self.obs_host,
                port=self.obs_port,
                password=self.obs_password
            )
            print("✅ OBS WebSocket 연결 성공")

            # 사용 가능한 장면 목록 확인
            scene_info = self.obs_client.get_scene_list()
            scenes = [s.get("sceneName", "") for s in scene_info.scenes]
            print(f"사용 가능한 OBS 장면: {scenes}")

        except Exception as e:
            print(f"⚠️ OBS 연결 실패: {e}")
            self.obs_client = None
            self.obs_enabled = False

    def switch_obs_scene_by_floppy(self, floppy_content):
        """플로피 내용에 따라 OBS 장면 전환"""
        if not self.obs_enabled or not self.obs_client:
            return

        # 동적 장면 이름 생성 (예: "장면_00000001")
        # 또는 사전 정의된 매핑 사용
        scene_name = self.floppy_to_scene_mapping.get(floppy_content)

        # 매핑이 없으면 동적으로 생성
        if not scene_name:
            # 예: "00000001" -> "장면 1"
            try:
                scene_number = int(floppy_content)
                scene_name = f"장면 {scene_number}"
            except ValueError:
                print(f"⚠️ 잘못된 플로피 내용: {floppy_content}")
                return

        try:
            self.obs_client.set_current_program_scene(scene_name)
            print(f"✅ OBS 장면 전환: {scene_name}")
        except Exception as e:
            print(f"⚠️ OBS 장면 전환 실패: {e}")

    def check_floppy_disk_threaded(self):
        """별도 스레드에서 플로피 디스크 체크"""
        while self.floppy_check_running:
            try:
                if os.path.exists(self.floppy_drive_path):
                    files = os.listdir(self.floppy_drive_path)
                    txt_files = [f for f in files if f.lower().endswith('.txt')]
                    
                    if txt_files:
                        floppy_data = []
                        for filename in sorted(txt_files):
                            filepath = os.path.join(self.floppy_drive_path, filename)
                            try:
                                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read().strip()
                                    floppy_data.append((filename, content))
                            except Exception as e:
                                print(f"Error reading {filename}: {e}")
                        
                        # 결과를 큐에 넣기
                        self.floppy_check_queue.put(('found', floppy_data))
                    else:
                        self.floppy_check_queue.put(('empty', None))
                else:
                    self.floppy_check_queue.put(('not_found', None))
            except Exception as e:
                print(f"Floppy check thread error: {e}")
                self.floppy_check_queue.put(('error', None))
            
            # 체크 간격
            time.sleep(1.0)

    def check_floppy_disk(self):
        """플로피 디스크 존재 여부 확인 및 데이터 읽기"""
        try:
            if os.path.exists(self.floppy_drive_path):
                files = os.listdir(self.floppy_drive_path)
                txt_files = [f for f in files if f.lower().endswith('.txt')]

                if txt_files:
                    self.floppy_data = []
                    for filename in sorted(txt_files):  # 파일명 순서대로 정렬
                        filepath = os.path.join(self.floppy_drive_path, filename)
                        try:
                            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read().strip()
                                self.floppy_data.append((filename, content))
                                print(f"Read from floppy: [{filename}] -> {content}")
                        except Exception as e:
                            print(f"Error reading {filename}: {e}")

                    return True
            return False
        except Exception as e:
            print(f"Floppy check error: {e}")
            return False
            
    def load_floppy_videos(self):
        """플로피 데이터를 기반으로 MP4 동영상 로드"""
        self.floppy_videos = []  # VideoPlayer 인스턴스들을 저장할 리스트
        video_dir = os.path.join(self.script_dir, VIDEO_DIR_NAME)

        for filename, content in self.floppy_data:
            # content가 숫자라고 가정 (예: "00000001")
            mp4_filename = f"{content}.mp4"
            mp4_path = os.path.join(video_dir, mp4_filename)

            if os.path.exists(mp4_path):
                try:
                    # 각 비디오에 대해 VideoPlayer 인스턴스 생성
                    video_player = VideoPlayer(
                        mp4_path, 
                        self.content_box_width, 
                        self.content_box_height
                        #[1.0]  # 스케일 추가
                    )
                    self.floppy_videos.append(video_player)
                    print(f"Loaded video: {mp4_filename}")
                except Exception as e:
                    print(f"Error loading {mp4_filename}: {e}")
            else:
                print(f"Video not found: {mp4_filename}")

        # 현재 재생 중인 비디오 인덱스 초기화
        self.current_floppy_video_index = 0

    def create_multilingual_surface(self, text, size_type, color):
        if not text:
            font = self.get_current_font(size_type)
            return pygame.Surface((0, font.get_height()), pygame.SRCALPHA)

        char_surfaces = []
        total_width = 0
        max_height = 0

        for char in text:
            font = self.get_font_for_char(char, size_type)
            char_surf = font.render(char, True, color)
            char_surfaces.append(char_surf)
            total_width += char_surf.get_width()
            if char_surf.get_height() > max_height:
                max_height = char_surf.get_height()

        final_surface = pygame.Surface((total_width, max_height), pygame.SRCALPHA)
        current_x = 0
        for surf in char_surfaces:
            final_surface.blit(surf, (current_x, (max_height - surf.get_height()) // 2))
            current_x += surf.get_width()

        return final_surface
    
    def _load_videos(self):
        video_dir = os.path.join(self.script_dir, VIDEO_DIR_NAME)
        if not os.path.exists(video_dir):
            os.makedirs(video_dir)
            print(f"Created video directory: {video_dir}")
            return

        # 플로피 가이드용 비디오 시퀀스 (001.mp4, 002.mp4, 003.mp4)
        floppy_video_paths = []
        floppy_video_scales = []  # 각 비디오별 스케일 설정

        for i in range(1, 4):
            video_path = os.path.join(video_dir, f"{i:03d}.mp4")
            if os.path.exists(video_path):
                floppy_video_paths.append(video_path)

                # 001.mp4, 002.mp4는 0.6 스케일, 003.mp4는 0.8 스케일
                if i in [1, 2]:  # 001.mp4, 002.mp4
                    floppy_video_scales.append(0.7)  # 70% 크기
                else:  # 003.mp4
                    floppy_video_scales.append(0.8)  # 80% 크기

        if floppy_video_paths:
            # 기본 크기는 content_box 크기로 설정
            base_video_width = self.content_box_width
            base_video_height = self.content_box_height
            self.video_players['floppy'] = VideoPlayer(floppy_video_paths, base_video_width, base_video_height, floppy_video_scales)
            # 프레임 스킵 활성화
            # self.video_players['floppy'].skip_frames = True
        else:
            print(f"Warning: Floppy insert videos not found in {video_dir}")

        # 분석용 비디오 (기존 크기 유지)
        analysis_video_path = os.path.join(video_dir, "analysis.mp4")
        if os.path.exists(analysis_video_path):
            # 4:3 화면에 꽉 차게
            video_width = self.content_box_width
            video_height = self.content_box_height
            self.video_players['analysis'] = VideoPlayer(analysis_video_path, video_width, video_height)
        else:
            print(f"Warning: Analysis video not found at {analysis_video_path}")

    def _load_actual_fonts(self):
        # 이 메서드 안에서 모든 폰트 크기 계산과 로딩을 처리합니다.

        # 1. 기준 폰트 크기를 여기에 정의합니다.
        BASE_ENG_SIZES = {"normal": 72, "small": 54, "tiny": 36, "large": 90, "title": 158}
        BASE_KO_SIZES = {"normal": 60, "small": 45, "tiny": 30, "large": 69, "title": 120}

        # 2. scale_factor를 이용해 현재 해상도에 맞는 실제 크기(딕셔너리)를 계산합니다.
        #    max() 함수로 최소 크기를 보장합니다.
        eng_sizes = {
            size_type: max(12, int(base_size * self.scale_factor))
            for size_type, base_size in BASE_ENG_SIZES.items()
        }
        ko_sizes = {
            size_type: max(10, int(base_size * self.scale_factor))
            for size_type, base_size in BASE_KO_SIZES.items()
        }

        # --- 디버깅용 출력 (문제가 해결되면 이 print문들은 삭제해도 됩니다) ---
        print("--- Font Scaling Debug ---")
        print(f"Screen: {self.screen_width}x{self.screen_height}")
        print(f"Scale Factor: {self.scale_factor:.4f}")
        print(f"Calculated KO Font Sizes: {ko_sizes}")
        print("--------------------------")

        # 3. 계산된 크기로 폰트 객체를 생성합니다.
        self.fonts_en = {
            size_type: pygame.font.Font(self.eng_font_path, size)
            for size_type, size in eng_sizes.items()
        }

        ko_font_path_to_use = self.ko_font_path if self.ko_font_path else self.eng_font_path
        self.fonts_ko = {
            size_type: pygame.font.Font(ko_font_path_to_use, size)
            for size_type, size in ko_sizes.items()
        }

        fallback_path_to_use = self.fallback_font_path if self.fallback_font_path else self.eng_font_path
        self.fonts_fallback = {
            size_type: pygame.font.Font(fallback_path_to_use, size)
            for size_type, size in ko_sizes.items() # Fallback은 한글 크기 기준을 따름
        }

    def get_current_font(self, size_type="normal"):
        font_dict = self.fonts_ko if self.language == "KO" else self.fonts_en
        return font_dict.get(size_type, font_dict["normal"])

    def get_font_for_char(self, char, size_type="normal"):
        # 1. '←' 문자인지 먼저 확인하여 폴백 폰트를 반환합니다.
        if char == '←' and hasattr(self, 'fonts_fallback'):
            return self.fonts_fallback.get(size_type, self.fonts_fallback["normal"])

        # 2. 한글인지 확인합니다.
        is_hangul_char = ('\uAC00' <= char <= '\uD7A3') or \
                         ('\u1100' <= char <= '\u11FF') or \
                         ('\u3130' <= char <= '\u318F')
        if is_hangul_char:
            return self.fonts_ko.get(size_type, self.fonts_ko["normal"])

        # 3. 그 외에는 기본 영어 폰트를 반환합니다.
        return self.fonts_en.get(size_type, self.fonts_en["normal"])


    def get_unified_line_height(self, size_type="normal"):
        current_font = self.get_current_font(size_type)
        return current_font.get_linesize()

    def _calculate_content_box(self):
        self.screen_width, self.screen_height = pygame.display.get_surface().get_size()
        self.content_box_width = int(self.screen_height * ASPECT_RATIO)
        self.content_box_height = self.screen_height

        if self.content_box_width > self.screen_width:
            self.content_box_width = self.screen_width
            self.content_box_height = int(self.screen_width / ASPECT_RATIO)

        self.content_box_x = (self.screen_width - self.content_box_width) // 2
        self.content_box_y = (self.screen_height - self.content_box_height) // 2
        print(
            f"Screen: {self.screen_width}x{self.screen_height}, "
            f"Content Box: {self.content_box_width}x{self.content_box_height} "
            f"at ({self.content_box_x},{self.content_box_y})"
        )

    def _init_texts(self):
        self.texts = {
            "EN": {
                "window_title": "RAEMCTRL Psychology Test - 1958",
                "new_title_team": "(C) NATJAM", "new_title_main": "RAEMCTRL", "new_title_version": "v_5.1",
                "new_title_loading": "Please Wait...", "new_title_copy_year": "1958\n1628",
                "intro_header": "RAEMCTRL",
                "intro_p1_body": "[RESEARCH INSTITUTE INTRODUCTION]\n\nWelcome to the NATJAM.\nOur facility is dedicated to the \nunderstanding of the human mind\nthrough rigorous scientific methodologies\nand advanced analytical techniques.\nWe strive for breakthroughs in cognitive science.",
                "intro_p2_body": "[PROJECT INTRODUCTION: RAEMCTRL]\n\nThe RAEMCTRL project utilizes \na series of psychological evaluations\nto construct a detailed cognitive profile\nof the subject.\nYour responses will be analyzed to understand various facets of your personality\nand decision-making processes.\nAll data is handled with utmost confidentiality.",
                "press_space_continue": "PRESS SPACE BAR TO CONTINUE",
                "press_any_key_close": "PRESS ANY KEY TO CLOSE",
                "name_input_title": "SUBJECT IDENTIFICATION", "name_input_prompt": "Please enter your full name:",
                "name_input_confidential": "All data will be kept confidential in accordance\nwith Institute protocols (1985-B7).",
                "name_input_enter_prompt": "Press ENTER to input your name",
                "psych_q_header": "QUESTION {current}/{total}:",
                # --- Updated Psych Test Prompt ---
                "psych_input_prompt": "YOUR SELECTION (1 / 2): ",
                # --- End Updated Psych Test Prompt ---
                "psych_result_header": "PSYCHOLOGICAL PROFILE: {name}", "your_keywords_header": "DOMINANT TRAITS:",
                "pre_floppy_notice_text": "Based on your psychological analysis,\nnow loading the Doctor's research data\nthat matches your subconsciousness.",
                "floppy_insert_guide_header": "DATA ARCHIVAL",
                "floppy_insert_guide_main_text": "Get records recognized on computer.",
                "floppy_insert_instruction": "Insert Disk and Press SPACE",
                "floppy_accessing": "ACCESSING FLOPPY DISK...\n\nVALIDATING MEDIA...",
                "visual_setup": "LOADING VISUAL STIMULUS...", "visual_display_header": "VISUAL INTERPRETATION ANALYSIS.\n\nOBSERVE THE FOLLOWING IMAGE:",
                "complete_screen_text": "ANALYSIS COMPLETE: {name}.\n\nTHANK YOU.\n\nSYSTEM RESETTING...",
                "art_film_notice_header": "SESSION CONCLUDED.\n\nNOW PRESENTING:\n'REFLECTIONS ON THE DIGITAL MIND'\n\n(AUTO-RESET IMMINENT)",
                "settings_title": "ENVIRONMENT CONFIGURATION", "settings_language": "LANGUAGE: ", "settings_sound": "SOUND: ",
                "settings_key_guide": "VIEW KEY GUIDE", "settings_back_to_game": "RETURN TO PREVIOUS", "settings_nav_hint": "(USE ARROW KEYS AND ENTER)",
                "lang_en": "ENGLISH", "lang_ko": "KOREAN", "sound_on": "[ON]", "sound_off": "[OFF]",
                "key_guide_title": "KEY ASSIGNMENTS", "key_f1_settings": "F1   - SYSTEM CONFIGURATION",
                "key_f9_auto": "F9   - TOGGLE AUTO-ADVANCE MODE", "key_f10_screenshot": "F10  - CAPTURE SCREEN IMAGE",
                "key_b_back": "← (Left Arrow) - RETURN TO PREVIOUS SCREEN (IF APPLICABLE)", "key_esc_exit": "ESC  - TERMINATE SESSION",
                "auto_on_label": "AUTO ON", "auto_off_label": "AUTO OFF", "image_missing": "Image Missing",
                "screenshot_saved": "Screenshot saved!", "error_sound_text": "!",
                "select_language_title": "SELECT LANGUAGE",
                "select_language_guide": "USE UP/DOWN ARROWS TO SELECT, PRESS ENTER TO CONFIRM",

                # --- New Trait Texts (EN) ---
                "trait_openness": "Openness",
                "trait_conscientiousness": "Conscientiousness",
                "trait_extraversion": "Extraversion",
                "trait_agreeableness": "Agreeableness",
                "trait_neuroticism": "Neuroticism",
                # --- End New Trait Texts (EN) ---

                # --- New Question Texts (EN) ---
                "q_yes": "1. YES",
                "q_no": "2. NO",

                "q1_opn": "I seek out topics that others seldom explore on my own.",
                "q2_opn": "I enjoy reading abstract works such as art criticism or philosophical texts.",
                "q3_con": "I make plans to finish tasks well before their deadlines.",
                "q4_con": "I check my progress periodically when working on assignments.",
                "q5_ext": "I initiate conversations with people I don’t know.",
                "q6_ext": "I feel energized when I’m in a group of people.",
                "q7_agr": "During conversations, I pay close attention to others’ facial expressions and body language.",
                "q8_agr": "Even when I disagree, I try to understand why someone thinks the way they do.",
                "q9_neu": "I find it difficult to calm myself when something unexpected happens.",
                # --- End New Question Texts (EN) ---
                "press_b_to_go_back": "Press ←(Left Arrow) to return to the previous screen",
                "number_input_enter_prompt": "Enter the number and press ENTER",
                "wrong_floppy_error": "Incorrect disk inserted.\nPlease remove the disk.",
            },
            "KO": {
                "window_title": "RAEMCTRL 심리 검사 - 1958",
                "new_title_team": "C) NATJAM", "new_title_main": "RAEMCTRL", "new_title_version": "v_5.1",
                "new_title_loading": "Please Wait...", "new_title_copy_year": "1958\n1628",
                "intro_header": "RAEMCTRL",
                "intro_p1_body": "[연구 배경]\n\n1950년대 영국의 한 괴짜 박사의 연구소...\n괴짜 박사 카펠하우드는 비밀리에\n무의식 연구를 시작한다.\n그는 오랜 연구 끝에 인간의 무의식을 바탕으로\n성격을 분류하는 데 성공했지만,\n의문의 사건으로 인해 연구를 세상에 밝히지 못하고\n한순간에 자취를 감춰버렸다...",
                "intro_p2_body": "[PROJECT: RAEMCTRL]\n\n수십 년의 시간이 흐른 뒤,\nC)NATJAM이 카펠하우드 박사의\n연구 일지를 발견하였고\n세상에 알리기로 결심한다.\n\n마침내 BIG5 성격 모델과 HTP 투사 검사를 결합해\n시각화 장치를 개발하였다.",
                "press_space_continue": "계속하려면 스페이스 바를 누르십시오",
                "press_any_key_close": "돌아가려면 아무 키나 누르십시오",
                "name_input_title": "피험자 식별", "name_input_prompt": "성함을 입력해 주십시오:",
                "name_input_confidential": "모든 데이터는 연구소 규약(1985-B7)에 따라\n기밀로 유지됩니다.",
                "name_input_enter_prompt": "이름을 입력하고 ENTER를 누르십시오",
                "psych_q_header": "질문 {current}/{total}:",
                # --- Updated Psych Test Prompt (KO) ---
                "psych_input_prompt": "선택 (1 / 2): ",
                # --- End Updated Psych Test Prompt (KO) ---
                "psych_result_header": "심리 분석 프로필: {name}", "your_keywords_header": "주요 성향:",
                # "pre_floppy_notice_text": "심리 검사 결과를 기반으로\n\n당신의 무의식과 일치하는\n\n박사의 연구 데이터가 보여집니다.",
                "pre_floppy_notice_text": "당신의 심리 검사 결과는\n총 162가지 성격 유형 중 하나와 매칭되며,\n해당 유형의 무의식 데이터를 기반으로\n박사의 연구 데이터를 불러옵니다.",
                "floppy_insert_guide_header": "플로피 디스크 삽입",
                "floppy_insert_guide_main_text": "컴퓨터에 기록을 인식시키십시오.",
                "floppy_insert_instruction": "디스크를 삽입하세요",
                "floppy_accessing": "플로피 디스크 접근 중...\n\n미디어 확인 중...",
                "visual_setup": "분석 시각화 로딩 중...", "visual_display_header": "HTP 분석.\n\n다음 이미지를 관찰하십시오:",
                "complete_screen_text": "분석 완료: {name}.\n\n감사합니다.\n\n시스템 재시작 중...",
                "art_film_notice_header": "세션 종료됨.\n\n\n\n(자동 재시작 예정)",
                "settings_title": "환경 설정", "settings_language": "언어: ", "settings_sound": "사운드: ",
                "settings_key_guide": "키 안내 보기", "settings_back_to_game": "이전으로 돌아가기",
                "settings_nav_hint": "(화살표 키와 ENTER 사용)", "lang_en": "영어", "lang_ko": "한국어",
                "sound_on": "[ON]", "sound_off": "[OFF]", "key_guide_title": "키 설명",
                "key_f1_settings": "F1   - 시스템 설정",
                "key_f9_auto": "F9   - 자동 진행 모드 전환",
                "key_f10_screenshot": "F10  - 화면 캡처", "key_b_back": "← (왼쪽 화살표) - 이전 화면으로 (해당 시)",
                "key_esc_exit": "ESC  - 세션 종료", "auto_on_label": "자동 ON", "auto_off_label": "자동 OFF",
                "image_missing": "이미지 없음", "screenshot_saved": "스크린샷 저장됨!", "error_sound_text": "!",
                "select_language_title": "언어 선택",
                "select_language_guide": "위/아래 화살표 키로 선택, ENTER로 확정",

                # --- New Trait Texts (KO) ---
                "trait_openness": "개방성",
                "trait_conscientiousness": "성실성",
                "trait_extraversion": "외향성",
                "trait_agreeableness": "우호성",
                "trait_neuroticism": "신경성",
                # --- End New Trait Texts (KO) ---

                # --- New Question Texts (KO) ---
                "q_yes": "1. 예",
                "q_no": "2. 아니오",

                "q1_opn": "나는 다른 사람이 잘 다루지 않는 주제에 흥미를 느껴 스스로 찾아본다.",
                "q2_opn": "나는 예술 작품이나 철학적인 글처럼 추상적인 내용을 즐겨 읽는다.",
                "q3_con": "나는 맡은 일을 마감 기한 이전에 끝내기 위해 계획을 세운다.",
                "q4_con": "나는 과제를 할 때, 중간중간 진행 상황을 점검한다.",
                "q5_ext": "나는 모르는 사람에게 먼저 말을 걸어본다.",
                "q6_ext": "나는 여러 사람이 모인 자리에서 활기를 느낀다.",
                "q7_agr": "나는 대화 중 상대의 언어가 아닌 표정, 몸짓 신호를 잘 알아차린다.",
                "q8_agr": "대화 중 내가 동의하지 않는 의견이라도, 그 사람이 왜 그렇게 생각했는지 이해하려고 한다.",
                "q9_neu": "나는 예상치 못한 일이 생기면 마음을 가라앉히기 어렵다.",
                # --- End New Question Texts (KO) ---
                "press_b_to_go_back": "←(왼쪽 화살표) 키를 눌러 이전 화면으로 돌아갑니다",
                "number_input_enter_prompt": "숫자를 입력하고 ENTER를 누르십시오",
                "wrong_floppy_error": "다른 플로피 디스크를 삽입하였습니다.\n\n플로피 디스크를 제거해주세요.",
            }
        }
    def _init_personality_mapping(self):
        """성격 유형과 플로피 번호 매핑"""
        self.personality_to_floppy = {}

        mappings = [
            ("O0-C0-E0-A0-N0", "001"),
            ("O0-C0-E0-A0-N1", "002"),
            ("O0-C0-E0-A1-N0", "003"),
            ("O0-C0-E0-A1-N1", "004"),
            ("O0-C0-E0-A2-N0", "005"),
            ("O0-C0-E0-A2-N1", "006"),
            ("O0-C0-E1-A0-N0", "007"),
            ("O0-C0-E1-A0-N1", "008"),
            ("O0-C0-E1-A1-N0", "009"),
            ("O0-C0-E1-A1-N1", "010"),
            ("O0-C0-E1-A2-N0", "011"),
            ("O0-C0-E1-A2-N1", "012"),
            ("O0-C0-E2-A0-N0", "013"),
            ("O0-C0-E2-A0-N1", "014"),
            ("O0-C0-E2-A1-N0", "015"),
            ("O0-C0-E2-A1-N1", "016"),
            ("O0-C0-E2-A2-N0", "017"),
            ("O0-C0-E2-A2-N1", "018"),
            ("O0-C1-E0-A0-N0", "019"),
            ("O0-C1-E0-A0-N1", "020"),
            ("O0-C1-E0-A1-N0", "021"),
            ("O0-C1-E0-A1-N1", "022"),
            ("O0-C1-E0-A2-N0", "023"),
            ("O0-C1-E0-A2-N1", "024"),
            ("O0-C1-E1-A0-N0", "025"),
            ("O0-C1-E1-A0-N1", "026"),
            ("O0-C1-E1-A1-N0", "027"),
            ("O0-C1-E1-A1-N1", "028"),
            ("O0-C1-E1-A2-N0", "029"),
            ("O0-C1-E1-A2-N1", "030"),
            ("O0-C1-E2-A0-N0", "031"),
            ("O0-C1-E2-A0-N1", "032"),
            ("O0-C1-E2-A1-N0", "033"),
            ("O0-C1-E2-A1-N1", "034"),
            ("O0-C1-E2-A2-N0", "035"),
            ("O0-C1-E2-A2-N1", "036"),
            ("O0-C2-E0-A0-N0", "037"),
            ("O0-C2-E0-A0-N1", "038"),
            ("O0-C2-E0-A1-N0", "039"),
            ("O0-C2-E0-A1-N1", "040"),
            ("O0-C2-E0-A2-N0", "041"),
            ("O0-C2-E0-A2-N1", "042"),
            ("O0-C2-E1-A0-N0", "043"),
            ("O0-C2-E1-A0-N1", "044"),
            ("O0-C2-E1-A1-N0", "045"),
            ("O0-C2-E1-A1-N1", "046"),
            ("O0-C2-E1-A2-N0", "047"),
            ("O0-C2-E1-A2-N1", "048"),
            ("O0-C2-E2-A0-N0", "049"),
            ("O0-C2-E2-A0-N1", "050"),
            ("O0-C2-E2-A1-N0", "051"),
            ("O0-C2-E2-A1-N1", "052"),
            ("O0-C2-E2-A2-N0", "053"),
            ("O0-C2-E2-A2-N1", "054"),
            ("O1-C0-E0-A0-N0", "055"),
            ("O1-C0-E0-A0-N1", "056"),
            ("O1-C0-E0-A1-N0", "057"),
            ("O1-C0-E0-A1-N1", "058"),
            ("O1-C0-E0-A2-N0", "059"),
            ("O1-C0-E0-A2-N1", "060"),
            ("O1-C0-E1-A0-N0", "061"),
            ("O1-C0-E1-A0-N1", "062"),
            ("O1-C0-E1-A1-N0", "063"),
            ("O1-C0-E1-A1-N1", "064"),
            ("O1-C0-E1-A2-N0", "065"),
            ("O1-C0-E1-A2-N1", "066"),
            ("O1-C0-E2-A0-N0", "067"),
            ("O1-C0-E2-A0-N1", "068"),
            ("O1-C0-E2-A1-N0", "069"),
            ("O1-C0-E2-A1-N1", "070"),
            ("O1-C0-E2-A2-N0", "071"),
            ("O1-C0-E2-A2-N1", "072"),
            ("O1-C1-E0-A0-N0", "073"),
            ("O1-C1-E0-A0-N1", "074"),
            ("O1-C1-E0-A1-N0", "075"),
            ("O1-C1-E0-A1-N1", "076"),
            ("O1-C1-E0-A2-N0", "077"),
            ("O1-C1-E0-A2-N1", "078"),
            ("O1-C1-E1-A0-N0", "079"),
            ("O1-C1-E1-A0-N1", "080"),
            ("O1-C1-E1-A1-N0", "081"),
            ("O1-C1-E1-A1-N1", "082"),
            ("O1-C1-E1-A2-N0", "083"),
            ("O1-C1-E1-A2-N1", "084"),
            ("O1-C1-E2-A0-N0", "085"),
            ("O1-C1-E2-A0-N1", "086"),
            ("O1-C1-E2-A1-N0", "087"),
            ("O1-C1-E2-A1-N1", "088"),
            ("O1-C1-E2-A2-N0", "089"),
            ("O1-C1-E2-A2-N1", "090"),
            ("O1-C2-E0-A0-N0", "091"),
            ("O1-C2-E0-A0-N1", "092"),
            ("O1-C2-E0-A1-N0", "093"),
            ("O1-C2-E0-A1-N1", "094"),
            ("O1-C2-E0-A2-N0", "095"),
            ("O1-C2-E0-A2-N1", "096"),
            ("O1-C2-E1-A0-N0", "097"),
            ("O1-C2-E1-A0-N1", "098"),
            ("O1-C2-E1-A1-N0", "099"),
            ("O1-C2-E1-A1-N1", "100"),
            ("O1-C2-E1-A2-N0", "101"),
            ("O1-C2-E1-A2-N1", "102"),
            ("O1-C2-E2-A0-N0", "103"),
            ("O1-C2-E2-A0-N1", "104"),
            ("O1-C2-E2-A1-N0", "105"),
            ("O1-C2-E2-A1-N1", "106"),
            ("O1-C2-E2-A2-N0", "107"),
            ("O1-C2-E2-A2-N1", "108"),
            ("O2-C0-E0-A0-N0", "109"),
            ("O2-C0-E0-A0-N1", "110"),
            ("O2-C0-E0-A1-N0", "111"),
            ("O2-C0-E0-A1-N1", "112"),
            ("O2-C0-E0-A2-N0", "113"),
            ("O2-C0-E0-A2-N1", "114"),
            ("O2-C0-E1-A0-N0", "115"),
            ("O2-C0-E1-A0-N1", "116"),
            ("O2-C0-E1-A1-N0", "117"),
            ("O2-C0-E1-A1-N1", "118"),
            ("O2-C0-E1-A2-N0", "119"),
            ("O2-C0-E1-A2-N1", "120"),
            ("O2-C0-E2-A0-N0", "121"),
            ("O2-C0-E2-A0-N1", "122"),
            ("O2-C0-E2-A1-N0", "123"),
            ("O2-C0-E2-A1-N1", "124"),
            ("O2-C0-E2-A2-N0", "125"),
            ("O2-C0-E2-A2-N1", "126"),
            ("O2-C1-E0-A0-N0", "127"),
            ("O2-C1-E0-A0-N1", "128"),
            ("O2-C1-E0-A1-N0", "129"),
            ("O2-C1-E0-A1-N1", "130"),
            ("O2-C1-E0-A2-N0", "131"),
            ("O2-C1-E0-A2-N1", "132"),
            ("O2-C1-E1-A0-N0", "133"),
            ("O2-C1-E1-A0-N1", "134"),
            ("O2-C1-E1-A1-N0", "135"),
            ("O2-C1-E1-A1-N1", "136"),
            ("O2-C1-E1-A2-N0", "137"),
            ("O2-C1-E1-A2-N1", "138"),
            ("O2-C1-E2-A0-N0", "139"),
            ("O2-C1-E2-A0-N1", "140"),
            ("O2-C1-E2-A1-N0", "141"),
            ("O2-C1-E2-A1-N1", "142"),
            ("O2-C1-E2-A2-N0", "143"),
            ("O2-C1-E2-A2-N1", "144"),
            ("O2-C2-E0-A0-N0", "145"),
            ("O2-C2-E0-A0-N1", "146"),
            ("O2-C2-E0-A1-N0", "147"),
            ("O2-C2-E0-A1-N1", "148"),
            ("O2-C2-E0-A2-N0", "149"),
            ("O2-C2-E0-A2-N1", "150"),
            ("O2-C2-E1-A0-N0", "151"),
            ("O2-C2-E1-A0-N1", "152"),
            ("O2-C2-E1-A1-N0", "153"),
            ("O2-C2-E1-A1-N1", "154"),
            ("O2-C2-E1-A2-N0", "155"),
            ("O2-C2-E1-A2-N1", "156"),
            ("O2-C2-E2-A0-N0", "157"),
            ("O2-C2-E2-A0-N1", "158"),
            ("O2-C2-E2-A1-N0", "159"),
            ("O2-C2-E2-A1-N1", "160"),
            ("O2-C2-E2-A2-N0", "161"),
            ("O2-C2-E2-A2-N1", "162")
        ]

        for personality, floppy_num in mappings:
            self.personality_to_floppy[personality] = floppy_num

    def _init_floppy_keywords(self):
        """162개 플로피 번호에 대응하는 성격 원형 키워드를 초기화합니다."""
        self.floppy_keywords = [
            "조용한 탐험가", "차분한 중재자", "불안한 전략가", "낙천적인 실행자", "섬세한 분석가", "깊이 있는 조력자", 
            "따뜻한 설계자", "유쾌한 관찰자", "진지한 기획자", "엄격한 질문가", "적극적인 지휘자", "명랑한 힘", 
            "신중한 공감가", "도전적인 소통가", "냉철한 모험가", "열정적인 방랑자", "강직한 이방인", "기민한 안내자", 
            "내향적인 연결자", "에너지 넘치는 조정자", "단단한 지지자", "겸손한 균형자", "명료한 탐험가", "민감한 중재자", 
            "자신감 있는 전략가", "이성적인 실행자", "공감하는 분석가", "성실한 조력자", "감성적인 설계자", "직관적인 관찰자", 
            "조용한 기획자", "차분한 질문가", "불안한 지휘자", "낙천적인 힘", "섬세한 공감가", "깊이 있는 소통가", 
            "따뜻한 모험가", "긴장된 완벽주의자", "진지한 이방인", "엄격한 안내자", "적극적인 연결자", "명랑한 조정자", 
            "신중한 지지자", "도전적인 균형자", "냉철한 탐험가", "열정적인 중재자", "강직한 전략가", "기민한 실행자", 
            "내향적인 분석가", "에너지 넘치는 조력자", "단단한 설계자", "겸손한 관찰자", "명료한 기획자", "민감한 질문가", 
            "자신감 있는 지휘자", "이성적인 힘", "공감하는 공감가", "성실한 소통가", "감성적인 모험가", "직관적인 방랑자", 
            "조용한 이방인", "차분한 안내자", "불안한 연결자", "낙천적인 조정자", "섬세한 지지자", "깊이 있는 균형자", 
            "따뜻한 탐험가", "유쾌한 중재자", "진지한 전략가", "엄격한 실행자", "적극적인 분석가", "명랑한 조력자", 
            "신중한 설계자", "도전적인 관찰자", "냉철한 기획자", "열정적인 질문가", "강직한 지휘자", "기민한 힘의 보유자", 
            "내향적인 공감가", "에너지 넘치는 소통가", "단단한 모험가", "겸손한 방랑자", "명료한 이방인", "민감한 안내자", 
            "자신감 있는 연결자", "이성적인 조정자", "공감하는 지지자", "성실한 균형자", "감성적인 탐험가", "직관적인 중재자", 
            "조용한 전략가", "차분한 실행자", "불안한 분석가", "낙천적인 조력자", "섬세한 설계자", "깊이 있는 관찰자", 
            "따뜻한 기획자", "유쾌한 질문가", "진지한 지휘자", "엄격한 힘의 보유자", "적극적인 공감가", "명랑한 소통가", 
            "신중한 모험가", "도전적인 방랑자", "냉철한 이방인", "열정적인 안내자", "강직한 연결자", "기민한 조정자", 
            "내향적인 지지자", "에너지 넘치는 균형자", "단단한 탐험가", "겸손한 중재자", "명료한 전략가", "민감한 실행자", 
            "자신감 있는 분석가", "이성적인 조력자", "공감하는 설계자", "성실한 관찰자", "감성적인 기획자", "직관적인 질문가", 
            "조용한 지휘자", "차분한 힘의 보유자", "불안한 공감가", "낙천적인 소통가", "섬세한 모험가", "깊이 있는 방랑자", 
            "따뜻한 이방인", "유쾌한 안내자", "진지한 연결자", "엄격한 조정자", "적극적인 지지자", "명랑한 균형자", 
            "신중한 탐험가", "도전적인 중재자", "냉철한 전략가", "열정적인 실행자", "강직한 분석가", "기민한 조력자", 
            "내향적인 설계자", "에너지 넘치는 관찰자", "단단한 기획자", "겸손한 질문가", "명료한 지휘자", "민감한 힘의 보유자", 
            "자신감 있는 공감가", "이성적인 소통가", "공감하는 모험가", "성실한 방랑자", "감성적인 이방인", "직관적인 안내자", 
            "조용한 연결자", "차분한 조정자", "불안한 지지자", "낙천적인 균형자", "섬세한 탐험가", "깊이 있는 중재자", 
            "따뜻한 전략가", "유쾌한 실행자", "진지한 분석가", "엄격한 조력자", "적극적인 설계자", "명랑한 관찰자"
        ]
    
    def get_floppy_number(self):
        """심리검사 결과에 따른 플로피 번호 반환"""
        o = self.psych_test_results.get("Openness", 0)
        c = self.psych_test_results.get("Conscientiousness", 0)
        e = self.psych_test_results.get("Extraversion", 0)
        a = self.psych_test_results.get("Agreeableness", 0)
        n = self.psych_test_results.get("Neuroticism", 0)

        personality_key = f"O{o}-C{c}-E{e}-A{a}-N{n}"
        return self.personality_to_floppy.get(personality_key, "001")
    
    def _init_psych_questions_data(self):
        # --- Updated Psychological Questions Data ---
        self.psych_questions_data_template = [
            # 1. Openness Q1
            {"id": STATE_PSYCH_TEST_Q1, "question_key_stem": "q1_opn",
             "option_key_stems": ["q_yes", "q_no"], # Yes, No
             "result_mapping": {"1": {"Openness": 1}, "2": {}}, # "1" for Yes, "2" for No
             "next_state": STATE_PSYCH_TEST_Q2},
            # 2. Openness Q2
            {"id": STATE_PSYCH_TEST_Q2, "question_key_stem": "q2_opn",
             "option_key_stems": ["q_yes", "q_no"],
             "result_mapping": {"1": {"Openness": 1}, "2": {}},
             "next_state": STATE_PSYCH_TEST_Q3},
            # 3. Conscientiousness Q1
            {"id": STATE_PSYCH_TEST_Q3, "question_key_stem": "q3_con",
             "option_key_stems": ["q_yes", "q_no"],
             "result_mapping": {"1": {"Conscientiousness": 1}, "2": {}},
             "next_state": STATE_PSYCH_TEST_Q4},
            # 4. Conscientiousness Q2
            {"id": STATE_PSYCH_TEST_Q4, "question_key_stem": "q4_con",
             "option_key_stems": ["q_yes", "q_no"],
             "result_mapping": {"1": {"Conscientiousness": 1}, "2": {}},
             "next_state": STATE_PSYCH_TEST_Q5},
            # 5. Extraversion Q1
            {"id": STATE_PSYCH_TEST_Q5, "question_key_stem": "q5_ext",
             "option_key_stems": ["q_yes", "q_no"],
             "result_mapping": {"1": {"Extraversion": 1}, "2": {}},
             "next_state": STATE_PSYCH_TEST_Q6},
            # 6. Extraversion Q2
            {"id": STATE_PSYCH_TEST_Q6, "question_key_stem": "q6_ext",
             "option_key_stems": ["q_yes", "q_no"],
             "result_mapping": {"1": {"Extraversion": 1}, "2": {}},
             "next_state": STATE_PSYCH_TEST_Q7},
            # 7. Agreeableness Q1
            {"id": STATE_PSYCH_TEST_Q7, "question_key_stem": "q7_agr",
             "option_key_stems": ["q_yes", "q_no"],
             "result_mapping": {"1": {"Agreeableness": 1}, "2": {}},
             "next_state": STATE_PSYCH_TEST_Q8},
            # 8. Agreeableness Q2
            {"id": STATE_PSYCH_TEST_Q8, "question_key_stem": "q8_agr",
             "option_key_stems": ["q_yes", "q_no"],
             "result_mapping": {"1": {"Agreeableness": 1}, "2": {}},
             "next_state": STATE_PSYCH_TEST_Q9},
            # 9. Neuroticism Q1
            {"id": STATE_PSYCH_TEST_Q9, "question_key_stem": "q9_neu",
             "option_key_stems": ["q_yes", "q_no"],
             "result_mapping": {"1": {"Neuroticism": 1}, "2": {}},
             "next_state": STATE_SHOW_RESULT}
        ]
        # --- End Updated Psychological Questions Data ---

    def get_current_psych_questions(self):
        questions = []
        for q_template in self.psych_questions_data_template:
            q_data = q_template.copy()
            q_data["question"] = self.get_text(q_template["question_key_stem"])
            q_data["options"] = [self.get_text(stem) for stem in q_template["option_key_stems"]]
            questions.append(q_data)
        return questions

    def get_text(self, key, **kwargs):
        try:
            return self.texts[self.language][key].format(**kwargs)
        except KeyError:
            if self.language != "EN":
                try:
                    return self.texts["EN"][key].format(**kwargs)
                except KeyError:
                    return f"<{key}_MISSING_IN_EN>"
            return f"<{key}_MISSING>"
        except Exception as e: # General exception for formatting errors
            print(f"Error formatting text for key '{key}' with args {kwargs}: {e}")
            return f"<{key}_FORMAT_ERROR>"


    def _find_font(self, preferred_font_name, fallback_font_list, font_dir_abs_path):
        # 1. font_dir_abs_path가 제공된 경우에만 로컬 경로에서 선호 폰트 검색
        if font_dir_abs_path:
            font_path = os.path.join(font_dir_abs_path, preferred_font_name)
            if os.path.exists(font_path):
                return font_path

        # 2. 시스템에 설치된 폰트에서 선호 폰트 검색
        if hasattr(pygame.font, 'match_font'):
            try:
                system_font_path = pygame.font.match_font(preferred_font_name)
                if system_font_path:
                    return system_font_path
            except Exception:
                pass  # 폰트를 못 찾아도 오류를 내지 않고 계속 진행

        # 3. 폴백 폰트 목록을 순회하며 검색
        for font_name in fallback_font_list:
            # 로컬 경로가 있으면 로컬에서 먼저 검색
            if font_dir_abs_path:
                font_path = os.path.join(font_dir_abs_path, font_name)
                if os.path.exists(font_path):
                    return font_path
            # 시스템에서 폴백 폰트 검색
            if hasattr(pygame.font, 'match_font'):
                try:
                    system_font_path = pygame.font.match_font(font_name)
                    if system_font_path:
                        return system_font_path
                except Exception:
                    pass

        print(f"Warning: Font '{preferred_font_name}' and fallbacks not found. Using Pygame default.")
        return None

    def _load_sounds(self):
        sound_dir = os.path.join(self.script_dir, SOUND_DIR_NAME)
        self.sounds = {}
        sound_files = {
            "typing": ("type.wav", 0.4),
            "text": ("text.wav", 0.4),
            "error": ("error.wav", 0.5),
            "boot": ("boot.wav", 0.6),
            "floppy": ("floppy_insert2.wav", 0.7),
            "menu_select": ("floppy_insert.wav", 0.5),
            "scan": ("scan.wav", 1.0)
        }
        for name, (file, vol) in sound_files.items():
            try:
                sound_path = os.path.join(sound_dir, file)
                if not os.path.exists(sound_path): # Check if sound file exists
                    print(f"Warning: Sound file not found '{sound_path}'")
                    self.sounds[name] = None
                    continue
                print(f"Loading sound: {name} from {sound_path}")
                sound = pygame.mixer.Sound(sound_path)
                sound.set_volume(vol)
                self.sounds[name] = sound
            except Exception as e:
                print(f"Warning: Error loading sound '{file}': {e}")
                self.sounds[name] = None

    def _load_all_sketches(self):
        sketches = []
        sketches_dir_path = os.path.join(self.script_dir, SKETCH_DIR_NAME)
        if not os.path.isdir(sketches_dir_path): return sketches
        sketch_display_width = self.content_box_width // 2
        sketch_display_height = self.content_box_height // 2
        for filename in os.listdir(sketches_dir_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                try:
                    img_path = os.path.join(sketches_dir_path, filename)
                    sketch = pygame.image.load(img_path).convert()
                    ow, oh = sketch.get_size()
                    aspect = ow / oh if oh > 0 else 1
                    nw, nh = sketch_display_width, int(sketch_display_width / aspect) if aspect > 0 else sketch_display_height
                    if nh > sketch_display_height:
                        nh = sketch_display_height
                        nw = int(nh * aspect)
                    sketches.append(pygame.transform.smoothscale(sketch, (nw, nh)))
                except Exception as e:
                    print(f"Error loading sketch {filename}: {e}")
        if not sketches:
            dummy = pygame.Surface((sketch_display_width, sketch_display_height))
            dummy.fill(self.colors["dark_green"])
            pygame.draw.line(dummy, self.colors["green"], (0, 0), (sketch_display_width, sketch_display_height), 3)
            pygame.draw.line(dummy, self.colors["green"], (sketch_display_width, 0), (0, sketch_display_height), 3)
            sketches.append(dummy)
        return sketches

    def set_state(self, new_state, record_history=True):
        # 기존 상태에서 벗어날 때 플로피 체크 스레드 중지
        if self.game_state == STATE_FLOPPY_INSERT_GUIDE and new_state != STATE_FLOPPY_INSERT_GUIDE:
            self.floppy_check_running = False
        current_state_for_history = self.game_state
        print(f"STATE: {self.game_state} -> {new_state}")

        self.typing_speed = TYPING_SPEED_DEFAULT

        pygame.key.set_repeat()
        
        if record_history and current_state_for_history != new_state:
            if not ((current_state_for_history == STATE_SETTINGS and new_state == STATE_KEY_GUIDE) or
                    (current_state_for_history == STATE_KEY_GUIDE and new_state == STATE_SETTINGS)):
                self.history_stack.append(current_state_for_history)

        self.game_state = new_state
        self.current_text_key = ""
        self.current_text_args = {}
        self.current_text = ""
        self.displayed_text = ""
        self.typing_index = 0
        self.typing_timer = 0
        self.input_guiding_text = ""
        self.user_input_active = False
        self.user_input_text = ""
        self.needs_space_to_progress = False
        self.delay_timer = 0
        self.delay_duration = AUTO_PROGRESS_DELAY_DEFAULT
        self.last_activity_time = time.time()

        if new_state == STATE_INTRODUCTION_P1:
            # if self.game_state == STATE_ART_FILM_NOTICE:
            #     self.language = "EN"  # 기본 언어로 초기화
            #     pygame.display.set_caption(self.get_text("window_title"))
            #     self._load_actual_fonts()  # 폰트 다시 로드
            self.current_text_key = "intro_p1_body"
            self.displayed_text = "" # Start typing from beginning
            self.typing_index = 0
            self.typing_speed = 0.005 # 매우 빠른 타이핑 속도로 설정 (기존 TYPING_SPEED_DEFAULT는 0.025)
            self.needs_space_to_progress = True
            self.delay_duration = 8.0
            self.delay_timer = 0
        elif new_state == STATE_INTRODUCTION_P2:
            self.current_text_key = "intro_p2_body"
            self.displayed_text = ""
            self.typing_index = 0
            self.typing_speed = 0.005
            self.needs_space_to_progress = True
            self.delay_duration = 8.0
            self.delay_timer = 0
        elif new_state == STATE_NEW_TITLE:
            self.play_sound("boot")
            self.delay_duration = 3.0
            self.current_text_key = "new_title_main"
            self.displayed_text = ""
            self.typing_index = 0
        elif new_state == STATE_LANGUAGE_SELECT:
            self.current_settings_selection = 0
        elif new_state == STATE_NAME_INPUT:
            self.input_max_length = MAX_NAME_LENGTH
            self.user_name = ""
            self.psych_test_answers = []
            self.psych_test_results = {trait: 0 for trait in self.all_traits_keys}
            self.user_input_active = True
            pygame.key.set_repeat(300, 30)
            pygame.key.start_text_input()
            self.current_text_key = "name_input_title"
            self.displayed_text = ""
            self.typing_index = 0
            self.ime_composition_text = ""
            self.ime_composition_cursor = 0
        # --- Updated Psych Test State Initialization ---
        elif new_state.startswith("PSYCH_TEST_Q"):
            pygame.key.start_text_input()
            pygame.key.stop_text_input()  # IME 비활성화
            current_psych_qs = self.get_current_psych_questions()
            q_data = next((q for q in current_psych_qs if q["id"] == new_state), None)
            if q_data:
                self.current_question_index = current_psych_qs.index(q_data)
                # Calculate total number of questions (9 in this case)
                total_questions = len(self.psych_questions_data_template)
                q_text_header = self.get_text("psych_q_header", current=self.current_question_index + 1, total=total_questions)
                
                # Construct question text with options
                full_question_text = f"{q_text_header}\n\n{q_data['question']}\n\n"
                for opt_text in q_data['options']: # Options are already full texts
                    full_question_text += f"  {opt_text}\n"

                self.current_text = full_question_text
                self.input_guiding_text = self.get_text("psych_input_prompt")
                self.input_max_length = MAX_ANSWER_LENGTH
                self.displayed_text = ""
                self.typing_index = 0
                pygame.key.start_text_input() # Keep for consistency, though only 1 or 2 expected
            else:
                print(f"Error: Question data not found for state {new_state}")
                self.set_state(STATE_NAME_INPUT, record_history=False)
        # --- End Updated Psych Test State Initialization ---
        elif new_state == STATE_SHOW_RESULT:
            self._calculate_psych_results()
            self.current_text_key = "psych_result_header"
            self.current_text_args = {"name": self.user_name.upper()}
            self.needs_space_to_progress = True
            self.displayed_text = ""
            self.typing_index = 0
        elif new_state == STATE_PRE_FLOPPY_NOTICE:
            self.current_text_key = "pre_floppy_notice_text"
            self.delay_duration = 5.0  # 5초간 보여줍니다.
            self.needs_space_to_progress = False # 스페이스 바 입력이 필요 없습니다.
            # 타이핑 효과 없이 텍스트를 바로 표시합니다.
            self.current_text = self.get_text(self.current_text_key)
            self.displayed_text = self.current_text
            self.typing_index = len(self.current_text)
            self.delay_timer = 0 # 딜레이 타이머를 초기화합니다.
        elif new_state == STATE_FLOPPY_INSERT_GUIDE:
            self.current_text_key = "floppy_insert_guide_main_text"
            self.needs_space_to_progress = True
            self.floppy_anim_y_offset = 0
            self.floppy_anim_dir = 1
            self.displayed_text = ""
            self.typing_index = 0
        elif new_state == STATE_WRONG_FLOPPY_ERROR:
            self.current_text_key = "wrong_floppy_error"
            self.needs_space_to_progress = False # 스페이스바로 진행 안 함
            self.current_text = self.get_text(self.current_text_key)
            self.displayed_text = self.current_text # 바로 텍스트 표시
            self.typing_index = len(self.current_text)
        elif new_state == STATE_FLOPPY_CHECK:
            self.current_text_key = "floppy_accessing"
            self.play_sound("floppy")
            self.delay_duration = 3.0
            self.displayed_text = ""
            self.typing_index = 0
            self.floppy_progress_timer = 0  # 프로그레스 타이머 초기화
            self.floppy_progress_started = False  # 프로그레스 시작 플래그
        elif new_state == STATE_VISUAL_ANALYSIS_SETUP:
            self.current_text_key = "visual_setup"
            if self.loaded_sketches: self.current_sketch_image = random.choice(self.loaded_sketches)
            self.delay_duration = 1.0
            self.displayed_text = ""
            self.typing_index = 0
        elif new_state == STATE_VISUAL_ANALYSIS_DISPLAY:
            self.play_sound("scan")
            self.current_text_key = "visual_display_header"
            self.needs_space_to_progress = True
            self.displayed_text = ""
            self.typing_index = 0
            # 프롬프트 타이머 초기화
            self.visual_display_prompt_timer = 0
            self.visual_display_prompt_visible = False
            # OBS 장면 전환 추가
            if self.floppy_data and self.current_floppy_video_index < len(self.floppy_data):
                filename, content = self.floppy_data[self.current_floppy_video_index]
                self.switch_obs_scene_by_floppy(content)
        elif new_state == STATE_COMPLETE_SCREEN:
            self.current_text_key = "complete_screen_text"
            self.current_text_args = {"name": self.user_name.upper()}
            self.needs_space_to_progress = True
            self.displayed_text = ""
            self.typing_index = 0

            floppy_number = int(self.get_floppy_number())
            archetype_keyword = self.floppy_keywords[floppy_number - 1] if 0 < floppy_number <= len(self.floppy_keywords) else "알 수 없는 유형"
            visitor_data = {
                'name': self.user_name,
                'O': self.psych_test_results.get("Openness", 0),
                'C': self.psych_test_results.get("Conscientiousness", 0),
                'E': self.psych_test_results.get("Extraversion", 0),
                'A': self.psych_test_results.get("Agreeableness", 0),
                'N': self.psych_test_results.get("Neuroticism", 0),
                'floppy_key': floppy_number,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'keywords': [archetype_keyword]
            }
            self.data_logger.log_visitor_data(visitor_data)
            if self.printer_controller.is_connected:
                print("Printing label in background...")
                print_thread = threading.Thread(
                    target=self.printer_controller.print_psychology_results,
                    args=(visitor_data,)
                )
                print_thread.daemon = True
                print_thread.start()
        elif new_state == STATE_ART_FILM_NOTICE:
            self.current_text_key = "art_film_notice_header"
            self.delay_duration = 7.0
            self.displayed_text = ""
            self.typing_index = 0
        elif new_state == STATE_SETTINGS:
            self.current_text_key = "settings_title"
            self.current_settings_selection = 0
            self.current_text = self.get_text(self.current_text_key) # Load immediately for settings
            self.displayed_text = self.current_text
            self.typing_index = len(self.current_text)
        elif new_state == STATE_KEY_GUIDE:
            self.current_text_key = "key_guide_title"
            self.current_text = self.get_text(self.current_text_key) # Load immediately for key guide
            self.displayed_text = self.current_text
            self.typing_index = len(self.current_text)

        if self.current_text_key and not self.current_text:
            if not (new_state == STATE_SETTINGS or new_state == STATE_KEY_GUIDE or new_state == STATE_LANGUAGE_SELECT or new_state.startswith("PSYCH_TEST_Q")):
                self.current_text = self.get_text(self.current_text_key, **self.current_text_args)
                self.displayed_text = ""
                self.typing_index = 0
        elif self.current_text_key and new_state not in [STATE_SETTINGS, STATE_KEY_GUIDE, STATE_LANGUAGE_SELECT] and not new_state.startswith("PSYCH_TEST_Q"):
             # Ensure current_text is loaded if not done by specific state logic
             if not self.current_text: # if not already loaded by specific state logic that sets self.current_text directly
                self.current_text = self.get_text(self.current_text_key, **self.current_text_args)


    def _calculate_psych_results(self):
        self.psych_test_results = {trait: 0 for trait in self.all_traits_keys}
        current_psych_qs_templates = self.psych_questions_data_template
        for i, ans in enumerate(self.psych_test_answers):
            if 0 <= i < len(current_psych_qs_templates):
                q_data = current_psych_qs_templates[i]
                if ans in q_data["result_mapping"]:
                    for trait_key, val in q_data["result_mapping"][ans].items():
                        self.psych_test_results[trait_key] = self.psych_test_results.get(trait_key, 0) + val

    def _calculate_top_keywords(self, num_keywords=NUM_TOP_KEYWORDS):
        if not self.psych_test_results: return []
        # Ensure trait keys match exactly (case-sensitive)
        sorted_traits = sorted(self.psych_test_results.items(), key=lambda item: item[1], reverse=True)
        valid_keywords_data = [(k, s) for k, s in sorted_traits if s > 0]
        
        # Get text for traits, handling potential missing keys gracefully
        keywords_to_return = []
        for item_key, _ in valid_keywords_data[:num_keywords]:
            # Construct the text key like "trait_openness"
            text_key = f"trait_{item_key.lower()}"
            trait_text = self.get_text(text_key)
            if not trait_text.startswith("<") and not trait_text.endswith("_MISSING>"): # Check if text was found
                 keywords_to_return.append(trait_text)
            else:
                print(f"Warning: Text for trait key '{text_key}' not found. Using raw key: {item_key}")
                keywords_to_return.append(item_key) # Fallback to raw key name
        return keywords_to_return


    def take_screenshot(self):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            fn = os.path.join(self.screenshot_dir, f"screenshot_{timestamp}.png")
            pygame.image.save(self.screen, fn)
            print(f"Screenshot: {fn}")
            font = self.get_current_font("small")
            surf = font.render(self.get_text("screenshot_saved"), True, self.colors["black"], self.colors["green"])
            x = self.content_box_x + 10
            y = self.content_box_y + self.content_box_height - surf.get_height() - 10
            if x < 0 or y < self.content_box_y:
                x, y = 10, self.screen_height - surf.get_height() - 10
            self.screen.blit(surf, (x, y))
            pygame.display.flip()
            pygame.time.wait(500)
        except Exception as e:
            print(f"Screenshot error: {e}")

    def _go_back(self):
        if self.history_stack:
            prev_state = self.history_stack.pop()
            if self.game_state.startswith("PSYCH_TEST_Q") and self.psych_test_answers:
                self.psych_test_answers.pop()
                # also need to decrement current_question_index if going back within psych test
                if prev_state.startswith("PSYCH_TEST_Q"):
                     current_psych_qs = self.get_current_psych_questions()
                     q_data = next((q for q in current_psych_qs if q["id"] == prev_state), None)
                     if q_data:
                         self.current_question_index = current_psych_qs.index(q_data)

            elif self.game_state == STATE_SHOW_RESULT and prev_state.startswith("PSYCH_TEST_Q") and self.psych_test_answers:
                self.psych_test_answers.pop()
                 # self.current_question_index should be the last question index
                current_psych_qs = self.get_current_psych_questions()
                if current_psych_qs: # Should always be true if we got here
                    self.current_question_index = len(current_psych_qs) -1


            self.set_state(prev_state, record_history=False)
        else:
            self.play_sound("error")

    def handle_events(self):
        for event in pygame.event.get():
            # # --- 여기부터 임시 디버깅 코드 ---
            # if event.type in [pygame.KEYDOWN, pygame.KEYUP]:
            #     print(f"EVENT DETECTED --- Type: {event.type}, Key: {event.key}, Unicode: '{event.unicode}'")
            # # --- 여기까지 임시 디버깅 코드 ---
            self.last_activity_time = time.time()

            if event.type == pygame.QUIT:
                self.running = False

            # # --- 추가된 KEYUP 이벤트 처리 블록 ---
            # # 키에서 손을 뗄 때를 기준으로 B키 입력을 감지합니다.
            # if event.type == pygame.KEYUP:
            #     if event.key == pygame.K_b:
            #         # 이름 입력, 언어 선택 화면을 제외한 모든 곳에서 뒤로가기 허용
            #         if self.game_state not in [STATE_NAME_INPUT, STATE_LANGUAGE_SELECT]:
            #             self._go_back()
            #         # 여기서 처리가 끝나므로 아래 코드로 넘어가지 않도록 continue 사용
            #         continue
            # # --- 여기까지 추가 ---

            if event.type == pygame.TEXTEDITING:
                if self.user_input_active:
                    self.ime_composition_text = event.text
                    self.ime_composition_cursor = event.start
                    self.cursor_timer = 0
                    self.show_cursor = True

            if event.type == pygame.TEXTINPUT: # Handles actual character input
                if self.user_input_active:
                    self.ime_composition_text = ""
                    self.ime_composition_cursor = 0
                    self._handle_user_text_input(event)
                
                # if event.text.lower() == 'b':
                #     if self.game_state not in [STATE_NAME_INPUT, STATE_LANGUAGE_SELECT]:
                #         self._go_back()
                #         return

            if event.type == pygame.KEYDOWN:
                # 1. 상태와 관계없이 항상 작동해야 하는 키들을 최우선으로 배치
                if event.key == pygame.K_LEFT:
                    if self.game_state not in [STATE_NAME_INPUT, STATE_LANGUAGE_SELECT]:
                        self._go_back()
                    continue # 뒤로가기 처리 후 다른 로직 실행 방지
                if event.key == pygame.K_ESCAPE:
                    if self.game_state in [STATE_INTRODUCTION_P1, STATE_INTRODUCTION_P2]:
                        self.set_state(STATE_NEW_TITLE, record_history=False)
                    elif self.game_state in [STATE_SETTINGS, STATE_KEY_GUIDE]:
                        self._go_back()
                    else:
                        self.running = False
                    continue # ESC 키 처리 후 다른 키 눌림 로직 무시

                if event.key == pygame.K_F10:
                    self.take_screenshot()
                elif event.key == pygame.K_F9:
                    self.auto_mode_active = not self.auto_mode_active
                    print(f"Auto mode: {'ON' if self.auto_mode_active else 'OFF'}")
                elif event.key == pygame.K_F1:
                    if self.game_state not in [STATE_SETTINGS, STATE_KEY_GUIDE]:
                        self.previous_game_state_for_settings = self.game_state
                        self.set_state(STATE_SETTINGS)

                # 2. 특정 게임 상태(State)에 따라 다르게 작동하는 로직
                elif self.game_state == STATE_LANGUAGE_SELECT:
                    if event.key == pygame.K_UP:
                        self.current_settings_selection = (self.current_settings_selection - 1) % 2
                        self.play_sound("typing")
                    elif event.key == pygame.K_DOWN:
                        self.current_settings_selection = (self.current_settings_selection + 1) % 2
                        self.play_sound("typing")
                    elif event.key == pygame.K_RETURN:
                        self.language = "EN" if self.current_settings_selection == 0 else "KO"
                        pygame.display.set_caption(self.get_text("window_title"))
                        self._load_actual_fonts()
                        self.set_state(STATE_NAME_INPUT)

                elif self.game_state == STATE_SETTINGS:
                    self._handle_settings_input(event)

                elif self.game_state == STATE_KEY_GUIDE:
                    if event.key:
                        self._go_back()

                # 3. 사용자 입력이 활성화되었을 때의 처리 (이름, 질문 답변 등)
                elif self.user_input_active:
                    self._handle_user_text_input(event) # Handles KEYDOWN for Enter, Backspace

                # 4. 스페이스바를 눌러 진행해야 하는 경우
                elif not self.user_input_active and self.needs_space_to_progress and event.key == pygame.K_SPACE:
                    # 타이핑 애니메이션이 진행 중인지 확인
                    if self.current_text and self.typing_index < len(self.current_text):
                        # 1. 타이핑 중이면, 애니메이션을 즉시 완료시킴
                        self.typing_index = len(self.current_text)
                        self.displayed_text = self.current_text
                        # self.play_sound("menu_select") # 건너뛰기 효과음 재생
                    else:
                        # 2. 타이핑이 이미 완료된 상태면, 다음 화면으로 진행
                        if self.game_state == STATE_INTRODUCTION_P1:
                            self.set_state(STATE_INTRODUCTION_P2)
                            self.play_sound("typing")
                        elif self.game_state == STATE_INTRODUCTION_P2:
                            self.set_state(STATE_NEW_TITLE)
                            self.play_sound("typing")
                        elif self.game_state == STATE_SHOW_RESULT:
                            self.set_state(STATE_PRE_FLOPPY_NOTICE)
                        # elif self.game_state == STATE_FLOPPY_INSERT_GUIDE:
                        #     # 플로피가 감지되면 스페이스바 없이도 진행
                        #     if self.floppy_data:
                        #         self.set_state(STATE_FLOPPY_CHECK)
                        #         self.play_sound("floppy")
                        #     else:
                        #         # 기존 스페이스바 처리 유지 (테스트용)
                        #         self.set_state(STATE_FLOPPY_CHECK)
                        #         self.play_sound("floppy")
                        elif self.game_state == STATE_VISUAL_ANALYSIS_DISPLAY:
                            self.set_state(STATE_COMPLETE_SCREEN)
                        elif self.game_state == STATE_COMPLETE_SCREEN:
                            self.set_state(STATE_ART_FILM_NOTICE)

    def _handle_timed_and_auto_transitions(self, dt, current_time_ms):
        state_changed_by_timer_this_frame = False

        if self.game_state == STATE_INTRODUCTION_P1:
            self.delay_timer += dt
            if self.delay_timer >= self.delay_duration:
                self.set_state(STATE_INTRODUCTION_P2)
                state_changed_by_timer_this_frame = True
        elif self.game_state == STATE_INTRODUCTION_P2:
            self.delay_timer += dt
            if self.delay_timer >= self.delay_duration:
                self.set_state(STATE_INTRODUCTION_P1) # Loop back to P1 if space not pressed
                state_changed_by_timer_this_frame = True
        elif self.game_state == STATE_NEW_TITLE:
            self.delay_timer += dt
            if self.delay_timer >= self.delay_duration:
                # 1. 언어를 한국어로 변경
                self.language = "KO"
                # 2. 변경된 언어에 맞춰 창 제목과 폰트 다시 로드
                pygame.display.set_caption(self.get_text("window_title"))
                self._load_actual_fonts()
                # 3. 이름 입력 상태로 전환
                self.set_state(STATE_NAME_INPUT)
                state_changed_by_timer_this_frame = True
        elif self.game_state == STATE_PRE_FLOPPY_NOTICE:
            self.delay_timer += dt
            if self.delay_timer >= self.delay_duration:
                self.set_state(STATE_FLOPPY_INSERT_GUIDE)
                state_changed_by_timer_this_frame = True
        elif self.game_state == STATE_FLOPPY_CHECK:
            # 기존 delay_timer 대신 floppy_progress_timer 체크
            if self.floppy_progress_started and self.floppy_progress_timer >= self.delay_duration:
                self.set_state(STATE_VISUAL_ANALYSIS_SETUP)
                state_changed_by_timer_this_frame = True
        elif self.game_state == STATE_VISUAL_ANALYSIS_SETUP:
            self.delay_timer += dt
            if self.delay_timer >= self.delay_duration:
                self.set_state(STATE_VISUAL_ANALYSIS_DISPLAY)
                state_changed_by_timer_this_frame = True
        elif self.game_state == STATE_ART_FILM_NOTICE:
            self.delay_timer += dt
            if self.delay_timer >= self.delay_duration:
                # self.language = "EN"
                pygame.display.set_caption(self.get_text("window_title"))
                self._load_actual_fonts()
                self.set_state(STATE_INTRODUCTION_P1, record_history=False)
                state_changed_by_timer_this_frame = True

        if not state_changed_by_timer_this_frame and self.auto_mode_active:
            if self.needs_space_to_progress and not self.user_input_active:
                typing_truly_done = not self.current_text or self.typing_index >= len(self.current_text)
                if typing_truly_done:
                    if (pygame.time.get_ticks() / 1000.0) - self.last_activity_time >= AUTO_PROGRESS_DELAY_DEFAULT:
                        next_state_for_auto_mode = None
                        if self.game_state == STATE_SHOW_RESULT:
                            next_state_for_auto_mode = STATE_FLOPPY_INSERT_GUIDE
                        elif self.game_state == STATE_VISUAL_ANALYSIS_DISPLAY:
                            next_state_for_auto_mode = STATE_COMPLETE_SCREEN
                        elif self.game_state == STATE_COMPLETE_SCREEN:
                            next_state_for_auto_mode = STATE_ART_FILM_NOTICE
                        # Introduction P1/P2 auto-loop is handled by their own timers.
                        # Floppy insert guide requires space.

                        if next_state_for_auto_mode:
                            print(f"Auto-progressing from: {self.game_state} to {next_state_for_auto_mode}")
                            self.set_state(next_state_for_auto_mode)


    
    def render_text_with_glow(self, text, base_x_abs, base_y_abs, color,
                              size_type="normal", max_w_in_box=None,
                              line_height_override=None,
                              center_x_rel_to_box=False, center_y_rel_to_box=False):
        """
        기존 render_text_multiline을 감싸서 빛 번짐 효과를 추가합니다.
        """
        if self.glow_enabled:
            # 빛 번짐(Glow) 레이어 먼저 렌더링
            glow_color = self.colors.get("glow_green", (0, 50, 0))
            for offset_x, offset_y in self.glow_offsets:
                self.render_text_multiline(
                    text, base_x_abs + offset_x, base_y_abs + offset_y, glow_color,
                    size_type, max_w_in_box, line_height_override,
                    center_x_rel_to_box, center_y_rel_to_box
                )

        # 원본 텍스트 렌더링
        # 이 함수의 반환값(다음 y 위치, 마지막 사각형)이 중요하므로 마지막에 호출
        return self.render_text_multiline(
            text, base_x_abs, base_y_abs, color,
            size_type, max_w_in_box, line_height_override,
            center_x_rel_to_box, center_y_rel_to_box
        )
    # PsychologyTest 클래스 내부에 위치합니다.
    # 기존 render_text_multiline 메소드를 아래 코드로 대체하거나 수정합니다.
    def render_text_multiline(self, text, base_x_abs, base_y_abs, color,
                              size_type="normal", max_w_in_box=None,
                              line_height_override=None,
                              center_x_rel_to_box=False, center_y_rel_to_box=False):
        # (기존 render_text_multiline 함수 코드는 그대로 유지)
        # 🐛 버그 수정: .size(' ')[0] 처럼 너비 값만 가져오도록 수정
        if not text: return base_y_abs, None

        actual_line_render_step = line_height_override if line_height_override is not None \
            else self.get_unified_line_height(size_type)

        input_lines = text.splitlines()
        all_rendered_line_surfaces = []
        max_line_width_for_block_centering = 0

        for line_idx, original_line_text in enumerate(input_lines):
            if not original_line_text.strip() and original_line_text:
                empty_surf = pygame.Surface((1, actual_line_render_step), pygame.SRCALPHA)
                empty_surf.fill((0,0,0,0))
                all_rendered_line_surfaces.append(empty_surf)
                max_line_width_for_block_centering = max(max_line_width_for_block_centering, 1)
                continue
            if not original_line_text:
                if line_idx < len(input_lines) -1:
                    empty_surf = pygame.Surface((1, actual_line_render_step), pygame.SRCALPHA)
                    empty_surf.fill((0,0,0,0))
                    all_rendered_line_surfaces.append(empty_surf)
                continue

            line_segments = []
            current_line_segment_width = 0
            words = original_line_text.split(' ')

            for word_idx, word in enumerate(words):
                if not word and not line_segments:
                    if word_idx < len(words) - 1:
                        font_for_space_in_word = self.get_font_for_char(' ', size_type)
                        space_width_in_word = font_for_space_in_word.size(' ')[0] # 🐛 수정
                        line_segments.append((None, space_width_in_word))
                        current_line_segment_width += space_width_in_word
                    continue
                if not word and line_segments:
                    font_for_space_in_word = self.get_font_for_char(' ', size_type)
                    space_width_in_word = font_for_space_in_word.size(' ')[0] # 🐛 수정
                    if max_w_in_box and current_line_segment_width + space_width_in_word > max_w_in_box and line_segments:
                        line_surf_final = self._finalize_line_surface(line_segments, actual_line_render_step, color)
                        all_rendered_line_surfaces.append(line_surf_final)
                        max_line_width_for_block_centering = max(max_line_width_for_block_centering, line_surf_final.get_width())
                        line_segments = []
                        current_line_segment_width = 0
                    line_segments.append((None, space_width_in_word))
                    current_line_segment_width += space_width_in_word
                    continue

                current_word_char_surfaces = []
                current_word_width = 0
                for char_in_word in word:
                    font_for_char = self.get_font_for_char(char_in_word, size_type)
                    char_surf = font_for_char.render(char_in_word, True, color)
                    current_word_char_surfaces.append((char_surf, char_surf.get_width()))
                    current_word_width += char_surf.get_width()

                space_width = self.get_font_for_char(' ', size_type).size(' ')[0] # 🐛 수정
                if max_w_in_box and line_segments and \
                   (current_line_segment_width + (space_width if line_segments else 0) + current_word_width > max_w_in_box):
                    line_surf_final = self._finalize_line_surface(line_segments, actual_line_render_step, color)
                    all_rendered_line_surfaces.append(line_surf_final)
                    max_line_width_for_block_centering = max(max_line_width_for_block_centering, line_surf_final.get_width())
                    line_segments = []
                    current_line_segment_width = 0
                
                if line_segments and word:
                    line_segments.append((None, space_width))
                    current_line_segment_width += space_width

                line_segments.extend(current_word_char_surfaces)
                current_line_segment_width += current_word_width

            if line_segments:
                line_surf_final = self._finalize_line_surface(line_segments, actual_line_render_step, color)
                all_rendered_line_surfaces.append(line_surf_final)
                max_line_width_for_block_centering = max(max_line_width_for_block_centering, line_surf_final.get_width())

        total_block_h = len(all_rendered_line_surfaces) * actual_line_render_step
        current_render_y_abs = base_y_abs
        if center_y_rel_to_box:
            current_render_y_abs = base_y_abs - total_block_h // 2
            if self.game_state == STATE_NEW_TITLE:
                current_render_y_abs = self.content_box_y + self.content_box_height * 0.4 - total_block_h // 2
        
        last_line_rect_abs = None
        for line_surface_to_blit in all_rendered_line_surfaces:
            final_x_pos = base_x_abs
            if center_x_rel_to_box:
                final_x_pos = base_x_abs - line_surface_to_blit.get_width() // 2
            if not center_x_rel_to_box :
                final_x_pos = max(self.content_box_x + (self.content_box_width // CONTENT_BOX_PADDING_RATIO), final_x_pos)

            line_rect = line_surface_to_blit.get_rect(topleft=(final_x_pos, current_render_y_abs))
            self.screen.blit(line_surface_to_blit, line_rect)
            current_render_y_abs += actual_line_render_step
            last_line_rect_abs = line_rect

        return current_render_y_abs, last_line_rect_abs

    def _finalize_line_surface(self, line_segments, line_height, color_unused):
        if not line_segments:
            # Return a transparent surface with 1 width to ensure it takes up space if it's an empty line.
            return pygame.Surface((1, line_height), pygame.SRCALPHA)

        line_total_width = sum(part[1] for part in line_segments) # Sum of (surface, width)
        final_line_surf = pygame.Surface((line_total_width if line_total_width > 0 else 1, line_height), pygame.SRCALPHA)
        final_line_surf.fill((0,0,0,0)) # Transparent background

        current_char_x = 0
        for char_surf, char_w in line_segments:
            if char_surf: # If it's a rendered character surface
                # Vertically center each character segment on its line
                y_pos_char = (line_height - char_surf.get_height()) // 2
                final_line_surf.blit(char_surf, (current_char_x, y_pos_char))
            current_char_x += char_w # Move X for next segment (char or space)
        return final_line_surf


    def _handle_user_text_input(self, event):
        current_psych_qs = self.get_current_psych_questions()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            if self.ime_composition_text:
                return
            if self.game_state == STATE_NAME_INPUT and self.user_input_text.strip():
                self.user_name = self.user_input_text.strip()
                self.user_input_active = False
                pygame.key.stop_text_input()
                self.ime_composition_text = ""
                self.ime_composition_cursor = 0
                self.set_state(STATE_PSYCH_TEST_Q1) # Start with the first new psych question
            # --- Updated Psych Test Input Handling for 1 or 2 ---
            elif self.game_state.startswith("PSYCH_TEST_Q") and \
                 (not self.current_text or self.typing_index >= len(self.current_text)) and \
                 self.user_input_text.strip() in "12": # Check for '1' or '2'
                if not self.user_input_text.strip():
                    self.play_sound("error")
                    return # 함수 종료
                self.psych_test_answers.append(self.user_input_text.strip())
                self.user_input_active = False # Deactivate input for this question
                # pygame.key.stop_text_input() # Stop for this question
                self.user_input_text = "" # Clear for next question
                
                q_data = next((q for q in current_psych_qs if q["id"] == self.game_state), None)
                if q_data:
                    self.set_state(q_data["next_state"])
                else: # Should not happen if logic is correct
                    print(f"Error: Could not find next state from {self.game_state}")
                    self.set_state(STATE_SHOW_RESULT) # Fallback
            # --- End Updated Psych Test Input Handling ---
            else:
                self.play_sound("error")
                if self.game_state.startswith("PSYCH_TEST_Q"):
                    self.user_input_text = "" # Clear invalid input
            return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
            if self.ime_composition_text:
                # Let IME handle backspace during composition. If not, clear composition.
                # self.ime_composition_text = self.ime_composition_text[:-1] # Basic handling if IME doesn't
                pass # Usually handled by TEXTEDITING event or IME system itself
            elif self.user_input_text:
                self.user_input_text = self.user_input_text[:-1]
                self.play_sound("typing")
            else:
                self.play_sound("error")
            return

        if event.type == pygame.TEXTINPUT:
            if self.game_state == STATE_NAME_INPUT and len(self.user_input_text) < self.input_max_length:
                self.user_input_text += event.text
                self.play_sound("typing")
            # --- Updated Psych Test TEXTINPUT for 1 or 2 ---
            elif self.game_state.startswith("PSYCH_TEST_Q") and \
                 (not self.current_text or self.typing_index >= len(self.current_text)) and \
                 event.text.isdigit() and event.text in "12": # Only accept '1' or '2'
                if not self.user_input_text: # Only accept if current input is empty
                    self.user_input_text = event.text
                    self.play_sound("typing")
                # If already '1' or '2', don't append, effectively enforcing MAX_ANSWER_LENGTH = 1 for these.
            # --- End Updated Psych Test TEXTINPUT ---


    def _handle_settings_input(self, event):
        num_options = 4
        if event.key == pygame.K_UP:
            self.current_settings_selection = (self.current_settings_selection - 1 + num_options) % num_options
            self.play_sound("typing")
        elif event.key == pygame.K_DOWN:
            self.current_settings_selection = (self.current_settings_selection + 1) % num_options
            self.play_sound("typing")
        elif event.key == pygame.K_RETURN:
            self.play_sound("menu_select") # Use a selection sound
            if self.current_settings_selection == 0:
                self.language = "KO" if self.language == "EN" else "EN"
                pygame.display.set_caption(self.get_text("window_title"))
                self._load_actual_fonts()
                # Refresh settings screen text with new language
                self.current_text_key = "settings_title"
                self.current_text = self.get_text(self.current_text_key)
                self.displayed_text = self.current_text
                self.typing_index = len(self.current_text)

            elif self.current_settings_selection == 1:
                self.sound_enabled = not self.sound_enabled
            elif self.current_settings_selection == 2:
                self.set_state(STATE_KEY_GUIDE)
            elif self.current_settings_selection == 3:
                # self.set_state(self.previous_game_state_for_settings, record_history=False)
                self._go_back() # Use go_back to return to previous state from history

    def update_state_logic(self):
        dt = self.clock.get_time() / 1000.0
        current_time_ms = pygame.time.get_ticks()

        if self.current_text and self.typing_index < len(self.current_text):
            self.typing_timer += dt
            if self.typing_timer >= self.typing_speed:
                self.typing_timer = 0
                self.displayed_text += self.current_text[self.typing_index]

                if self.current_text[self.typing_index] not in ['\n', ' ']:
                    self.play_sound("text", force_channel_id=self.TYPING_SOUND_CHANNEL_ID, play_only_if_channel_free=True)
                self.typing_index += 1

                if self.typing_index >= len(self.current_text):
                    if self.game_state in [STATE_NAME_INPUT] or self.game_state.startswith("PSYCH_TEST_Q"):
                        self.user_input_active = True
                        if self.game_state.startswith("PSYCH_TEST_Q"):
                             pygame.key.set_repeat(0,0) # Disable key repeat for single digit psych answers


        elif self.game_state in [STATE_NAME_INPUT] or self.game_state.startswith("PSYCH_TEST_Q"):
            if not self.user_input_active and (not self.current_text or self.typing_index >= len(self.current_text)):
                self.user_input_active = True
                if self.game_state.startswith("PSYCH_TEST_Q"):
                    pygame.key.set_repeat(0,0)


        self.cursor_timer += dt
        if self.cursor_timer >= self.cursor_interval:
            self.cursor_timer = 0
            self.show_cursor = not self.show_cursor

        if self.game_state == STATE_FLOPPY_INSERT_GUIDE:
            self.floppy_anim_y_offset += self.floppy_anim_dir * self.floppy_anim_speed * dt
            if abs(self.floppy_anim_y_offset) > self.floppy_anim_range:
                self.floppy_anim_y_offset = self.floppy_anim_range * self.floppy_anim_dir
                self.floppy_anim_dir *= -1
            # 스레드가 실행 중이 아니면 시작
            if not self.floppy_check_thread or not self.floppy_check_thread.is_alive():
                self.floppy_check_running = True
                self.floppy_check_thread = threading.Thread(target=self.check_floppy_disk_threaded)
                self.floppy_check_thread.daemon = True
                self.floppy_check_thread.start()

            try:
                status, data = self.floppy_check_queue.get_nowait()
                if status == 'found' and data:
                    self.floppy_check_running = False  # 스레드 중지

                    # 기대하는 플로피 번호와 실제 삽입된 플로피 번호를 비교합니다.
                    expected_floppy_num_str = self.get_floppy_number()
                    # data는 [(filename, content), ...] 형식이므로 첫 번째 파일의 content를 확인
                    actual_floppy_num_str = data[0][1] if data else None

                    # 문자열을 정수로 변환하여 비교 (안전성을 위해)
                    try:
                        is_correct_floppy = int(expected_floppy_num_str) == int(actual_floppy_num_str)
                    except (ValueError, TypeError):
                        is_correct_floppy = False # 변환 실패 시 무조건 다른 것으로 간주

                    if not is_correct_floppy:
                        # 잘못된 플로피가 삽입됨
                        print(f"Wrong floppy. Expected: {expected_floppy_num_str}, Got: {actual_floppy_num_str}")
                        self.set_state(STATE_WRONG_FLOPPY_ERROR)
                        self.play_sound("error") # 에러 사운드 재생
                    else:
                        # 올바른 플로피가 삽입됨
                        self.floppy_data = data
                        self.load_floppy_videos()
                        self.set_state(STATE_FLOPPY_CHECK)
                        self.play_sound("floppy")

            except queue.Empty:
                pass  # 큐가 비어있으면 그냥 진행

        # 플로피 체크 화면에서 타이핑 완료 시 프로그레스 시작
        if self.game_state == STATE_FLOPPY_CHECK:
            if self.typing_index >= len(self.current_text) and not self.floppy_progress_started:
                self.floppy_progress_started = True
                self.floppy_progress_timer = 0  # 프로그레스 시작 시점에 타이머 리셋

            if self.floppy_progress_started:
                self.floppy_progress_timer += dt

        # Visual display screen 프롬프트 타이머 업데이트
        if self.game_state == STATE_VISUAL_ANALYSIS_DISPLAY:
            self.visual_display_prompt_timer += dt

            # 3초 주기로 반복
            cycle_time = self.visual_display_prompt_timer % 4.0

            # 처음 1초 동안만 표시
            self.visual_display_prompt_visible = cycle_time < 1.0

        if self.game_state == STATE_WRONG_FLOPPY_ERROR:
            # 잘못된 플로피가 제거되었는지 확인 (A드라이브가 사라졌는지 체크)
            if not os.path.exists(self.floppy_drive_path):
                print("Wrong floppy removed. Returning to guide.")
                self.set_state(STATE_FLOPPY_INSERT_GUIDE) # 제거되면 다시 삽입 안내 화면으로
        
        self._handle_timed_and_auto_transitions(dt, current_time_ms)


    def _draw_language_select_screen(self, box_center_x, box_center_y, text_max_width):
        lh_large = self.get_unified_line_height("large")
        lh_normal = self.get_unified_line_height("normal")
        lh_small = self.get_unified_line_height("small")

        title_text = self.get_text("select_language_title")
        title_y_pos = self.content_box_y + self.content_box_height * 0.3
        self.render_text_with_glow(title_text, box_center_x, title_y_pos,
                               self.colors["green"], size_type="large",
                               max_w_in_box=text_max_width, line_height_override=lh_large,
                               center_x_rel_to_box=True, center_y_rel_to_box=True) # Center Y for the block

        options_display_texts = [self.get_text("lang_en"), self.get_text("lang_ko")]
        current_y_options = title_y_pos + lh_large * 1.5 # Start options below title
        for i, option_disp_text in enumerate(options_display_texts):
            display_text = f"> {option_disp_text}" if i == self.current_settings_selection else f"  {option_disp_text}"
            # Render each option centered horizontally, starting from current_y_options
            option_y_draw = current_y_options + i * lh_normal * 1.5 # Space out options
            self.render_text_with_glow(display_text, box_center_x, option_y_draw,
                                   self.colors["green"], size_type="normal",
                                   max_w_in_box=text_max_width, line_height_override=lh_normal,
                                   center_x_rel_to_box=True, center_y_rel_to_box=False) # Y is top of this line

        guide_y_pos = self.content_box_y + self.content_box_height * 0.7
        guide_text_to_display = self.get_text("select_language_guide")
        self.render_text_with_glow(guide_text_to_display, box_center_x, guide_y_pos,
                               self.colors["green"], size_type="small",
                               max_w_in_box=text_max_width,
                               line_height_override=lh_small,
                               center_x_rel_to_box=True, center_y_rel_to_box=False)


    def _draw_new_title_screen(self, box_center_x, box_center_y, text_max_width):
        current_y = self.content_box_y

        lh_small = self.get_unified_line_height("small")
        team_text = self.get_text("new_title_team")
        padding_top = 20
        self.render_text_with_glow(team_text,
                                   self.content_box_x + 20, current_y + padding_top,
                                   self.colors["green"],
                                   size_type="small",
                                   max_w_in_box=text_max_width,
                                   line_height_override=lh_small,
                                   center_x_rel_to_box=False, center_y_rel_to_box=False)

        lh_title = self.get_unified_line_height("title")
        title_block_center_y = self.content_box_y + int(self.content_box_height * 0.40)

        # Use self.displayed_text for typing effect
        self.render_text_with_glow(self.displayed_text,
                                   box_center_x, title_block_center_y,
                                   self.colors["green"],
                                   size_type="title",
                                   max_w_in_box=text_max_width,
                                   line_height_override=lh_title,
                                   center_x_rel_to_box=True, center_y_rel_to_box=True)

        # current_y should be calculated based on where the title block ended if it were fully rendered
        # For simplicity, let's assume the title takes up roughly its line height for vertical positioning of subsequent elements.
        # A more accurate way would be to render the full title_text to get its height.
        # title_full_surf_for_height_calc = self.create_multilingual_surface(self.get_text("new_title_main"), "title", self.colors["green"])
        # title_actual_height = title_full_surf_for_height_calc.get_height()
        # current_y = title_block_center_y + title_actual_height / 2 # Bottom of the centered title block

        # Simplified current_y update based on title line height only
        current_y = title_block_center_y + (lh_title // 2)


        lh_large = self.get_unified_line_height("large")
        version_text = self.get_text("new_title_version")
        # Position version text slightly below the main title area
        version_text_top_y = current_y + int(lh_large * 0.1) # Small gap after title

        # Render version text and update current_y to its bottom
        current_y, _ = self.render_text_with_glow(version_text,
                                   box_center_x, version_text_top_y,
                                   self.colors["green"],
                                   size_type="large",
                                   max_w_in_box=text_max_width,
                                   line_height_override=lh_large,
                                   center_x_rel_to_box=True, center_y_rel_to_box=False) # center_y is false as version_text_top_y is the top

        lh_normal = self.get_unified_line_height("normal")
        loading_text = self.get_text("new_title_loading")
        # Position loading text below version text
        loading_text_top_y = current_y + int(lh_normal * 1.0) # A bit more space

        current_y, _ = self.render_text_with_glow(loading_text,
                                   box_center_x, loading_text_top_y,
                                   self.colors["green"],
                                   size_type="normal",
                                   max_w_in_box=text_max_width,
                                   line_height_override=lh_normal,
                                   center_x_rel_to_box=True, center_y_rel_to_box=False)


        bar_w = text_max_width * 0.6
        bar_h = lh_normal * 0.7 # Make bar height relative to normal font
        # Position progress bar below loading text
        bar_top_y = current_y + int(lh_normal * 0.3) # Small gap

        bar_x = box_center_x - bar_w / 2
        progress = min(1.0, self.delay_timer / self.delay_duration if self.delay_duration > 0 else 0)

        pygame.draw.rect(self.screen, self.colors["dark_green"], (bar_x, bar_top_y, bar_w, bar_h), 2) # Border
        pygame.draw.rect(self.screen, self.colors["green"],
                         (bar_x + 2, bar_top_y + 2, (bar_w - 4) * progress, bar_h - 4)) # Fill
        
        # 패딩 계산 (우상단 시간 UI와 동일하게)
        box_padding = self.content_box_width // CONTENT_BOX_PADDING_RATIO

        lh_small_year = self.get_unified_line_height("small") # Use specific lh for year
        year_text = self.get_text("new_title_copy_year")
        year_lines = year_text.splitlines()
        max_year_line_width = 0
        if year_lines:
            for yr_line in year_lines:
                 # Use create_multilingual_surface for accurate width of mixed-script lines
                year_line_surf = self.create_multilingual_surface(yr_line, "small", self.colors["green"])
                max_year_line_width = max(max_year_line_width, year_line_surf.get_width())


        # 오른쪽 패딩: 우상단 시간 UI와 동일하게 box_padding 사용
        year_text_x = self.content_box_x + self.content_box_width - max_year_line_width - box_padding
        num_year_lines = len(year_lines)
        year_text_block_height = num_year_lines * lh_small_year # Approximate block height
        
         # 아래쪽 패딩: 우상단과 동일한 box_padding 사용
        year_text_top_y = self.content_box_y + self.content_box_height - year_text_block_height - box_padding

        self.render_text_with_glow(year_text,
                                   year_text_x, # Align based on calculated max_width
                                   year_text_top_y,
                                   self.colors["green"],
                                   size_type="small",
                                   max_w_in_box=text_max_width, # It won't wrap if x is specific
                                   line_height_override=lh_small_year,
                                   center_x_rel_to_box=False, # Explicit X
                                   center_y_rel_to_box=False) # Explicit Y

    def _draw_introduction_screen(self, state, box_center_x, text_max_width, dt_y_abs):
        lh_title = self.get_unified_line_height("title")
        header_text = self.get_text("intro_header")
    
        # 1. 상단 여백을 조절합니다. (1.5를 1.0으로 변경)
        header_top_y = self.content_box_y + int(lh_title * 0.5) 
    
        if self.glow_enabled:
            glow_color = self.colors.get("glow_green")
            for ox, oy in self.glow_offsets:
                header_surf_glow = self.create_multilingual_surface(header_text, "title", glow_color)
                header_rect_glow = header_surf_glow.get_rect(centerx=box_center_x + ox, top=header_top_y + oy)
                self.screen.blit(header_surf_glow, header_rect_glow)
    
        header_surf = self.create_multilingual_surface(header_text, "title", self.colors["green"])
        header_rect = header_surf.get_rect(centerx=box_center_x, top=header_top_y)
        self.screen.blit(header_surf, header_rect)
    
        lh_normal = self.get_unified_line_height("normal")
        
        # 2. 헤더와 본문 사이 간격을 조절합니다. (0.8을 0.3으로 변경)
        intro_text_y_start = header_rect.bottom + int(lh_title * 0.3)
    
        # self.displayed_text is used here for typing effect
        self.render_text_with_glow(self.displayed_text,
                           box_center_x,
                           intro_text_y_start, self.colors["green"],
                           size_type="normal",
                           max_w_in_box=text_max_width,
                           line_height_override=lh_normal,
                           center_x_rel_to_box=True, center_y_rel_to_box=False)
    
        # Show "Press Space" only when typing is complete
        if not self.current_text or self.typing_index >= len(self.current_text) :
            proceed_text = self.get_text("press_space_continue")
            if self.glow_enabled:
                glow_color = self.colors.get("glow_green")
                for ox, oy in self.glow_offsets:
                     proceed_text_surf_glow = self.create_multilingual_surface(proceed_text, "normal", glow_color)
                     proceed_text_rect_glow = proceed_text_surf_glow.get_rect(centerx=box_center_x + ox, bottom=dt_y_abs - int(lh_normal * 0.5) + oy)
                     self.screen.blit(proceed_text_surf_glow, proceed_text_rect_glow)
            
            proceed_text_surf = self.create_multilingual_surface(proceed_text, "normal", self.colors["green"])
            proceed_text_rect = proceed_text_surf.get_rect(centerx=box_center_x, bottom=dt_y_abs - int(lh_normal * 0.5))
            self.screen.blit(proceed_text_surf, proceed_text_rect)
    
            if self.show_cursor:
                font_normal_obj_for_cursor = self.get_current_font("normal")
                self.draw_block_cursor(proceed_text_rect.right + font_normal_obj_for_cursor.size(" ")[0] * 0.5,
                                       proceed_text_rect.top,
                                       font_normal_obj_for_cursor, self.colors["green"], "normal")


    def _draw_floppy_guide_screen(self, box_center_x, box_center_y, text_max_width):
        # 비디오를 먼저 그리기 (상단에 크게 배치)
        video_was_drawn = False
        if 'floppy' in self.video_players:
            current_time_ms = pygame.time.get_ticks()
            frame = self.video_players['floppy'].get_frame(current_time_ms)

            if frame:
                # 현재 재생 중인 비디오 인덱스 확인
                current_video_index = self.video_players['floppy'].get_current_video_index()

                # 비디오별로 다른 Y 위치 설정
                if current_video_index in [0, 1]:  # 001.mp4(인덱스 0), 002.mp4(인덱스 1)
                    video_y_ratio = 0.10  # 15% 지점 (더 아래로)
                else:  # 003.mp4(인덱스 2)
                    video_y_ratio = 0.05  # 5% 지점 (상단에)

                # 비디오를 중앙에 배치
                video_x = self.content_box_x + (self.content_box_width - frame.get_width()) // 2
                video_y = self.content_box_y + int(self.content_box_height * video_y_ratio)

                video_rect = frame.get_rect(topleft=(video_x, video_y))
                video_surface_with_scanlines = frame.copy()
                #self.apply_static_scanline_effect(video_surface_with_scanlines)
                self.screen.blit(video_surface_with_scanlines, video_rect)
                video_was_drawn = True

        # 비디오가 표시되지 않은 경우에만 대체 애니메이션 표시
        if not video_was_drawn:
            # 기존 플로피 애니메이션도 더 크게 조정
            monitor_width = int(self.content_box_width * 0.5)  # 0.3에서 0.5로 확대
            monitor_height = int(self.content_box_height * 0.4)  # 0.3에서 0.4로 확대
            monitor_x = box_center_x - monitor_width / 2
            monitor_y = self.content_box_y + self.content_box_height * 0.1  # 0.15에서 0.1로 올림

            monitor_area_height = monitor_height + 5 + (monitor_height*0.1) + 5 + (monitor_height*0.1*1.5)
            monitor_surface = pygame.Surface((monitor_width, monitor_area_height * 1.2), pygame.SRCALPHA)
            monitor_surface.fill((0,0,0,0))

            pygame.draw.rect(monitor_surface, self.colors["green"], (0, 0, monitor_width, monitor_height), 2)
            slot_width = monitor_width * 0.6
            slot_height = monitor_height * 0.1
            slot_x_rel = monitor_width/2 - slot_width/2
            slot_y_rel = monitor_height + 5
            pygame.draw.rect(monitor_surface, self.colors["green"], (slot_x_rel, slot_y_rel, slot_width, slot_height), 2)

            floppy_width = slot_width * 0.9
            floppy_height = slot_height * 1.5
            floppy_x_rel = monitor_width/2 - floppy_width / 2
            floppy_base_y_rel = slot_y_rel + slot_height / 2 - floppy_height / 2
            current_floppy_y_rel = floppy_base_y_rel + self.floppy_anim_y_offset

            pygame.draw.rect(monitor_surface, self.colors["floppy_body"], (floppy_x_rel, current_floppy_y_rel, floppy_width, floppy_height))
            pygame.draw.rect(monitor_surface, self.colors["green"], (floppy_x_rel, current_floppy_y_rel, floppy_width, floppy_height), 1)
            shutter_width = floppy_width * 0.3
            shutter_height = floppy_height * 0.8
            shutter_x_rel = floppy_x_rel + floppy_width - shutter_width - 5
            shutter_y_rel = current_floppy_y_rel + (floppy_height - shutter_height) / 2
            pygame.draw.rect(monitor_surface, self.colors["floppy_shutter"], (shutter_x_rel, shutter_y_rel, shutter_width, shutter_height))

            #self.apply_static_scanline_effect(monitor_surface)
            self.screen.blit(monitor_surface, (monitor_x, monitor_y))

        # 텍스트는 화면 하단에 배치하고 행간을 줄임
        lh_large = self.get_unified_line_height("large")
        lh_normal = self.get_unified_line_height("normal")
        lh_small = self.get_unified_line_height("small")

        # 행간을 줄이기 위한 압축된 라인 높이
        compressed_lh_large = int(lh_large * 0.8)  # 20% 압축
        compressed_lh_normal = int(lh_normal * 0.8)  # 20% 압축
        compressed_lh_small = int(lh_small * 0.8)  # 20% 압축

        header_text = self.get_text("floppy_insert_guide_header")

        # 헤더 텍스트를 더 위로 이동 (화면의 5% 지점)
        header_y = self.content_box_y + int(self.content_box_height * 0.05)
        self.render_text_with_glow(header_text, box_center_x, header_y,
                                   self.colors["green"], size_type="large",
                                   max_w_in_box=text_max_width,
                                   line_height_override=compressed_lh_large, center_x_rel_to_box=True)

        # 메인 텍스트 위치도 더 아래로 조정 (화면의 80% 지점)
        text_y_pos = self.content_box_y + self.content_box_height * 0.80

        next_y, _ = self.render_text_with_glow(self.displayed_text, box_center_x, text_y_pos,
                                   self.colors["green"], size_type="normal",
                                   max_w_in_box=text_max_width * 0.9,
                                   line_height_override=compressed_lh_normal, center_x_rel_to_box=True)

        if not self.current_text or self.typing_index >= len(self.current_text):
            font_small_obj = self.get_current_font("small")

            # 플로피 번호를 포함한 안내 문구 생성
            floppy_number = self.get_floppy_number()

            # 언어에 따라 다른 형식 사용
            if self.language == "KO":
                instruction_text = f"{floppy_number} 디스크를 삽입하세요"
            else:
                instruction_text = f"Insert Disk {floppy_number}"

            # 인스트럭션 텍스트 간격도 줄임
            instruction_y_pos = next_y + int(compressed_lh_small * 0.5)

            if self.glow_enabled:
                glow_color = self.colors.get("glow_green")
                for ox, oy in self.glow_offsets:
                    instruction_surf_glow = self.create_multilingual_surface(instruction_text, "small", glow_color)
                    instruction_rect_glow = instruction_surf_glow.get_rect(centerx=box_center_x+ox, top=instruction_y_pos+oy)
                    self.screen.blit(instruction_surf_glow, instruction_rect_glow)

            instruction_surf = self.create_multilingual_surface(instruction_text, "small", self.colors["green"])
            instruction_rect = instruction_surf.get_rect(centerx=box_center_x, top=instruction_y_pos)
            self.screen.blit(instruction_surf, instruction_rect)

            if self.show_cursor:
                self.draw_block_cursor(instruction_rect.right + font_small_obj.size(" ")[0] * 0.5,
                                       instruction_rect.top,
                                       font_small_obj, self.colors["green"], "small")
    
    def _draw_show_result_screen(self, content_x_start, content_y_start, box_center_x, text_max_width):
        lh_normal = self.get_unified_line_height("normal")
        lh_small = self.get_unified_line_height("small")

        # Use self.displayed_text for the title's typing effect
        title_end_y, title_rect = self.render_text_with_glow(
            self.displayed_text, # This will be "PSYCHOLOGICAL PROFILE: NAME" after typing
            box_center_x, content_y_start, self.colors["green"],
            size_type="normal", max_w_in_box=text_max_width, line_height_override=lh_normal,
            center_x_rel_to_box=True, center_y_rel_to_box=False # Y is top
        )

        # Only draw chart and keywords if title typing is complete
        if not self.current_text or self.typing_index >= len(self.current_text):
            # Calculate available height for chart and keywords
            # dt_y_abs is the y-coordinate of the date/time string at the bottom
            dt_x_abs, dt_y_abs_val, _, _, _ = self._draw_base_ui_elements() # Get dt_y_abs for bottom boundary
            
            bottom_area_height_for_space_prompt = lh_normal * 1.25 # Space for "Press Space" + padding

            # Start Y for chart area, after the title
            chart_area_start_y = title_end_y + lh_small # Small gap after title

            # Calculate available vertical space for chart and keywords
            available_height_for_chart_and_keywords = dt_y_abs_val - bottom_area_height_for_space_prompt - chart_area_start_y
            
            # Radar chart parameters
            # Make chart size responsive to available height, but also capped by width
            chart_size = min(text_max_width * 0.4, available_height_for_chart_and_keywords * 0.35)
            #chart_size = int(chart_size * self.scale_factor) # Minimum size for visibility

            # Center chart vertically in the space between title and keywords_y_pos (approx)
            # Keywords will take some space at the bottom of this available area
            keywords_block_approx_height = lh_small * 4 # Header + 1-2 lines of keywords
            chart_vertical_space = available_height_for_chart_and_keywords - keywords_block_approx_height
            
            chart_cy = chart_area_start_y + chart_vertical_space * 0.3 + chart_size / 2 # Adjusted centering: 40% down in its space
            chart_cx = box_center_x

            # Ensure chart doesn't overlap title or go too low
            chart_cy = max(chart_cy, title_end_y + chart_size / 2 + lh_normal) # Min distance from title
            
            ordered_labels_keys = self.all_traits_keys

            self.draw_radar_chart(self.screen, self.user_name, self.psych_test_results,
                                  ordered_labels_keys, chart_cx, chart_cy, chart_size, self.colors["green"])

            # 플로피 번호 계산
            floppy_number = self.get_floppy_number()
    
            # 성격 점수 문자열 생성
            o_score = self.psych_test_results.get("Openness", 0)
            c_score = self.psych_test_results.get("Conscientiousness", 0)
            e_score = self.psych_test_results.get("Extraversion", 0)
            a_score = self.psych_test_results.get("Agreeableness", 0)
            n_score = self.psych_test_results.get("Neuroticism", 0)
    
            # 전체 텍스트를 여러 줄로 구성
            keyword_header_text = self.get_text("your_keywords_header")
            score_text = f"O{o_score}-C{c_score}-E{e_score}-A{a_score}-N{n_score}"
            floppy_text = f"FLOPPY KEY: {floppy_number}"
            
            # 모든 텍스트를 하나로 합침 (줄바꿈 포함)
            full_text = f"{keyword_header_text} {score_text}\n{floppy_text}"
            
            # Position below the chart
            keywords_y_pos = chart_cy + chart_size * 0.6 + lh_normal * 2.5
            
            # Ensure text doesn't overlap with "Press Space" area
            max_keywords_y = dt_y_abs_val - bottom_area_height_for_space_prompt - lh_small
            
            # 텍스트의 줄 수를 고려하여 Y 위치 조정
            num_lines = full_text.count('\n') + 1
            keywords_y_pos = min(keywords_y_pos, max_keywords_y - num_lines * lh_small)
    
            # 전체 텍스트를 small 크기로 한 번에 렌더링
            self.render_text_with_glow(full_text, box_center_x, keywords_y_pos,
                                       self.colors["green"], size_type="small",
                                       max_w_in_box=text_max_width * 0.9,
                                       line_height_override=lh_small,
                                       center_x_rel_to_box=True, center_y_rel_to_box=False)

    def _draw_floppy_check_screen(self, box_center_x, text_max_width):
        lh_normal = self.get_unified_line_height("normal")
        # Use self.displayed_text for typing effect
        self.render_text_with_glow(self.displayed_text, box_center_x,
                                   self.content_box_y + self.content_box_height // 3, # Centered more or less
                                   self.colors["green"], size_type="normal",
                                   max_w_in_box=text_max_width,
                                   line_height_override=lh_normal, center_x_rel_to_box=True, center_y_rel_to_box=True) # Center Y for the block

        # Progress bar shown after typing is complete
        if not self.current_text or self.typing_index >= len(self.current_text):
            progress = min(1.0, max(0.0, self.floppy_progress_timer / self.delay_duration if self.delay_duration > 0 else 0))
            bar_w = self.content_box_width // 2
            bar_h = int(self.content_box_height / 20) # Relative bar height
            bar_x = box_center_x - bar_w // 2
            bar_y = self.content_box_y + self.content_box_height * 2 // 3 # Position bar lower
            
            pygame.draw.rect(self.screen, self.colors["dark_green"], (bar_x, bar_y, bar_w, bar_h)) # Background/border
            pygame.draw.rect(self.screen, self.colors["green"],
                             (bar_x + 3, bar_y + 3, (bar_w - 6) * progress, bar_h - 6)) # Progress fill
            
            font_normal_obj = self.get_current_font("normal")
            perc_text_surf = self.create_multilingual_surface(f"{int(progress * 100)}%", "normal", self.colors["green"]) # Use create_multilingual
            # Position percentage text next to the bar
            self.screen.blit(perc_text_surf,
                             (bar_x + bar_w + 15, bar_y + bar_h // 2 - perc_text_surf.get_height() // 2))


    def _draw_visual_setup_screen(self, box_center_x, text_max_width):
        lh_normal = self.get_unified_line_height("normal")
        # Use self.displayed_text for typing effect
        self.render_text_with_glow(self.displayed_text, box_center_x,
                                   self.content_box_y + self.content_box_height // 2, # Vertically centered
                                   self.colors["green"], size_type="normal",
                                   max_w_in_box=text_max_width,
                                   line_height_override=lh_normal, center_x_rel_to_box=True, center_y_rel_to_box=True) # Center Y for the block

    def _draw_visual_display_screen(self, content_y_start, box_center_x, text_max_width, dt_y_abs):
        # 미디어만 전체 화면에 표시
        media_was_drawn = False

        # 플로피에서 로드한 비디오가 있으면 우선 표시
        if self.floppy_videos and 0 <= self.current_floppy_video_index < len(self.floppy_videos):
            current_video_player = self.floppy_videos[self.current_floppy_video_index]
            current_time_ms = pygame.time.get_ticks()
            frame = current_video_player.get_frame(current_time_ms)

            if frame:
                # 4:3 화면에 꽉 차게 표시
                video_rect = frame.get_rect(topleft=(self.content_box_x, self.content_box_y))
                video_surface_with_scanlines = frame.copy()
                #self.apply_static_scanline_effect(video_surface_with_scanlines)
                self.screen.blit(video_surface_with_scanlines, video_rect)
                media_was_drawn = True

                # 비디오 정보 표시 (선택사항)
                # if self.current_floppy_video_index < len(self.floppy_data):
                #     filename, content = self.floppy_data[self.current_floppy_video_index]
                #     info_text = f"Video: {content}.mp4"
                #     # 화면 상단에 작은 텍스트로 표시
                #     info_surf = self.create_multilingual_surface(
                #         info_text, "small", self.colors["green"])
                #     self.screen.blit(info_surf, 
                #         (self.content_box_x + 10, self.content_box_y + 10))

        elif 'analysis' in self.video_players:
            current_time_ms = pygame.time.get_ticks()
            frame = self.video_players['analysis'].get_frame(current_time_ms)

            if frame:
                # 4:3 화면에 꽉 차게 표시
                video_rect = frame.get_rect(topleft=(self.content_box_x, self.content_box_y))
                video_surface_with_scanlines = frame.copy()
                #self.apply_static_scanline_effect(video_surface_with_scanlines)
                self.screen.blit(video_surface_with_scanlines, video_rect)
                media_was_drawn = True

        if not media_was_drawn and self.current_sketch_image:
            # 스케치 이미지를 4:3 화면에 꽉 차게 표시
            scaled_sketch = pygame.transform.smoothscale(
                self.current_sketch_image, 
                (self.content_box_width, self.content_box_height)
            )

            sketch_rect = scaled_sketch.get_rect(topleft=(self.content_box_x, self.content_box_y))
            self.screen.blit(scaled_sketch, sketch_rect)

        # 프롬프트가 보여야 할 때만 표시
        if self.visual_display_prompt_visible:
            proceed_text = self.get_text("press_space_continue")
            font_normal = self.get_current_font("normal")
            line_height_for_prompt = self.get_unified_line_height("normal")

            if self.glow_enabled:
                glow_color = self.colors.get("glow_green")
                for ox, oy in self.glow_offsets:
                    proceed_surf_glow = self.create_multilingual_surface(proceed_text, "normal", glow_color)
                    proceed_rect_glow = proceed_surf_glow.get_rect(centerx=box_center_x + ox,
                                                                   bottom=dt_y_abs - line_height_for_prompt * 0.5 + oy)
                    self.screen.blit(proceed_surf_glow, proceed_rect_glow)

            proceed_surf = self.create_multilingual_surface(proceed_text, "normal", self.colors["green"])
            proceed_rect = proceed_surf.get_rect(centerx=box_center_x,
                                                 bottom=dt_y_abs - line_height_for_prompt * 0.5)
            self.screen.blit(proceed_surf, proceed_rect)

            if self.show_cursor:
                cursor_x = proceed_rect.right + font_normal.size(" ")[0] * 0.5
                self.draw_block_cursor(cursor_x, proceed_rect.top,
                                       font_normal, self.colors["green"], "normal")


    def _draw_complete_screen(self, box_center_x, text_max_width):
        lh_normal = self.get_unified_line_height("normal")
        # Use self.displayed_text for typing effect
        self.render_text_with_glow(self.displayed_text, box_center_x,
                                   self.content_box_y + self.content_box_height // 2, # Vertically centered
                                   self.colors["green"], size_type="normal",
                                   max_w_in_box=text_max_width,
                                   line_height_override=lh_normal, center_x_rel_to_box=True, center_y_rel_to_box=True)

    def _draw_art_film_screen(self, box_center_x, text_max_width):
        lh_large = self.get_unified_line_height("large")
        # Use self.displayed_text for typing effect
        self.render_text_with_glow(self.displayed_text, box_center_x,
                                   self.content_box_y + self.content_box_height // 2, # Vertically centered
                                   self.colors["green"], size_type="large",
                                   max_w_in_box=text_max_width,
                                   line_height_override=lh_large, center_x_rel_to_box=True, center_y_rel_to_box=True)

    def _draw_settings_screen(self, content_x_start, content_y_start, text_max_width):
        lh_normal = self.get_unified_line_height("normal")
        lh_large = self.get_unified_line_height("large") # For title

        # Settings title is displayed immediately (no typing)
        # self.displayed_text should already be set to the title in set_state
        title_y, _ = self.render_text_with_glow(
            self.displayed_text, # This is "ENVIRONMENT CONFIGURATION"
            content_x_start, content_y_start, self.colors["green"],
            size_type="large", max_w_in_box=text_max_width,
            line_height_override=lh_large # Use large line height for title
        )
        current_y = title_y # Start options below title
        
        options = [
            f"{self.get_text('settings_language')}{self.get_text('lang_ko' if self.language == 'KO' else 'lang_en')}",
            f"{self.get_text('settings_sound')}{self.get_text('sound_on') if self.sound_enabled else self.get_text('sound_off')}",
            self.get_text('settings_key_guide'),
            self.get_text('settings_back_to_game')
        ]
        
        option_lh = lh_normal # Use normal line height for options
        current_y += int(option_lh * 0.5) # Add a small gap after title

        for i, option_text_raw in enumerate(options):
            display_text = f"> {option_text_raw}" if i == self.current_settings_selection else f"  {option_text_raw}"
            
            # Render each option text. Note: content_x_start is the left alignment point.
            next_y_after_option, _ = self.render_text_with_glow(
                display_text, content_x_start, current_y,
                self.colors["green"], size_type="normal",
                max_w_in_box=text_max_width,
                line_height_override=option_lh
            )
            current_y = next_y_after_option + int(option_lh * 0.1) # Small gap between options
        
        hint_font_size_type = "small"
        hint_lh = self.get_unified_line_height(hint_font_size_type)
        # Position hint near the bottom, centered
        hint_y_pos = self.content_box_y + self.content_box_height - (hint_lh * 2) # Above date/time
        
        self.render_text_with_glow(
            self.get_text("settings_nav_hint"),
            self.content_box_x + self.content_box_width // 2, # Center X of hint
            hint_y_pos, self.colors["green"],
            size_type=hint_font_size_type, max_w_in_box=text_max_width,
            line_height_override=hint_lh, center_x_rel_to_box=True # Center the hint text block
        )

    def _draw_key_guide_screen(self, content_x_start, content_y_start, text_max_width, dt_y_abs):
        lh_normal = self.get_unified_line_height("normal")
        lh_small = self.get_unified_line_height("small")
        font_small_obj = self.get_current_font("small") # For "any key to close"

        # Key guide title is displayed immediately (no typing)
        # self.displayed_text is set in set_state
        title_y, _ = self.render_text_with_glow(self.displayed_text, # This is "KEY ASSIGNMENTS"
                                               content_x_start, content_y_start, self.colors["green"],
                                               size_type="normal", max_w_in_box=text_max_width, line_height_override=lh_normal)
        current_y = title_y + int(lh_normal * 0.5) # Gap after title

        key_bindings = [
            self.get_text("key_f1_settings"), self.get_text("key_f9_auto"),
            self.get_text("key_f10_screenshot"), self.get_text("key_b_back"),
            self.get_text("key_esc_exit"),
        ]
        font_normal_obj = self.get_current_font("normal") # For indent calculation
        indent_width = font_normal_obj.size("  ")[0] # Two spaces for indent

        for binding in key_bindings:
            # Render each binding indented
            _, last_rect = self.render_text_with_glow(binding, content_x_start + indent_width, current_y,
                                                      self.colors["green"], size_type="normal",
                                                      max_w_in_box=text_max_width - indent_width, # Adjust max width for indent
                                                      line_height_override=lh_normal)
            current_y = last_rect.bottom + int(lh_normal * 0.3) # Gap between bindings

        close_text = self.get_text("press_any_key_close")
        # 안내 문구도 수동으로 빛 번짐 적용
        if self.glow_enabled:
            glow_color = self.colors.get("glow_green")
            for ox, oy in self.glow_offsets:
                close_surf_glow = self.create_multilingual_surface(close_text, "small", glow_color)
                close_rect_glow = close_surf_glow.get_rect(centerx=self.content_box_x + self.content_box_width // 2 + ox,
                                                       bottom=dt_y_abs - lh_small * 0.5 + oy)
                self.screen.blit(close_surf_glow, close_rect_glow)
        # Use create_multilingual_surface for "any key" text
        close_surf = self.create_multilingual_surface(close_text, "small", self.colors["green"])
        close_rect = close_surf.get_rect(centerx=self.content_box_x + self.content_box_width // 2, # Center X
                                         bottom=dt_y_abs - lh_small * 0.5) # Position above date/time
        self.screen.blit(close_surf, close_rect)


    def _draw_name_input_screen(self, box_center_x, text_max_width, dt_y_abs):
        lh_large = self.get_unified_line_height("large")
        lh_normal = self.get_unified_line_height("normal")
        lh_small = self.get_unified_line_height("small") # For confidential text
        font_normal_obj = self.get_current_font("normal") # For dash line and input prompt

        current_y = self.content_box_y + self.content_box_height // 6 # Start title lower

        # Title (e.g., "SUBJECT IDENTIFICATION") with typing effect
        title_num_lines_approx = self.get_text("name_input_title").count('\n') + 1 # Approx lines for full title
        title_block_height_approx = title_num_lines_approx * lh_large
        
        # Render the currently typed portion of the title
        # The Y position for render_text_multiline is the top of the text block
        self.render_text_with_glow(self.displayed_text, # Uses self.displayed_text for typing
                                    box_center_x, current_y,
                                    self.colors["green"], size_type="large",
                                    max_w_in_box=text_max_width, line_height_override=lh_large,
                                    center_x_rel_to_box=True, center_y_rel_to_box=False) # Y is top

        # Update current_y to be below the fully rendered title (approximate)
        current_y += title_block_height_approx + int(lh_large * 0.3) # Add gap after title

        if not self.current_text or self.typing_index >= len(self.current_text): # If title typing is done
            # Dash line
            dash_char_width = font_normal_obj.size("-")[0] if font_normal_obj.size("-")[0] > 0 else 10 # Width of a dash
            num_dashes = (self.content_box_width // dash_char_width) - 12 # Approx num dashes
            dash_line = "-" * num_dashes
            # Use create_multilingual_surface for dash line for safety, though likely not needed
            dash_surf = self.create_multilingual_surface(dash_line, "normal", self.colors["green"])
            dash_rect = dash_surf.get_rect(centerx=box_center_x, top=current_y)
            self.screen.blit(dash_surf, dash_rect)
            current_y = dash_rect.bottom + int(lh_normal * 1.2) # Gap after dash

            # "Please enter your full name:" prompt
            prompt_text = self.get_text("name_input_prompt")
            if self.glow_enabled:
                for ox, oy in self.glow_offsets:
                    prompt_surf_glow = self.create_multilingual_surface(prompt_text, "normal", self.colors.get("glow_green"))
                    prompt_rect_glow = prompt_surf_glow.get_rect(centerx=box_center_x + ox, top=current_y + oy)
                    self.screen.blit(prompt_surf_glow, prompt_rect_glow)
            prompt_surf = self.create_multilingual_surface(prompt_text, "normal", self.colors["green"])
            prompt_rect = prompt_surf.get_rect(centerx=box_center_x, top=current_y)
            self.screen.blit(prompt_surf, prompt_rect)
            current_y = prompt_rect.bottom + int(lh_normal * 0.5) # Gap after prompt

            # User input text display (name being typed)
            display_text_for_input = self.user_input_text + self.ime_composition_text
            if self.glow_enabled:
                for ox, oy in self.glow_offsets:
                    input_text_surf_glow = self.create_multilingual_surface(display_text_for_input, "normal", self.colors.get("glow_green"))
                    input_text_rect_glow = input_text_surf_glow.get_rect(centerx=box_center_x + ox, top=current_y + oy)
                    self.screen.blit(input_text_surf_glow, input_text_rect_glow)
            input_text_surf = self.create_multilingual_surface(display_text_for_input, "normal", self.colors["green"])
            input_text_rect = input_text_surf.get_rect(centerx=box_center_x, top=current_y)
            self.screen.blit(input_text_surf, input_text_rect)
            
            # Underline for input field
            underline_y = input_text_rect.bottom + 3
            # Underline width based on MAX_NAME_LENGTH and approx char width
            # Use 'M' as a representative wide character for average width calculation
            ref_char_width_for_underline = font_normal_obj.size("M")[0] if font_normal_obj.size("M")[0] > 0 else 15
            underline_width = ref_char_width_for_underline * self.input_max_length
            pygame.draw.line(self.screen, self.colors["dark_green"],
                             (box_center_x - underline_width // 2, underline_y),
                             (box_center_x + underline_width // 2, underline_y), 2)

            # Cursor drawing
            if self.user_input_active and self.show_cursor:
                cursor_x_abs = input_text_rect.left # Default to start of input area
                if display_text_for_input: # If there's text (typed or composing)
                    # Calculate width of the displayed text (user_input + ime_composition)
                    # We already have input_text_surf for this
                    cursor_x_abs = input_text_rect.left + input_text_surf.get_width()
                elif not self.user_input_text and not self.ime_composition_text: # No text at all
                    cursor_x_abs = input_text_rect.centerx # Center cursor if field is empty
                
                # Use the font_normal_obj for cursor metrics, as input text uses "normal" size
                self.draw_block_cursor(cursor_x_abs, input_text_rect.top,
                                       font_normal_obj, self.colors["green"], "normal")

            current_y = underline_y + int(lh_normal * 1.5) # Gap after underline

            # Confidentiality notice
            self.render_text_with_glow(self.get_text("name_input_confidential"), box_center_x, current_y,
                                       self.colors["green"], size_type="small", max_w_in_box=text_max_width * 0.9,
                                       line_height_override=lh_small, center_x_rel_to_box=True)

            # "Press ENTER" prompt near bottom
            enter_prompt_text = self.get_text("name_input_enter_prompt")
            if self.glow_enabled:
                for ox, oy in self.glow_offsets:
                    enter_prompt_surf_glow = self.create_multilingual_surface(enter_prompt_text, "normal", self.colors.get("glow_green"))
                    enter_prompt_rect_glow = enter_prompt_surf_glow.get_rect(centerx=box_center_x + ox, bottom=dt_y_abs - int(lh_normal*0.5) + oy)
                    self.screen.blit(enter_prompt_surf_glow, enter_prompt_rect_glow)
            enter_prompt_surf = self.create_multilingual_surface(enter_prompt_text, "normal", self.colors["green"])
            enter_prompt_rect = enter_prompt_surf.get_rect(centerx=box_center_x, bottom=dt_y_abs - int(lh_normal*0.5))
            self.screen.blit(enter_prompt_surf, enter_prompt_rect)


    def _draw_psych_test_screen(self, content_x_start, content_y_start, text_max_width):
        lh_normal = self.get_unified_line_height("normal")
        font_normal_obj = self.get_current_font("normal") # For input prompt and answer

        # Render the question text (self.displayed_text has the typing effect)
        # content_x_start is the left alignment for the question block
        next_y_after_question, last_question_line_rect = self.render_text_with_glow(
            self.displayed_text, # This contains "QUESTION X/Y \n\n Question text \n\n 1. Yes \n 2. No"
            content_x_start, content_y_start, self.colors["green"],
            size_type="normal",
            max_w_in_box=text_max_width, line_height_override=lh_normal
        )

        # Only show input prompt and cursor if question typing is complete
        if not self.current_text or self.typing_index >= len(self.current_text):
            # Position input prompt line below the last line of the question/options
            input_line_y = next_y_after_question 
            if last_question_line_rect: # If question text was actually rendered
                 input_line_y = last_question_line_rect.bottom + int(lh_normal * 0.1) # Small gap
            else: # Fallback if no question text (should not happen)
                 input_line_y += int(lh_normal * 0.5)


            # "YOUR SELECTION (1.YES / 2.NO): " prompt
            input_prompt_text = self.get_text("psych_input_prompt") # Already has "YOUR SELECTION..."
            if self.glow_enabled:
                for ox, oy in self.glow_offsets:
                    input_prompt_surf_glow = self.create_multilingual_surface(input_prompt_text, "normal", self.colors.get("glow_green"))
                    self.screen.blit(input_prompt_surf_glow, (content_x_start + ox, input_line_y + oy))
            input_prompt_surf = self.create_multilingual_surface(input_prompt_text, "normal", self.colors["green"])
            # Draw prompt at content_x_start (left aligned)
            self.screen.blit(input_prompt_surf, (content_x_start, input_line_y))

            # User's answer ('1' or '2')
            input_text_x = content_x_start + input_prompt_surf.get_width() # Position answer after prompt
            if self.glow_enabled:
                for ox, oy in self.glow_offsets:
                    answer_surf_glow = self.create_multilingual_surface(self.user_input_text, "normal", self.colors.get("glow_green"))
                    self.screen.blit(answer_surf_glow, (input_text_x + ox, input_line_y + oy))
            # Use create_multilingual_surface for the single digit answer for consistency
            answer_surf = self.create_multilingual_surface(self.user_input_text, "normal", self.colors["green"])
            self.screen.blit(answer_surf, (input_text_x, input_line_y))

            if self.user_input_active and self.show_cursor:
                # Cursor after the typed answer ('1' or '2')
                cursor_x = input_text_x + answer_surf.get_width()
                self.draw_block_cursor(cursor_x, input_line_y, # Align cursor top with text top
                                       font_normal_obj, self.colors["green"], "normal")
            # --- 추가된 안내 문구 렌더링 부분 ---
            dt_x_abs, dt_y_abs, _, _, _ = self._draw_base_ui_elements()
            box_center_x = self.content_box_x + self.content_box_width // 2
            lh_small = self.get_unified_line_height("small")

            # "숫자 입력 후 ENTER" 안내
            enter_prompt_text = self.get_text("number_input_enter_prompt")
            enter_prompt_surf = self.create_multilingual_surface(enter_prompt_text, "small", self.colors["green"])
            # 위치 계산: 뒤로가기 안내 문구 바로 위에 오도록 설정
            enter_prompt_rect = enter_prompt_surf.get_rect(centerx=box_center_x, bottom=dt_y_abs - int(lh_small * 0.5))
            self.render_text_with_glow(enter_prompt_text, enter_prompt_rect.x, enter_prompt_rect.y, self.colors["green"], "small", center_x_rel_to_box=False)

            # "뒤로가기(B)" 안내 (빛 번짐 효과 적용)
            back_key_text = self.get_text("press_b_to_go_back")
            back_key_surf = self.create_multilingual_surface(back_key_text, "small", self.colors["green"])
            # 위치 계산: 화면 맨 아래 날짜/시간 바로 위에 오도록 설정
            back_key_rect = back_key_surf.get_rect(centerx=box_center_x, bottom=enter_prompt_rect.top) # ENTER 안내 문구 위에 위치하도록 수정
            # render_text_with_glow를 사용하여 빛 번짐 효과 렌더링
            self.render_text_with_glow(back_key_text, back_key_rect.x, back_key_rect.y, self.colors["green"], "small", center_x_rel_to_box=False)
            # --- 여기까지 수정 ---


    def draw_screen(self):
        self.screen.fill(self.colors["black"])

        if self.debug_draw_content_box_border:
            pygame.draw.rect(self.screen, self.colors["gray"],
                             (self.content_box_x - 1, self.content_box_y - 1,
                              self.content_box_width + 2, self.content_box_height + 2), 1)

        dt_x_abs, dt_y_abs, dt_surface, auto_mode_surf, auto_mode_rect = self._draw_base_ui_elements()

        content_x_start = self.content_box_x + (self.content_box_width // CONTENT_BOX_PADDING_RATIO)
        # Adjusted content_y_start for more padding from top, affects where text blocks begin.
        content_y_start = self.content_box_y + (self.content_box_height // 10) # Was // 7
        
        box_center_x = self.content_box_x + self.content_box_width // 2
        box_center_y = self.content_box_y + self.content_box_height // 2
        text_max_width = self.content_box_width - 2 * (self.content_box_width // CONTENT_BOX_PADDING_RATIO)

        if self.game_state == STATE_LANGUAGE_SELECT:
            self._draw_language_select_screen(box_center_x, box_center_y, text_max_width)
        elif self.game_state == STATE_NEW_TITLE:
            self._draw_new_title_screen(box_center_x, box_center_y, text_max_width)
        elif self.game_state == STATE_INTRODUCTION_P1:
            self._draw_introduction_screen(STATE_INTRODUCTION_P1, box_center_x, text_max_width, dt_y_abs)
        elif self.game_state == STATE_INTRODUCTION_P2:
            self._draw_introduction_screen(STATE_INTRODUCTION_P2, box_center_x, text_max_width, dt_y_abs)
        elif self.game_state == STATE_NAME_INPUT:
            self._draw_name_input_screen(box_center_x, text_max_width, dt_y_abs)
        elif self.game_state.startswith("PSYCH_TEST_Q"):
            # 질문을 화면 중앙으로 이동
            adjusted_y_start = self.content_box_y + (self.content_box_height // 4)  # 상단에서 1/4 지점부터 시작
            self._draw_psych_test_screen(content_x_start, adjusted_y_start, text_max_width)
        elif self.game_state == STATE_SHOW_RESULT:
            self._draw_show_result_screen(content_x_start, content_y_start, box_center_x, text_max_width)
        elif self.game_state == STATE_PRE_FLOPPY_NOTICE:
            self._draw_complete_screen(box_center_x, text_max_width)
        elif self.game_state == STATE_FLOPPY_INSERT_GUIDE:
            self._draw_floppy_guide_screen(box_center_x, box_center_y, text_max_width)
        elif self.game_state == STATE_WRONG_FLOPPY_ERROR:
            lh_normal = self.get_unified_line_height("normal")
            self.render_text_with_glow(self.displayed_text, box_center_x, box_center_y,
                                       self.colors["green"], size_type="normal",
                                       max_w_in_box=text_max_width,
                                       line_height_override=lh_normal,
                                       center_x_rel_to_box=True, center_y_rel_to_box=True)
        elif self.game_state == STATE_FLOPPY_CHECK:
            self._draw_floppy_check_screen(box_center_x, text_max_width)
        elif self.game_state == STATE_VISUAL_ANALYSIS_SETUP:
            self._draw_visual_setup_screen(box_center_x, text_max_width)
        elif self.game_state == STATE_VISUAL_ANALYSIS_DISPLAY:
            self._draw_visual_display_screen(content_y_start, box_center_x, text_max_width, dt_y_abs)
        elif self.game_state == STATE_COMPLETE_SCREEN:
            self._draw_complete_screen(box_center_x, text_max_width)
        elif self.game_state == STATE_ART_FILM_NOTICE:
            self._draw_art_film_screen(box_center_x, text_max_width)
        elif self.game_state == STATE_SETTINGS:
            self._draw_settings_screen(content_x_start, content_y_start, text_max_width)
        elif self.game_state == STATE_KEY_GUIDE:
            self._draw_key_guide_screen(content_x_start, content_y_start, text_max_width, dt_y_abs)

        # Draw "Press Space" prompt if applicable (not for intro screens, they handle their own)
        if self.needs_space_to_progress and self.game_state not in [
            STATE_INTRODUCTION_P1, STATE_INTRODUCTION_P2, # Handled in _draw_introduction_screen
            STATE_FLOPPY_INSERT_GUIDE, # Handled in its own draw function
            STATE_NEW_TITLE, STATE_LANGUAGE_SELECT, # No space prompt needed
            STATE_NAME_INPUT, # Uses Enter prompt
            STATE_VISUAL_ANALYSIS_DISPLAY
        ] and not self.game_state.startswith("PSYCH_TEST_Q"): # Psych test uses Enter
            if not self.current_text or self.typing_index >= len(self.current_text):
                 self._draw_proceed_prompt(dt_y_abs, box_center_x)


        # Always draw date/time and auto mode status on top of other screen content
        # --- 여기부터 수정 ---
        # 시간 UI를 그릴 우상단 Y좌표를 여기서 직접 계산
        box_padding = self.content_box_width // CONTENT_BOX_PADDING_RATIO
        time_ui_y = self.content_box_y + box_padding
        
        # 반환된 dt_y_abs(하단 기준) 대신 새로 계산한 time_ui_y(상단 기준)를 사용해 그립니다.
        if self.game_state != STATE_VISUAL_ANALYSIS_DISPLAY:
            self.screen.blit(dt_surface, (dt_x_abs, time_ui_y))
        # --- 여기까지 수정 ---
        # self.screen.blit(auto_mode_surf, auto_mode_rect)
        
        # Apply scanlines to the entire screen (except for videos which have it applied locally)
        # if not ( (self.game_state == STATE_FLOPPY_INSERT_GUIDE and 'floppy' in self.video_players and self.video_players['floppy'].last_valid_frame) or \
        #          (self.game_state == STATE_VISUAL_ANALYSIS_DISPLAY and 'analysis' in self.video_players and self.video_players['analysis'].last_valid_frame) ) :
        #     if not (self.game_state == STATE_FLOPPY_INSERT_GUIDE and not ('floppy' in self.video_players and self.video_players['floppy'].last_valid_frame)): # if not floppy guide screen with its own scanlined monitor surf
        #          self.apply_static_scanline_effect(self.screen)
        #self.apply_static_scanline_effect(self.screen)

        pygame.display.flip()

    def _apply_random_glitch_effect(self):
        if random.random() < 0.0007: # Low probability
            original_surface_copy = self.screen.copy()
            glitch_color = random.choice([self.colors["white"], self.colors["black"], self.colors["green"]])
            self.screen.fill(glitch_color)
            if self.sound_enabled and "error" in self.sounds and self.sounds["error"]:
                 if random.random() < 1 : self.play_sound("error") # Play error sound sometimes with glitch
            pygame.display.flip()
            pygame.time.wait(random.randint(30, 80)) # Shorter, more frequent glitches
            self.screen.blit(original_surface_copy, (0, 0))
            # Optionally, add some line displacement here for a more complex glitch
            if random.random() < 0.5:
                for _ in range(random.randint(5,15)):
                    y_glitch = random.randint(0, self.screen_height)
                    x_offset = random.randint(-20, 20)
                    h_glitch = random.randint(1,3)
                    try:
                        glitched_strip = original_surface_copy.subsurface(pygame.Rect(0, y_glitch, self.screen_width, h_glitch)).copy()
                        self.screen.blit(glitched_strip, (x_offset, y_glitch))
                    except ValueError: # In case subsurface is out of bounds
                        pass
                pygame.display.flip()
                pygame.time.wait(random.randint(20,50))
                self.screen.blit(original_surface_copy, (0,0)) # Restore again


    def apply_static_scanline_effect(self, target_surface):
        pattern_height = self.scanline_visible_rows + self.scanline_gap_rows
        line_color = (*self.colors["black"], 70) # Slightly transparent black for scanlines (RGBA)
        
        # Create a scanline overlay surface once if it doesn't exist or dimensions change
        # This is an optimization, but direct drawing is fine for now.
        
        for y in range(target_surface.get_height()):
            if (y % pattern_height) >= self.scanline_visible_rows:
                # Draw line directly on target_surface
                pygame.draw.line(target_surface, line_color, (0, y), (target_surface.get_width(), y), 1)


    def draw_block_cursor(self, x_abs, y_abs, font_to_use, color, size_type="normal"):
        # M-width is a common way to get a representative character width
        char_width_M = font_to_use.size("M")[0]
        char_width_space = font_to_use.size(" ")[0] # Fallback if M is not available (e.g. some fonts)

        if char_width_M > 0:
            char_width = char_width_M
        elif char_width_space > 0: # If M is 0 (e.g. symbol font), use space width * 2
            char_width = char_width_space * 1.5 # Make it a bit wider than a space
        else:
            char_width = 10 # Absolute fallback if font gives no width info

        # Use unified line height for cursor height calculation
        unified_char_height = self.get_unified_line_height(size_type)
        # Visual height of the cursor block (slightly smaller than full line height)
        scaled_padding = max(1, int(4 * self.scale_factor))
        cursor_height_visual = max(1, unified_char_height - scaled_padding) # Ensure at least 1px, with padding
        
        # Correct Y position for the cursor block to align with text baseline
        # y_abs is typically the top of the text line.
        # We want the cursor to sit on the baseline, or appear vertically centered within the line.
        # (unified_char_height - cursor_height_visual) // 2 will center it vertically.
        cursor_y_corrected = y_abs + (unified_char_height - cursor_height_visual) // 2

        cursor_rect = pygame.Rect(x_abs, cursor_y_corrected, char_width, cursor_height_visual)
        pygame.draw.rect(self.screen, color, cursor_rect, 0) # Filled rectangle

    def _draw_base_ui_elements(self):
        # This method doesn't draw to screen directly, but prepares surfaces and rects
        # Screen border debug
        if self.debug_draw_content_box_border:
            pygame.draw.rect(self.screen, self.colors["gray"], # Drawn directly for debug
                             (self.content_box_x - 1, self.content_box_y - 1,
                              self.content_box_width + 2, self.content_box_height + 2), 1)

        box_padding = self.content_box_width // CONTENT_BOX_PADDING_RATIO
        # font_small = self.get_current_font("small") # 기존 small 폰트는 그대로 둡니다.
        lh_tiny = self.get_unified_line_height("tiny") # <<< 'tiny' 폰트의 높이를 가져옵니다.
        lh_small = self.get_unified_line_height("small") # 기존 small도 유지

        # Date/Time display
        dt_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Use create_multilingual_surface for date/time as it might contain numbers/symbols
        dt_surface = self.create_multilingual_surface(dt_text, "tiny", self.colors["green"]) # <<< "small"을 "tiny"로 변경
        
        dt_x_abs = self.content_box_x + self.content_box_width - dt_surface.get_width() - box_padding
        dt_y_abs = self.content_box_y + box_padding + self.content_box_height - lh_tiny - box_padding# <<< Y좌표를 상단 기준으로 변경
        # --- 여기부터 수정 ---
        if self.glow_enabled:
            # 시간 UI의 빛 번짐 효과를 그릴 '실제' 좌표 (우상단 기준)
            time_ui_y_for_glow = self.content_box_y + box_padding
            
            glow_color = self.colors.get("glow_green")
            for ox, oy in self.glow_offsets:
                dt_surface_glow = self.create_multilingual_surface(dt_text, "tiny", glow_color)
                # 빛 번짐 효과를 그릴 때만 계산된 우상단 좌표를 사용합니다.
                self.screen.blit(dt_surface_glow, (dt_x_abs + ox, time_ui_y_for_glow + oy))
        # --- 여기까지 수정 ---
        # Auto mode display
        auto_mode_text_str = self.get_text("auto_on_label") if self.auto_mode_active else self.get_text("auto_off_label")
        auto_mode_color = self.colors["green"] if self.auto_mode_active else self.colors["red_auto_off"]
        # Use create_multilingual_surface for auto mode text
        # Auto mode는 기존 'small' 크기를 유지합니다.
        auto_mode_surf = self.create_multilingual_surface(auto_mode_text_str, "small", auto_mode_color)
        
        auto_mode_rect = auto_mode_surf.get_rect(topright=(self.content_box_x + self.content_box_width - box_padding,
                                                          self.content_box_y + box_padding)) # Align to top-right of content box
        if self.glow_enabled:
            glow_color = self.colors.get("glow_green") if self.auto_mode_active else (80,0,0)
            for ox, oy in self.glow_offsets:
                auto_mode_surf_glow = self.create_multilingual_surface(auto_mode_text_str, "small", glow_color)
                # self.screen.blit(auto_mode_surf_glow, (auto_mode_rect.x + ox, auto_mode_rect.y + oy))
        # Original auto_mode_surf is returned, but we will blit it directly here now
        # self.screen.blit(auto_mode_surf, auto_mode_rect)
        
        # dt_y_abs를 tiny 폰트 높이(lh_tiny)를 사용하도록 수정합니다.
        return dt_x_abs, dt_y_abs, dt_surface, auto_mode_surf, auto_mode_rect


    def _draw_proceed_prompt(self, dt_y_abs, box_center_x):
        show_prompt = False
        # Determine if the "Press Space" prompt should be shown
        if self.needs_space_to_progress and \
           (not self.current_text or self.typing_index >= len(self.current_text)):
            # Only show for these specific states where space is the primary progression mechanism
            # and they don't have their own specific "proceed" messages drawn elsewhere.
            if self.game_state in [STATE_SHOW_RESULT, 
                                   STATE_VISUAL_ANALYSIS_DISPLAY, STATE_COMPLETE_SCREEN]:
                show_prompt = True

        if show_prompt:
            proceed_text = self.get_text("press_space_continue")
            font_normal = self.get_current_font("normal") # Get the font object
            line_height_for_prompt = self.get_unified_line_height("normal")
            if self.glow_enabled:
                glow_color = self.colors.get("glow_green")
                for ox, oy in self.glow_offsets:
                    proceed_surf_glow = self.create_multilingual_surface(proceed_text, "normal", glow_color)
                    proceed_rect_glow = proceed_surf_glow.get_rect(centerx=box_center_x + ox,
                                                                   bottom=dt_y_abs - line_height_for_prompt * 0.5 + oy)
                    self.screen.blit(proceed_surf_glow, proceed_rect_glow)
            # Use create_multilingual_surface for the prompt text
            proceed_surf = self.create_multilingual_surface(proceed_text, "normal", self.colors["green"])
            proceed_rect = proceed_surf.get_rect(centerx=box_center_x,
                                                 bottom=dt_y_abs - line_height_for_prompt * 0.5) # Position above date/time
            self.screen.blit(proceed_surf, proceed_rect)

            if self.show_cursor:
                cursor_x = proceed_rect.right + font_normal.size(" ")[0] * 0.5 # Space after text
                self.draw_block_cursor(cursor_x, proceed_rect.top, # Align cursor top with text top
                                       font_normal, self.colors["green"], "normal")


    def draw_radar_chart(self, surface, name, data_dict, labels_ordered_keys, chart_center_x_abs, chart_center_y_abs,
                     size, color):
        num_vars = len(labels_ordered_keys)
        max_val_on_chart = 2 # For traits with 2 questions. Neuroticism max is 2 now.
        if num_vars == 0: return

        angle_step = 2 * math.pi / num_vars
        font_small = self.get_current_font("small") # Get font object

        # Draw grid lines (concentric polygons) - 더 세밀한 눈금 (0.5 단위)
        grid_steps = [0.5, 1.0, 1.5, 2.0]
        for step in grid_steps:
            radius = size * (step / float(max_val_on_chart))
            grid_points = []
            for j in range(num_vars):
                angle = j * angle_step - math.pi / 2 # Start at top
                grid_points.append((chart_center_x_abs + radius * math.cos(angle),
                                    chart_center_y_abs + radius * math.sin(angle)))
            if len(grid_points) > 2:
                # 0.5 단위 선은 더 희미하게 표시
                if step % 1.0 == 0:
                    pygame.draw.polygon(surface, self.colors["dark_green"], grid_points, 4) # 정수 단위는 진하게
                else:
                    # 0.5 단위는 점선 효과를 위해 여러 짧은 선분으로 그리기
                    for k in range(len(grid_points)):
                        start_point = grid_points[k]
                        end_point = grid_points[(k + 1) % len(grid_points)]
                        # 점선 효과
                        segments = 20
                        for seg in range(0, segments, 2):  # 2칸씩 건너뛰어 점선 효과
                            t1 = seg / float(segments)
                            t2 = min((seg + 1) / float(segments), 1.0)
                            x1 = start_point[0] + (end_point[0] - start_point[0]) * t1
                            y1 = start_point[1] + (end_point[1] - start_point[1]) * t1
                            x2 = start_point[0] + (end_point[0] - start_point[0]) * t2
                            y2 = start_point[1] + (end_point[1] - start_point[1]) * t2
                            pygame.draw.line(surface, self.colors["dark_green"], (x1, y1), (x2, y2), 4)

        # Draw axes lines from center to edge for each variable
        for i, trait_key in enumerate(labels_ordered_keys):
            angle = i * angle_step - math.pi / 2
            end_x = chart_center_x_abs + size * math.cos(angle)
            end_y = chart_center_y_abs + size * math.sin(angle)
            pygame.draw.line(surface, self.colors["dark_green"], (chart_center_x_abs, chart_center_y_abs), (end_x, end_y), 2)

            # Get trait display name and render it
            label_text_key = f"trait_{trait_key.lower()}" # e.g. "trait_openness"
            label_text = self.get_text(label_text_key).capitalize()
            # If get_text fails, use trait_key as fallback
            if label_text.startswith("<") and label_text.endswith("_MISSING>"):
                label_text = trait_key.capitalize()

            # 언어별로 다른 오프셋 적용
            if self.language == "KO":
                # 한글은 더 가까이 배치
                base_offset = font_small.get_height() * 1.2# * self.scale_factor  # 기본 오프셋을 작게

                # 각도에 따른 추가 오프셋 (한글용)
                angle_deg = math.degrees(angle + math.pi / 2) % 360

                # 상단 레이블 (개방성)
                if 340 <= angle_deg or angle_deg <= 20:
                    extra_offset = 0 # font_small.get_height() * 0.1
                # 좌우 레이블들
                elif 70 <= angle_deg <= 110 or 250 <= angle_deg <= 290:
                    extra_offset = font_small.get_height() * 0.1
                else:
                    extra_offset = 0

            else:  # English
                # 영어는 더 멀리 배치
                base_offset = font_small.get_height() * 1.8# * self.scale_factor # 기본 오프셋을 크게

                # 각도에 따른 추가 오프셋 (영어용)
                angle_deg = math.degrees(angle + math.pi / 2) % 360

                # 상단 레이블 (Openness)
                if 340 <= angle_deg or angle_deg <= 20:
                    extra_offset = - font_small.get_height() * 0.4
                # 오른쪽 레이블들 (Conscientiousness)
                elif 60 <= angle_deg <= 80:
                    extra_offset = font_small.get_height() * 1.0  # 더 많이 밀어냄
                # 왼쪽 레이블들 (Neuroticism)
                elif 280 <= angle_deg <= 300:
                    extra_offset = font_small.get_height() * 0.8
                # 나머지 레이블들
                else:
                    extra_offset = - font_small.get_height() * 0.6

            total_offset = base_offset + extra_offset

            lx = chart_center_x_abs + (size + total_offset) * math.cos(angle)
            ly = chart_center_y_abs + (size + total_offset) * math.sin(angle)

            if self.glow_enabled:
                glow_color = self.colors.get("glow_green")
                for ox, oy in self.glow_offsets:
                     label_surf_glow = self.create_multilingual_surface(label_text, "small", glow_color)
                     label_rect_glow = label_surf_glow.get_rect(center=(lx + ox, ly + oy))
                     surface.blit(label_surf_glow, label_rect_glow)

            # 레이블 렌더링
            label_surf = self.create_multilingual_surface(label_text, "small", color)
            label_rect = label_surf.get_rect(center=(lx, ly))

            # 특정 레이블에 대한 미세 조정 (영어 긴 단어들)
            if self.language == "EN":
                if trait_key.lower() == "conscientiousness":
                    # Conscientiousness는 오른쪽으로 약간 더 이동
                    label_rect.centerx += font_small.get_height() * 0.5
                elif trait_key.lower() == "neuroticism":
                    # Neuroticism은 왼쪽으로 약간 더 이동
                    label_rect.centerx -= font_small.get_height() * 0.3

            surface.blit(label_surf, label_rect)

        # Plot data points
        points = []
        for i, trait_key in enumerate(labels_ordered_keys):
            angle = i * angle_step - math.pi / 2
            value = data_dict.get(trait_key, 0)
            # Normalize value against max_val_on_chart for plotting
            norm_val = min(value / float(max_val_on_chart), 1.0) * size if max_val_on_chart > 0 else 0
            norm_val = max(0, norm_val) # Ensure non-negative radius for plotting
            points.append((chart_center_x_abs + norm_val * math.cos(angle),
                           chart_center_y_abs + norm_val * math.sin(angle)))

        if len(points) > 2:
            pygame.draw.polygon(surface, color, points, 3) # Draw outline of the data shape
            # Create a temporary surface for the filled polygon with alpha transparency
            temp_alpha_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            temp_alpha_surface.fill((0,0,0,0)) # Fully transparent
            pygame.draw.polygon(temp_alpha_surface, (*color, 150), points) # Draw filled polygon with alpha
            surface.blit(temp_alpha_surface, (0,0)) # Blit onto main surface

    def play_sound(self, sound_key, force_channel_id=None, play_only_if_channel_free=False):
        if self.sound_enabled and sound_key in self.sounds and self.sounds[sound_key]:
            sound_to_play = self.sounds[sound_key]
            try:
                if force_channel_id is not None:
                    channel = pygame.mixer.Channel(force_channel_id)
                    if play_only_if_channel_free:
                        if not channel.get_busy():
                            channel.play(sound_to_play)
                    else:
                        channel.play(sound_to_play) # Play even if busy (will interrupt)
                else:
                    sound_to_play.play() # Play on any available channel
            except Exception as e:
                # This can happen if mixer channels are exhausted or other pygame.mixer errors
                print(f"Could not play sound '{sound_key}' (channel_id: {force_channel_id}): {e}")
        elif not self.sound_enabled:
            pass # Sound is disabled
        elif sound_key not in self.sounds or not self.sounds[sound_key]:
             print(f"Sound key '{sound_key}' not found or sound not loaded.")


    def cleanup(self):
        # 플로피 체크 스레드 종료
        if hasattr(self, 'floppy_check_running'):
            self.floppy_check_running = False
            if hasattr(self, 'floppy_check_thread') and self.floppy_check_thread:
                self.floppy_check_thread.join(timeout=1.0)
        
        if hasattr(self, 'data_logger'):
            self.data_logger.stop()
        
        for player in self.video_players.values():
            player.close()
        self.video_players.clear()

        # 플로피 비디오 플레이어 정리
        if hasattr(self, 'floppy_videos'):
            for video_player in self.floppy_videos:
                video_player.close()
            self.floppy_videos.clear()
        print("Video players released.")
        # OBS 연결 해제
        if self.obs_client:
            try:
                self.obs_client.disconnect()
                print("✅ OBS 연결 해제")
            except Exception as e:
                print(f"⚠️ OBS 연결 해제 실패: {e}")


    def run(self):
        while self.running:
            self.handle_events()
            self.update_state_logic()
            self.draw_screen()
            self._apply_random_glitch_effect() # Apply glitch after drawing normal screen

            # 플로피 가이드 화면에서는 낮은 프레임레이트 사용
            if self.game_state == STATE_FLOPPY_INSERT_GUIDE:
                self.clock.tick(60)  # 30 FPS로 제한
            else:
                self.clock.tick(60)  # 일반 화면은 60 FPS
        print("Exiting Program...")
        self.cleanup()


# --- 메인 실행 부분 ---
if __name__ == "__main__":
    game_instance = None
    try:
        game_instance = PsychologyTest()
        game_instance.run()
    except Exception as main_exception:
        print(f"\n--- CRITICAL RUNTIME ERROR ---")
        print(f"Error Type: {type(main_exception).__name__}")
        print(f"Error Message: {main_exception}")
        import traceback
        traceback.print_exc()
        print("------------------------------")
    finally:
        # if game_instance:
        #     game_instance.cleanup() # Ensure cleanup is called if instance exists
        if hasattr(pygame, 'mixer') and pygame.mixer.get_init():
            pygame.mixer.quit()
        if pygame.get_init():
            pygame.quit()
        print("Pygame resources released. Program terminated.")
        # sys.exit() # sys.exit() might be problematic if run in some environments like IDEs.
                   # Pygame quit should be enough to terminate.
                   # If script needs to force exit status, can be re-enabled.

#사운드추가, 스크린샷 잡버그

# 에러 느낌 고민필요
# Warning: Analysis video not found at C:\capstone\raemctrl\videos\analysis.mp4






# 룰베이스 스케치 인식 (관상팀..교수님조언)
# 사소한것들... 나중에 영어버전


# !!!!!!!!!!!!
# 최종에는 플로피인서트가이드 상태에서 스페이스바 눌러도 안넘어가게

# 최종 프로그램 두 개(각 데탑 두 대 모두) 전체 사운드 볼륨 체크
# 최종 전체 플로우 및 화면 디테일 상세히 체크
# 처음 두 소개 페이지 문구 crt모니터에서 확인하고 수정
# 유선 스피커 다이소에서 사서 로그 표시하는 컴퓨터에 연결 
# 에러 시 흰깜빡임 눈 아픔 어두운환경에서 <- 다시 체크해보기
# !!!!!!!!!!!!