import matplotlib.pyplot as plt
import numpy as np
import pygame
import os

class Program:
    @staticmethod
    def read_map_file(file_path):
        with open(file_path, 'r') as file:
            # Đọc kích thước bản đồ
            N = int(file.readline().strip())

            # Tạo ma trận để lưu trữ bản đồ
            map_matrix = [[[] for _ in range(N)] for _ in range(N)]

            # Đọc N dòng tiếp theo và lưu vào ma trận
            for i in range(N):
                line = file.readline().strip()
                # Chia các phòng theo dấu chấm (.)
                row = [cell.split(' ') for cell in line.split('.')]
                map_matrix[i] = row

            return N, map_matrix

    @staticmethod
    def update_map(file_path):
        N, map_matrix = Program.read_map_file(file_path)

        for i in range(N):
            for j in range(N):
                neighbors = [
                    (i-1, j),  # Trên
                    (i+1, j),  # Dưới
                    (i, j-1),  # Trái
                    (i, j+1)   # Phải
                ]
                e = map_matrix[i][j]  # Lấy ký tự chính từ ô

                # Xác định ký tự bổ sung cần thêm
                if 'P' in e:
                    p = 'B'
                elif 'W' in e:
                    p = 'S'
                elif 'P_G' in e:
                    p = 'W_H'
                elif 'H_P' in e:
                    p = 'G_L'
                else:
                    p = None  # Nếu không có phần tử hợp lệ

                # Thêm ký tự bổ sung vào các ô kề bên
                if p:  # Nếu có phần tử bổ sung hợp lệ
                    for ni, nj in neighbors:
                        # Kiểm tra xem ô kề bên có nằm trong phạm vi của bản đồ hay không
                        if 0 <= ni < N and 0 <= nj < N:
                            # Thêm ký tự bổ sung vào ô kề bên nếu nó chưa có
                            if p not in map_matrix[ni][nj]:
                                map_matrix[ni][nj].append(p)  # Thêm ký tự vào ô kề
                                if '-' in map_matrix[ni][nj]: map_matrix[ni][nj].remove('-')
        return N, map_matrix

    

    @staticmethod
    def draw_map(N, map_matrix):
        pygame.init()
        size = 20  # Kích thước mỗi ô vuông
        screen_width = 900 # Thêm không gian cho thông tin bên cạnh
        screen_height = 900  # Thêm không gian cho thông tin bên dưới
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Wumpus World")

        # Định nghĩa màu sắc
        colors = {
            'P': (139, 69, 19),     # Brown
            'W': (0, 0, 0),         # Black
            'A': (0, 0, 255),       # Blue
            'G': (255, 215, 0),     # Gold
            'P_G': (255, 0, 0),     # Red
            'H_P': (0, 255, 0),     # Green
            'B': (173, 216, 230),   # Light Blue
            'S': (105, 105, 105)    # Gray
        }
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.fill((255, 255, 255))  # Màu nền trắng

            # Vẽ bản đồ
            for i in range(N):
                for j in range(N):
                    x, y = j * size, i * size
                    pygame.draw.rect(screen, (200, 200, 200), (x, y, size, size), 1)  # Vẽ ô vuông

                    # Vẽ từng ký tự trong ô
                    for element in map_matrix[i][j]:
                        if element in colors:
                            color = colors[element]
                            pygame.draw.circle(screen, color, (x + size // 2, y + size // 2), size // 4)

            # Thêm thông tin khác ở bên cạnh hoặc bên dưới bản đồ
            font = pygame.font.SysFont(None, 36)
            info_text = font.render("Score: 0", True, (0, 0, 0))
            screen.blit(info_text, (screen_width - 180, 10))

            pygame.display.flip()

        pygame.quit()