class OutputManager:
    def __init__(self, file_path="output.txt"):
        self.file_path = file_path
        self.file = open(file_path, "w")  # Mở file ở chế độ ghi đè

    def write_action(self, position, action):
        """
        Ghi hành động của agent vào file.
        """
        self.file.write(f"{position}: {action}\n")

    def close_file(self):
        """
        Đóng file output.
        """
        self.file.close()