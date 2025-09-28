import random
import os
import json
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional

# 枚举定义
class TileType(Enum):
    START = "起点"
    TRUST_EVOLUTION = "信任进化"
    HAWK_DOVE = "鹰鸽博弈"
    RESOURCE_RICH = "资源丰富"
    NATURAL_DISASTER = "自然灾害"
    COOPERATION_SANCTUARY = "合作圣地"
    DECEPTION_SWAMP = "欺骗沼泽"
    MUTATION_EVENT = "突变事件"
    EVOLUTION_LAB = "进化实验室"
    END = "终点"

class CardType(Enum):
    COOPERATION = "合作卡"
    DECEPTION = "欺骗卡"
    EVOLUTION = "进化卡"
    EVENT = "事件卡"
    ABILITY = "能力卡"
    ENVIRONMENT_CHANGE = "环境变化卡"

class AbilityType(Enum):
    ALTRUISTIC_GENE = "利他基因"
    SCHEME_MASTER = "阴谋大师"
    ENVIRONMENT_ADAPTATION = "环境适应"
    EFFICIENT_METABOLISM = "高效代谢"
    SYMBIOTIC_BOND = "共生纽带"
    DEFENSE_MECHANISM = "防御机制"
    GROUP_DETERRENCE = "群体威慑"
    EXPLOIT_CHAOS = "趁火打劫"
    TENACIOUS_VITALITY = "顽强生命力"
    STRATEGY_SHIFT = "策略变形"
    EVOLUTION_BURST = "进化爆发"
    PREDATORY_INSTINCT = "捕食本能"
    RESOURCE_CONTROL = "资源控制"
    DISASTER_EXPERT = "灾难专家"
    TACTICAL_UPGRADE = "战术升级"
    DESPERATE_SURVIVAL = "绝境求生"
    ECOLOGICAL_TRANSFORMATION = "生态改造"
    EVOLUTIONARY_ADVANTAGE = "进化优势"
    RAPID_ADAPTATION = "快速适应"
    POPULATION_RESILIENCE = "种群韧性"

# 卡牌类
class Card:
    def __init__(self, card_type: CardType, name: str = "", description: str = ""):
        self.card_type = card_type
        self.name = name
        self.description = description
    
    def __str__(self):
        return f"{self.card_type.value}: {self.name}"

# 能力卡类
class AbilityCard(Card):
    def __init__(self, ability_type: AbilityType, description: str):
        super().__init__(CardType.ABILITY, ability_type.value, description)
        self.ability_type = ability_type

# 事件卡类
class EventCard(Card):
    def __init__(self, name: str, description: str):
        super().__init__(CardType.EVENT, name, description)

# 环境变化卡类
class EnvironmentChangeCard(Card):
    def __init__(self, name: str, description: str):
        super().__init__(CardType.ENVIRONMENT_CHANGE, name, description)

# 格子类
class Tile:
    def __init__(self, tile_type: TileType, position: int):
        self.tile_type = tile_type
        self.position = position
    
    def __str__(self):
        return f"{self.position}: {self.tile_type.value}"

# 玩家类
class Player:
    def __init__(self, name: str, player_id: int):
        self.name = name
        self.player_id = player_id
        self.position = 0  # 起始位置
        self.cooperation_cards = []
        self.deception_cards = []
        self.evolution_cards = []
        self.ability_cards = []
        self.event_cards = []
        self.evolution_points = 0
        self.is_active = True
        self.consecutive_no_gain = 0  # 连续未获得进化卡的回合数
        self.has_visited_end = False  # 是否已经访问过终点
    
    def get_hand_size_limit(self):
        """计算手牌上限"""
        return len(self.evolution_cards) // 2
    
    def check_hand_size(self):
        """检查手牌是否超过上限，超过则弃置多余的牌"""
        limit = self.get_hand_size_limit()
        total_strategy_cards = len(self.cooperation_cards) + len(self.deception_cards)
        
        if total_strategy_cards > limit:
            # 需要弃置多余的牌
            excess = total_strategy_cards - limit
            # 简单实现：随机弃置
            for _ in range(excess):
                if self.cooperation_cards and random.random() < 0.5:
                    self.cooperation_cards.pop()
                elif self.deception_cards:
                    self.deception_cards.pop()
    
    def has_card(self, card_type: CardType):
        """检查玩家是否有某种类型的卡牌"""
        if card_type == CardType.COOPERATION:
            return len(self.cooperation_cards) > 0
        elif card_type == CardType.DECEPTION:
            return len(self.deception_cards) > 0
        elif card_type == CardType.EVENT:
            return len(self.event_cards) > 0
        return False
    
    def use_card(self, card_type: CardType):
        """使用一张卡牌"""
        if card_type == CardType.COOPERATION and self.cooperation_cards:
            return self.cooperation_cards.pop(0)
        elif card_type == CardType.DECEPTION and self.deception_cards:
            return self.deception_cards.pop(0)
        elif card_type == CardType.EVENT and self.event_cards:
            return self.event_cards.pop(0)
        return None
    
    def add_card(self, card: Card):
        """添加一张卡牌到玩家手牌"""
        if card.card_type == CardType.COOPERATION:
            self.cooperation_cards.append(card)
        elif card.card_type == CardType.DECEPTION:
            self.deception_cards.append(card)
        elif card.card_type == CardType.EVOLUTION:
            self.evolution_cards.append(card)
        elif card.card_type == CardType.ABILITY:
            self.ability_cards.append(card)
        elif card.card_type == CardType.EVENT:
            self.event_cards.append(card)
    
    def get_total_evolution_cards(self):
        """获取进化卡总数"""
        return len(self.evolution_cards)
    
    def is_eliminated(self):
        """检查玩家是否被淘汰"""
        if len(self.evolution_cards) == 0:
            return True  # 物种灭绝
        # 可选规则：发展停滞
        if self.consecutive_no_gain >= 2:
            return True
        return False
    
    def has_won(self):
        """检查玩家是否获胜"""
        return len(self.evolution_cards) >= 20
    
    def __str__(self):
        return f"玩家{self.player_id}: {self.name} (位置: {self.position}, 进化卡: {len(self.evolution_cards)}, 进化点数: {self.evolution_points})"

# 牌库类
class Deck:
    def __init__(self, card_type: CardType):
        self.card_type = card_type
        self.cards = []
        self.discard_pile = []
    
    def add_card(self, card: Card):
        """添加卡牌到牌库"""
        self.cards.append(card)
    
    def shuffle(self):
        """洗牌"""
        random.shuffle(self.cards)
    
    def draw(self, count=1):
        """从牌库抽牌"""
        drawn_cards = []
        for _ in range(count):
            if not self.cards:
                # 如果牌库空了，重新洗入弃牌堆
                if self.discard_pile:
                    self.cards = self.discard_pile.copy()
                    self.discard_pile = []
                    self.shuffle()
                else:
                    break  # 牌库和弃牌堆都空了
            
            if self.cards:
                drawn_cards.append(self.cards.pop())
        
        return drawn_cards
    
    def discard(self, card: Card):
        """弃置一张卡牌"""
        self.discard_pile.append(card)
    
    def size(self):
        """返回牌库剩余卡牌数量"""
        return len(self.cards)

# 游戏类
class EvolutionGame:
    def __init__(self, player_names: List[str], log_folder: str = "game_logs"):
        self.players = [Player(name, i+1) for i, name in enumerate(player_names)]
        self.current_player_index = 0
        self.round_count = 0
        self.game_over = False
        self.winner = None
        
        # 创建日志文件夹
        self.log_folder = log_folder
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)
        
        # 生成日志文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(log_folder, f"evolution_game_{timestamp}.txt")
        
        # 初始化牌库
        self.cooperation_deck = Deck(CardType.COOPERATION)
        self.deception_deck = Deck(CardType.DECEPTION)
        self.evolution_deck = Deck(CardType.EVOLUTION)
        self.event_deck = Deck(CardType.EVENT)
        self.ability_deck = Deck(CardType.ABILITY)
        self.environment_change_deck = Deck(CardType.ENVIRONMENT_CHANGE)
        
        # 初始化地图
        self.tiles = self._create_board()
        
        # 初始化牌库
        self._initialize_decks()
        
        # 游戏开始日志
        self._log_game_start()
    
    def _create_board(self):
        """创建游戏地图"""
        # 简化版地图，实际游戏可以根据需要扩展
        tiles = []
        tile_types = [
            TileType.START,
            TileType.TRUST_EVOLUTION,
            TileType.RESOURCE_RICH,
            TileType.HAWK_DOVE,
            TileType.NATURAL_DISASTER,
            TileType.COOPERATION_SANCTUARY,
            TileType.DECEPTION_SWAMP,
            TileType.MUTATION_EVENT,
            TileType.EVOLUTION_LAB,
            TileType.END
        ]
        
        for i, tile_type in enumerate(tile_types):
            tiles.append(Tile(tile_type, i))
        
        return tiles
    
    def _initialize_decks(self):
        """初始化各个牌库"""
        # 合作卡 (25张)
        for i in range(25):
            self.cooperation_deck.add_card(Card(CardType.COOPERATION, f"合作卡{i+1}"))
        
        # 欺骗卡 (25张)
        for i in range(25):
            self.deception_deck.add_card(Card(CardType.DECEPTION, f"欺骗卡{i+1}"))
        
        # 进化卡 (125张)
        for i in range(125):
            self.evolution_deck.add_card(Card(CardType.EVOLUTION, f"进化卡{i+1}"))
        
        # 事件卡 (30张) - 简化版，只实现部分事件
        event_descriptions = {
            "基因突变": "抽取3张进化卡，但你的下个回合无法移动",
            "群体迁徙": "所有玩家移动到下一个与当前所在格类型相同的格子",
            "互利共生": "选择一名玩家，双方各抽取2张进化卡",
            "加速进化": "你抽取2张进化卡，并可以立即额外移动2步",
            "自然选择": "当前进化卡数量最少的玩家必须弃置2张进化卡",
        }
        
        for name, desc in event_descriptions.items():
            self.event_deck.add_card(EventCard(name, desc))
        
        # 能力卡 (20张) - 简化版，只实现部分能力
        ability_descriptions = {
            AbilityType.ALTRUISTIC_GENE: "当你打出合作卡时，可以指定一名其他玩家抽取1张进化卡",
            AbilityType.SCHEME_MASTER: "当你打出欺骗卡时，可以查看任意一名玩家的手牌",
            AbilityType.ENVIRONMENT_ADAPTATION: "你免疫自然灾害格的弃卡效果",
            AbilityType.EFFICIENT_METABOLISM: "在资源丰富格出欺骗卡时，额外多抽取1张进化卡",
            AbilityType.TENACIOUS_VITALITY: "手牌上限增加3张，弃置进化卡时可以少弃1张",
        }
        
        for ability_type, desc in ability_descriptions.items():
            self.ability_deck.add_card(AbilityCard(ability_type, desc))
        
        # 环境变化卡 (10张) - 简化版
        environment_descriptions = {
            "干旱降临": "将最近的一个资源丰富格变为自然灾害格",
            "绿洲形成": "将最近的一个自然灾害格变为资源丰富格",
            "地震破坏": "将当前玩家所在格左右两侧的格子都变为自然灾害格",
        }
        
        for name, desc in environment_descriptions.items():
            self.environment_change_deck.add_card(EnvironmentChangeCard(name, desc))
        
        # 洗牌
        self.cooperation_deck.shuffle()
        self.deception_deck.shuffle()
        self.evolution_deck.shuffle()
        self.event_deck.shuffle()
        self.ability_deck.shuffle()
        self.environment_change_deck.shuffle()
        
        # 分发起始手牌
        for player in self.players:
            # 起始策略卡 = 玩家人数-1
            strategy_cards_count = len(self.players) - 1
            for _ in range(strategy_cards_count):
                if random.random() < 0.5:
                    card = self.cooperation_deck.draw()[0]
                    player.add_card(card)
                else:
                    card = self.deception_deck.draw()[0]
                    player.add_card(card)
            
            # 起始进化卡 (5张)
            evolution_cards = self.evolution_deck.draw(5)
            for card in evolution_cards:
                player.add_card(card)
    
    def _log_game_start(self):
        """记录游戏开始信息"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write("Evolution Game - 游戏开始\n")
            f.write("=" * 50 + "\n")
            f.write(f"游戏时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"玩家数量: {len(self.players)}\n")
            f.write("玩家列表:\n")
            for player in self.players:
                f.write(f"  {player}\n")
            f.write("\n")
            f.write("地图布局:\n")
            for tile in self.tiles:
                f.write(f"  {tile}\n")
            f.write("\n")
    
    def _log_turn_start(self, player: Player):
        """记录回合开始信息"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n回合 {self.round_count} - {player.name} 的回合\n")
            f.write("-" * 30 + "\n")
    
    def _log_event(self, event: str):
        """记录游戏事件"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"{event}\n")
    
    def _log_game_state(self):
        """记录当前游戏状态"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write("\n当前游戏状态:\n")
            for player in self.players:
                status = "活跃" if player.is_active else "淘汰"
                f.write(f"  {player.name}: 位置{player.position}, 进化卡{len(player.evolution_cards)}, 进化点数{player.evolution_points} ({status})\n")
    
    def get_current_player(self) -> Player:
        """获取当前玩家"""
        return self.players[self.current_player_index]
    
    def get_next_player(self) -> Player:
        """获取下一个活跃玩家"""
        next_index = (self.current_player_index + 1) % len(self.players)
        while not self.players[next_index].is_active:
            next_index = (next_index + 1) % len(self.players)
        return self.players[next_index]
    
    def move_to_next_player(self):
        """移动到下一个玩家"""
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        # 如果下一个玩家被淘汰，继续找下一个
        if not self.players[self.current_player_index].is_active:
            self.move_to_next_player()
    
    def display_board(self):
        """显示当前地图状态"""
        print("\n当前地图状态:")
        for tile in self.tiles:
            players_on_tile = [p for p in self.players if p.position == tile.position and p.is_active]
            player_names = ", ".join([p.name for p in players_on_tile])
            if players_on_tile:
                print(f"  {tile} - 玩家: {player_names}")
            else:
                print(f"  {tile}")
    
    def roll_dice(self) -> int:
        """掷骰子"""
        return random.randint(1, 6)
    
    def resolve_trust_evolution(self, player: Player, choices: Dict[Player, CardType]):
        """处理信任进化格子事件"""
        self._log_event(f"{player.name} 触发了信任进化事件")
        
        results = {}
        for p1, card_type1 in choices.items():
            for p2, card_type2 in choices.items():
                if p1 != p2 and choices.get(p1) == card_type1 and choices.get(p2) == card_type2:
                    # 双方互相选择
                    if card_type1 == CardType.COOPERATION and card_type2 == CardType.COOPERATION:
                        p1.evolution_points += 2
                        p2.evolution_points += 2
                        results[(p1, p2)] = "合作 vs 合作: 双方各获得2点进化点数"
                    elif card_type1 == CardType.COOPERATION and card_type2 == CardType.DECEPTION:
                        p1.evolution_points += 1
                        evolution_cards = self.evolution_deck.draw(3)
                        for card in evolution_cards:
                            p2.add_card(card)
                        results[(p1, p2)] = "合作 vs 欺骗: 合作方获得1点进化点数，欺骗方抽取3张进化卡"
                    elif card_type1 == CardType.DECEPTION and card_type2 == CardType.DECEPTION:
                        if p1.evolution_cards:
                            p1.evolution_cards.pop()
                        if p2.evolution_cards:
                            p2.evolution_cards.pop()
                        results[(p1, p2)] = "欺骗 vs 欺骗: 双方各弃置1张进化卡"
        
        # 所有玩家可以补充一张合作或欺骗卡
        for p in self.players:
            if p.is_active:
                if random.random() < 0.5:
                    card = self.cooperation_deck.draw()[0]
                    p.add_card(card)
                    self._log_event(f"{p.name} 补充了一张合作卡")
                else:
                    card = self.deception_deck.draw()[0]
                    p.add_card(card)
                    self._log_event(f"{p.name} 补充了一张欺骗卡")
        
        # 记录结果
        for pair, result in results.items():
            self._log_event(f"  {pair[0].name} 和 {pair[1].name}: {result}")
    
    def resolve_hawk_dove(self, player1: Player, player2: Player, choice1: CardType, choice2: CardType):
        """处理鹰鸽博弈事件"""
        self._log_event(f"{player1.name} 和 {player2.name} 进行鹰鸽博弈")
        
        # 修复：处理所有四种情况
        if choice1 == CardType.COOPERATION and choice2 == CardType.COOPERATION:
            player1.evolution_points += 2
            player2.evolution_points += 2
            result = "鸽 vs 鸽: 双方各获得2点进化点数"
        elif choice1 == CardType.COOPERATION and choice2 == CardType.DECEPTION:
            player1.evolution_points += 1
            evolution_cards = self.evolution_deck.draw(3)
            for card in evolution_cards:
                player2.add_card(card)
            result = "鸽 vs 鹰: 鸽方获得1点进化点数，鹰方抽取3张进化卡"
        elif choice1 == CardType.DECEPTION and choice2 == CardType.COOPERATION:
            evolution_cards = self.evolution_deck.draw(3)
            for card in evolution_cards:
                player1.add_card(card)
            player2.evolution_points += 1
            result = "鹰 vs 鸽: 鹰方抽取3张进化卡，鸽方获得1点进化点数"
        else:  # 欺骗 vs 欺骗
            # 双方各弃置2张进化卡
            for _ in range(2):
                if player1.evolution_cards:
                    player1.evolution_cards.pop()
            for _ in range(2):
                if player2.evolution_cards:
                    player2.evolution_cards.pop()
            result = "鹰 vs 鹰: 双方各弃置2张进化卡"
        
        self._log_event(f"  结果: {result}")
        
        # 参与玩家可以补充一张所出牌型的卡
        if choice1 == CardType.COOPERATION:
            card = self.cooperation_deck.draw()[0]
            player1.add_card(card)
        else:
            card = self.deception_deck.draw()[0]
            player1.add_card(card)
        
        if choice2 == CardType.COOPERATION:
            card = self.cooperation_deck.draw()[0]
            player2.add_card(card)
        else:
            card = self.deception_deck.draw()[0]
            player2.add_card(card)
    
    def resolve_resource_rich(self, player: Player, choice: CardType):
        """处理资源丰富格子事件"""
        self._log_event(f"{player.name} 在资源丰富格出了{choice.value}")
        
        if choice == CardType.COOPERATION:
            evolution_cards = self.evolution_deck.draw(2)
            for card in evolution_cards:
                player.add_card(card)
            self._log_event(f"  {player.name} 抽取了2张进化卡")
        else:  # 欺骗卡
            dice_roll = self.roll_dice()
            self._log_event(f"  {player.name} 掷出了{dice_roll}")
            if dice_roll >= 5:  # 5-6
                evolution_cards = self.evolution_deck.draw(4)
                for card in evolution_cards:
                    player.add_card(card)
                self._log_event(f"  {player.name} 抽取了4张进化卡")
            else:
                self._log_event(f"  {player.name} 一无所获")
    
    def resolve_natural_disaster(self, player: Player, choice: CardType, target: Player = None):
        """处理自然灾害格子事件"""
        self._log_event(f"{player.name} 在自然灾害格出了{choice.value}")
        
        if choice == CardType.COOPERATION:
            self._log_event(f"  {player.name} 免疫了本次灾害")
        else:  # 欺骗卡
            if player.evolution_cards:
                player.evolution_cards.pop()
                self._log_event(f"  {player.name} 弃置了1张进化卡")
            
            if target and target.is_active and target != player:
                if target.evolution_cards:
                    target.evolution_cards.pop()
                    self._log_event(f"  {player.name} 使 {target.name} 弃置了1张进化卡")
    
    def resolve_tile_event(self, player: Player, tile: Tile):
        """处理格子事件"""
        if tile.tile_type == TileType.START:
            self._log_event(f"{player.name} 停留在起点，无效果")
        
        elif tile.tile_type == TileType.TRUST_EVOLUTION:
            # 简化版：每个玩家随机选择目标和卡牌类型
            choices = {}
            for p in self.players:
                if p.is_active and p != player:
                    target = random.choice([p for p in self.players if p.is_active and p != player])
                    card_type = random.choice([CardType.COOPERATION, CardType.DECEPTION])
                    choices[p] = (target, card_type)
            
            # 转换为目标-卡牌类型的映射
            target_choices = {}
            for p, (target, card_type) in choices.items():
                target_choices[p] = card_type
            
            self.resolve_trust_evolution(player, target_choices)
        
        elif tile.tile_type == TileType.HAWK_DOVE:
            # 当前玩家随机选择一名对手进行博弈
            opponents = [p for p in self.players if p.is_active and p != player]
            if opponents:
                opponent = random.choice(opponents)
                choice1 = random.choice([CardType.COOPERATION, CardType.DECEPTION])
                choice2 = random.choice([CardType.COOPERATION, CardType.DECEPTION])
                self.resolve_hawk_dove(player, opponent, choice1, choice2)
        
        elif tile.tile_type == TileType.RESOURCE_RICH:
            choice = random.choice([CardType.COOPERATION, CardType.DECEPTION])
            self.resolve_resource_rich(player, choice)
        
        elif tile.tile_type == TileType.NATURAL_DISASTER:
            choice = random.choice([CardType.COOPERATION, CardType.DECEPTION])
            opponents = [p for p in self.players if p.is_active and p != player]
            target = random.choice(opponents) if opponents and choice == CardType.DECEPTION else None
            self.resolve_natural_disaster(player, choice, target)
        
        elif tile.tile_type == TileType.MUTATION_EVENT:
            event_card = self.event_deck.draw()[0]
            player.add_card(event_card)
            self._log_event(f"{player.name} 获得事件卡: {event_card.name}")
        
        elif tile.tile_type == TileType.EVOLUTION_LAB:
            if len(player.evolution_cards) >= 2:
                # 支付2张进化卡
                player.evolution_cards = player.evolution_cards[:-2]
                ability_card = self.ability_deck.draw()[0]
                player.add_card(ability_card)
                self._log_event(f"{player.name} 获得了能力卡: {ability_card.name}")
            else:
                self._log_event(f"{player.name} 没有足够的进化卡使用进化实验室")
        
        elif tile.tile_type == TileType.END:
            if not player.has_visited_end:  # 首次抵达
                evolution_cards = self.evolution_deck.draw(3)
                for card in evolution_cards:
                    player.add_card(card)
                player.evolution_points += 2
                player.has_visited_end = True
                self._log_event(f"{player.name} 首次抵达终点，获得3张进化卡和2点进化点数")
            else:
                self._log_event(f"{player.name} 再次抵达终点，无效果")
        
        # 检查手牌上限
        player.check_hand_size()
    
    def play_turn(self):
        """执行一个回合"""
        player = self.get_current_player()
        
        if not player.is_active:
            self.move_to_next_player()
            return
        
        self._log_turn_start(player)
        self.display_board()
        
        # 阶段一：掷骰与移动
        dice_roll = self.roll_dice()
        self._log_event(f"{player.name} 掷出了{dice_roll}")
        
        player.position = (player.position + dice_roll) % len(self.tiles)
        current_tile = self.tiles[player.position]
        self._log_event(f"{player.name} 移动到了位置 {player.position}: {current_tile.tile_type.value}")
        
        # 阶段二：触发并结算格子事件
        self.resolve_tile_event(player, current_tile)
        
        # 阶段三：可选行动 (简化版)
        if random.random() < 0.3:  # 30%概率执行可选行动
            action = random.choice(["兑换进化点数", "使用事件卡", "发动能力"])
            self._log_event(f"{player.name} 执行了可选行动: {action}")
            
            if action == "兑换进化点数" and player.evolution_points > 0:
                points_to_use = random.randint(1, player.evolution_points)
                evolution_cards = self.evolution_deck.draw(points_to_use)
                for card in evolution_cards:
                    player.add_card(card)
                player.evolution_points -= points_to_use
                self._log_event(f"{player.name} 兑换了{points_to_use}点进化点数，获得了{len(evolution_cards)}张进化卡")
        
        # 阶段四：环境变化 (简化版)
        if random.random() < 0.2:  # 20%概率执行环境变化
            if self.environment_change_deck.size() > 0:
                env_card = self.environment_change_deck.draw()[0]
                self._log_event(f"{player.name} 触发了环境变化: {env_card.name}")
        
        # 检查玩家状态
        if player.is_eliminated():
            player.is_active = False
            self._log_event(f"{player.name} 被淘汰了!")
        
        if player.has_won():
            self.game_over = True
            self.winner = player
            self._log_event(f"{player.name} 获得了胜利!")
        
        # 记录游戏状态
        self._log_game_state()
        
        # 移动到下一个玩家
        if not self.game_over:
            self.move_to_next_player()
            self.round_count += 1
    
    def play_game(self, max_rounds=100):
        """执行完整游戏"""
        self._log_event("游戏开始!")
        
        while not self.game_over and self.round_count < max_rounds:
            self.play_turn()
            
            # 检查是否只剩一个玩家
            active_players = [p for p in self.players if p.is_active]
            if len(active_players) == 1:
                self.game_over = True
                self.winner = active_players[0]
                self._log_event(f"{self.winner.name} 是最后的幸存者，获得了胜利!")
                break
        
        if self.round_count >= max_rounds and not self.game_over:
            self._log_event("游戏达到最大回合数，平局!")
        
        # 记录游戏结果
        self._log_game_result()
        
        return self.winner
    
    def _log_game_result(self):
        """记录游戏结果"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write("\n" + "=" * 50 + "\n")
            f.write("游戏结束!\n")
            if self.winner:
                f.write(f"获胜者: {self.winner.name}\n")
            else:
                f.write("游戏平局!\n")
            
            f.write("\n最终排名:\n")
            ranked_players = sorted(self.players, key=lambda p: len(p.evolution_cards), reverse=True)
            for i, player in enumerate(ranked_players):
                status = "获胜" if player == self.winner else "淘汰" if not player.is_active else "活跃"
                f.write(f"{i+1}. {player.name}: {len(player.evolution_cards)}张进化卡 ({status})\n")

# 主函数
def main():
    print("Evolution Game - 进化游戏")
    print("=" * 30)
    
    # 获取玩家数量
    while True:
        try:
            num_players = int(input("请输入玩家数量 (2-7): "))
            if 2 <= num_players <= 7:
                break
            else:
                print("玩家数量必须在2-7之间")
        except ValueError:
            print("请输入有效的数字")
    
    # 获取玩家名称
    player_names = []
    for i in range(num_players):
        name = input(f"请输入玩家{i+1}的名称: ")
        player_names.append(name)
    
    # 创建游戏
    game = EvolutionGame(player_names)
    
    # 开始游戏
    print("\n游戏开始!")
    winner = game.play_game()
    
    if winner:
        print(f"\n游戏结束! 获胜者是: {winner.name}")
    else:
        print("\n游戏结束! 平局!")
    
    print(f"\n游戏记录已保存到: {game.log_file}")

if __name__ == "__main__":
    main()