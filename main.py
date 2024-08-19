import pygame
import sys
import os
from Program import Program  # Import class Program
from agent import Agent      # Import class Agent

# Kích thước màn hình
WIDTH, HEIGHT = 900, 650
BUTTON_HEIGHT = 50
BUTTON_WIDTH = 200

def draw_buttons(screen, buttons):
    # Đặt đường dẫn đến thư mục chứa font
    font_folder = "Gliker"  # Tên thư mục chứa font
    font_file = "Gliker Semi Bold.ttf"  # Tên file font
    font_path = os.path.join(font_folder, font_file)

    # Khởi tạo font Gliker
    title_font = pygame.font.Font(font_path, 110)
    
    # Vẽ tiêu đề với viền trắng
    title_text = title_font.render("Wumpus World", True, (102, 76, 40))
    title_rect = title_text.get_rect(center=(WIDTH // 2, 85))  # Căn giữa tiêu đề

    # Vẽ viền trắng cho tiêu đề
    shadow_offset = 2  # Độ lệch của viền
    shadow_color = (255, 255, 255)  # Màu trắng cho viền
    for offset in [(shadow_offset, shadow_offset), (-shadow_offset, shadow_offset), 
                   (shadow_offset, -shadow_offset), (-shadow_offset, -shadow_offset)]:
        screen.blit(title_font.render("Wumpus World", True, shadow_color), 
                    title_rect.move(offset))

    # Vẽ tiêu đề chính
    screen.blit(title_text, title_rect)

    # Tính toán vị trí để căn giữa buttons
    total_height = len(buttons) * (BUTTON_HEIGHT + 10)  # Tổng chiều cao của tất cả buttons
    start_y = (HEIGHT - total_height) // 2  # Bắt đầu từ vị trí giữa màn hình

    # Vẽ các button
    for index, button in enumerate(buttons):
        button_rect = pygame.Rect((WIDTH - BUTTON_WIDTH) // 2, start_y + index * (BUTTON_HEIGHT + 10), BUTTON_WIDTH, BUTTON_HEIGHT)  # Căn giữa
        pygame.draw.rect(screen, (100, 200, 100), button_rect)  # Nền button
        pygame.draw.rect(screen, (0, 0, 0), button_rect, 2)  # Viền đen
        
        # Khởi tạo font Gliker cho các button
        font = pygame.font.Font(font_path, 36)
        text = font.render(button, True, (0, 0, 0))
        
        # Căn giữa văn bản trong button
        text_rect = text.get_rect(center=button_rect.center)
        screen.blit(text, text_rect)

def main():
    os.environ['SDL_VIDEO_WINDOW_POS'] = "280,50"
    pygame.init()  # Khởi tạo hệ thống Pygame
    agent = Agent(1, 1)

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Wumpus World")

    # Tải hình nền
    image_folder = os.path.join(os.getcwd(), 'image')
    background_image = pygame.image.load(os.path.join(image_folder, 'background.jpg'))
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))  # Thay đổi kích thước hình nền cho phù hợp với kích thước cửa sổ

    buttons = ['input.txt', 'map1.txt', 'map3.txt', 'map4.txt', 'map5.txt']

    selecting_file = True
    while selecting_file:
        screen.blit(background_image, (0, 0))  # Vẽ hình nền
        draw_buttons(screen, buttons)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                selecting_file = False
                pygame.quit()
                sys.exit()  # Đảm bảo thoát đúng cách
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                for index, button in enumerate(buttons):
                    button_rect = pygame.Rect((WIDTH - BUTTON_WIDTH) // 2, (HEIGHT - len(buttons) * (BUTTON_HEIGHT + 10)) // 2 + index * (BUTTON_HEIGHT + 10), BUTTON_WIDTH, BUTTON_HEIGHT)  # Căn giữa
                    if button_rect.collidepoint(mouse_pos):
                        selecting_file = False
                        pygame.display.set_caption("Wumpus World")
                        agent.run(button)  # Chạy game với file đã chọn

        # Kiểm tra trước khi gọi pygame.display.flip() để tránh lỗi
        if pygame.get_init():
            pygame.display.flip()

    pygame.quit()  # Đảm bảo thoát hệ thống Pygame khi kết thúc

if __name__ == "__main__":
    main()
