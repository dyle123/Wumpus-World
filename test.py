def show_game_over(self, screen):
    # Tạo cửa sổ thông báo "Game Over"
    game_over_window = tk.Tk()
    game_over_window.title("You Lost")
    game_over_window.geometry("900x506")  # Thay đổi kích thước cửa sổ

    # Đường dẫn đến thư mục chứa hình ảnh
    image_folder = os.path.join(os.getcwd(), 'image')

    # Mở hình ảnh nền GIF
    background_image_path = os.path.join(image_folder, "adtime.gif")
    background_image = Image.open(background_image_path)

    # Tạo canvas để đặt hình nền (Lớp nền)
    canvas = tk.Canvas(game_over_window, width=900, height=506)
    canvas.pack(fill="both", expand=True)

    # Tạo danh sách các khung hình đã được thu nhỏ (resized) để hiển thị dưới dạng ảnh động
    frames = []
    for frame in ImageSequence.Iterator(background_image):
        resized_frame = frame.resize((900, 506), Image.LANCZOS)
        frames.append(ImageTk.PhotoImage(resized_frame))

    # Hiển thị ảnh động trên canvas (Lớp nền)
    def update_frame(index):
        frame = frames[index]
        canvas.create_image(0, 0, image=frame, anchor="nw")
        game_over_window.after(100, update_frame, (index + 1) % len(frames))

    # Bắt đầu hiển thị ảnh động từ khung đầu tiên
    update_frame(0)

    # Thêm văn bản và button trực tiếp vào cửa sổ (không dùng lớp trên "transparent")
    label_game_over = tk.Label(game_over_window, text="You Lost", font=("Gliker Semi Bold", 48), fg="#FF99CC", bg="white")
    label_game_over.place(x=450, y=100, anchor="center")

    label_score = tk.Label(game_over_window, text=f"Score: {self.score}", font=("Gliker Semi Bold", 24), fg="white", bg="white")
    label_score.place(x=450, y=200, anchor="center")

    label_health = tk.Label(game_over_window, text=f"Health: {self.health}", font=("Gliker Semi Bold", 24), fg="white", bg="white")
    label_health.place(x=450, y=250, anchor="center")

    # Thêm button "Retry" và "Quit"
    retry_button = tk.Button(game_over_window, text="Retry", command=lambda: restart_game(self, game_over_window))
    quit_button = tk.Button(game_over_window, text="Quit", command=lambda: exit_game(self))
    retry_button.place(x=350, y=400, width=100, height=50)
    quit_button.place(x=550, y=400, width=100, height=50)

    game_over_window.mainloop()