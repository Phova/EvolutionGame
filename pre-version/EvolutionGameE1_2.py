import random
from enum import Enum
from typing import List, Dict, Optional, Tuple, Any
import os
import datetime

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
    FINISH = "终点格"

class ActionType(Enum):
    COOPERATE = "合作"
    DECEIVE = "欺骗"

# 卡牌基类
class Card:
    def __init__(self, card_type: CardType, name: str = ""):
        self.card_type = card_type
        self.name = name
    
    def __str__(self):
        return f"{self.card_type.value}: {self.name}"

# 策略卡（合作/欺骗）
class StrategyCard(Card):
    def __init__(self, action_type: ActionType):
        card_type = CardType.COOPERATION if action_type == ActionType.COOPERATE else CardType.DECEPTION
        super().__init__(card_type, action_type.value)
        self.action_type = action_type

# 进化卡
class EvolutionCard(Card):
    def __init__(self):
        super().__init__(CardType.EVOLUTION, "进化卡")

# 事件卡
class EventCard(Card):
    def __init__(self, name: str, effect: str):
        super().__init__(CardType.EVENT, name)
        self.effect = effect

# 环境变化卡
class EnvironmentChangeCard(Card):
    def __init__(self, name: str, effect: str):
        super().__init__(CardType.ENVIRONMENT_CHANGE, name)
        self.effect = effect

# 能力卡
class AbilityCard(Card):
    def __init__(self, name: str, effect: str):
        super().__init__(CardType.ABILITY, name)
        self.effect = effect

# 游戏格子
class Grid:
    def __init__(self, grid_type: GridType, position: int):
        self.grid_type = grid_type
        self.position = position
    
    def __str__(self):
        return f"{self.position}: {self.grid_type.value}"
    
    def get_symbol(self):
        """获取格子的符号表示"""
        symbols = {
            GridType.START: "起",
            GridType.TRUST_EVOLUTION: "信",
            GridType.HAWK_DOVE: "鹰",
            GridType.RESOURCE_RICH: "资",
            GridType.NATURAL_DISASTER: "灾",
            GridType.COOPERATION_SANCTUARY: "合",
            GridType.DECEPTION_SWAMP: "欺",
            GridType.MUTATION_EVENT: "事",
            GridType.EVOLUTION_LAB: "实",
            GridType.FINISH: "终"
        }
        return symbols.get(self.grid_type, "?")

# 玩家类
class Player:
    def __init__(self, name: str, marker: str):
        self.name = name
        self.marker = marker
        self.position = 0  # 起始位置
        self.hand = {
            CardType.COOPERATION: [],
            CardType.DECEPTION: [],
            CardType.EVOLUTION: [],
            CardType.EVENT: [],
            CardType.ABILITY: []
        }
        self.evolution_points = 0
        self.abilities = []  # 获得的能力卡
        self.is_eliminated = False
    
    def get_hand_limit(self) -> int:
        """计算手牌上限（仅针对合作卡和欺骗卡）"""
        evolution_cards_count = len(self.hand[CardType.EVOLUTION])
        return evolution_cards_count // 2  # 向下取整
    
    def check_hand_limit(self):
        """检查并调整手牌数量，确保不超过上限"""
        hand_limit = self.get_hand_limit()
        total_strategy_cards = len(self.hand[CardType.COOPERATION]) + len(self.hand[CardType.DECEPTION])
        
        if total_strategy_cards > hand_limit:
            # 需要弃置多余的牌
            excess = total_strategy_cards - hand_limit
            # 简单实现：随机弃置
            for _ in range(excess):
                if self.hand[CardType.COOPERATION] and self.hand[CardType.DECEPTION]:
                    # 随机选择弃置合作卡或欺骗卡
                    if random.random() < 0.5:
                        self.hand[CardType.COOPERATION].pop()
                    else:
                        self.hand[CardType.DECEPTION].pop()
                elif self.hand[CardType.COOPERATION]:
                    self.hand[CardType.COOPERATION].pop()
                elif self.hand[CardType.DECEPTION]:
                    self.hand[CardType.DECEPTION].pop()
    
    def add_card(self, card: Card):
        """添加卡牌到手牌"""
        if card.card_type in [CardType.COOPERATION, CardType.DECEPTION, CardType.EVOLUTION]:
            self.hand[card.card_type].append(card)
            # 如果是策略卡，需要检查手牌上限
            if card.card_type in [CardType.COOPERATION, CardType.DECEPTION]:
                self.check_hand_limit()
        elif card.card_type == CardType.ABILITY:
            self.abilities.append(card)
        elif card.card_type == CardType.EVENT:
            self.hand[CardType.EVENT].append(card)
    
    def remove_card(self, card_type: CardType, count: int = 1):
        """从手牌中移除指定类型的卡牌"""
        if card_type in self.hand and len(self.hand[card_type]) >= count:
            for _ in range(count):
                self.hand[card_type].pop()
            return True
        return False
    
    def has_evolution_cards(self, count: int) -> bool:
        """检查是否有足够数量的进化卡"""
        return len(self.hand[CardType.EVOLUTION]) >= count
    
    def get_evolution_card_count(self) -> int:
        """获取进化卡数量"""
        return len(self.hand[CardType.EVOLUTION])
    
    def is_victorious(self) -> bool:
        """检查是否获胜（拥有20张或更多进化卡）"""
        return self.get_evolution_card_count() >= 20
    
    def is_eliminated_check(self) -> bool:
        """检查是否被淘汰（进化卡数量为0）"""
        if self.get_evolution_card_count() == 0:
            self.is_eliminated = True
        return self.is_eliminated

# 游戏板类
class GameBoard:
    def __init__(self, grid_count: int = 24):  # 默认24个格子的环形路径
        self.grids = []
        self.grid_count = grid_count
        self.initialize_grids()
    
    def initialize_grids(self):
        """初始化游戏板上的格子"""
        # 创建起点格
        self.grids.append(Grid(GridType.START, 0))
        
        # 创建其他格子（简化实现，实际应根据规则分布）
        # 使用固定分布以便更好地展示地图
        grid_types = [
            GridType.RESOURCE_RICH,
            GridType.TRUST_EVOLUTION,
            GridType.NATURAL_DISASTER,
            GridType.HAWK_DOVE,
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
            GridType.EVOLUTION_LAB,
            GridType.RESOURCE_RICH,
            GridType.TRUST_EVOLUTION,
            GridType.NATURAL_DISASTER,
            GridType.HAWK_DOVE,
            GridType.COOPERATION_SANCTUARY,
            GridType.DECEPTION_SWAMP,
            GridType.MUTATION_EVENT,
            GridType.FINISH
        ]
        
        for i in range(1, self.grid_count):
            self.grids.append(Grid(grid_types[i-1], i))
    
    def get_grid(self, position: int) -> Grid:
        """获取指定位置的格子"""
        # 处理环形路径
        actual_position = position % self.grid_count
        return self.grids[actual_position]
    
    def change_grid_type(self, position: int, new_type: GridType):
        """改变指定位置格子的类型（环境变化卡效果）"""
        if 0 <= position < len(self.grids):
            self.grids[position].grid_type = new_type
    
    def display_map(self, players: List[Player], log_func=print):
        """显示地图和玩家位置"""
        log_func("\n" + "="*60)
        log_func("游戏地图")
        log_func("="*60)
        
        # 显示格子类型
        grid_line = "|"
        for i, grid in enumerate(self.grids):
            grid_line += f" {grid.get_symbol()}{i:2d} |"
        log_func(grid_line)
        
        # 显示玩家位置
        for i in range(len(players)):
            player_line = "|"
            for j, grid in enumerate(self.grids):
                players_on_grid = [p for p in players if p.position == j and not p.is_eliminated]
                if players_on_grid:
                    # 显示该位置上的玩家标记
                    markers = "".join([p.marker for p in players_on_grid])
                    player_line += f" {markers:3s} |"
                else:
                    player_line += "     |"
            log_func(player_line)
        
        # 显示格子类型说明
        log_func("\n格子类型说明:")
        log_func("起:起点格 | 信:信任进化格 | 鹰:鹰鸽博弈格 | 资:资源丰富格 | 灾:自然灾害格")
        log_func("合:合作圣地格 | 欺:欺骗沼泽格 | 事:突变事件格 | 实:进化实验室格 | 终:终点格")
        log_func("="*60)

# 牌库类
class Deck:
    def __init__(self, card_type: CardType):
        self.card_type = card_type
        self.cards = []
        self.discard_pile = []
    
    def initialize_deck(self, card_count: int, card_class, **kwargs):
        """初始化牌库"""
        self.cards = [card_class(**kwargs) for _ in range(card_count)]
        self.shuffle()
    
    def shuffle(self):
        """洗牌"""
        random.shuffle(self.cards)
    
    def draw(self, count: int = 1) -> List[Card]:
        """抽牌"""
        drawn_cards = []
        for _ in range(count):
            if not self.cards:
                # 如果牌库空了，将弃牌堆洗牌后作为新牌库
                if self.discard_pile:
                    self.cards = self.discard_pile
                    self.discard_pile = []
                    self.shuffle()
                else:
                    # 牌库和弃牌堆都为空，无法抽牌
                    break
            
            if self.cards:
                drawn_cards.append(self.cards.pop())
        
        return drawn_cards
    
    def add_to_discard(self, card: Card):
        """将卡牌加入弃牌堆"""
        self.discard_pile.append(card)
    
    def is_empty(self) -> bool:
        """检查牌库是否为空"""
        return len(self.cards) == 0 and len(self.discard_pile) == 0
    
    def get_remaining_cards(self) -> int:
        """获取剩余卡牌数量"""
        return len(self.cards) + len(self.discard_pile)

# 游戏类
class EvolutionGame:
    def __init__(self, player_names: List[str], game_id: str = None):
        self.players = [Player(name, f"P{i+1}") for i, name in enumerate(player_names)]
        self.board = GameBoard()
        self.current_player_index = 0
        self.turn_order_clockwise = True
        self.game_over = False
        self.winner = None
        
        # 游戏ID和日志设置
        if game_id is None:
            self.game_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        else:
            self.game_id = game_id
        
        # 创建日志目录
        self.log_dir = "game_logs"
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        
        # 初始化日志文件
        self.log_file = open(os.path.join(self.log_dir, f"game_{self.game_id}.txt"), "w", encoding="utf-8")
        self.log("=== Evolution Game 开始 ===")
        self.log(f"游戏ID: {self.game_id}")
        self.log(f"玩家: {', '.join(player_names)}")
        
        # 初始化各种牌库
        self.cooperation_deck = Deck(CardType.COOPERATION)
        self.deception_deck = Deck(CardType.DECEPTION)
        self.evolution_deck = Deck(CardType.EVOLUTION)
        self.event_deck = Deck(CardType.EVENT)
        self.environment_change_deck = Deck(CardType.ENVIRONMENT_CHANGE)
        self.ability_deck = Deck(CardType.ABILITY)
        
        self.initialize_decks()
        self.initial_deal()
        
        # 游戏开始时显示地图
        self.board.display_map(self.players, self.log)
    
    def log(self, message: str):
        """记录游戏日志，同时输出到控制台和文件"""
        print(message)
        self.log_file.write(message + "\n")
        self.log_file.flush()  # 确保立即写入文件
    
    def initialize_decks(self):
        """初始化所有牌库"""
        # 合作卡和欺骗卡
        self.cooperation_deck.initialize_deck(25, StrategyCard, action_type=ActionType.COOPERATE)
        self.deception_deck.initialize_deck(25, StrategyCard, action_type=ActionType.DECEIVE)
        
        # 进化卡
        self.evolution_deck.initialize_deck(125, EvolutionCard)
        
        # 事件卡（简化实现，实际应根据描述创建不同的事件卡）
        self.event_deck.initialize_deck(30, EventCard, name="事件卡", effect="随机事件效果")
        
        # 环境变化卡（简化实现）
        self.environment_change_deck.initialize_deck(10, EnvironmentChangeCard, name="环境变化卡", effect="改变地图格局")
        
        # 能力卡（简化实现）
        self.ability_deck.initialize_deck(20, AbilityCard, name="能力卡", effect="特殊能力效果")
    
    def initial_deal(self):
        """初始发牌"""
        player_count = len(self.players)
        
        for player in self.players:
            # 起始手牌：总数为(玩家数-1)张策略卡
            strategy_card_count = player_count - 1
            cooperation_cards = self.cooperation_deck.draw(strategy_card_count // 2)
            deception_cards = self.deception_deck.draw(strategy_card_count - len(cooperation_cards))
            
            for card in cooperation_cards:
                player.add_card(card)
            for card in deception_cards:
                player.add_card(card)
            
            # 5张进化卡
            evolution_cards = self.evolution_deck.draw(5)
            for card in evolution_cards:
                player.add_card(card)
            
            self.log(f"{player.name} 获得起始手牌: {strategy_card_count}张策略卡和5张进化卡")
    
    def get_current_player(self) -> Player:
        """获取当前回合玩家"""
        return self.players[self.current_player_index]
    
    def next_player(self):
        """移动到下一个玩家"""
        # 检查是否所有玩家都被淘汰
        active_players = [p for p in self.players if not p.is_eliminated]
        if len(active_players) == 0:
            self.game_over = True
            self.log("所有玩家都被淘汰，游戏结束！")
            return
        
        # 查找下一个未被淘汰的玩家
        original_index = self.current_player_index
        attempts = 0
        max_attempts = len(self.players)  # 防止无限循环
        
        while attempts < max_attempts:
            if self.turn_order_clockwise:
                self.current_player_index = (self.current_player_index + 1) % len(self.players)
            else:
                self.current_player_index = (self.current_player_index - 1) % len(self.players)
            
            attempts += 1
            
            # 如果找到未被淘汰的玩家，退出循环
            if not self.get_current_player().is_eliminated:
                break
            
            # 如果回到起点，说明没有找到未被淘汰的玩家
            if self.current_player_index == original_index:
                self.game_over = True
                self.log("没有可行动的玩家，游戏结束！")
                break
    
    def roll_dice(self) -> int:
        """掷骰子"""
        return random.randint(1, 6)
    
    def move_player(self, player: Player, steps: int):
        """移动玩家"""
        player.position = (player.position + steps) % self.board.grid_count
    
    def resolve_grid_effect(self, player: Player, grid: Grid):
        """解析格子效果"""
        grid_type = grid.grid_type
        
        if grid_type == GridType.START:
            # 起点格无效果
            pass
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
        elif grid_type == GridType.FINISH:
            self.resolve_finish(player)
    
    def safe_draw_strategy_card(self, deck: Deck) -> Optional[Card]:
        """安全地抽取策略卡，如果牌库为空则返回None"""
        if deck.is_empty():
            return None
        drawn_cards = deck.draw(1)
        return drawn_cards[0] if drawn_cards else None
    
    def resolve_trust_evolution(self, current_player: Player):
        """解析信任进化格效果"""
        self.log(f"{current_player.name} 触发了信任进化格")
        
        # 所有玩家秘密指定一名其他玩家作为目标
        targets = {}
        for player in self.players:
            if player.is_eliminated:
                continue
            # 简化实现：随机选择目标
            available_targets = [p for p in self.players if p != player and not p.is_eliminated]
            if available_targets:
                targets[player] = random.choice(available_targets)
        
        # 所有玩家同时出牌
        actions = {}
        for player in self.players:
            if player.is_eliminated:
                continue
            # 简化实现：随机出牌
            if player.hand[CardType.COOPERATION] and player.hand[CardType.DECEPTION]:
                action = random.choice([ActionType.COOPERATE, ActionType.DECEIVE])
            elif player.hand[CardType.COOPERATION]:
                action = ActionType.COOPERATE
            elif player.hand[CardType.DECEPTION]:
                action = ActionType.DECEIVE
            else:
                # 没有策略卡，无法参与
                continue
            
            actions[player] = action
            # 使用一张牌
            if action == ActionType.COOPERATE:
                player.remove_card(CardType.COOPERATION)
            else:
                player.remove_card(CardType.DECEPTION)
        
        # 结算效果
        for player, target in targets.items():
            if player not in actions or target not in actions:
                continue
            
            player_action = actions[player]
            target_action = actions[target]
            
            if player_action == ActionType.COOPERATE and target_action == ActionType.COOPERATE:
                # 合作 vs 合作：双方各获得2点进化点数
                player.evolution_points += 2
                target.evolution_points += 2
                self.log(f"{player.name} 和 {target.name} 合作，各获得2点进化点数")
            elif player_action == ActionType.COOPERATE and target_action == ActionType.DECEIVE:
                # 合作 vs 欺骗：出合作方获得1点进化点数，出欺骗方抽取3张进化卡
                player.evolution_points += 1
                evolution_cards = self.evolution_deck.draw(3)
                for card in evolution_cards:
                    target.add_card(card)
                self.log(f"{player.name} 被 {target.name} 欺骗，{player.name} 获得1点进化点数，{target.name} 抽取3张进化卡")
            elif player_action == ActionType.DECEIVE and target_action == ActionType.COOPERATE:
                # 欺骗 vs 合作：出欺骗方抽取3张进化卡，出合作方获得1点进化点数
                evolution_cards = self.evolution_deck.draw(3)
                for card in evolution_cards:
                    player.add_card(card)
                target.evolution_points += 1
                self.log(f"{player.name} 欺骗了 {target.name}，{player.name} 抽取3张进化卡，{target.name} 获得1点进化点数")
            else:  # 欺骗 vs 欺骗
                # 双方各弃置1张进化卡
                if player.has_evolution_cards(1):
                    player.remove_card(CardType.EVOLUTION)
                if target.has_evolution_cards(1):
                    target.remove_card(CardType.EVOLUTION)
                self.log(f"{player.name} 和 {target.name} 互相欺骗，各弃置1张进化卡")
        
        # 所有玩家可补充一张合作或欺骗卡
        for player in self.players:
            if player.is_eliminated:
                continue
            # 简化实现：随机补充
            if random.random() < 0.5:
                card = self.safe_draw_strategy_card(self.cooperation_deck)
            else:
                card = self.safe_draw_strategy_card(self.deception_deck)
            
            if card:
                player.add_card(card)
                self.log(f"{player.name} 补充了一张{card.card_type.value}")
            else:
                self.log(f"{player.name} 无法补充策略卡，牌库已空")
    
    def resolve_hawk_dove(self, current_player: Player):
        """解析鹰鸽博弈格效果"""
        self.log(f"{current_player.name} 触发了鹰鸽博弈格")
        
        # 当前回合玩家指定一名对手
        available_opponents = [p for p in self.players if p != current_player and not p.is_eliminated]
        if not available_opponents:
            return
        
        opponent = random.choice(available_opponents)
        self.log(f"{current_player.name} 选择了与 {opponent.name} 进行鹰鸽博弈")
        
        # 双方秘密出牌
        if current_player.hand[CardType.COOPERATION] and current_player.hand[CardType.DECEPTION]:
            current_action = random.choice([ActionType.COOPERATE, ActionType.DECEIVE])
        elif current_player.hand[CardType.COOPERATION]:
            current_action = ActionType.COOPERATE
        elif current_player.hand[CardType.DECEPTION]:
            current_action = ActionType.DECEIVE
        else:
            # 没有策略卡，无法参与
            return
        
        if opponent.hand[CardType.COOPERATION] and opponent.hand[CardType.DECEPTION]:
            opponent_action = random.choice([ActionType.COOPERATE, ActionType.DECEIVE])
        elif opponent.hand[CardType.COOPERATION]:
            opponent_action = ActionType.COOPERATE
        elif opponent.hand[CardType.DECEPTION]:
            opponent_action = ActionType.DECEIVE
        else:
            # 没有策略卡，无法参与
            return
        
        # 使用一张牌
        if current_action == ActionType.COOPERATE:
            current_player.remove_card(CardType.COOPERATION)
        else:
            current_player.remove_card(CardType.DECEPTION)
        
        if opponent_action == ActionType.COOPERATE:
            opponent.remove_card(CardType.COOPERATION)
        else:
            opponent.remove_card(CardType.DECEPTION)
        
        # 结算效果
        if current_action == ActionType.COOPERATE and opponent_action == ActionType.COOPERATE:
            # 鸽 vs 鸽：双方各获得2点进化点数
            current_player.evolution_points += 2
            opponent.evolution_points += 2
            self.log(f"{current_player.name} 和 {opponent.name} 都选择合作，各获得2点进化点数")
        elif current_action == ActionType.DECEIVE and opponent_action == ActionType.COOPERATE:
            # 鹰 vs 鸽：出鹰方抽取3张进化卡，出鸽方获得1点进化点数
            evolution_cards = self.evolution_deck.draw(3)
            for card in evolution_cards:
                current_player.add_card(card)
            opponent.evolution_points += 1
            self.log(f"{current_player.name} 欺骗了 {opponent.name}，{current_player.name} 抽取3张进化卡，{opponent.name} 获得1点进化点数")
        elif current_action == ActionType.COOPERATE and opponent_action == ActionType.DECEIVE:
            # 鸽 vs 鹰：出鹰方抽取3张进化卡，出鸽方获得1点进化点数
            evolution_cards = self.evolution_deck.draw(3)
            for card in evolution_cards:
                opponent.add_card(card)
            current_player.evolution_points += 1
            self.log(f"{opponent.name} 欺骗了 {current_player.name}，{opponent.name} 抽取3张进化卡，{current_player.name} 获得1点进化点数")
        else:  # 鹰 vs 鹰
            # 双方各弃置2张进化卡
            if current_player.has_evolution_cards(2):
                current_player.remove_card(CardType.EVOLUTION, 2)
            if opponent.has_evolution_cards(2):
                opponent.remove_card(CardType.EVOLUTION, 2)
            self.log(f"{current_player.name} 和 {opponent.name} 都选择欺骗，各弃置2张进化卡")
        
        # 参与玩家可补充一张所出牌型的卡
        if current_action == ActionType.COOPERATE:
            card = self.safe_draw_strategy_card(self.cooperation_deck)
        else:
            card = self.safe_draw_strategy_card(self.deception_deck)
        
        if card:
            current_player.add_card(card)
        
        if opponent_action == ActionType.COOPERATE:
            card = self.safe_draw_strategy_card(self.cooperation_deck)
        else:
            card = self.safe_draw_strategy_card(self.deception_deck)
        
        if card:
            opponent.add_card(card)
    
    def resolve_resource_rich(self, current_player: Player):
        """解析资源丰富格效果"""
        self.log(f"{current_player.name} 触发了资源丰富格")
        
        # 所有玩家出一张牌
        for player in self.players:
            if player.is_eliminated:
                continue
            
            # 简化实现：随机出牌
            if player.hand[CardType.COOPERATION] and player.hand[CardType.DECEPTION]:
                action = random.choice([ActionType.COOPERATE, ActionType.DECEIVE])
            elif player.hand[CardType.COOPERATION]:
                action = ActionType.COOPERATE
            elif player.hand[CardType.DECEPTION]:
                action = ActionType.DECEIVE
            else:
                # 没有策略卡，无法参与
                continue
            
            # 使用一张牌
            if action == ActionType.COOPERATE:
                player.remove_card(CardType.COOPERATION)
                # 出合作卡：抽取2张进化卡
                evolution_cards = self.evolution_deck.draw(2)
                for card in evolution_cards:
                    player.add_card(card)
                self.log(f"{player.name} 选择合作，抽取2张进化卡")
            else:
                player.remove_card(CardType.DECEPTION)
                # 出欺骗卡：掷骰子，1-4无所获，5-6抽取4张进化卡
                dice_roll = self.roll_dice()
                if dice_roll >= 5:
                    evolution_cards = self.evolution_deck.draw(4)
                    for card in evolution_cards:
                        player.add_card(card)
                    self.log(f"{player.name} 选择欺骗，掷出{dice_roll}，抽取4张进化卡")
                else:
                    self.log(f"{player.name} 选择欺骗，掷出{dice_roll}，无所获")
    
    def resolve_natural_disaster(self, current_player: Player):
        """解析自然灾害格效果"""
        self.log(f"{current_player.name} 触发了自然灾害格")
        
        # 所有玩家出一张牌
        for player in self.players:
            if player.is_eliminated:
                continue
            
            # 简化实现：随机出牌
            if player.hand[CardType.COOPERATION] and player.hand[CardType.DECEPTION]:
                action = random.choice([ActionType.COOPERATE, ActionType.DECEIVE])
            elif player.hand[CardType.COOPERATION]:
                action = ActionType.COOPERATE
            elif player.hand[CardType.DECEPTION]:
                action = ActionType.DECEIVE
            else:
                # 没有策略卡，无法参与
                continue
            
            # 使用一张牌
            if action == ActionType.COOPERATE:
                player.remove_card(CardType.COOPERATION)
                # 出合作卡：免疫本次灾害
                self.log(f"{player.name} 选择合作，免疫自然灾害")
            else:
                player.remove_card(CardType.DECEPTION)
                # 出欺骗卡：必须弃置1张进化卡，然后可以指定一名其他玩家也必须弃置1张进化卡
                if player.has_evolution_cards(1):
                    player.remove_card(CardType.EVOLUTION)
                    # 简化实现：随机指定一名其他玩家
                    available_targets = [p for p in self.players if p != player and not p.is_eliminated]
                    if available_targets:
                        target = random.choice(available_targets)
                        if target.has_evolution_cards(1):
                            target.remove_card(CardType.EVOLUTION)
                            self.log(f"{player.name} 选择欺骗，弃置1张进化卡，并让 {target.name} 也弃置1张进化卡")
                        else:
                            self.log(f"{player.name} 选择欺骗，弃置1张进化卡，但 {target.name} 没有进化卡可弃置")
                    else:
                        self.log(f"{player.name} 选择欺骗，弃置1张进化卡，但没有其他玩家可指定")
                else:
                    self.log(f"{player.name} 选择欺骗，但没有进化卡可弃置")
    
    def resolve_cooperation_sanctuary(self, current_player: Player):
        """解析合作圣地格效果"""
        self.log(f"{current_player.name} 触发了合作圣地格")
        
        # 记录所有玩家的选择
        actions = {}
        for player in self.players:
            if player.is_eliminated:
                continue
            
            # 简化实现：随机出牌
            if player.hand[CardType.COOPERATION] and player.hand[CardType.DECEPTION]:
                action = random.choice([ActionType.COOPERATE, ActionType.DECEIVE])
            elif player.hand[CardType.COOPERATION]:
                action = ActionType.COOPERATE
            elif player.hand[CardType.DECEPTION]:
                action = ActionType.DECEIVE
            else:
                # 没有策略卡，无法参与
                continue
            
            actions[player] = action
            # 使用一张牌
            if action == ActionType.COOPERATE:
                player.remove_card(CardType.COOPERATION)
            else:
                player.remove_card(CardType.DECEPTION)
        
        # 结算效果
        cooperators = [player for player, action in actions.items() if action == ActionType.COOPERATE]
        deceivers = [player for player, action in actions.items() if action == ActionType.DECEIVE]
        
        # 处理合作者
        for player in cooperators:
            # 可选择另一位也出合作卡的玩家
            other_cooperators = [p for p in cooperators if p != player]
            if other_cooperators:
                partner = random.choice(other_cooperators)
                # 双方各抽取3张进化卡
                evolution_cards = self.evolution_deck.draw(3)
                for card in evolution_cards:
                    player.add_card(card)
                evolution_cards = self.evolution_deck.draw(3)
                for card in evolution_cards:
                    partner.add_card(card)
                self.log(f"{player.name} 和 {partner.name} 合作，各抽取3张进化卡")
            else:
                self.log(f"{player.name} 选择合作，但没有其他合作者，无收益")
        
        # 处理欺骗者
        for player in deceivers:
            # 单独抽取4张进化卡
            evolution_cards = self.evolution_deck.draw(4)
            for card in evolution_cards:
                player.add_card(card)
            self.log(f"{player.name} 选择欺骗，单独抽取4张进化卡")
            
            # 下家获得一次免费的挑战权
            next_player_index = (self.players.index(player) + 1) % len(self.players)
            next_player = self.players[next_player_index]
            if not next_player.is_eliminated:
                # 记录挑战权（简化实现）
                self.log(f"{next_player.name} 获得对 {player.name} 的免费挑战权")
    
    def resolve_deception_swamp(self, current_player: Player):
        """解析欺骗沼泽格效果"""
        self.log(f"{current_player.name} 触发了欺骗沼泽格")
        
        # 记录所有玩家的选择
        actions = {}
        for player in self.players:
            if player.is_eliminated:
                continue
            
            # 简化实现：随机出牌
            if player.hand[CardType.COOPERATION] and player.hand[CardType.DECEPTION]:
                action = random.choice([ActionType.COOPERATE, ActionType.DECEIVE])
            elif player.hand[CardType.COOPERATION]:
                action = ActionType.COOPERATE
            elif player.hand[CardType.DECEPTION]:
                action = ActionType.DECEIVE
            else:
                # 没有策略卡，无法参与
                continue
            
            actions[player] = action
            # 使用一张牌
            if action == ActionType.COOPERATE:
                player.remove_card(CardType.COOPERATION)
            else:
                player.remove_card(CardType.DECEPTION)
        
        # 结算效果
        for player, action in actions.items():
            if action == ActionType.DECEIVE:
                # 出欺骗卡：可以查看能力牌库顶3张牌，拿取其中1张
                self.log(f"{player.name} 选择欺骗，查看能力牌库顶3张牌并拿取1张")
                # 简化实现：随机获得一张能力卡
                if not self.ability_deck.is_empty():
                    ability_card = self.ability_deck.draw(1)[0]
                    player.add_card(ability_card)
                    self.log(f"{player.name} 获得了能力卡: {ability_card.name}")
                else:
                    self.log("能力牌库已空，无法获得能力卡")
            
            elif action == ActionType.COOPERATE:
                # 出合作卡：可指定一名出欺骗卡的玩家，阻止其收益，并因此抽取1张进化卡
                deceivers = [p for p, a in actions.items() if a == ActionType.DECEIVE]
                if deceivers:
                    target = random.choice(deceivers)
                    # 阻止目标获得能力卡（简化实现）
                    self.log(f"{player.name} 选择合作，阻止了 {target.name} 获得能力卡，并抽取1张进化卡")
                    evolution_card = self.evolution_deck.draw(1)
                    if evolution_card:
                        player.add_card(evolution_card[0])
                else:
                    self.log(f"{player.name} 选择合作，但没有欺骗者可指定，无收益")
    
    def resolve_mutation_event(self, current_player: Player):
        """解析突变事件格效果"""
        self.log(f"{current_player.name} 触发了突变事件格")
        
        # 抽一张事件卡并立即执行其效果
        if not self.event_deck.is_empty():
            event_card = self.event_deck.draw(1)[0]
            self.log(f"{current_player.name} 抽到事件卡: {event_card.name}")
            # 简化实现：随机效果
            effect_type = random.randint(1, 5)
            
            if effect_type == 1:
                # 基因突变：抽取3张进化卡，但下个回合无法移动
                evolution_cards = self.evolution_deck.draw(3)
                for card in evolution_cards:
                    current_player.add_card(card)
                # 记录下回合无法移动（简化实现）
                self.log(f"{current_player.name} 获得基因突变效果：抽取3张进化卡，但下回合无法移动")
            elif effect_type == 2:
                # 群体迁徙：所有玩家移动到下一个与当前所在格类型相同的格子
                current_grid_type = self.board.get_grid(current_player.position).grid_type
                for player in self.players:
                    if player.is_eliminated:
                        continue
                    # 找到下一个相同类型的格子
                    next_position = (player.position + 1) % self.board.grid_count
                    while self.board.get_grid(next_position).grid_type != current_grid_type:
                        next_position = (next_position + 1) % self.board.grid_count
                    player.position = next_position
                    self.log(f"{player.name} 移动到位置 {next_position}")
            elif effect_type == 3:
                # 互利共生：选择一名玩家，双方各抽取2张进化卡
                available_players = [p for p in self.players if p != current_player and not p.is_eliminated]
                if available_players:
                    target = random.choice(available_players)
                    evolution_cards = self.evolution_deck.draw(2)
                    for card in evolution_cards:
                        current_player.add_card(card)
                    evolution_cards = self.evolution_deck.draw(2)
                    for card in evolution_cards:
                        target.add_card(card)
                    self.log(f"{current_player.name} 和 {target.name} 互利共生，各抽取2张进化卡")
            elif effect_type == 4:
                # 自然选择：当前进化卡数量最少的玩家必须弃置2张进化卡
                active_players = [p for p in self.players if not p.is_eliminated]
                if active_players:
                    min_evolution_count = min(p.get_evolution_card_count() for p in active_players)
                    victims = [p for p in active_players if p.get_evolution_card_count() == min_evolution_count]
                    for victim in victims:
                        if victim.has_evolution_cards(2):
                            victim.remove_card(CardType.EVOLUTION, 2)
                            self.log(f"{victim.name} 被自然选择，弃置2张进化卡")
                        elif victim.has_evolution_cards(1):
                            victim.remove_card(CardType.EVOLUTION, 1)
                            self.log(f"{victim.name} 被自然选择，弃置1张进化卡")
                        else:
                            self.log(f"{victim.name} 被自然选择，但没有进化卡可弃置")
            else:
                # 加速进化：抽取2张进化卡，并可以立即额外移动2步
                evolution_cards = self.evolution_deck.draw(2)
                for card in evolution_cards:
                    current_player.add_card(card)
                self.move_player(current_player, 2)
                new_grid = self.board.get_grid(current_player.position)
                self.log(f"{current_player.name} 获得加速进化效果：抽取2张进化卡，并移动到位置 {current_player.position} ({new_grid.grid_type.value})")
                self.resolve_grid_effect(current_player, new_grid)
        else:
            self.log("事件牌库已空，无效果")
    
    def resolve_evolution_lab(self, current_player: Player):
        """解析进化实验室格效果"""
        self.log(f"{current_player.name} 触发了进化实验室格")
        
        # 可支付2张进化卡的代价，获得一张能力卡
        if current_player.has_evolution_cards(2):
            current_player.remove_card(CardType.EVOLUTION, 2)
            if not self.ability_deck.is_empty():
                ability_card = self.ability_deck.draw(1)[0]
                current_player.add_card(ability_card)
                self.log(f"{current_player.name} 支付2张进化卡，获得了能力卡: {ability_card.name}")
            else:
                self.log("能力牌库已空，无效果")
        else:
            self.log(f"{current_player.name} 没有足够的进化卡支付代价")
    
    def resolve_finish(self, current_player: Player):
        """解析终点格效果"""
        self.log(f"{current_player.name} 抵达了终点格")
        
        # 首次抵达此格的玩家立即抽取3张进化卡并获得2点进化点数
        # 简化实现：每次抵达都有效果
        evolution_cards = self.evolution_deck.draw(3)
        for card in evolution_cards:
            current_player.add_card(card)
        current_player.evolution_points += 2
        self.log(f"{current_player.name} 获得3张进化卡和2点进化点数")
    
    def optional_actions(self, current_player: Player):
        """执行可选行动"""
        # 简化实现：随机选择是否执行可选行动
        if random.random() < 0.5:
            # 兑换进化点数
            if current_player.evolution_points > 0:
                points_to_convert = random.randint(1, current_player.evolution_points)
                evolution_cards = self.evolution_deck.draw(points_to_convert)
                if evolution_cards:
                    for card in evolution_cards:
                        current_player.add_card(card)
                    current_player.evolution_points -= points_to_convert
                    self.log(f"{current_player.name} 兑换了{points_to_convert}点进化点数，获得{len(evolution_cards)}张进化卡")
                else:
                    self.log("进化牌库已空，无法兑换")
        
        # 简化实现：不使用事件卡和能力卡
    
    def environment_change(self, current_player: Player):
        """执行环境变化（可选规则）"""
        # 简化实现：随机决定是否执行环境变化
        if random.random() < 0.3 and not self.environment_change_deck.is_empty():
            environment_card = self.environment_change_deck.draw(1)[0]
            self.log(f"{current_player.name} 抽到环境变化卡: {environment_card.name}")
            
            # 简化实现：随机改变一个格子的类型
            grid_to_change = random.randint(1, self.board.grid_count - 2)  # 不改变起点和终点
            new_type = random.choice([gt for gt in GridType if gt not in [GridType.START, GridType.FINISH]])
            self.board.change_grid_type(grid_to_change, new_type)
            self.log(f"位置 {grid_to_change} 的格子变为 {new_type.value}")
    
    def check_elimination(self):
        """检查是否有玩家被淘汰"""
        for player in self.players:
            if not player.is_eliminated and player.is_eliminated_check():
                self.log(f"{player.name} 的物种灭绝了！")
    
    def check_victory(self) -> bool:
        """检查是否有玩家获胜"""
        # 检查进化胜利条件
        for player in self.players:
            if not player.is_eliminated and player.is_victorious():
                self.game_over = True
                self.winner = player
                self.log(f"{player.name} 获得了进化胜利！")
                return True
        
        # 检查场上只剩一名玩家的情况
        active_players = [p for p in self.players if not p.is_eliminated]
        if len(active_players) == 1:
            self.game_over = True
            self.winner = active_players[0]
            self.log(f"{self.winner.name} 是场上唯一的玩家，获得胜利！")
            return True
        
        # 检查是否所有玩家都被淘汰
        if len(active_players) == 0:
            self.game_over = True
            self.log("所有玩家都被淘汰，游戏结束！")
            return True
        
        return False
    
    def display_player_status(self):
        """显示所有玩家状态"""
        self.log("\n玩家状态:")
        for player in self.players:
            if player.is_eliminated:
                self.log(f"{player.name} ({player.marker}): 已淘汰")
            else:
                self.log(f"{player.name} ({player.marker}): 位置{player.position}, 进化卡{player.get_evolution_card_count()}张, 进化点数{player.evolution_points}点")
    
    def play_turn(self):
        """执行一个完整的回合"""
        current_player = self.get_current_player()
        
        if current_player.is_eliminated:
            self.next_player()
            return
        
        self.log(f"\n=== {current_player.name} 的回合开始 ===")
        
        # 显示当前地图状态
        self.board.display_map(self.players, self.log)
        self.display_player_status()
        
        # 阶段一：掷骰与移动
        dice_roll = self.roll_dice()
        self.log(f"{current_player.name} 掷出 {dice_roll} 点")
        
        self.move_player(current_player, dice_roll)
        new_grid = self.board.get_grid(current_player.position)
        self.log(f"{current_player.name} 移动到位置 {current_player.position} ({new_grid.grid_type.value})")
        
        # 阶段二：触发并结算格子事件
        self.resolve_grid_effect(current_player, new_grid)
        
        # 阶段三：可选行动
        self.optional_actions(current_player)
        
        # 阶段四：环境变化（可选规则）
        self.environment_change(current_player)
        
        # 检查淘汰和胜利条件
        self.check_elimination()
        if self.check_victory():
            return
        
        # 回合结束，移动到下一个玩家
        self.next_player()
    
    def play_game(self):
        """主游戏循环"""
        round_count = 1
        while not self.game_over and round_count <= 100:  # 防止无限循环
            self.log(f"\n--- 第 {round_count} 轮 ---")
            self.play_turn()
            round_count += 1
        
        if self.winner:
            self.log(f"\n=== 游戏结束！{self.winner.name} 获胜！ ===")
        else:
            self.log("\n=== 游戏结束！没有玩家获胜 ===")
        
        # 关闭日志文件
        self.log_file.close()
        
        # 显示最终结果
        print(f"\n游戏已结束，详细日志保存在: {os.path.join(self.log_dir, f'game_{self.game_id}.txt')}")

# 主程序
if __name__ == "__main__":
    # 创建游戏实例
    player_names = ["玩家1", "玩家2", "玩家3"]
    game = EvolutionGame(player_names)
    
    # 开始游戏
    game.play_game()
