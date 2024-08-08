from Program import Program
import pygame
import os
import matplotlib as plt
import time
import tkinter as tk
from tkinter import messagebox
import sys
import subprocess
from PIL import Image, ImageTk, ImageDraw, ImageFont



class Agent:
    def __init__(self, x, y):
        self.x = x  # Vị trí theo trục x
        self.y = y  # Vị trí theo trục y
        self.direction = 'right'  # Hướng mà tác nhân đang đối diện
        self.jar = 0
        self.hp_pos = {}
        self.health = 100  # Sức khỏe của tác nhân
        self.alive = True  # Kiểm tra xem tác nhân còn sống hay không
        self.arrows = float('inf')  # Tác nhân có vô hạn tên
        self.percepts = {}  # Lưu trữ các percepts hiện tại
        self.score = 0  # Điểm số của tác nhân
        self.element_images = {'up': None, 'down': None, 'left': None, 'right': None, 'W': None, 'P': None, 'G': None,'H_P':None, 'P_G':None}
        self.percepts_image = {'B':None, 'S': None, 'G_L': None, 'W_H': None}
        self.gold_appear_time = {}
        self.gas_pos = []
        
    @staticmethod
    def realpos_to_virpos(N, x, y):
        return N - x, y + 1

    @staticmethod
    def virpos_to_realpos(N, x, y):
        return N - x, y - 1

    def graph(self, screen, N, map_matrix, agent_x, agent_y):
        # Kích thước mỗi ô
        cell_size = 75

        # Vẽ ma trận
        screen.fill((255, 255, 255))  # Màu nền trắng
        font = pygame.font.Font(None, 36)  # Tạo font để in ký tự

        for x in range(N):  # X đại diện cho hàng trong ma trận Wumpus World
            for y in range(N):  # Y đại diện cho cột
                # Tính toán tọa độ ô
                rect = pygame.Rect(y * cell_size, x * cell_size, cell_size, cell_size)  # Đọc bình thường

                # Vẽ ô với viền
                pygame.draw.rect(screen, (255, 255, 255), rect)  # Vẽ ô trống
                pygame.draw.rect(screen, (0, 0, 0), rect, 1)  # Vẽ viền

                # Hiển thị hình ảnh tại vị trí của tác nhân
                if x == agent_x and y == agent_y:
                    agent_rect = self.element_images[self.direction].get_rect(bottomleft=(rect.left, rect.bottom))
                    screen.blit(self.element_images[self.direction], agent_rect.topleft)
                    # Tọa độ cho element và percepts
                    element_char_x = rect.left + self.element_images[self.direction].get_width() + 3  # Bắt đầu từ bên phải của agent
                    element_char_y = rect.bottom - self.element_images[self.direction].get_height()  # Bắt đầu từ bên dưới

                    percept_char_x = rect.right - 3  # Bắt đầu từ bên phải
                    percept_char_y = rect.top + 2  # Bắt đầu từ góc trên bên phải
                    
                    for char in map_matrix[x][y]:  # Duyệt qua từng ký tự trong ô
                        if char in self.element_images:
                            element_rect = self.element_images[char].get_rect(topleft=(element_char_x, element_char_y))
                            screen.blit(self.element_images[char], element_rect.topleft)
                            element_char_x += self.element_images[char].get_width() + 2  # Di chuyển qua bên phải
                        elif char in self.percepts_image:
                            percept_rect = self.percepts_image[char].get_rect(topright=(percept_char_x, percept_char_y))
                            screen.blit(self.percepts_image[char], percept_rect.topleft)
                            percept_char_x -= self.percepts_image[char].get_width() + 2  # Di chuyển qua bên trái
                        else:
                            text = font.render(char, True, (0, 0, 0))  # Tạo đối tượng văn bản
                            text_rect = text.get_rect(topright=(percept_char_x, percept_char_y))  # Căn từ góc trên bên phải
                            screen.blit(text, text_rect)  # Vẽ văn bản lên ô
                            percept_char_x -= text.get_width() + 2  # Di chuyển qua bên trái

        # Vẽ thông tin điểm số và sức khỏe ở góc trên bên phải
        info_font = pygame.font.Font(None, 28)
        score_text = info_font.render(f"Score: {self.score}", True, (0, 0, 0))
        health_text = info_font.render(f"Health: {self.health}", True, (0, 0, 0))

        # Lấy kích thước của cửa sổ màn hình
        screen_width, screen_height = screen.get_size()

        # Vị trí hiển thị thông tin ở góc trên bên phải
        score_position = (75 * N + 100, 10)
        health_position = (75 * N + 100, 50)

        screen.blit(score_text, score_position)
        screen.blit(health_text, health_position)   

        pygame.display.flip()  # Cập nhật màn hình
        current_pos = (agent_x, agent_y)

        if 'G' in map_matrix[agent_x][agent_y]:  # Kiểm tra ô có vàng
                if current_pos not in self.gold_appear_time:
                    self.gold_appear_time[current_pos] = time.time()
                elif time.time() - self.gold_appear_time[current_pos] >= 1:
                    self.getgold = True
                    self.score += 5000
                    map_matrix[agent_x][agent_y].remove('G')
                    self.gold_appear_time.pop(current_pos)

        elif 'H_P' in map_matrix[agent_x][agent_y]:  # Kiểm tra ô có bình máu
                if current_pos not in self.hp_pos:
                    self.hp_pos[current_pos] = time.time()
                elif time.time() - self.hp_pos[current_pos] >= 1:
                    self.jar += 1
                    map_matrix[agent_x][agent_y].remove('H_P')
                    self.hp_pos.pop(current_pos)
                    if self.health < 100:
                        self.jar -= 1
                        self.health += 25

        elif 'P_G' in map_matrix[agent_x][agent_y]:  # Kiểm tra ô có Poison Gas
                if current_pos not in self.gas_pos:  # Nếu chưa có trong gas_pos
                    self.health -= 25
                    if self.jar > 0:    
                        self.jar -= 1
                        self.health += 25
                    elif self.health ==0: self.alive = False
                    self.gas_pos.append(current_pos)  # Lưu vị trí vào gas_pos
        elif 'P'in map_matrix[agent_x][agent_y] or 'W' in  map_matrix[agent_x][agent_y]:
                self.alive = False
        else: self.gas_pos.clear()

    def run(self, file_path):
        # Lấy kích thước và ma trận từ Program
        N, map_matrix = Program.update_map(file_path)
        agent_x = 1
        agent_y = 1
        agent_x, agent_y = Agent.virpos_to_realpos(N, agent_x, agent_y)

        # Khởi tạo Pygame
        pygame.init()
        screen = pygame.display.set_mode((600, 600))  # Kích thước cửa sổ
        pygame.display.set_caption("Wumpus World")
        image_folder = os.path.join(os.getcwd(), 'image')

        # Tải hình ảnh của tác nhân
        self.element_images = {
            'up': pygame.image.load(os.path.join(image_folder, 'up.png')),
            'down': pygame.image.load(os.path.join(image_folder, 'down.png')),
            'left': pygame.image.load(os.path.join(image_folder, 'left.png')),
            'right': pygame.image.load(os.path.join(image_folder, 'right.png')),
            'W': pygame.image.load(os.path.join(image_folder, 'wum.png')),
            'P': pygame.image.load(os.path.join(image_folder, 'pit.png')),
            'G': pygame.image.load(os.path.join(image_folder, 'gold.png')),
            'H_P': pygame.image.load(os.path.join(image_folder, 'hp.png')),
            'P_G': pygame.image.load(os.path.join(image_folder, 'gas.png')),
        }

        
        for key in self.element_images:
            self.element_images[key] = pygame.transform.scale(self.element_images[key], (30, 30))  # Thay đổi kích thước hình ảnh
        

        
        # Tải hình ảnh của percepts
        # Tạo từ điển chứa các hình ảnh của percepts
        self.percepts_image = {
            'B': pygame.image.load(os.path.join(image_folder, 'breeze.png')),
            'S': pygame.image.load(os.path.join(image_folder, 'stench.png')),
            'G_L': pygame.image.load(os.path.join(image_folder, 'glow.png')),
            'W_H': pygame.image.load(os.path.join(image_folder, 'whiff.png')),
        }

        
        for key in self.percepts_image:
            self.percepts_image[key] = pygame.transform.scale(self.percepts_image[key], (20, 20))  # Thay đổi kích thước hình ảnh

        directions = ['up', 'right', 'down', 'left']

        while self.alive:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.alive = False
                elif event.type == pygame.KEYDOWN:
                    self.score -= 10
                    if event.key == pygame.K_LEFT:
                        current_index = directions.index(self.direction)
                        self.direction = directions[(current_index - 1) % 4]
                    elif event.key == pygame.K_RIGHT:
                        current_index = directions.index(self.direction)
                        self.direction = directions[(current_index + 1) % 4]
                    elif event.key == pygame.K_UP:
                        if self.direction == 'up':
                            agent_x = max(agent_x - 1, 0)
                        elif self.direction == 'down':
                            agent_x = min(agent_x + 1, N - 1)
                        elif self.direction == 'left':
                            agent_y = max(agent_y - 1, 0)
                        elif self.direction == 'right':
                            agent_y = min(agent_y + 1, N - 1)

                     # Lấy tọa độ hiện tại của tác nhân
            

            if self.health <= 0 or self.alive == False:
                show_game_over(self,screen)
                self.alive = False
               
                break

            self.graph(screen, N, map_matrix, agent_x, agent_y)
        show_game_over(self,screen)

def show_game_over(self, screen):
    # Tạo cửa sổ thông báo "Game Over"
    game_over_window = tk.Tk()
    game_over_window.title("Game Over")
    game_over_window.geometry("800x450")  # Thay đổi kích thước cửa sổ

    # Đường dẫn đến thư mục chứa hình ảnh
    image_folder = os.path.join(os.getcwd(), 'image')
   
    # Mở hình ảnh nền
    background_image_path = os.path.join(image_folder, "adtime.jpg")
    background_image = Image.open(background_image_path)
    background_photo = ImageTk.PhotoImage(background_image)

    # Tạo canvas để đặt hình nền
    canvas = tk.Canvas(game_over_window, width=800, height=450)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=background_photo, anchor="nw")

    # Tạo ảnh có nền trong suốt và văn bản
    def create_text_image(text, font_path, font_size, text_color):
        image = Image.new('RGBA', (800, 100), (0, 0, 0, 0))  # Tạo ảnh trong suốt
        draw = ImageDraw.Draw(image)
        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((800 - text_width) // 2, (100 - text_height) // 2)
        draw.text(position, text, font=font, fill=text_color)
        return ImageTk.PhotoImage(image)

    # Sử dụng font hệ thống Comic Sans MS
    font_path = "comic.ttf"  # Comic Sans MS thường có sẵn trên hầu hết các hệ thống

    # Tạo ảnh văn bản "Game Over"
    game_over_image = create_text_image("Game Over", font_path, 60, (255,153,204))
    canvas.create_image(400, 50, image=game_over_image, anchor="center")

    # Tạo ảnh văn bản cho điểm số và sức khỏe
    score_image = create_text_image(f"Score: {self.score}", font_path, 24, "white")
    health_image = create_text_image(f"Health: {self.health}", font_path, 24, "white")
    canvas.create_image(400, 150, image=score_image, anchor="center")
    canvas.create_image(400, 200, image=health_image, anchor="center")

     # Tạo các lớp phủ bán trong suốt
    overlay_color = "#000000"  # Màu nền của lớp phủ
    overlay_opacity = 128  # Độ mờ (0-255)

    replay_overlay = canvas.create_rectangle(300, 300, 400, 350, fill=overlay_color, stipple="gray25")
    exit_overlay = canvas.create_rectangle(450, 300, 550, 350, fill=overlay_color, stipple="gray25")

    # Tạo nút "Chơi lại"
    replay_button = tk.Button(game_over_window, text="Retry", font=("Comic Sans MS", 20), command=lambda: restart_game(self, game_over_window))
    replay_button_window = canvas.create_window(300, 300, anchor="nw", window=replay_button)

    # Tạo nút "Thoát game"
    exit_button = tk.Button(game_over_window, text="Quit", font=("Comic Sans MS", 20), command=lambda: exit_game(self))
    exit_button_window = canvas.create_window(450, 300, anchor="nw", window=exit_button)


    game_over_window.mainloop()

def restart_game(self, game_over_window):
    game_over_window.destroy()
    pygame.quit()  # Kết thúc Pygame
    subprocess.call([sys.executable, 'main.py'])  # Gọi lại script chính (main.py)

def exit_game(self):
    pygame.quit()
    sys.exit()