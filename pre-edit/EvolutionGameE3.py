import random
import os
import json
from datetime import datetime
from enum import Enum
from typing import List, Dict, Tuple, Optional

# 枚举定义
class CardType(Enum):
    COOPERATION = "合作卡"
    DECEPTION = "欺骗卡"
    EVOLUTION = "进化卡"
    EVENT = "事件卡"
    ENVIRONMENT_CHANGE = "环境变化卡"
    ABILITY = "能力卡"

class GridType(Enum):
    START = "起点格"
    TRUST_EVOLUTION = "信任进化格"
    HAWK_DOVE = "鹰鸽博弈格"
    RESOURCE_RICH = "资源丰富格"
    NATURAL_DISASTER = "自然灾害格"
    COOPERATION_SANCTUARY = "合作圣地格"
    DECEPTION_SWAMP = "欺骗沼泽格"
    MUTATION_EVENT = "突变事件格"
    EVOLUTION_LAB = "进化实验室格"
    END = "终点格"

class ActionType(Enum):
    COOPERATE = "合作"
    DECEIVE = "欺骗"

# 卡牌类
class Card:
    def __init__(self, card_type: CardType, name: str = "", description: str = ""):
        self.card_type = card_type
        self.name = name
        self.description = description
    
    def __str__(self):
        return f"{self.card_type.value}: {self.name}"

# 玩家类
class Player:
    def __init__(self, player_id: int, name: str):
        self.player_id = player_id
        self.name = name
        self.position = 0  # 在地图上的位置
        self.hand = {
            CardType.COOPERATION: [],
            CardType.DECEPTION: [],
            CardType.EVOLUTION: [],
            CardType.EVENT: [],
            CardType.ABILITY: []
        }
        self.evolution_points = 0
        self.eliminated = False
        self.symbiosis_target = None  # 共生纽带目标
    
    def get_hand_size(self):
        return sum(len(cards) for cards in self.hand.values())
    
    def get_cooperation_deception_count(self):
        return len(self.hand[CardType.COOPERATION]) + len(self.hand[CardType.DECEPTION])
    
    def get_evolution_card_count(self):
        return len(self.hand[CardType.EVOLUTION])
    
    def get_hand_limit(self):
        # 手牌上限 = 进化卡数量 / 2 (向下取整)
        return self.get_evolution_card_count() // 2
    
    def check_hand_limit(self):
        # 检查手牌是否超过上限，如果超过则弃置多余的牌
        limit = self.get_hand_limit()
        current_count = self.get_cooperation_deception_count()
        
        if current_count > limit:
            excess = current_count - limit
            # 简单实现：随机弃置多余的牌
            all_cards = self.hand[CardType.COOPERATION] + self.hand[CardType.DECEPTION]
            random.shuffle(all_cards)
            
            for _ in range(excess):
                if all_cards:
                    card = all_cards.pop()
                    if card in self.hand[CardType.COOPERATION]:
                        self.hand[CardType.COOPERATION].remove(card)
                    else:
                        self.hand[CardType.DECEPTION].remove(card)
    
    def add_card(self, card: Card):
        if card.card_type in self.hand:
            self.hand[card.card_type].append(card)
    
    def remove_card(self, card_type: CardType, count: int = 1):
        if card_type in self.hand and len(self.hand[card_type]) >= count:
            removed = self.hand[card_type][:count]
            self.hand[card_type] = self.hand[card_type][count:]
            return removed
        return []
    
    def has_card_type(self, card_type: CardType):
        return len(self.hand[card_type]) > 0
    
    def __str__(self):
        return f"玩家{self.player_id}: {self.name} (位置: {self.position}, 进化卡: {self.get_evolution_card_count()}, 进化点数: {self.evolution_points})"

# 游戏地图类
class GameBoard:
    def __init__(self, grid_count: int = 24):
        self.grid_count = grid_count
        self.grids = []
        self.initialize_grids()
    
    def initialize_grids(self):
        # 创建基础地图布局
        grid_types = [
            GridType.START,
            GridType.TRUST_EVOLUTION,
            GridType.RESOURCE_RICH,
            GridType.HAWK_DOVE,
            GridType.NATURAL_DISASTER,
            GridType.COOPERATION_SANCTUARY,
            GridType.DECEPTION_SWAMP,
            GridType.MUTATION_EVENT,
            GridType.EVOLUTION_LAB,
            GridType.RESOURCE_RICH,
            GridType.TRUST_EVOLUTION,
            GridType.NATURAL_DISASTER,
            GridType.HAWK_DOVE,
            GridType.COOPERATION_SANCTUARY,
            GridType.DECEPTION_SWAMP,
            GridType.MUTATION_EVENT,
            GridType.RESOURCE_RICH,
            GridType.TRUST_EVOLUTION,
            GridType.NATURAL_DISASTER,
            GridType.HAWK_DOVE,
            GridType.COOPERATION_SANCTUARY,
            GridType.DECEPTION_SWAMP,
            GridType.MUTATION_EVENT,
            GridType.END
        ]
        
        self.grids = grid_types[:self.grid_count]
    
    def get_grid_type(self, position: int) -> GridType:
        return self.grids[position % self.grid_count]
    
    def change_grid(self, position: int, new_type: GridType):
        if 0 <= position < len(self.grids):
            self.grids[position] = new_type

# 游戏引擎类
class EvolutionGame:
    def __init__(self, player_names: List[str], log_directory: str = "game_logs"):
        self.players = [Player(i, name) for i, name in enumerate(player_names)]
        self.board = GameBoard()
        self.current_player_index = 0
        self.round_count = 0
        self.game_over = False
        self.winner = None
        self.log_directory = log_directory
        self.game_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(log_directory, f"evolution_game_{self.game_id}.txt")
        
        # 创建日志目录
        os.makedirs(log_directory, exist_ok=True)
        
        # 初始化卡牌堆
        self.initialize_decks()
        
        # 游戏设置
        self.setup_game()
        
        # 开始游戏日志
        self.log_game_start()
    
    def initialize_decks(self):
        # 创建卡牌堆（简化版，实际游戏应有更多卡牌和效果）
        self.cooperation_deck = [Card(CardType.COOPERATION) for _ in range(25)]
        self.deception_deck = [Card(CardType.DECEPTION) for _ in range(25)]
        self.evolution_deck = [Card(CardType.EVOLUTION) for _ in range(125)]
        self.event_deck = self.create_event_deck()
        self.ability_deck = self.create_ability_deck()
        self.environment_change_deck = self.create_environment_change_deck()
        
        # 洗牌
        random.shuffle(self.cooperation_deck)
        random.shuffle(self.deception_deck)
        random.shuffle(self.evolution_deck)
        random.shuffle(self.event_deck)
        random.shuffle(self.ability_deck)
        random.shuffle(self.environment_change_deck)
    
    def create_event_deck(self):
        # 创建事件卡牌堆（简化版）
        events = [
            ("基因突变", "抽取3张进化卡，但你的下个回合无法移动"),
            ("互利共生", "选择一名玩家，双方各抽取2张进化卡"),
            ("自然选择", "当前进化卡数量最少的玩家必须弃置2张进化卡"),
            ("加速进化", "你抽取2张进化卡，并可以立即额外移动2步"),
            ("种群繁荣", "如果你在本回合触发事件时出的是合作卡，获得3张进化卡"),
        ]
        
        return [Card(CardType.EVENT, name, desc) for name, desc in events * 6]  # 每种事件卡6张
    
    def create_ability_deck(self):
        # 创建能力卡牌堆（简化版）
        abilities = [
            ("利他基因", "当你打出合作卡时，指定一名其他玩家抽取1张进化卡"),
            ("阴谋大师", "当你打出欺骗卡时，可以查看任意一名玩家的手牌数量"),
            ("环境适应", "免疫自然灾害格出欺骗卡时必须弃置1张进化卡的效果"),
            ("高效代谢", "在资源丰富格出欺骗卡且骰子掷出5或6，额外多抽取1张进化卡"),
            ("共生纽带", "与一名玩家建立共生关系，当他因你出合作卡而收益时，你也额外抽取1张进化卡"),
        ]
        
        return [Card(CardType.ABILITY, name, desc) for name, desc in abilities * 4]  # 每种能力卡4张
    
    def create_environment_change_deck(self):
        # 创建环境变化卡牌堆（简化版）
        changes = [
            ("干旱降临", "将地图上最近的一个资源丰富格永久变为自然灾害格"),
            ("绿洲形成", "将地图上最近的一个自然灾害格永久变为资源丰富格"),
            ("地震破坏", "将当前回合玩家所在格左右两侧的格子都变为自然灾害格"),
            ("生态恢复", "将地图上任意一个自然灾害格变为信任进化格"),
            ("气候宜人", "本回合内，所有玩家在触发格子事件时，若出合作卡则额外获得1张进化卡"),
        ]
        
        return [Card(CardType.ENVIRONMENT_CHANGE, name, desc) for name, desc in changes * 2]  # 每种环境变化卡2张
    
    def setup_game(self):
        # 分发起始手牌
        initial_hand_size = len(self.players) - 1
        
        for player in self.players:
            # 分发起始合作卡和欺骗卡
            for _ in range(initial_hand_size):
                # 玩家自行决定起始手牌中合作卡与欺骗卡的比例（这里随机分配）
                if random.random() < 0.5 and self.cooperation_deck:
                    player.add_card(self.cooperation_deck.pop())
                elif self.deception_deck:
                    player.add_card(self.deception_deck.pop())
            
            # 分发5张进化卡
            for _ in range(5):
                if self.evolution_deck:
                    player.add_card(self.evolution_deck.pop())
        
        # 决定起始玩家
        self.current_player_index = random.randint(0, len(self.players) - 1)
        
        self.log(f"游戏设置完成！起始玩家是: {self.players[self.current_player_index].name}")
    
    def log(self, message: str):
        # 记录游戏日志
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
        
        print(log_entry.strip())
    
    def log_game_start(self):
        self.log("=" * 50)
        self.log("Evolution Game 开始！")
        self.log(f"游戏ID: {self.game_id}")
        self.log(f"玩家数量: {len(self.players)}")
        self.log("玩家列表:")
        for player in self.players:
            self.log(f"  - {player.name} (ID: {player.player_id})")
        self.log("=" * 50)
    
    def get_current_player(self) -> Player:
        return self.players[self.current_player_index]
    
    def get_next_player(self) -> Player:
        next_index = (self.current_player_index + 1) % len(self.players)
        return self.players[next_index]
    
    def move_to_next_player(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        
        # 跳过已淘汰的玩家
        while self.get_current_player().eliminated and not self.game_over:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
    
    def roll_dice(self) -> int:
        return random.randint(1, 6)
    
    def draw_card(self, deck: List[Card], player: Player, card_type: CardType) -> bool:
        if deck:
            card = deck.pop()
            player.add_card(card)
            self.log(f"{player.name} 抽取了一张{card_type.value}")
            return True
        return False
    
    def play_turn(self):
        if self.game_over:
            return
        
        current_player = self.get_current_player()
        
        if current_player.eliminated:
            self.move_to_next_player()
            return
        
        self.log(f"第 {self.round_count + 1} 轮，{current_player.name} 的回合开始")
        
        # 阶段一：掷骰与移动
        dice_roll = self.roll_dice()
        self.log(f"{current_player.name} 掷出 {dice_roll} 点")
        
        current_player.position = (current_player.position + dice_roll) % self.board.grid_count
        grid_type = self.board.get_grid_type(current_player.position)
        self.log(f"{current_player.name} 移动到位置 {current_player.position} ({grid_type.value})")
        
        # 阶段二：触发并结算格子事件
        self.resolve_grid_event(current_player, grid_type)
        
        # 阶段三：可选行动
        self.optional_actions(current_player)
        
        # 阶段四：生态调查（简化版，跳过）
        # 阶段四：环境变化（简化版，跳过）
        
        # 检查手牌上限
        current_player.check_hand_limit()
        
        # 检查胜利条件
        self.check_win_conditions()
        
        # 移动到下一个玩家
        if not self.game_over:
            self.move_to_next_player()
            self.round_count += 1
    
    def resolve_grid_event(self, player: Player, grid_type: GridType):
        if grid_type == GridType.START:
            self.log(f"{player.name} 停留在起点格，无效果")
        
        elif grid_type == GridType.TRUST_EVOLUTION:
            self.resolve_trust_evolution(player)
        
        elif grid_type == GridType.HAWK_DOVE:
            self.resolve_hawk_dove(player)
        
        elif grid_type == GridType.RESOURCE_RICH:
            self.resolve_resource_rich(player)
        
        elif grid_type == GridType.NATURAL_DISASTER:
            self.resolve_natural_disaster(player)
        
        elif grid_type == GridType.COOPERATION_SANCTUARY:
            self.resolve_cooperation_sanctuary(player)
        
        elif grid_type == GridType.DECEPTION_SWAMP:
            self.resolve_deception_swamp(player)
        
        elif grid_type == GridType.MUTATION_EVENT:
            self.resolve_mutation_event(player)
        
        elif grid_type == GridType.EVOLUTION_LAB:
            self.resolve_evolution_lab(player)
        
        elif grid_type == GridType.END:
            self.resolve_end_grid(player)
    
    def resolve_trust_evolution(self, current_player: Player):
        self.log("触发信任进化格事件")
        
        # 所有玩家同时指定一名其他玩家作为目标，并出牌
        # 简化版：随机选择目标和出牌
        actions = {}
        
        for player in self.players:
            if player.eliminated:
                continue
                
            # 随机选择目标（不能是自己）
            target_options = [p for p in self.players if p != player and not p.eliminated]
            if not target_options:
                continue
                
            target = random.choice(target_options)
            action = random.choice([ActionType.COOPERATE, ActionType.DECEIVE])
            actions[player] = (target, action)
        
        # 结算每一对相互指定的玩家
        for player, (target, action) in actions.items():
            if target in actions and actions[target][0] == player:
                target_action = actions[target][1]
                
                if action == ActionType.COOPERATE and target_action == ActionType.COOPERATE:
                    # 合作 vs 合作：双方各获得2点进化点数
                    player.evolution_points += 2
                    target.evolution_points += 2
                    self.log(f"{player.name} 和 {target.name} 相互合作，各获得2点进化点数")
                
                elif action == ActionType.COOPERATE and target_action == ActionType.DECEIVE:
                    # 合作 vs 欺骗：出合作方获得1点进化点数，出欺骗方立即抽取3张进化卡
                    player.evolution_points += 1
                    for _ in range(3):
                        self.draw_card(self.evolution_deck, target, CardType.EVOLUTION)
                    self.log(f"{player.name} 合作但被 {target.name} 欺骗，{player.name} 获得1点进化点数，{target.name} 抽取3张进化卡")
                
                elif action == ActionType.DECEIVE and target_action == ActionType.COOPERATE:
                    # 欺骗 vs 合作：出合作方获得1点进化点数，出欺骗方立即抽取3张进化卡
                    target.evolution_points += 1
                    for _ in range(3):
                        self.draw_card(self.evolution_deck, player, CardType.EVOLUTION)
                    self.log(f"{target.name} 合作但被 {player.name} 欺骗，{target.name} 获得1点进化点数，{player.name} 抽取3张进化卡")
                
                elif action == ActionType.DECEIVE and target_action == ActionType.DECEIVE:
                    # 欺骗 vs 欺骗：双方各弃置1张进化卡
                    if player.has_card_type(CardType.EVOLUTION):
                        player.remove_card(CardType.EVOLUTION, 1)
                    if target.has_card_type(CardType.EVOLUTION):
                        target.remove_card(CardType.EVOLUTION, 1)
                    self.log(f"{player.name} 和 {target.name} 相互欺骗，各弃置1张进化卡")
        
        # 所有玩家可补充一张合作或欺骗卡
        for player in self.players:
            if not player.eliminated:
                if random.random() < 0.5 and self.cooperation_deck:
                    self.draw_card(self.cooperation_deck, player, CardType.COOPERATION)
                elif self.deception_deck:
                    self.draw_card(self.deception_deck, player, CardType.DECEPTION)
    
    def resolve_hawk_dove(self, current_player: Player):
        self.log("触发鹰鸽博弈格事件")
        
        # 当前回合玩家可指定一名对手
        target_options = [p for p in self.players if p != current_player and not p.eliminated]
        if not target_options:
            self.log("没有可指定的对手，事件跳过")
            return
        
        target = random.choice(target_options)
        self.log(f"{current_player.name} 指定 {target.name} 进行鹰鸽博弈")
        
        # 双方秘密出牌
        current_action = random.choice([ActionType.COOPERATE, ActionType.DECEIVE])
        target_action = random.choice([ActionType.COOPERATE, ActionType.DECEIVE])
        
        # 结算
        if current_action == ActionType.COOPERATE and target_action == ActionType.COOPERATE:
            # 鸽 vs 鸽：双方各获得2点进化点数
            current_player.evolution_points += 2
            target.evolution_points += 2
            self.log(f"{current_player.name} 和 {target.name} 都选择合作，各获得2点进化点数")
        
        elif current_action == ActionType.DECEIVE and target_action == ActionType.COOPERATE:
            # 鹰 vs 鸽：出鸽方获得1点进化点数，出鹰方立即抽取3张进化卡
            target.evolution_points += 1
            for _ in range(3):
                self.draw_card(self.evolution_deck, current_player, CardType.EVOLUTION)
            self.log(f"{current_player.name} 选择欺骗，{target.name} 选择合作，{target.name} 获得1点进化点数，{current_player.name} 抽取3张进化卡")
        
        elif current_action == ActionType.COOPERATE and target_action == ActionType.DECEIVE:
            # 鸽 vs 鹰：出鸽方获得1点进化点数，出鹰方立即抽取3张进化卡
            current_player.evolution_points += 1
            for _ in range(3):
                self.draw_card(self.evolution_deck, target, CardType.EVOLUTION)
            self.log(f"{current_player.name} 选择合作，{target.name} 选择欺骗，{current_player.name} 获得1点进化点数，{target.name} 抽取3张进化卡")
        
        elif current_action == ActionType.DECEIVE and target_action == ActionType.DECEIVE:
            # 鹰 vs 鹰：双方各弃置2张进化卡
            current_player.remove_card(CardType.EVOLUTION, min(2, current_player.get_evolution_card_count()))
            target.remove_card(CardType.EVOLUTION, min(2, target.get_evolution_card_count()))
            self.log(f"{current_player.name} 和 {target.name} 都选择欺骗，各弃置2张进化卡")
        
        # 参与玩家可补充一张所出牌型的卡
        if current_action == ActionType.COOPERATE and self.cooperation_deck:
            self.draw_card(self.cooperation_deck, current_player, CardType.COOPERATION)
        elif self.deception_deck:
            self.draw_card(self.deception_deck, current_player, CardType.DECEPTION)
        
        if target_action == ActionType.COOPERATE and self.cooperation_deck:
            self.draw_card(self.cooperation_deck, target, CardType.COOPERATION)
        elif self.deception_deck:
            self.draw_card(self.deception_deck, target, CardType.DECEPTION)
    
    def resolve_resource_rich(self, current_player: Player):
        self.log("触发资源丰富格事件")
        
        # 所有玩家出一张牌
        for player in self.players:
            if player.eliminated:
                continue
                
            action = random.choice([ActionType.COOPERATE, ActionType.DECEIVE])
            
            if action == ActionType.COOPERATE:
                # 出合作卡：从进化牌库抽取2张进化卡
                for _ in range(2):
                    self.draw_card(self.evolution_deck, player, CardType.EVOLUTION)
                self.log(f"{player.name} 选择合作，抽取2张进化卡")
            else:
                # 出欺骗卡：掷骰子，1-4无所获，5-6抽取4张进化卡
                dice_roll = self.roll_dice()
                if dice_roll >= 5:
                    for _ in range(4):
                        self.draw_card(self.evolution_deck, player, CardType.EVOLUTION)
                    self.log(f"{player.name} 选择欺骗，掷出{dice_roll}，抽取4张进化卡")
                else:
                    self.log(f"{player.name} 选择欺骗，掷出{dice_roll}，无所获")
    
    def resolve_natural_disaster(self, current_player: Player):
        self.log("触发自然灾害格事件")
        
        # 所有玩家出一张牌
        for player in self.players:
            if player.eliminated:
                continue
                
            action = random.choice([ActionType.COOPERATE, ActionType.DECEIVE])
            
            if action == ActionType.COOPERATE:
                # 出合作卡：免疫本次灾害
                self.log(f"{player.name} 选择合作，免疫自然灾害")
            else:
                # 出欺骗卡：必须弃置1张进化卡，然后可以指定一名其他玩家也必须弃置1张进化卡
                if player.has_card_type(CardType.EVOLUTION):
                    player.remove_card(CardType.EVOLUTION, 1)
                    self.log(f"{player.name} 选择欺骗，弃置1张进化卡")
                    
                    # 指定一名其他玩家
                    target_options = [p for p in self.players if p != player and not p.eliminated]
                    if target_options:
                        target = random.choice(target_options)
                        if target.has_card_type(CardType.EVOLUTION):
                            target.remove_card(CardType.EVOLUTION, 1)
                            self.log(f"{player.name} 指定 {target.name} 也必须弃置1张进化卡")
    
    def resolve_cooperation_sanctuary(self, current_player: Player):
        self.log("触发合作圣地格事件")
        
        # 所有玩家出一张牌
        actions = {}
        cooperators = []
        
        for player in self.players:
            if player.eliminated:
                continue
                
            action = random.choice([ActionType.COOPERATE, ActionType.DECEIVE])
            actions[player] = action
            
            if action == ActionType.COOPERATE:
                cooperators.append(player)
        
        # 结算
        for player, action in actions.items():
            if action == ActionType.COOPERATE:
                # 出合作卡：可选择另一位也出合作卡的玩家，双方各抽取3张进化卡
                if len(cooperators) > 1:  # 至少有另一个合作者
                    other_cooperators = [p for p in cooperators if p != player]
                    if other_cooperators:
                        partner = random.choice(other_cooperators)
                        for _ in range(3):
                            self.draw_card(self.evolution_deck, player, CardType.EVOLUTION)
                            self.draw_card(self.evolution_deck, partner, CardType.EVOLUTION)
                        self.log(f"{player.name} 和 {partner.name} 在合作圣地合作，各抽取3张进化卡")
                else:
                    self.log(f"{player.name} 在合作圣地选择合作，但没有其他合作者，无收益")
            
            else:  # 欺骗
                # 出欺骗卡：单独抽取4张进化卡，但下家获得一次免费的挑战权
                for _ in range(4):
                    self.draw_card(self.evolution_deck, player, CardType.EVOLUTION)
                self.log(f"{player.name} 在合作圣地选择欺骗，抽取4张进化卡")
                
                # 下家获得免费挑战权（简化版：记录日志）
                next_player = self.get_next_player()
                self.log(f"{next_player.name} 获得一次免费的鹰鸽博弈挑战权，可对 {player.name} 发起挑战")
    
    def resolve_deception_swamp(self, current_player: Player):
        self.log("触发欺骗沼泽格事件")
        
        # 所有玩家出一张牌
        actions = {}
        deceivers = []
        
        for player in self.players:
            if player.eliminated:
                continue
                
            action = random.choice([ActionType.COOPERATE, ActionType.DECEIVE])
            actions[player] = action
            
            if action == ActionType.DECEIVE:
                deceivers.append(player)
        
        # 结算
        for player, action in actions.items():
            if action == ActionType.DECEIVE:
                # 出欺骗卡：可以查看能力牌库顶3张牌，拿取其中1张加入手牌
                if len(self.ability_deck) >= 3:
                    # 简化版：直接抽取一张能力卡
                    if self.ability_deck:
                        self.draw_card(self.ability_deck, player, CardType.ABILITY)
                        self.log(f"{player.name} 在欺骗沼泽选择欺骗，获得一张能力卡")
                else:
                    self.log(f"{player.name} 在欺骗沼泽选择欺骗，但能力牌库不足，无收益")
            
            else:  # 合作
                # 出合作卡：可指定一名出欺骗卡的玩家，阻止其获得收益，并因此抽取1张进化卡作为奖励
                if deceivers:
                    target = random.choice(deceivers)
                    self.log(f"{player.name} 在欺骗沼泽选择合作，阻止了 {target.name} 的欺骗收益")
                    
                    # 抽取1张进化卡作为奖励
                    self.draw_card(self.evolution_deck, player, CardType.EVOLUTION)
    
    def resolve_mutation_event(self, current_player: Player):
        self.log("触发突变事件格事件")
        
        if self.event_deck:
            event_card = self.event_deck.pop()
            self.log(f"{current_player.name} 抽取事件卡: {event_card.name} - {event_card.description}")
            
            # 执行事件效果（简化版）
            if event_card.name == "基因突变":
                for _ in range(3):
                    self.draw_card(self.evolution_deck, current_player, CardType.EVOLUTION)
                # 下回合无法移动的效果在游戏逻辑中处理
                
            elif event_card.name == "互利共生":
                target_options = [p for p in self.players if p != current_player and not p.eliminated]
                if target_options:
                    target = random.choice(target_options)
                    for _ in range(2):
                        self.draw_card(self.evolution_deck, current_player, CardType.EVOLUTION)
                        self.draw_card(self.evolution_deck, target, CardType.EVOLUTION)
                    self.log(f"{current_player.name} 和 {target.name} 达成互利共生，各抽取2张进化卡")
                
            elif event_card.name == "自然选择":
                # 找到进化卡数量最少的玩家
                min_evolution = min(p.get_evolution_card_count() for p in self.players if not p.eliminated)
                victims = [p for p in self.players if p.get_evolution_card_count() == min_evolution and not p.eliminated]
                
                for victim in victims:
                    victim.remove_card(CardType.EVOLUTION, min(2, victim.get_evolution_card_count()))
                    self.log(f"{victim.name} 成为自然选择的受害者，弃置2张进化卡")
                
            elif event_card.name == "加速进化":
                for _ in range(2):
                    self.draw_card(self.evolution_deck, current_player, CardType.EVOLUTION)
                # 额外移动2步的效果在游戏逻辑中处理
                
            elif event_card.name == "种群繁荣":
                # 假设当前玩家在触发事件时出了合作卡
                for _ in range(3):
                    self.draw_card(self.evolution_deck, current_player, CardType.EVOLUTION)
                self.log(f"{current_player.name} 触发种群繁荣，获得3张进化卡")
        else:
            self.log("事件牌库已空，无效果")
    
    def resolve_evolution_lab(self, current_player: Player):
        self.log("触发进化实验室格事件")
        
        # 当前玩家可支付2张进化卡的代价，获得一张能力卡
        if current_player.get_evolution_card_count() >= 2 and self.ability_deck:
            current_player.remove_card(CardType.EVOLUTION, 2)
            self.draw_card(self.ability_deck, current_player, CardType.ABILITY)
            self.log(f"{current_player.name} 支付2张进化卡，获得一张能力卡")
        else:
            self.log(f"{current_player.name} 无法支付代价或能力牌库已空，无效果")
    
    def resolve_end_grid(self, current_player: Player):
        self.log("触发终点格事件")
        
        # 首次抵达此格的玩家立即抽取3张进化卡并获得2点进化点数
        # 简化版：每次抵达都有效果
        for _ in range(3):
            self.draw_card(self.evolution_deck, current_player, CardType.EVOLUTION)
        current_player.evolution_points += 2
        self.log(f"{current_player.name} 抵达终点，抽取3张进化卡并获得2点进化点数")
    
    def optional_actions(self, current_player: Player):
        self.log(f"{current_player.name} 的可选行动阶段")
        
        # 简化版：随机选择是否执行可选行动
        if random.random() < 0.3:  # 30%概率执行可选行动
            action_type = random.choice(["兑换进化点数", "使用事件卡", "发动能力"])
            
            if action_type == "兑换进化点数" and current_player.evolution_points > 0:
                # 兑换进化点数：以1:1的比例抽取进化卡
                points_to_spend = random.randint(1, current_player.evolution_points)
                for _ in range(points_to_spend):
                    self.draw_card(self.evolution_deck, current_player, CardType.EVOLUTION)
                current_player.evolution_points -= points_to_spend
                self.log(f"{current_player.name} 兑换了{points_to_spend}点进化点数，抽取{points_to_spend}张进化卡")
            
            elif action_type == "使用事件卡" and current_player.has_card_type(CardType.EVENT):
                # 使用事件卡（简化版：随机使用一张）
                event_card = current_player.remove_card(CardType.EVENT, 1)[0]
                self.log(f"{current_player.name} 使用了事件卡: {event_card.name}")
                # 实际游戏中应根据事件卡效果执行相应操作
            
            elif action_type == "发动能力" and current_player.has_card_type(CardType.ABILITY):
                # 发动能力（简化版：随机使用一张）
                ability_card = current_player.hand[CardType.ABILITY][0]  # 使用第一张能力卡
                self.log(f"{current_player.name} 发动了能力: {ability_card.name}")
                # 实际游戏中应根据能力卡效果执行相应操作
    
    def check_win_conditions(self):
        # 检查胜利条件：进化卡数量达到20张
        for player in self.players:
            if not player.eliminated and player.get_evolution_card_count() >= 20:
                self.game_over = True
                self.winner = player
                self.log(f"游戏结束！{player.name} 获得了进化胜利！")
                self.log_game_end()
                return
        
        # 检查失败条件：进化卡数量降为零
        active_players = [p for p in self.players if not p.eliminated]
        for player in active_players:
            if player.get_evolution_card_count() == 0:
                player.eliminated = True
                self.log(f"{player.name} 的物种灭绝，退出游戏")
        
        # 如果只剩一名玩家，该玩家获胜
        active_players = [p for p in self.players if not p.eliminated]
        if len(active_players) == 1:
            self.game_over = True
            self.winner = active_players[0]
            self.log(f"游戏结束！{self.winner.name} 是最后的幸存者，获得胜利！")
            self.log_game_end()
            return
        elif len(active_players) == 0:
            self.game_over = True
            self.log("游戏结束！所有玩家都被淘汰，没有获胜者！")
            self.log_game_end()
            return
        
        # 检查发展停滞（可选规则，简化版跳过）
    
    def log_game_end(self):
        self.log("=" * 50)
        self.log("游戏最终状态：")
        for player in self.players:
            status = "已淘汰" if player.eliminated else "存活"
            self.log(f"{player.name}: 进化卡{player.get_evolution_card_count()}张, 进化点数{player.evolution_points}点, 状态: {status}")
        self.log("=" * 50)
    
    def play_game(self, max_rounds: int = 100):
        self.log("开始游戏主循环")
        
        while not self.game_over and self.round_count < max_rounds:
            self.play_turn()
        
        if self.round_count >= max_rounds:
            self.log(f"达到最大回合数{max_rounds}，游戏强制结束")
            # 找到进化卡最多的玩家作为获胜者
            max_evolution = max(p.get_evolution_card_count() for p in self.players if not p.eliminated)
            winners = [p for p in self.players if p.get_evolution_card_count() == max_evolution and not p.eliminated]
            
            if winners:
                self.winner = random.choice(winners) if len(winners) > 1 else winners[0]
                self.log(f"{self.winner.name} 拥有最多的进化卡({max_evolution}张)，获得胜利！")
            
            self.log_game_end()

# 主函数
def main():
    # 创建玩家
    player_names = ["玩家A", "玩家B", "玩家C", "玩家D"]
    
    # 创建游戏实例
    game = EvolutionGame(player_names, "evolution_game_logs")
    
    # 开始游戏
    game.play_game(max_rounds=50)

if __name__ == "__main__":
    main()