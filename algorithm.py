from pysat.solvers import Glucose3
from agent import Agent
from Program import Program
from output import OutputManager
import time

class Algorithm:

    def __init__(self, agent):
        self.agent = agent  # Truyền agent vào để sử dụng các thuộc tính của agent
        self.kb = Glucose3()
        self.N = None  # Kích thước ma trận
        self.map_matrix = None  # Ma trận Wumpus World
        self.current_position = (1, 1)  # Vị trí hiện tại của agent
        self.visited = set()  # Tập hợp các ô đã được ghé thăm
        self.dead_zone = set()
        self.safe = set()  # Tập hợp các ô an toàn
        self.wumpus_alive = True  # Giả sử Wumpus còn sống
        self.has_gold = False  # Agent chưa có vàng
        self.facing_direction = 'up'  # Hướng ban đầu
        self.directions = ['up', 'right', 'down', 'left'] 
        self.output_manager = OutputManager()
        self.ACTION = ()
        self.KO = False
        # Ánh xạ các ký tự sang số nguyên
        self.symbols = {
            'P': 1,
            'W': 2,
            'A': 3,
            'G': 4,
            'P_G': 5,
            'H_P': 6,
            'B': 7,
            'S': 8,
            'G_L': 9,
            'W_H': 10
        }
        # Tạo danh sách các biến mệnh đề
        self.variables = {}
        self.max_var = 0
    
    def some_method(self):
        # Some method that might modify self.ACTION
        pass

    def var(self, i, j, k):
        if (i, j, k) not in self.variables:
            self.max_var += 1
            self.variables[(i, j, k)] = self.max_var
        return self.variables[(i, j, k)]

    def add_clause(self, clause):
        self.kb.add_clause(clause)

    def tell(self, i, j, k, truth_value=True):
        var = self.var(i, j, k)
        if truth_value:
            self.add_clause([var])
        else:
            self.add_clause([-var])

    def ask(self, i, j, k):
        var = self.var(i, j, k)
        return self.kb.solve(assumptions=[var])

    def update_kb(self, percepts):
        i, j = self.current_position
        # Percept Breeze
        if 'B' in percepts:
            self.add_clause([self.var(i - 1, j, 'P'), self.var(i + 1, j, 'P'), self.var(i, j - 1, 'P'),
                             self.var(i, j + 1, 'P')])
            self.add_clause([-self.var(i, j, 'P')])  # Ô hiện tại không phải là hố
        else:
            self.add_clause([-self.var(i - 1, j, 'P')])
            self.add_clause([-self.var(i + 1, j, 'P')])
            self.add_clause([-self.var(i, j - 1, 'P')])
            self.add_clause([-self.var(i, j + 1, 'P')])
        # Percept Stench
        if 'S' in percepts:
            self.add_clause([self.var(i - 1, j, 'W'), self.var(i + 1, j, 'W'), self.var(i, j - 1, 'W'),
                             self.var(i, j + 1, 'W')])
            self.add_clause([-self.var(i, j, 'W')])  # Ô hiện tại không phải là Wumpus
        else:
            self.add_clause([-self.var(i - 1, j, 'W')])
            self.add_clause([-self.var(i + 1, j, 'W')])
            self.add_clause([-self.var(i, j - 1, 'W')])
            self.add_clause([-self.var(i, j + 1, 'W')])
        # Percept Whiff
        if 'W_H' in percepts:
            self.add_clause([self.var(i - 1, j, 'P_G'), self.var(i + 1, j, 'P_G'), self.var(i, j - 1, 'P_G'),
                             self.var(i, j + 1, 'P_G')])
            self.add_clause([-self.var(i, j, 'P_G')])  # Ô hiện tại không phải là Poisonous Gas
        else:
            self.add_clause([-self.var(i - 1, j, 'P_G')])
            self.add_clause([-self.var(i + 1, j, 'P_G')])
            self.add_clause([-self.var(i, j - 1, 'P_G')])
            self.add_clause([-self.var(i, j + 1, 'P_G')])

        # Percept Glow
        if 'G_L' in percepts:
            self.add_clause([self.var(i - 1, j, 'H_P'), self.var(i + 1, j, 'H_P'), self.var(i, j - 1, 'H_P'),
                             self.var(i, j + 1, 'H_P')])
            self.add_clause([-self.var(i, j, 'H_P')])  # Ô hiện tại không phải là Healing Potions
        else:
            self.add_clause([-self.var(i - 1, j, 'H_P')])
            self.add_clause([-self.var(i + 1, j, 'H_P')])
            self.add_clause([-self.var(i, j - 1, 'H_P')])
            self.add_clause([-self.var(i + 1, j, 'H_P')])

    def check_safe(self, x, y):
        if (x, y) in self.visited or (x, y) in self.safe:
            return True
        if not self.ask(x, y, 'P') and not self.ask(x, y, 'W') and not self.ask(x, y, 'P_G'):
            self.safe.add((x, y))
            return True
        return False

    def get_neighbors(self, x, y):
        neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        valid_neighbors = [(nx, ny) for nx, ny in neighbors if 0 <= nx < self.N and 0 <= ny < self.N]
        return valid_neighbors

    def find_path(self, start, end):
        queue = [(start, [])]  # Hàng đợi chứa các ô và đường đi tương ứng
        visited = set()  # Tập hợp các ô đã được duyệt

        while queue:
            current, path = queue.pop(0)
            visited.add(current)

            if current == end:
                return path  # Trả về đường đi nếu tìm thấy

            neighbors = self.get_neighbors(*current)
            for neighbor in neighbors:
                if neighbor not in visited and self.check_safe(*neighbor):
                    new_path = path + [neighbor]
                    queue.append((neighbor, new_path))
        return None  # Không tìm thấy đường đi


    def get_action_path(self, start, end):
        path = self.find_path(start, end)
        if path is None:
            return None, None

        action_path = []
        position_path = [start]
        directions = ['up', 'right', 'down', 'left']
        for i in range(len(path)):
            current_pos = position_path[-1]
            next_pos = path[i]
            
            # Xác định hướng cần di chuyển
            if next_pos[0] > current_pos[0]:  # Di chuyển xuống dưới
                desired_direction = 'down'
            elif next_pos[0] < current_pos[0]:  # Di chuyển lên trên
                desired_direction = 'up'
            elif next_pos[1] > current_pos[1]:  # Di chuyển sang phải
                desired_direction = 'right'
            else:  # Di chuyển sang trái
                desired_direction = 'left'

            # Xoay agent cho đến khi hướng đúng
            while self.facing_direction != desired_direction:
                if (self.facing_direction == 'up' and desired_direction == 'right') or (self.facing_direction == 'right' and desired_direction == 'down') or (self.facing_direction == 'down' and desired_direction == 'left') or (self.facing_direction == 'left' and desired_direction == 'up'):
                    action_path.append('turn_right')
                    position_path.append(current_pos)
                    current_index = directions.index(self.facing_direction)
                    self.facing_direction = directions[(current_index + 1) % 4]
                else:
                    action_path.append('turn_left')
                    position_path.append(current_pos)
                    current_index = self.directions.index(self.facing_direction)
                    self.facing_direction = self.directions[(current_index - 1) % 4] 
            # Di chuyển tới ô tiếp theo
            action_path.append('move_fw')
            position_path.append(next_pos)

        return position_path, action_path



    def find_nearest_safe_unvisited(self):
        queue = [(self.current_position, 0)]  # Hàng đợi chứa các ô và khoảng cách tương ứng
        visited = set()  # Tập hợp các ô đã được duyệt

        while queue:
            current, distance = queue.pop(0)
            visited.add(current)

            if current not in self.visited and self.check_safe(*current):
                return current  # Trả về ô nếu tìm thấy

            neighbors = self.get_neighbors(*current)
            for neighbor in neighbors:
                if neighbor not in visited:
                    queue.append((neighbor, distance + 1))
        return None  # Không tìm thấy ô an toàn gần nhất

    def explore(self, file_path):
        self.ACTION = []
        self.N, self.map_matrix = Program.update_map(file_path)
        self.current_position = Agent.virpos_to_realpos(self.N, 1, 1)
        self.visited.add(self.current_position)  # Đánh dấu ô bắt đầu là đã ghé thăm
        
        self.safe.add(self.current_position)  # Đánh dấu ô bắt đầu là an toàn
        done = False  # Đặt done thành False để vòng lặp tiếp tục cho đến khi hoàn tất các nhiệm vụ
        while not done:
            # Cập nhật cơ sở tri thức dựa trên các percepts hiện tại
            percepts = self.map_matrix[self.current_position[0]][self.current_position[1]]
            
            self.update_kb(percepts)

            if 'P' in percepts or 'W' in percepts or self.agent.health <= 0:
                self.output_manager.write_action(Agent.realpos_to_virpos(self.N, *self.current_position), 'die') # Ghi action vào file
                print(f'{Agent.realpos_to_virpos(self.N, *self.current_position)}: die')
                break  # Dừng game nếu agent chết

            # Kiểm tra xem có thể lấy vàng hay không
            if 'G' in percepts:
                percepts.remove('G')
                self.agent.action = 'grab'  # Thực hiện hành động 'grab'
                self.ACTION.append('grab')
                self.output_manager.write_action(Agent.realpos_to_virpos(self.N, *self.current_position), self.agent.action) # Ghi action vào file
                print(f'{Agent.realpos_to_virpos(self.N, *self.current_position)}: grab')

            # Kiểm tra Healing Potions
            if 'H_P' in percepts:
                percepts.remove('H_P')
                neighbors = self.get_neighbors(self.current_position[0], self.current_position[1])
                for nb in neighbors:
                    per = self.map_matrix[nb[0]][nb[1]]
                    per.remove('G_L')
                self.agent.action = 'grab'  # Thực hiện hành động 'grab'
                self.ACTION.append('grab')
                self.output_manager.write_action(Agent.realpos_to_virpos(self.N, *self.current_position), self.agent.action) # Ghi action vào file
                print(f'{Agent.realpos_to_virpos(self.N, *self.current_position)}: grab')

            # Kiểm tra Poisonous Gas
            if 'P_G' in percepts:
                self.output_manager.write_action(Agent.realpos_to_virpos(self.N, *self.current_position), 'damaged') # Ghi action vào file
                print(f'{Agent.realpos_to_virpos(self.N, *self.current_position)}: damaged')
                if self.agent.jar > 0 and self.agent.health < 100: # Kiểm tra nếu có bình máu và máu < 100
                    self.agent.action = 'heal' # Sử dụng bình máu
                    self.ACTION.append('heal')
                    self.output_manager.write_action(Agent.realpos_to_virpos(self.N, *self.current_position), self.agent.action) # Ghi action vào file
                    print(f'{Agent.realpos_to_virpos(self.N, *self.current_position)}: heal')

            if 'S' in percepts: 
                self.agent.action = 'shoot'  # Thực hiện hành động 'grab'
                self.ACTION.append('shoot')
                self.output_manager.write_action(Agent.realpos_to_virpos(self.N, *self.current_position), self.agent.action) # Ghi action vào file
                print(f'{Agent.realpos_to_virpos(self.N, *self.current_position)}: shoot')
                if(self.KO == True):
                    print('trúng')
                    x, y = self.current_position
                    if self.facing_direction == 'up':
                        target_x, target_y = x - 1, y
                    elif self.facing_direction == 'right':
                        target_x, target_y = x, y + 1
                    elif self.facing_direction == 'down':
                        target_x, target_y = x + 1, y
                    elif self.facing_direction == 'left':
                        target_x, target_y = x, y - 1
                    if 0 <= target_x < self.N and 0 <= target_y < self.N:
                        per = self.map_matrix[target_x][target_y]
                        if 'W' in per: 
                            per.remove('W')
                            neighbors = self.get_neighbors(target_x, target_y)
                            for nb in neighbors:
                                per = self.map_matrix[nb[0]][nb[1]]
                                per.remove('S')
                            self.update_kb(per)

            # Nếu đã có tất cả vàng, tìm đường về vị trí ban đầu (1, 1)
            if self.check_all_gold_collected():
                print('HAVE ALL GOLD')
                position_path, action_path = self.get_action_path(self.current_position, Agent.virpos_to_realpos(self.N, 1, 1))
                if action_path is not None:
                    for action, position in zip(action_path, position_path[1:]):  # Sử dụng zip
                        self.agent.action = action
                        self.ACTION.append(action)
                        self.current_position = position
                        self.output_manager.write_action(Agent.realpos_to_virpos(self.N, *self.current_position), self.agent.action) # Ghi action vào file
                        print(f'{Agent.realpos_to_virpos(self.N, *self.current_position)}: {self.agent.action}')
                    self.ACTION.append('climb')
                    done = True  # Đánh dấu hoàn tất khi đã thu thập tất cả vàng và về vị trí ban đầu
                else:
                    done = True  # Nếu không tìm thấy đường về, kết thúc vòng lặp

            # Tìm ô an toàn gần nhất chưa được ghé thăm
            next_position = self.find_nearest_safe_unvisited()
            if next_position is None:
                # Nếu không còn ô an toàn nào, quay lại ô trước đó
                done = True
            else:
                # Tìm đường đi đến ô an toàn gần nhất
                position_path, action_path = self.get_action_path(self.current_position, next_position)
                if action_path is not None:
                    for action, position in zip(action_path, position_path[1:]):
                        self.agent.action = action
                        self.ACTION.append(action)
                        self.current_position = position
                        self.output_manager.write_action(Agent.realpos_to_virpos(self.N, *self.current_position), self.agent.action) # Ghi action vào file
                        print(f'{Agent.realpos_to_virpos(self.N, *self.current_position)}: {self.agent.action}')
                    self.visited.add(self.current_position)
                else:
                    # Nếu không tìm thấy đường đi, quay lại ô trước đó
                    done = True
        Agent.path = self.ACTION
        self.output_manager.close_file() # Đóng file output sau khi thoát khỏi vòng lặp while
    def check_all_gold_collected(self):
        """
        Kiểm tra xem tất cả vàng trong bản đồ đã được thu thập hay chưa.
        """
        for i in range(self.N):
            for j in range(self.N):
                if 'G' in self.map_matrix[i][j]:
                    return False
        return True