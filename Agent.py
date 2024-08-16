from Program import Program
import pygame
import os
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

    def load_images(self, image_folder):
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

        self.percepts_image = {
            'B': pygame.image.load(os.path.join(image_folder, 'breeze.png')),
            'S': pygame.image.load(os.path.join(image_folder, 'stench.png')),
            'G_L': pygame.image.load(os.path.join(image_folder, 'glow.png')),
            'W_H': pygame.image.load(os.path.join(image_folder, 'whiff.png')),
        }
        for key in self.percepts_image:
            self.percepts_image[key] = pygame.transform.scale(self.percepts_image[key], (20, 20))  # Thay đổi kích thước hình
        
    @staticmethod
    def realpos_to_virpos(N, x, y):
        return N - x, y + 1

    @staticmethod
    def virpos_to_realpos(N, x, y):
        return N - x, y - 1

    
    def graph(self, screen, N, map_matrix, agent_x, agent_y):
        # Kích thước mỗi ô
        cell_size = 60
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
                    

        # Vẽ thông tin điểm số và sức khỏe ở góc trên bên phải
        info_font = pygame.font.Font(None, 28)
        score_text = info_font.render(f"Score: {self.score}", True, (0, 0, 0))
        health_text = info_font.render(f"Health: {self.health}", True, (0, 0, 0))

        # Vị trí hiển thị thông tin ở góc trên bên phải
        score_position = (cell_size * N + 100, 10)
        health_position = (cell_size * N + 100, 50)

        screen.blit(score_text, score_position)
        screen.blit(health_text, health_position)

        # Hiển thị các hình ảnh và tên của percepts và elements dưới score và health
        # Từ điển ánh xạ từ key sang tên cụ thể của các elements và percepts
        element_name_map = (
            'Move Up',
            'Move Down',
             'Move Left',
             'Move Right',
            'Wumpus',
             'Pit',
            'Gold',
            'Healing Potions',
             'Poisonous Gas'
        )

        percept_name_map = (
            'Breeze',
            'Stench',
            'Glow',
            'Whiff'
        )
        element_y_position = 90  # Vị trí y để bắt đầu hiển thị các phần tử và percepts
        for i, (key, image) in enumerate(self.element_images.items()):
            if image:  # Kiểm tra nếu hình ảnh tồn tại
                image_rect = image.get_rect(topleft=(cell_size * N + 100, element_y_position))
                screen.blit(image, image_rect.topleft)
                text = info_font.render(element_name_map[i], True, (0, 0, 0))  # Lấy tên từ element_name_map
                screen.blit(text, (cell_size * N + 140, element_y_position))
                element_y_position += image.get_height() + 10  # Cập nhật vị trí y cho phần tử tiếp theo

        percept_y_position = element_y_position  # Tiếp tục từ vị trí dưới cùng của elements
        for i, (key, image) in enumerate(self.percepts_image.items()):
            if image:  # Kiểm tra nếu hình ảnh tồn tại
                image_rect = image.get_rect(topleft=(cell_size * N + 100, percept_y_position))
                screen.blit(image, image_rect.topleft)
                text = info_font.render(percept_name_map[i], True, (0, 0, 0))  # Lấy tên từ percept_name_map
                screen.blit(text, (cell_size * N + 140, percept_y_position))
                percept_y_position += image.get_height() + 10  # Cập nhật vị trí y cho percept tiếp theo

        pygame.display.flip()  # Cập nhật màn hình
        current_pos = (agent_x, agent_y)

   
    def run(self, file_path):
        # Lấy kích thước và ma trận từ Program
        N, map_matrix = Program.update_map(file_path)
        agent_x = 1
        agent_y = 1
        agent_x, agent_y = Agent.virpos_to_realpos(N, agent_x, agent_y)

        # Khởi tạo Pygame
        pygame.init()
        screen = pygame.display.set_mode((900,650))  # Kích thước cửa sổ
        pygame.display.set_caption("Wumpus World")
        image_folder = os.path.join(os.getcwd(), 'image')

        # Tải hình ảnh của tác nhân và percepts
        self.load_images(image_folder)

        # Vẽ trạng thái ban đầu và nút Play
        self.graph(screen, N, map_matrix, agent_x, agent_y)
        button_rect = draw_play_button(screen)
        pygame.display.flip()

        # Chờ người dùng nhấn nút Play
        play_game = False
        while not play_game:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if button_rect.collidepoint(event.pos):
                        play_game = True  # Người dùng nhấn nút Play, bắt đầu trò chơi

        # Sau khi nhấn nút Play, bắt đầu trò chơi
        directions = ['up', 'right', 'down', 'left']
        position_path = [(1, 2), (1, 2), (2, 2), (3, 2), (3, 2), (3, 2), (3, 2), (3, 3)]
        action_path = ['move_fw', 'turn_left', 'move_fw', 'move_fw', 'grab', 'turn_right', 'shoot', 'move_fw']

        path_index = 0  # Chỉ số hiện tại của path
        while self.alive:
            # Cập nhật màn hình với trạng thái hiện tại của agent
            self.graph(screen, N, map_matrix, agent_x, agent_y)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.alive = False

            if path_index < len(position_path):
                # Cập nhật vị trí và hành động
                action = action_path[path_index]
                self.score -= 10
                if action == 'turn_left':
                    current_index = directions.index(self.direction)
                    self.direction = directions[(current_index - 1) % 4]
                elif action == 'turn_right':
                    current_index = directions.index(self.direction)
                    self.direction = directions[(current_index + 1) % 4]
                elif action == 'move_fw':
                    if self.direction == 'up':
                        agent_x = max(agent_x - 1, 0)
                    elif self.direction == 'down':
                        agent_x = min(agent_x + 1, N - 1)
                    elif self.direction == 'left':
                        agent_y = max(agent_y - 1, 0)
                    elif self.direction == 'right':
                        agent_y = min(agent_y + 1, N - 1)
                elif action == 'shoot':
                    self.score -= 90
                    if self.direction == 'up':
                        target_x, target_y = agent_x - 1, agent_y
                    elif self.direction == 'down':
                        target_x, target_y = agent_x + 1, agent_y
                    elif self.direction == 'left':
                        target_x, target_y = agent_x, agent_y - 1
                    elif self.direction == 'right':
                        target_x, target_y = agent_x, agent_y + 1

                    # Kiểm tra nếu ô kế bên có Wumpus
                    if 0 <= target_x < N and 0 <= target_y < N and 'W' in map_matrix[target_x][target_y]:
                        # Bắn trúng Wumpus
                        pygame.mixer.init()
                        wumpus_death_sound = pygame.mixer.Sound(os.path.join(image_folder, 'wumpus_death.mp3'))
                        wumpus_death_sound.play()  # Phát âm thanh
                        pygame.time.delay(1300)  # Delay để quan sát chuyển động của agent
                        map_matrix[target_x][target_y].remove('W') # Xóa Wumpus khỏi map

                # Cập nhật màn hình với trạng thái hiện tại của agent
                self.graph(screen, N, map_matrix, agent_x, agent_y)

                # Chuyển sang bước tiếp theo trong path
                path_index += 1
                pygame.time.delay(400)  # Delay để quan sát chuyển động của agent

            if self.health <= 0 or not self.alive:
                show_game_over(self, screen)

def show_game_over(self, screen):
    # Tạo cửa sổ thông báo "Game Over"
    game_over_window = tk.Tk()
    game_over_window.title("You Lost")
    game_over_window.geometry("900x506")  # Thay đổi kích thước cửa sổ

    # Đường dẫn đến thư mục chứa hình ảnh
    image_folder = os.path.join(os.getcwd(), 'image')

    # Mở hình ảnh nền
    background_image_path = os.path.join(image_folder, "adtime.jpg")
    background_image = Image.open(background_image_path)
    background_photo = ImageTk.PhotoImage(background_image)

    # Tạo canvas để đặt hình nền
    canvas = tk.Canvas(game_over_window, width=900, height=506)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=background_photo, anchor="nw")

    # Tạo ảnh có nền trong suốt và văn bản
    def create_text_image(text, font_path, font_size, text_color, bg_color, width, height):
        image = Image.new('RGBA', (width, height), bg_color + (128,))  # Tạo ảnh bán trong suốt
        draw = ImageDraw.Draw(image)
        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((width - text_width) // 2, (height - text_height) // 2)
        draw.text(position, text, font=font, fill=text_color)
        return ImageTk.PhotoImage(image)
    
    def create_text_image_no(text, font_path, font_size, text_color):
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
    font_folder = "Gliker"  # Tên thư mục chứa font
    font_file = "Gliker Semi Bold.ttf"  # Tên file font
    font_path = os.path.join(font_folder, font_file)
    # Tạo ảnh văn bản "Game Over"
    game_over_image = create_text_image_no("You Lost", font_path, 100, (255,153,204))
    canvas.create_image(450, 100, image=game_over_image, anchor="center")

    # Tạo ảnh văn bản cho điểm số và sức khỏe
    score_image = create_text_image_no(f"Score: {self.score}", font_path, 24, "white")
    health_image = create_text_image_no(f"Health: {self.health}", font_path, 24, "white")
    canvas.create_image(450, 200, image=score_image, anchor="center")
    canvas.create_image(450, 250, image=health_image, anchor="center")

    # Tạo ảnh bán trong suốt cho nút "Retry" và "Quit"
    retry_image = create_text_image("Retry", font_path, 20, "white", (255,255,255), 100, 50)
    quit_image = create_text_image("Quit", font_path, 20, "white", (255,255,255), 100, 50)

    # Thêm hình ảnh có chứa văn bản và lớp phủ bán trong suốt vào canvas
    retry_button = canvas.create_image(350, 400, image=retry_image, anchor="center")
    quit_button = canvas.create_image(550, 400, image=quit_image, anchor="center")

    # Tạo sự kiện click cho các nút
    canvas.tag_bind(retry_button, "<Button-1>", lambda event: restart_game(self, game_over_window))
    canvas.tag_bind(quit_button, "<Button-1>", lambda event: exit_game(self))

    game_over_window.mainloop()

def show_game_end(self, screen):
    # Tạo cửa sổ thông báo "Game Over"
    game_over_window = tk.Tk()
    game_over_window.title("End Game")
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
    def create_text_image(text, font_path, font_size, text_color, bg_color, width, height):
        image = Image.new('RGBA', (width, height), bg_color + (128,))  # Tạo ảnh bán trong suốt
        draw = ImageDraw.Draw(image)
        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((width - text_width) // 2, (height - text_height) // 2)
        draw.text(position, text, font=font, fill=text_color)
        return ImageTk.PhotoImage(image)
    
    def create_text_image_no(text, font_path, font_size, text_color):
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
    game_over_image = create_text_image_no("End Game", font_path, 60, (255,153,204))
    canvas.create_image(400, 50, image=game_over_image, anchor="center")


    # Tạo ảnh văn bản cho điểm số và sức khỏe
    score_image = create_text_image_no(f"Score: {self.score}", font_path, 24, "white")
    health_image = create_text_image_no(f"Health: {self.health}", font_path, 24, "white")
    canvas.create_image(400, 150, image=score_image, anchor="center")
    canvas.create_image(400, 200, image=health_image, anchor="center")

    # Tạo ảnh bán trong suốt cho nút "Retry" và "Quit"
    retry_image = create_text_image("Retry", font_path, 20, "white", (255,255,255), 100, 50)
    quit_image = create_text_image("Quit", font_path, 20, "white", (255,255,255), 100, 50)

    # Thêm hình ảnh có chứa văn bản và lớp phủ bán trong suốt vào canvas
    retry_button = canvas.create_image(220, 330, image=retry_image, anchor="nw")
    quit_button = canvas.create_image(470, 330, image=quit_image, anchor="nw")

    # Tạo sự kiện click cho các nút
    canvas.tag_bind(retry_button, "<Button-1>", lambda event: restart_game(self, game_over_window))
    canvas.tag_bind(quit_button, "<Button-1>", lambda event: exit_game(self))

    game_over_window.mainloop()



def restart_game(self, game_over_window):
    game_over_window.destroy()
    pygame.quit()  # Kết thúc Pygame
    subprocess.call([sys.executable, 'main.py'])  # Gọi lại script chính (main.py)

def exit_game(self):
    pygame.quit()
    sys.exit()
 # Hàm để vẽ nút Play
def draw_play_button(screen):
        button_color = (0, 48, 143)  # Màu xanh lá cho nút Play
        button_rect = pygame.Rect(750, 580, 100, 50)  # Vị trí và kích thước của nút
        pygame.draw.rect(screen, button_color, button_rect)
        font = pygame.font.Font(None, 36)
        text = font.render("Play", True, (255,255,255))
        screen.blit(text, (button_rect.centerx - text.get_width() // 2, button_rect.centery - text.get_height() // 2))
        return button_rect



