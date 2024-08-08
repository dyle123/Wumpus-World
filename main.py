import pygame
import sys
from Program import Program  # Import class Program
from Agent import Agent      # Import class Agent
import os

# Kích thước màn hình
WIDTH, HEIGHT = 600, 500
BUTTON_HEIGHT = 50
BUTTON_WIDTH = 200

def draw_buttons(screen, buttons):
    # Vẽ tiêu đề
    title_font = pygame.font.Font(None, 48)
    title_text = title_font.render("SELECT INPUT FILE", True, (255, 255, 255))
    title_rect = title_text.get_rect(center=(WIDTH // 2, 30))  # Căn giữa tiêu đề
    screen.blit(title_text, title_rect)

    # Tính toán vị trí để căn giữa buttons
    total_height = len(buttons) * (BUTTON_HEIGHT + 10)  # Tổng chiều cao của tất cả buttons
    start_y = (HEIGHT - total_height) // 2  # Bắt đầu từ vị trí giữa màn hình

    # Vẽ các button
    for index, button in enumerate(buttons):
        button_rect = pygame.Rect((WIDTH - BUTTON_WIDTH) // 2, start_y + index * (BUTTON_HEIGHT + 10), BUTTON_WIDTH, BUTTON_HEIGHT)  # Căn giữa
        pygame.draw.rect(screen, (100, 200, 100), button_rect)  # Nền button
        pygame.draw.rect(screen, (0, 0, 0), button_rect, 2)  # Viền đen
        font = pygame.font.Font(None, 36)
        text = font.render(button, True, (0, 0, 0))
        
        # Căn giữa văn bản trong button
        text_rect = text.get_rect(center=button_rect.center)
        screen.blit(text, text_rect)

def main():
    pygame.init()
    agent = Agent(1, 1)

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Select File Input")

    # Tải hình nền
    image_folder = os.path.join(os.getcwd(), 'image')
    background_image = pygame.image.load(os.path.join(image_folder, 'bg.jpg'))

    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))  # Thay đổi kích thước hình nền cho phù hợp với kích thước cửa sổ

    buttons = ['input.txt', 'map2.txt', 'map3.txt', 'map4.txt', 'map5.txt']

    selecting_file = True
    while selecting_file:
        screen.blit(background_image, (0, 0))  # Vẽ hình nền
        draw_buttons(screen, buttons)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                selecting_file = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                for index, button in enumerate(buttons):
                    button_rect = pygame.Rect((WIDTH - BUTTON_WIDTH) // 2, (HEIGHT - len(buttons) * (BUTTON_HEIGHT + 10)) // 2 + index * (BUTTON_HEIGHT + 10), BUTTON_WIDTH, BUTTON_HEIGHT)  # Căn giữa
                    if button_rect.collidepoint(mouse_pos):
                        selecting_file = False
                        screen = pygame.display.set_mode((600, 600))  # Thay đổi kích thước cửa sổ cho bản đồ
                        pygame.display.set_caption("Wumpus World")
                        agent.run(button)  # Chạy game với file đã chọn

        pygame.display.flip()

if __name__ == "__main__":
    main()
