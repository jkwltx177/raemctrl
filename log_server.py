import pygame
import socket
import json
import struct
import random
from datetime import datetime
import threading

# --- [시작] SecondaryMonitorDisplay 클래스 코드 ---
class SecondaryMonitorDisplay:
    def __init__(self):
        # 9인치 서브모니터 설정 (4:3 비율)
        self.screen_width = 480
        self.screen_height = 350
        self.session_count = 0

        pygame.init() 
        
        # 전체화면 또는 창 모드를 선택할 수 있습니다.
        # self.secondary_screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.NOFRAME)
        self.secondary_screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        pygame.display.set_caption("RAEMCTRL Data Logger (Server)")
            
        try:
            self.font = pygame.font.Font('fonts/CourierPrime-Regular.ttf', 18)
            self.font_small = pygame.font.Font('fonts/CourierPrime-Regular.ttf', 14)
        except:
            print("CourierPrime font not found, using fallback")
            self.font = pygame.font.SysFont('Courier New', 18)
            self.font_small = pygame.font.SysFont('Courier New', 14)
            
        self.log_buffer = []
        self.max_lines = 20
        self.left_margin = 10
        self.line_height = 20
        self.top_margin = 8
        self.cursor_visible = True
        self.cursor_timer = 0
        self.glow_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self.title = "RAEMCTRL DATA LOGGER v5.1 - LISTENING"
        self.is_connected = False

    def add_log_lines(self, lines):
        """여러 줄 추가"""
        for line in lines:
            self.log_buffer.append({
                'text': line,
                'timestamp': pygame.time.get_ticks(),
                'glow_alpha': 255
            })
        if len(self.log_buffer) > 100:
            self.log_buffer = self.log_buffer[-80:]
    
    def render(self):
        """9인치 서브모니터에 최적화된 렌더링"""
        # (render 메서드 내용은 ver66.py에서 그대로 복사)
        # --- [시작] render 메서드 ---
        self.secondary_screen.fill((0, 0, 0))
        
        # 타이틀 바 (연결 상태에 따라 색상 변경)
        title_bar_color = (0, 50, 0) if self.is_connected else (50, 0, 0)
        title_text = self.title
        if self.is_connected:
            title_text = "RAEMCTRL DATA LOGGER v5.1 - CONNECTED"

        pygame.draw.rect(self.secondary_screen, title_bar_color, 
                        (0, 0, self.screen_width, 22))
        title_surf = self.font_small.render(title_text, True, (0, 255, 0))
        self.secondary_screen.blit(title_surf, (self.left_margin, 10))
        
        time_str = datetime.now().strftime("%H:%M:%S")
        time_surf = self.font_small.render(time_str, True, (0, 200, 0))
        time_x = self.screen_width - time_surf.get_width() - self.left_margin * 2
        self.secondary_screen.blit(time_surf, (time_x, 10))
        
        pygame.draw.line(self.secondary_screen, (0, 100, 0), 
                        (0, 22), (self.screen_width, 22), 1)
        
        self.glow_surface.fill((0, 0, 0, 0))
        
        current_time = pygame.time.get_ticks()
        
        visible_lines = self.log_buffer[-self.max_lines:]
        
        y_offset = 35
        
        for i, line_data in enumerate(visible_lines):
            line = line_data['text']
            age = current_time - line_data['timestamp']
            
            glow_alpha = max(0, line_data['glow_alpha'] - age // 50)
            line_data['glow_alpha'] = glow_alpha
            
            if len(line) > 65:
                line = line[:62] + "..."
            
            if "Thread" in line and "name:" in line:
                color = (0, 255, 0)
            elif "//" in line:
                parts = line.split("//", 1)
                
                if parts[0].strip():
                    text_surf = self.font.render(parts[0], True, (0, 200, 0))
                    self.secondary_screen.blit(text_surf, (self.left_margin, y_offset))
                    
                    if len(parts) > 1:
                        comment_x = self.left_margin + text_surf.get_width()
                        max_comment_width = self.screen_width - comment_x - self.left_margin
                        comment_text = "//" + parts[1]
                        
                        if self.font.size(comment_text)[0] > max_comment_width:
                            while self.font.size(comment_text + "...")[0] > max_comment_width and len(comment_text) > 10:
                                comment_text = comment_text[:-1]
                            comment_text += "..."
                        
                        comment_surf = self.font.render(comment_text, True, (0, 150, 0))
                        self.secondary_screen.blit(comment_surf, (comment_x, y_offset))
                
                if glow_alpha > 0:
                    for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        glow_surf = self.font.render(line, True, (0, glow_alpha//6, 0))
                        self.glow_surface.blit(glow_surf, (self.left_margin + ox, y_offset + oy))
                
                y_offset += self.line_height
                continue
            else:
                color = (0, 200, 0)
            
            text_surf = self.font.render(line, True, color)
            self.secondary_screen.blit(text_surf, (self.left_margin, y_offset))
            
            if glow_alpha > 100:
                for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    glow_surf = self.font.render(line, True, (0, glow_alpha//6, 0))
                    self.glow_surface.blit(glow_surf, (self.left_margin + ox, y_offset + oy))
            
            y_offset += self.line_height
        
        self.secondary_screen.blit(self.glow_surface, (0, 0))
        
        self.cursor_timer += 1
        if self.cursor_timer > 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
        
        if self.cursor_visible and visible_lines:
            cursor_y = y_offset
            if cursor_y < self.screen_height - 15:
                cursor_surf = self.font.render("_", True, (0, 255, 0))
                self.secondary_screen.blit(cursor_surf, (self.left_margin, cursor_y))
        
        if random.random() < 0.003:
            glitch_height = random.randint(1, 5)
            glitch_y = random.randint(30, self.screen_height - glitch_height - 10)
            glitch_offset = random.randint(-10, 10)
            
            glitch_area = pygame.Surface((self.screen_width, glitch_height))
            glitch_area.blit(self.secondary_screen, (glitch_offset, 0), 
                           (0, glitch_y, self.screen_width, glitch_height))
            self.secondary_screen.blit(glitch_area, (0, glitch_y))
        
        status_y = self.screen_height - 20
        # pygame.draw.line(self.secondary_screen, (0, 100, 0), 
        #                 (0, status_y - 5), (self.screen_width, status_y - 5), 1)
        
        if hasattr(self, 'session_count'):
            status_text = f"Sessions: {self.session_count} | Buffer: {len(self.log_buffer)}"
            status_surf = self.font_small.render(status_text, True, (0, 150, 0))
            self.secondary_screen.blit(status_surf, (self.left_margin, status_y))
        
        pygame.display.flip()
        # --- [끝] render 메서드 ---

    def set_session_count(self, count):
        self.session_count = count
# --- [끝] SecondaryMonitorDisplay 클래스 코드 ---


def receive_all(sock, n):
    """네트워크 소켓으로부터 정확히 n 바이트를 수신하는 헬퍼 함수"""
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

def handle_client(client_socket, display):
    """클라이언트 연결을 처리하는 스레드 함수"""
    print("✅ Client connected.")
    display.is_connected = True
    display.title = "RAEMCTRL DATA LOGGER v5.1 - CONNECTED" # 연결 상태 반영

    try:
        while True:
            # 1. 메시지 길이를 먼저 받음 (4바이트 정수)
            raw_msg_len = receive_all(client_socket, 4)
            if not raw_msg_len:
                break
            msg_len = struct.unpack('>I', raw_msg_len)[0]

            # 2. 실제 메시지 데이터를 받음
            raw_data = receive_all(client_socket, msg_len)
            if not raw_data:
                break
            
            # 3. JSON 데이터를 파싱하여 로그 라인으로 변환
            log_lines = json.loads(raw_data.decode('utf-8'))
            
            # 4. 디스플레이에 로그 라인 추가
            display.add_log_lines(log_lines)
            
    except (ConnectionResetError, BrokenPipeError):
        print("ℹ️ Client connection lost.")
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        print("🔴 Client disconnected.")
        display.is_connected = False
        display.title = "RAEMCTRL DATA LOGGER v5.1 - LISTENING" # 연결 끊김 상태 반영
        client_socket.close()

def main():
    # --- 서버 설정 ---
    HOST = '0.0.0.0'  # 모든 IP 주소에서 오는 연결을 허용
    PORT = 51985       # 사용할 포트 번호 (클라이언트와 동일해야 함)

    display = SecondaryMonitorDisplay()
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"🚀 Log server listening on port {PORT}...")

    # 서버 소켓을 논블로킹으로 만들어 Pygame 루프를 방해하지 않도록 함
    server_socket.setblocking(False)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # 새 클라이언트 연결 확인
        try:
            client_sock, addr = server_socket.accept()
            print(f"Accepted connection from {addr}")
            client_sock.setblocking(True) # 클라이언트 소켓은 블로킹으로 동작
            
            # 새 스레드를 만들어 클라이언트 처리
            thread = threading.Thread(target=handle_client, args=(client_sock, display))
            thread.daemon = True
            thread.start()
        except BlockingIOError:
            # 연결 요청이 없으면 에러 발생, 정상적인 상황이므로 무시
            pass

        # 화면 렌더링
        display.render()
        pygame.time.wait(30) # CPU 사용량 조절

    server_socket.close()
    pygame.quit()
    print("Log server terminated.")

if __name__ == "__main__":
    main()