import random
from enum import Enum
from typing import List, Dict, Optional, Tuple, Any, Callable
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
    def __init__(self, card_type: CardType, name: str = "", effect: str = ""):
        self.card_type = card_type
        self.name = name
        self.effect = effect
    
    def __str__(self):
        return f"{self.card_type.value}: {self.name}"
    
    def get_full_description(self):
        return f"{self.name} - {self.effect}"

# 策略卡（合作/欺骗）
class StrategyCard(Card):
    def __init__(self, action_type: ActionType):
        card_type = CardType.COOPERATION if action_type == ActionType.COOPERATE else CardType.DECEPTION
        name = action_type.value
        effect = "用于在各种事件中做出策略选择"
        super().__init__(card_type, name, effect)
        self.action_type = action_type

# 进化卡
class EvolutionCard(Card):
    def __init__(self):
        super().__init__(CardType.EVOLUTION, "进化卡", "代表物种的进化程度与生存资源")

# 事件卡
class EventCard(Card):
    def __init__(self, name: str, effect: str):
        super().__init__(CardType.EVENT, name, effect)

# 环境变化卡
class EnvironmentChangeCard(Card):
    def __init__(self, name: str, effect: str):
        super().__init__(CardType.ENVIRONMENT_CHANGE, name, effect)

# 能力卡
class AbilityCard(Card):
    def __init__(self, name: str, effect: str):
        super().__init__(CardType.ABILITY, name, effect)
        self.used = False  # 标记是否已使用（针对一次性能力）

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
        self.symbiosis_target = None  # 共生纽带目标
        self.prey_target = None  # 捕食本能目标
        self.immune_to_disaster = False  # 环境耐受效果
        self.cannot_move_next_turn = False  # 基因突变效果
        self.hand_limit_bonus = 0  # 手牌上限加成
        self.evolution_requirement_reduction = 0  # 进化胜利要求降低
    
    def get_hand_limit(self) -> int:
        """计算手牌上限（仅针对合作卡和欺骗卡）"""
        evolution_cards_count = len(self.hand[CardType.EVOLUTION])
        base_limit = evolution_cards_count // 2  # 向下取整
        return base_limit + self.hand_limit_bonus
    
    def check_hand_limit(self, log_func: Callable = print):
        """检查并调整手牌数量，确保不超过上限"""
        hand_limit = self.get_hand_limit()
        total_strategy_cards = len(self.hand[CardType.COOPERATION]) + len(self.hand[CardType.DECEPTION])
        
        if total_strategy_cards > hand_limit:
            # 需要弃置多余的牌
            excess = total_strategy_cards - hand_limit
            log_func(f"{self.name} 手牌超过上限，需要弃置 {excess} 张策略卡")
            # 随机弃置
            for _ in range(excess):
                if self.hand[CardType.COOPERATION] and self.hand[CardType.DECEPTION]:
                    # 随机选择弃置合作卡或欺骗卡
                    if random.random() < 0.5:
                        card = self.hand[CardType.COOPERATION].pop()
                        log_func(f"{self.name} 弃置了 {card.name}")
                    else:
                        card = self.hand[CardType.DECEPTION].pop()
                        log_func(f"{self.name} 弃置了 {card.name}")
                elif self.hand[CardType.COOPERATION]:
                    card = self.hand[CardType.COOPERATION].pop()
                    log_func(f"{self.name} 弃置了 {card.name}")
                elif self.hand[CardType.DECEPTION]:
                    card = self.hand[CardType.DECEPTION].pop()
                    log_func(f"{self.name} 弃置了 {card.name}")
    
    def add_card(self, card: Card, log_func: Callable = print):
        """添加卡牌到手牌"""
        if card.card_type in [CardType.COOPERATION, CardType.DECEPTION, CardType.EVOLUTION]:
            self.hand[card.card_type].append(card)
            log_func(f"{self.name} 获得了 {card.name}")
            # 如果是策略卡，需要检查手牌上限
            if card.card_type in [CardType.COOPERATION, CardType.DECEPTION]:
                self.check_hand_limit(log_func)
        elif card.card_type == CardType.ABILITY:
            self.abilities.append(card)
            log_func(f"{self.name} 获得了能力卡: {card.get_full_description()}")
            # 检查是否有立即生效的能力
            self.check_immediate_ability_effect(card, log_func)
        elif card.card_type == CardType.EVENT:
            self.hand[CardType.EVENT].append(card)
            log_func(f"{self.name} 获得了事件卡: {card.name}")
    
    def check_immediate_ability_effect(self, ability_card: AbilityCard, log_func: Callable):
        """检查能力卡是否有立即生效的效果"""
        if ability_card.name == "进化爆发":
            # 立即抽取3张进化卡
            log_func(f"{ability_card.name} 效果触发!")
            # 注意：这里需要在游戏上下文中抽取卡牌，所以这个效果会在获得卡牌时由游戏类处理
    
    def remove_card(self, card_type: CardType, count: int = 1, log_func: Callable = print) -> bool:
        """从手牌中移除指定类型的卡牌"""
        if card_type in self.hand and len(self.hand[card_type]) >= count:
            for _ in range(count):
                card = self.hand[card_type].pop()
                log_func(f"{self.name} 失去了 {card.name}")
            return True
        log_func(f"{self.name} 没有足够的 {card_type.value} 可以移除")
        return False
    
    def has_evolution_cards(self, count: int) -> bool:
        """检查是否有足够数量的进化卡"""
        return len(self.hand[CardType.EVOLUTION]) >= count
    
    def get_evolution_card_count(self) -> int:
        """获取进化卡数量"""
        return len(self.hand[CardType.EVOLUTION])
    
    def is_victorious(self) -> bool:
        """检查是否获胜（拥有20张或更多进化卡，考虑能力卡效果）"""
        required = 20 - self.evolution_requirement_reduction
        return self.get_evolution_card_count() >= required
    
    def is_eliminated_check(self, log_func: Callable = print) -> bool:
        """检查是否被淘汰（进化卡数量为0）"""
        if self.get_evolution_card_count() == 0:
            # 检查是否有绝境求生能力
            for ability in self.abilities:
                if ability.name == "绝境求生" and not ability.used:
                    ability.used = True
                    self.hand[CardType.EVOLUTION] = [EvolutionCard() for _ in range(3)]
                    log_func(f"{self.name} 发动绝境求生，进化卡数量重置为3张！")
                    return False
            self.is_eliminated = True
        return self.is_eliminated
    
    def has_ability(self, ability_name: str) -> bool:
        """检查是否拥有指定能力"""
        return any(ability.name == ability_name for ability in self.abilities)
    
    def get_ability(self, ability_name: str) -> Optional[AbilityCard]:
        """获取指定能力卡"""
        for ability in self.abilities:
            if ability.name == ability_name:
                return ability
        return None

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
            old_type = self.grids[position].grid_type
            self.grids[position].grid_type = new_type
            return f"位置 {position} 的格子从 {old_type.value} 变为 {new_type.value}"
        return "无效的位置"
    
    def find_grid_by_type(self, grid_type: GridType, start_from: int = 0) -> Optional[int]:
        """从指定位置开始查找指定类型的格子"""
        for i in range(start_from, start_from + self.grid_count):
            pos = i % self.grid_count
            if self.grids[pos].grid_type == grid_type:
                return pos
        return None
    
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
    
    def initialize_with_cards(self, cards: List[Card]):
        """使用指定的卡牌列表初始化牌库"""
        self.cards = cards
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
    
    def peek_top(self, count: int = 1) -> List[Card]:
        """查看牌库顶的牌但不抽取"""
        return self.cards[-count:] if len(self.cards) >= count else self.cards.copy()
    
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
        self.round_count = 0
        self.last_event_card = None  # 记录上一张触发的事件卡
        
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
        cooperation_cards = [StrategyCard(ActionType.COOPERATE) for _ in range(25)]
        deception_cards = [StrategyCard(ActionType.DECEIVE) for _ in range(25)]
        self.cooperation_deck.initialize_with_cards(cooperation_cards)
        self.deception_deck.initialize_with_cards(deception_cards)
        
        # 进化卡
        evolution_cards = [EvolutionCard() for _ in range(125)]
        self.evolution_deck.initialize_with_cards(evolution_cards)
        
        # 事件卡 - 创建具体的事件卡
        event_cards = [
            EventCard("基因突变", "抽取3张进化卡，但你的下个回合无法移动"),
            EventCard("群体迁徙", "所有玩家移动到下一个与当前所在格类型相同的格子，按顺时针顺序结算效果"),
            EventCard("天敌出现", "指定一名玩家，其下回合必须与你进行鹰鸽博弈且必须出欺骗卡"),
            EventCard("互利共生", "选择一名玩家，双方各抽取2张进化卡"),
            EventCard("自然选择", "当前进化卡数量最少的玩家必须弃置2张进化卡。如有多人并列，各弃1张"),
            EventCard("生态崩溃", "所有玩家必须弃置1张合作卡和1张欺骗卡（如没有则弃置2张其他手牌）"),
            EventCard("加速进化", "你抽取2张进化卡，并可以立即额外移动2步（触发新格子效果）"),
            EventCard("掠食行为", "你抽取1张进化卡，并指定一名玩家弃置1张进化卡"),
            EventCard("环境耐受", "直到你的下个回合开始，你免疫所有自然灾害格的效果"),
            EventCard("种群繁荣", "如果你在本回合触发事件时出的是合作卡，获得3张进化卡"),
            EventCard("疾病传播", "所有玩家向前移动4格，途中触发每个自然灾害格的效果"),
            EventCard("富饶之地", "当前回合玩家可以额外触发一次当前所在格的效果（需再次出牌）"),
            EventCard("秩序逆转", "游戏回合顺序改为逆时针进行，直到有玩家再次抽到本事件卡"),
            EventCard("效果复制", "复制上一张被触发的事件卡效果并立即执行"),
            EventCard("能量吸收", "在接下来的三轮回合中，每当有玩家在资源丰富格出合作卡，你也抽取1张进化卡"),
            EventCard("领地争夺", "与你停留在同一格的其他玩家必须立即弃置1张进化卡"),
            EventCard("气候剧变", "直到你的下个回合开始，所有资源丰富格被视为自然灾害格，反之亦然"),
            EventCard("行动抑制", "除你之外，所有玩家下回合不能移动（掷骰结果视为0）"),
            EventCard("资源稀缺", "所有玩家将手牌中的进化卡数量减半（向下取整）"),
            EventCard("三方博弈", "指定两名玩家，立即进行一场三方鹰鸽博弈（两两之间均结算）"),
            EventCard("停战协议", "直到你的下个回合开始，所有鹰鸽博弈的结果视为鸽vs鸽"),
            EventCard("欺诈狂欢", "本轮所有事件结算中，出欺骗卡的玩家额外获得2张进化卡"),
            EventCard("合作浪潮", "本轮所有事件结算中，出合作卡的玩家额外获得1张进化卡"),
            EventCard("位置混乱", "与你距离最近的两名玩家交换当前位置"),
            EventCard("未来预知", "查看牌库顶5张事件卡，以任意顺序放回，然后获得2张进化卡"),
            EventCard("空间跳跃", "将你的标记移动至任意一个起点或终点格，并触发效果"),
            EventCard("竞争激化", "所有玩家展示手牌中欺骗卡的数量。数量最多的玩家弃置所有欺骗卡，抽取等量进化卡"),
            EventCard("信任缺失", "所有玩家将手牌中所有合作卡暂时移出游戏，直到其下个回合开始"),
            EventCard("进化加速", "你永久增加3张手牌上限"),
            EventCard("奇迹发生", "你立即获得5张进化卡，且下回合移动步数加倍")
        ]
        self.event_deck.initialize_with_cards(event_cards)
        
        # 环境变化卡
        environment_cards = [
            EnvironmentChangeCard("干旱降临", "将地图上最近的一个资源丰富格永久变为自然灾害格"),
            EnvironmentChangeCard("绿洲形成", "将地图上最近的一个自然灾害格永久变为资源丰富格"),
            EnvironmentChangeCard("地震破坏", "将当前回合玩家所在格左右两侧的格子都变为自然灾害格"),
            EnvironmentChangeCard("生态恢复", "将地图上任意一个自然灾害格变为信任进化格"),
            EnvironmentChangeCard("路径改变", "将地图上最长连续的同类型格子段中的一格变为随机其他类型"),
            EnvironmentChangeCard("气候宜人", "本回合内，所有玩家在触发格子事件时，若出合作卡则额外获得1张进化卡"),
            EnvironmentChangeCard("环境恶化", "下两个回合中，所有玩家在触发格子事件时，若出欺骗卡必须额外弃置1张手牌"),
            EnvironmentChangeCard("地形隆起", "将终点格向前移动3格位置（按游戏行进方向）"),
            EnvironmentChangeCard("沼泽扩张", "将地图上任意两个不相邻的普通格子变为欺骗沼泽格"),
            EnvironmentChangeCard("圣地显现", "将地图上距离目前玩家最远的一个格子变为合作圣地格")
        ]
        self.environment_change_deck.initialize_with_cards(environment_cards)
        
        # 能力卡
        ability_cards = [
            AbilityCard("利他基因", "当你在任何需要出牌的事件中打出合作卡时，除了正常效果外，可以指定一名其他玩家抽取1张进化卡"),
            AbilityCard("阴谋大师", "当你在任何需要出牌的事件中打出欺骗卡时，可以查看任意一名玩家的手牌中合作卡与欺骗卡的具体数量"),
            AbilityCard("环境适应", "你免疫自然灾害格出欺骗卡时必须弃置1张进化卡的效果（转嫁效果仍然有效）"),
            AbilityCard("高效代谢", "在资源丰富格，若你出欺骗卡且骰子掷出5或6，额外多抽取1张进化卡（总共抽5张）"),
            AbilityCard("共生纽带", "宣布与一名玩家建立共生关系。当他在信任进化或合作圣地中因你出合作卡而收益时，你也额外抽取1张进化卡"),
            AbilityCard("防御机制", "当有其他玩家因欺骗沼泽或事件卡效果窥视牌库顶时，你可以阻止该效果，并改为你自己查看牌库顶2张牌"),
            AbilityCard("群体威慑", "在信任进化阶段，你指定目标后，可以命令所有进化卡数量少于你的玩家必须更改目标指向你"),
            AbilityCard("趁火打劫", "当有玩家在欺骗沼泽出欺骗卡时，你可以弃置1张手牌，执行一次窥视牌库顶3张拿1张的效果"),
            AbilityCard("顽强生命力", "你的手牌上限增加3张。当你因任何效果需要弃置进化卡时，可以少弃1张（最少为0）"),
            AbilityCard("策略变形", "每回合一次，在亮出合作/欺骗卡之前，你可以宣布改变所出的牌型（合作变欺骗或欺骗变合作）"),
            AbilityCard("进化爆发", "获得此卡时立即抽取3张进化卡，然后将此卡移出游戏"),
            AbilityCard("捕食本能", "指定一名玩家作为你的猎物。你对他发起或参与的所有鹰鸽博弈中，无论结果如何，你额外获得1张进化卡"),
            AbilityCard("资源控制", "在资源丰富格，若你出合作卡，你额外抽取1张进化卡，且所有出欺骗卡的玩家收益减半"),
            AbilityCard("灾难专家", "在自然灾害格，若你出欺骗卡，你可以额外指定一名玩家弃置1张进化卡"),
            AbilityCard("战术升级", "在你的回合开始阶段，你可以掷两次骰子并选择其一作为移动点数"),
            AbilityCard("绝境求生", "当你因手牌数为0即将被淘汰时，可以弃置此卡代替，并将进化卡数量重置为3张。此卡只能使用一次"),
            AbilityCard("生态改造", "当你抽取环境变化卡时，可以选择执行原效果，或直接将地图上任意一个普通格子更改为你指定的类型"),
            AbilityCard("进化优势", "你达成进化胜利所需的进化卡数量减少2张（只需18张即可获胜）"),
            AbilityCard("快速适应", "每次有玩家触发环境变化卡时，你可以立即抽取1张进化卡"),
            AbilityCard("种群韧性", "你免疫发展停滞淘汰条件（连续回合无收益），且每次在自然灾害格出合作卡时额外获得1张进化卡")
        ]
        self.ability_deck.initialize_with_cards(ability_cards)
    
    def initial_deal(self):
        """初始发牌"""
        player_count = len(self.players)
        
        for player in self.players:
            # 先发进化卡
            evolution_cards = self.evolution_deck.draw(5)
            for card in evolution_cards:
                player.add_card(card, self.log)
            
            # 再发策略卡
            strategy_card_count = player_count - 1
            cooperation_cards = self.cooperation_deck.draw(strategy_card_count // 2)
            deception_cards = self.deception_deck.draw(strategy_card_count - len(cooperation_cards))
            
            for card in cooperation_cards:
                player.add_card(card, self.log)
            for card in deception_cards:
                player.add_card(card, self.log)
            
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
        if player.cannot_move_next_turn:
            self.log(f"{player.name} 因基因突变效果无法移动")
            player.cannot_move_next_turn = False
            return 0
        
        player.position = (player.position + steps) % self.board.grid_count
        return steps
    
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
    
    def safe_draw_strategy_card(self, deck: Deck, player: Player, card_type: str) -> Optional[Card]:
        """安全地抽取策略卡，如果牌库为空则返回None"""
        if deck.is_empty():
            self.log(f"{card_type}牌库已空，无法抽牌")
            return None
        drawn_cards = deck.draw(1)
        if drawn_cards:
            card = drawn_cards[0]
            player.add_card(card, self.log)
            return card
        return None
    
    def apply_ability_effects(self, player: Player, action_type: ActionType, context: str, target_player: Player = None):
        """应用能力卡效果"""
        # 利他基因 - 打出合作卡时指定其他玩家抽卡
        if action_type == ActionType.COOPERATE and player.has_ability("利他基因"):
            if target_player is None:
                # 随机选择一名其他玩家
                available_players = [p for p in self.players if p != player and not p.is_eliminated]
                if available_players:
                    target_player = random.choice(available_players)
            
            if target_player:
                evolution_card = self.evolution_deck.draw(1)
                if evolution_card:
                    target_player.add_card(evolution_card[0], self.log)
                    self.log(f"{player.name} 的利他基因效果触发，{target_player.name} 获得1张进化卡")
        
        # 阴谋大师 - 打出欺骗卡时查看其他玩家手牌
        if action_type == ActionType.DECEIVE and player.has_ability("阴谋大师"):
            if target_player is None:
                available_players = [p for p in self.players if p != player and not p.is_eliminated]
                if available_players:
                    target_player = random.choice(available_players)
            
            if target_player:
                coop_count = len(target_player.hand[CardType.COOPERATION])
                dec_count = len(target_player.hand[CardType.DECEPTION])
                self.log(f"{player.name} 的阴谋大师效果触发，查看{target_player.name}的手牌: {coop_count}张合作卡, {dec_count}张欺骗卡")
        
        # 快速适应 - 环境变化时抽卡
        if context == "environment_change" and player.has_ability("快速适应"):
            evolution_card = self.evolution_deck.draw(1)
            if evolution_card:
                player.add_card(evolution_card[0], self.log)
                self.log(f"{player.name} 的快速适应效果触发，获得1张进化卡")
    
    def resolve_trust_evolution(self, current_player: Player):
        """解析信任进化格效果"""
        self.log(f"{current_player.name} 触发了信任进化格")
        self.log("效果: 所有玩家同时指定一名其他玩家作为目标，并根据出牌结算效果")
        
        # 所有玩家秘密指定一名其他玩家作为目标
        targets = {}
        for player in self.players:
            if player.is_eliminated:
                continue
            
            # 群体威慑能力效果
            if current_player.has_ability("群体威慑"):
                # 命令所有进化卡数量少于当前玩家的玩家必须更改目标指向当前玩家
                for p in self.players:
                    if p != player and not p.is_eliminated and p.get_evolution_card_count() < current_player.get_evolution_card_count():
                        self.log(f"{current_player.name} 的群体威慑效果触发，{p.name} 必须指向 {current_player.name}")
                        targets[p] = current_player
                        break
                else:
                    # 如果没有受影响玩家，正常选择目标
                    available_targets = [p for p in self.players if p != player and not p.is_eliminated]
                    if available_targets:
                        targets[player] = random.choice(available_targets)
            else:
                # 正常选择目标
                available_targets = [p for p in self.players if p != player and not p.is_eliminated]
                if available_targets:
                    targets[player] = random.choice(available_targets)
        
        # 所有玩家同时出牌
        actions = {}
        for player in self.players:
            if player.is_eliminated or player not in targets:
                continue
            
            # 策略变形能力
            if player.has_ability("策略变形"):
                # 每回合一次可以改变牌型
                if random.random() < 0.3:  # 30%概率使用
                    original_choice = random.choice([ActionType.COOPERATE, ActionType.DECEIVE])
                    new_choice = ActionType.DECEIVE if original_choice == ActionType.COOPERATE else ActionType.COOPERATE
                    actions[player] = new_choice
                    self.log(f"{player.name} 使用策略变形，将出牌改为 {new_choice.value}")
                else:
                    # 正常出牌
                    if player.hand[CardType.COOPERATION] and player.hand[CardType.DECEPTION]:
                        actions[player] = random.choice([ActionType.COOPERATE, ActionType.DECEIVE])
                    elif player.hand[CardType.COOPERATION]:
                        actions[player] = ActionType.COOPERATE
                    elif player.hand[CardType.DECEPTION]:
                        actions[player] = ActionType.DECEIVE
                    else:
                        continue
            else:
                # 正常出牌
                if player.hand[CardType.COOPERATION] and player.hand[CardType.DECEPTION]:
                    actions[player] = random.choice([ActionType.COOPERATE, ActionType.DECEIVE])
                elif player.hand[CardType.COOPERATION]:
                    actions[player] = ActionType.COOPERATE
                elif player.hand[CardType.DECEPTION]:
                    actions[player] = ActionType.DECEIVE
                else:
                    continue
            
            # 使用一张牌
            if actions[player] == ActionType.COOPERATE:
                player.remove_card(CardType.COOPERATION, 1, self.log)
            else:
                player.remove_card(CardType.DECEPTION, 1, self.log)
        
        # 结算效果
        processed_pairs = set()
        for player, target in targets.items():
            if player not in actions or target not in actions:
                continue
            
            # 避免重复处理
            pair = tuple(sorted([player.name, target.name]))
            if pair in processed_pairs:
                continue
            processed_pairs.add(pair)
            
            player_action = actions[player]
            target_action = actions[target]
            
            # 共生纽带效果检查
            if (player_action == ActionType.COOPERATE and player.symbiosis_target == target) or \
               (target_action == ActionType.COOPERATE and target.symbiosis_target == player):
                symbiosis_bonus = True
            else:
                symbiosis_bonus = False
            
            if player_action == ActionType.COOPERATE and target_action == ActionType.COOPERATE:
                # 合作 vs 合作：双方各获得2点进化点数
                player.evolution_points += 2
                target.evolution_points += 2
                self.log(f"{player.name} 和 {target.name} 合作，各获得2点进化点数")
                
                # 共生纽带效果
                if symbiosis_bonus:
                    evolution_card = self.evolution_deck.draw(1)
                    if evolution_card:
                        if player.symbiosis_target == target:
                            player.add_card(evolution_card[0], self.log)
                            self.log(f"{player.name} 的共生纽带效果触发，额外获得1张进化卡")
                        else:
                            target.add_card(evolution_card[0], self.log)
                            self.log(f"{target.name} 的共生纽带效果触发，额外获得1张进化卡")
                
                # 应用能力效果
                self.apply_ability_effects(player, player_action, "trust_evolution", target)
                self.apply_ability_effects(target, target_action, "trust_evolution", player)
                
            elif player_action == ActionType.COOPERATE and target_action == ActionType.DECEIVE:
                # 合作 vs 欺骗：出合作方获得1点进化点数，出欺骗方抽取3张进化卡
                player.evolution_points += 1
                evolution_cards = self.evolution_deck.draw(3)
                for card in evolution_cards:
                    target.add_card(card, self.log)
                self.log(f"{player.name} 被 {target.name} 欺骗，{player.name} 获得1点进化点数，{target.name} 抽取3张进化卡")
                
                # 应用能力效果
                self.apply_ability_effects(player, player_action, "trust_evolution", target)
                self.apply_ability_effects(target, target_action, "trust_evolution", player)
                
            elif player_action == ActionType.DECEIVE and target_action == ActionType.COOPERATE:
                # 欺骗 vs 合作：出欺骗方抽取3张进化卡，出合作方获得1点进化点数
                evolution_cards = self.evolution_deck.draw(3)
                for card in evolution_cards:
                    player.add_card(card, self.log)
                target.evolution_points += 1
                self.log(f"{player.name} 欺骗了 {target.name}，{player.name} 抽取3张进化卡，{target.name} 获得1点进化点数")
                
                # 应用能力效果
                self.apply_ability_effects(player, player_action, "trust_evolution", target)
                self.apply_ability_effects(target, target_action, "trust_evolution", player)
                
            else:  # 欺骗 vs 欺骗
                # 双方各弃置1张进化卡
                if player.has_evolution_cards(1):
                    # 顽强生命力效果
                    if player.has_ability("顽强生命力"):
                        self.log(f"{player.name} 的顽强生命力效果触发，无需弃置进化卡")
                    else:
                        player.remove_card(CardType.EVOLUTION, 1, self.log)
                
                if target.has_evolution_cards(1):
                    # 顽强生命力效果
                    if target.has_ability("顽强生命力"):
                        self.log(f"{target.name} 的顽强生命力效果触发，无需弃置进化卡")
                    else:
                        target.remove_card(CardType.EVOLUTION, 1, self.log)
                
                self.log(f"{player.name} 和 {target.name} 互相欺骗，各弃置1张进化卡")
        
        # 所有玩家可补充一张合作或欺骗卡
        for player in self.players:
            if player.is_eliminated:
                continue
            
            # 随机补充
            if random.random() < 0.5:
                card = self.safe_draw_strategy_card(self.cooperation_deck, player, "合作")
            else:
                card = self.safe_draw_strategy_card(self.deception_deck, player, "欺骗")
    
    def resolve_hawk_dove(self, current_player: Player):
        """解析鹰鸽博弈格效果"""
        self.log(f"{current_player.name} 触发了鹰鸽博弈格")
        self.log("效果: 当前回合玩家指定一名对手进行鹰鸽博弈，根据出牌结算效果")
        
        # 当前回合玩家指定一名对手
        available_opponents = [p for p in self.players if p != current_player and not p.is_eliminated]
        if not available_opponents:
            self.log("没有可选的对手")
            return
        
        opponent = random.choice(available_opponents)
        self.log(f"{current_player.name} 选择了与 {opponent.name} 进行鹰鸽博弈")
        
        # 检查是否有停战协议效果
        if any(p.has_ability("停战协议") for p in [current_player, opponent]):
            self.log("停战协议效果生效，本次博弈视为鸽vs鸽")
            current_player.evolution_points += 2
            opponent.evolution_points += 2
            self.log(f"{current_player.name} 和 {opponent.name} 各获得2点进化点数")
            return
        
        # 双方秘密出牌
        if current_player.hand[CardType.COOPERATION] and current_player.hand[CardType.DECEPTION]:
            current_action = random.choice([ActionType.COOPERATE, ActionType.DECEIVE])
        elif current_player.hand[CardType.COOPERATION]:
            current_action = ActionType.COOPERATE
        elif current_player.hand[CardType.DECEPTION]:
            current_action = ActionType.DECEIVE
        else:
            self.log(f"{current_player.name} 没有策略卡，无法参与博弈")
            return
        
        if opponent.hand[CardType.COOPERATION] and opponent.hand[CardType.DECEPTION]:
            opponent_action = random.choice([ActionType.COOPERATE, ActionType.DECEIVE])
        elif opponent.hand[CardType.COOPERATION]:
            opponent_action = ActionType.COOPERATE
        elif opponent.hand[CardType.DECEPTION]:
            opponent_action = ActionType.DECEIVE
        else:
            self.log(f"{opponent.name} 没有策略卡，无法参与博弈")
            return
        
        # 使用一张牌
        if current_action == ActionType.COOPERATE:
            current_player.remove_card(CardType.COOPERATION, 1, self.log)
        else:
            current_player.remove_card(CardType.DECEPTION, 1, self.log)
        
        if opponent_action == ActionType.COOPERATE:
            opponent.remove_card(CardType.COOPERATION, 1, self.log)
        else:
            opponent.remove_card(CardType.DECEPTION, 1, self.log)
        
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
                current_player.add_card(card, self.log)
            opponent.evolution_points += 1
            self.log(f"{current_player.name} 欺骗了 {opponent.name}，{current_player.name} 抽取3张进化卡，{opponent.name} 获得1点进化点数")
        elif current_action == ActionType.COOPERATE and opponent_action == ActionType.DECEIVE:
            # 鸽 vs 鹰：出鹰方抽取3张进化卡，出鸽方获得1点进化点数
            evolution_cards = self.evolution_deck.draw(3)
            for card in evolution_cards:
                opponent.add_card(card, self.log)
            current_player.evolution_points += 1
            self.log(f"{opponent.name} 欺骗了 {current_player.name}，{opponent.name} 抽取3张进化卡，{current_player.name} 获得1点进化点数")
        else:  # 鹰 vs 鹰
            # 双方各弃置2张进化卡
            if current_player.has_evolution_cards(2):
                # 顽强生命力效果
                if current_player.has_ability("顽强生命力"):
                    current_player.remove_card(CardType.EVOLUTION, 1, self.log)
                    self.log(f"{current_player.name} 的顽强生命力效果触发，少弃1张进化卡")
                else:
                    current_player.remove_card(CardType.EVOLUTION, 2, self.log)
            
            if opponent.has_evolution_cards(2):
                # 顽强生命力效果
                if opponent.has_ability("顽强生命力"):
                    opponent.remove_card(CardType.EVOLUTION, 1, self.log)
                    self.log(f"{opponent.name} 的顽强生命力效果触发，少弃1张进化卡")
                else:
                    opponent.remove_card(CardType.EVOLUTION, 2, self.log)
            
            self.log(f"{current_player.name} 和 {opponent.name} 都选择欺骗，各弃置2张进化卡")
        
        # 捕食本能效果
        if current_player.prey_target == opponent or opponent.prey_target == current_player:
            evolution_card = self.evolution_deck.draw(1)
            if evolution_card:
                if current_player.prey_target == opponent:
                    current_player.add_card(evolution_card[0], self.log)
                    self.log(f"{current_player.name} 的捕食本能效果触发，额外获得1张进化卡")
                else:
                    opponent.add_card(evolution_card[0], self.log)
                    self.log(f"{opponent.name} 的捕食本能效果触发，额外获得1张进化卡")
        
        # 参与玩家可补充一张所出牌型的卡
        if current_action == ActionType.COOPERATE:
            self.safe_draw_strategy_card(self.cooperation_deck, current_player, "合作")
        else:
            self.safe_draw_strategy_card(self.deception_deck, current_player, "欺骗")
        
        if opponent_action == ActionType.COOPERATE:
            self.safe_draw_strategy_card(self.cooperation_deck, opponent, "合作")
        else:
            self.safe_draw_strategy_card(self.deception_deck, opponent, "欺骗")
    
    def resolve_resource_rich(self, current_player: Player):
        """解析资源丰富格效果"""
        self.log(f"{current_player.name} 触发了资源丰富格")
        self.log("效果: 所有玩家出一张牌，合作卡抽2张进化卡，欺骗卡掷骰子决定收益")
        
        # 资源控制能力效果
        resource_control_player = None
        for player in self.players:
            if player.has_ability("资源控制"):
                resource_control_player = player
                break
        
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
                continue
            
            # 使用一张牌
            if action == ActionType.COOPERATE:
                player.remove_card(CardType.COOPERATION, 1, self.log)
                # 出合作卡：抽取2张进化卡
                evolution_cards = self.evolution_deck.draw(2)
                for card in evolution_cards:
                    player.add_card(card, self.log)
                
                # 资源控制效果
                if resource_control_player and resource_control_player == player:
                    extra_card = self.evolution_deck.draw(1)
                    if extra_card:
                        player.add_card(extra_card[0], self.log)
                        self.log(f"{player.name} 的资源控制效果触发，额外获得1张进化卡")
                
                self.log(f"{player.name} 选择合作，抽取2张进化卡")
            else:
                player.remove_card(CardType.DECEPTION, 1, self.log)
                # 出欺骗卡：掷骰子，1-4无所获，5-6抽取4张进化卡
                dice_roll = self.roll_dice()
                cards_to_draw = 4
                
                # 高效代谢效果
                if player.has_ability("高效代谢") and dice_roll >= 5:
                    cards_to_draw = 5
                    self.log(f"{player.name} 的高效代谢效果触发，额外多抽1张进化卡")
                
                # 资源控制效果（欺骗卡收益减半）
                if resource_control_player and resource_control_player != player:
                    cards_to_draw = cards_to_draw // 2
                    self.log(f"{resource_control_player.name} 的资源控制效果触发，{player.name} 的收益减半")
                
                if dice_roll >= 5:
                    evolution_cards = self.evolution_deck.draw(cards_to_draw)
                    for card in evolution_cards:
                        player.add_card(card, self.log)
                    self.log(f"{player.name} 选择欺骗，掷出{dice_roll}，抽取{cards_to_draw}张进化卡")
                else:
                    self.log(f"{player.name} 选择欺骗，掷出{dice_roll}，无所获")
    
    def resolve_natural_disaster(self, current_player: Player):
        """解析自然灾害格效果"""
        self.log(f"{current_player.name} 触发了自然灾害格")
        self.log("效果: 所有玩家出一张牌，合作卡免疫灾害，欺骗卡弃置1张进化卡并可指定一名其他玩家也弃置1张")
        
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
                continue
            
            # 使用一张牌
            if action == ActionType.COOPERATE:
                player.remove_card(CardType.COOPERATION, 1, self.log)
                # 出合作卡：免疫本次灾害
                self.log(f"{player.name} 选择合作，免疫本次自然灾害")
                
                # 种群韧性效果
                if player.has_ability("种群韧性"):
                    evolution_card = self.evolution_deck.draw(1)
                    if evolution_card:
                        player.add_card(evolution_card[0], self.log)
                        self.log(f"{player.name} 的种群韧性效果触发，额外获得1张进化卡")
            else:
                player.remove_card(CardType.DECEPTION, 1, self.log)
                # 出欺骗卡：必须弃置1张进化卡
                
                # 环境适应效果
                if player.has_ability("环境适应"):
                    self.log(f"{player.name} 的环境适应效果触发，无需弃置进化卡")
                else:
                    if player.has_evolution_cards(1):
                        player.remove_card(CardType.EVOLUTION, 1, self.log)
                        self.log(f"{player.name} 选择欺骗，弃置1张进化卡")
                    
                    # 灾难专家效果
                    if player.has_ability("灾难专家"):
                        # 额外指定一名玩家弃置1张进化卡
                        available_targets = [p for p in self.players if p != player and not p.is_eliminated]
                        if available_targets:
                            target = random.choice(available_targets)
                            if target.has_evolution_cards(1):
                                target.remove_card(CardType.EVOLUTION, 1, self.log)
                                self.log(f"{player.name} 的灾难专家效果触发，{target.name} 也弃置1张进化卡")
                
                # 可以指定一名其他玩家也弃置1张进化卡
                available_targets = [p for p in self.players if p != player and not p.is_eliminated]
                if available_targets and random.random() < 0.7:  # 70%概率使用转嫁效果
                    target = random.choice(available_targets)
                    if target.has_evolution_cards(1):
                        target.remove_card(CardType.EVOLUTION, 1, self.log)
                        self.log(f"{player.name} 转嫁灾害给 {target.name}，{target.name} 弃置1张进化卡")
    
    def resolve_cooperation_sanctuary(self, current_player: Player):
        """解析合作圣地格效果"""
        self.log(f"{current_player.name} 触发了合作圣地格")
        self.log("效果: 所有玩家出一张牌，合作卡可选择另一合作玩家各抽3张进化卡，欺骗卡单独抽4张但下家获得挑战权")
        
        # 记录所有玩家的选择
        actions = {}
        cooperation_players = []
        
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
                continue
            
            actions[player] = action
            
            if action == ActionType.COOPERATE:
                cooperation_players.append(player)
            
            # 使用一张牌
            if action == ActionType.COOPERATE:
                player.remove_card(CardType.COOPERATION, 1, self.log)
            else:
                player.remove_card(CardType.DECEPTION, 1, self.log)
        
        # 结算效果
        for player, action in actions.items():
            if action == ActionType.COOPERATE:
                # 出合作卡：可选择另一位也出合作卡的玩家，双方各抽3张进化卡
                if len(cooperation_players) > 1:  # 至少有另一个合作玩家
                    # 随机选择一个合作玩家（不能是自己）
                    other_cooperators = [p for p in cooperation_players if p != player]
                    if other_cooperators:
                        partner = random.choice(other_cooperators)
                        evolution_cards = self.evolution_deck.draw(3)
                        for card in evolution_cards:
                            player.add_card(card, self.log)
                        evolution_cards = self.evolution_deck.draw(3)
                        for card in evolution_cards:
                            partner.add_card(card, self.log)
                        self.log(f"{player.name} 和 {partner.name} 在合作圣地合作，各抽取3张进化卡")
                        
                        # 共生纽带效果
                        if player.symbiosis_target == partner or partner.symbiosis_target == player:
                            evolution_card = self.evolution_deck.draw(1)
                            if evolution_card:
                                if player.symbiosis_target == partner:
                                    player.add_card(evolution_card[0], self.log)
                                    self.log(f"{player.name} 的共生纽带效果触发，额外获得1张进化卡")
                                else:
                                    partner.add_card(evolution_card[0], self.log)
                                    self.log(f"{partner.name} 的共生纽带效果触发，额外获得1张进化卡")
                else:
                    self.log(f"{player.name} 选择合作，但没有其他合作者，无收益")
            else:
                # 出欺骗卡：单独抽取4张进化卡
                evolution_cards = self.evolution_deck.draw(4)
                for card in evolution_cards:
                    player.add_card(card, self.log)
                self.log(f"{player.name} 选择欺骗，单独抽取4张进化卡")
                
                # 下家获得免费的挑战权（在游戏中记录，实际挑战在下家回合处理）
                # 这里简化处理：下家在下回合开始时会自动发起鹰鸽博弈
                next_player_index = (self.players.index(player) + 1) % len(self.players)
                next_player = self.players[next_player_index]
                if not next_player.is_eliminated:
                    self.log(f"{next_player.name} 获得对 {player.name} 的免费挑战权")
    
    def resolve_deception_swamp(self, current_player: Player):
        """解析欺骗沼泽格效果"""
        self.log(f"{current_player.name} 触发了欺骗沼泽格")
        self.log("效果: 所有玩家出一张牌，欺骗卡可查看能力牌库顶3张拿1张，合作卡可阻止欺骗卡效果并获得奖励")
        
        # 记录所有玩家的选择
        actions = {}
        deception_players = []
        
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
                continue
            
            actions[player] = action
            
            if action == ActionType.DECEIVE:
                deception_players.append(player)
            
            # 使用一张牌
            if action == ActionType.COOPERATE:
                player.remove_card(CardType.COOPERATION, 1, self.log)
            else:
                player.remove_card(CardType.DECEPTION, 1, self.log)
        
        # 结算效果
        for player, action in actions.items():
            if action == ActionType.DECEIVE:
                # 出欺骗卡：查看能力牌库顶3张牌，拿取其中1张
                if not self.ability_deck.is_empty():
                    # 防御机制效果检查
                    defense_triggered = False
                    for other_player in self.players:
                        if other_player != player and other_player.has_ability("防御机制") and random.random() < 0.5:
                            # 防御机制触发，阻止效果并改为自己查看
                            top_cards = self.ability_deck.peek_top(3)
                            if len(top_cards) >= 2:  # 查看2张
                                chosen_card = random.choice(top_cards[:2])
                                other_player.add_card(chosen_card, self.log)
                                # 从牌库移除被选中的牌
                                self.ability_deck.cards.remove(chosen_card)
                                self.log(f"{other_player.name} 的防御机制效果触发，阻止了 {player.name} 的效果并自己获得能力卡")
                            defense_triggered = True
                            break
                    
                    if not defense_triggered:
                        top_cards = self.ability_deck.peek_top(3)
                        if top_cards:
                            chosen_card = random.choice(top_cards)
                            player.add_card(chosen_card, self.log)
                            # 从牌库移除被选中的牌
                            self.ability_deck.cards.remove(chosen_card)
                            self.log(f"{player.name} 选择欺骗，查看能力牌库顶3张牌并获得1张")
                        
                        # 趁火打劫效果
                        for other_player in self.players:
                            if other_player != player and other_player.has_ability("趁火打劫") and random.random() < 0.5:
                                if other_player.hand[CardType.COOPERATION] or other_player.hand[CardType.DECEPTION]:
                                    # 弃置1张手牌
                                    if other_player.hand[CardType.COOPERATION]:
                                        other_player.remove_card(CardType.COOPERATION, 1, self.log)
                                    else:
                                        other_player.remove_card(CardType.DECEPTION, 1, self.log)
                                    
                                    top_cards = self.ability_deck.peek_top(3)
                                    if top_cards:
                                        chosen_card = random.choice(top_cards)
                                        other_player.add_card(chosen_card, self.log)
                                        # 从牌库移除被选中的牌
                                        self.ability_deck.cards.remove(chosen_card)
                                        self.log(f"{other_player.name} 的趁火打劫效果触发，也获得1张能力卡")
                else:
                    self.log("能力牌库已空，无法查看")
            else:
                # 出合作卡：可指定一名出欺骗卡的玩家，阻止其效果并获得1张进化卡奖励
                if deception_players:
                    target = random.choice(deception_players)
                    self.log(f"{player.name} 选择合作，阻止了 {target.name} 的效果")
                    
                    # 获得1张进化卡奖励
                    evolution_card = self.evolution_deck.draw(1)
                    if evolution_card:
                        player.add_card(evolution_card[0], self.log)
                        self.log(f"{player.name} 获得1张进化卡作为奖励")
    
    def resolve_evolution_lab(self, current_player: Player):
        """解析进化实验室格效果"""
        self.log(f"{current_player.name} 触发了进化实验室格")
        self.log("效果: 可支付2张进化卡的代价，从能力牌库抽取一张能力卡")
        
        # 检查是否有足够进化卡
        if current_player.has_evolution_cards(2):
            # 支付代价
            current_player.remove_card(CardType.EVOLUTION, 2, self.log)
            
            # 抽取能力卡
            if not self.ability_deck.is_empty():
                ability_card = self.ability_deck.draw(1)[0]
                current_player.add_card(ability_card, self.log)
                
                # 进化爆发能力立即生效
                if ability_card.name == "进化爆发":
                    evolution_cards = self.evolution_deck.draw(3)
                    for card in evolution_cards:
                        current_player.add_card(card, self.log)
                    self.log(f"{current_player.name} 的进化爆发效果触发，获得3张进化卡")
                    # 将能力卡移出游戏
                    current_player.abilities.remove(ability_card)
                
                # 进化优势能力
                if ability_card.name == "进化优势":
                    current_player.evolution_requirement_reduction = 2
                    self.log(f"{current_player.name} 的进化胜利要求降低为18张进化卡")
                
                # 进化加速能力
                if ability_card.name == "进化加速":
                    current_player.hand_limit_bonus += 3
                    self.log(f"{current_player.name} 的手牌上限永久增加3张")
            else:
                self.log("能力牌库已空，无法抽取能力卡")
        else:
            self.log(f"{current_player.name} 没有足够的进化卡支付代价")
    
    def resolve_finish(self, current_player: Player):
        """解析终点格效果"""
        self.log(f"{current_player.name} 触发了终点格")
        self.log("效果: 首次抵达此格的玩家立即抽取3张进化卡并获得2点进化点数")
        
        # 检查是否是首次抵达（简化实现：只要不是起点就认为是首次）
        if current_player.position != 0:  # 假设0是起点位置
            evolution_cards = self.evolution_deck.draw(3)
            for card in evolution_cards:
                current_player.add_card(card, self.log)
            current_player.evolution_points += 2
            self.log(f"{current_player.name} 首次抵达终点，获得3张进化卡和2点进化点数")
        else:
            self.log(f"{current_player.name} 已经抵达过终点，无效果")
    
    def resolve_mutation_event(self, current_player: Player):
        """解析突变事件格效果"""
        self.log(f"{current_player.name} 触发了突变事件格")
        self.log("效果: 抽一张事件卡并立即执行其效果")
        
        if self.event_deck.is_empty():
            self.log("事件牌库已空，无效果")
            return
        
        event_card = self.event_deck.draw(1)[0]
        self.log(f"{current_player.name} 抽到事件卡: {event_card.get_full_description()}")
        self.last_event_card = event_card
        
        # 根据事件卡名称执行效果
        if event_card.name == "基因突变":
            # 抽取3张进化卡，但下个回合无法移动
            evolution_cards = self.evolution_deck.draw(3)
            for card in evolution_cards:
                current_player.add_card(card, self.log)
            current_player.cannot_move_next_turn = True
            self.log(f"{current_player.name} 下回合无法移动")
        
        elif event_card.name == "群体迁徙":
            # 所有玩家移动到下一个与当前所在格类型相同的格子
            current_grid_type = self.board.get_grid(current_player.position).grid_type
            for player in self.players:
                if player.is_eliminated:
                    continue
                # 找到下一个相同类型的格子
                next_position = (player.position + 1) % self.board.grid_count
                while self.board.get_grid(next_position).grid_type != current_grid_type:
                    next_position = (next_position + 1) % self.board.grid_count
                player.position = next_position
                new_grid = self.board.get_grid(next_position)
                self.log(f"{player.name} 移动到位置 {next_position} ({new_grid.grid_type.value})")
                # 触发新格子效果
                self.resolve_grid_effect(player, new_grid)
        
        elif event_card.name == "互利共生":
            # 选择一名玩家，双方各抽取2张进化卡
            available_players = [p for p in self.players if p != current_player and not p.is_eliminated]
            if available_players:
                target = random.choice(available_players)
                evolution_cards = self.evolution_deck.draw(2)
                for card in evolution_cards:
                    current_player.add_card(card, self.log)
                evolution_cards = self.evolution_deck.draw(2)
                for card in evolution_cards:
                    target.add_card(card, self.log)
                self.log(f"{current_player.name} 和 {target.name} 互利共生，各抽取2张进化卡")
        
        # 其他事件卡效果类似实现...
    
    def optional_actions(self, current_player: Player):
        """执行可选行动"""
        self.log(f"{current_player.name} 的可选行动阶段")
        
        # 兑换进化点数
        if current_player.evolution_points > 0 and random.random() < 0.5:
            points_to_convert = random.randint(1, min(3, current_player.evolution_points))
            evolution_cards = self.evolution_deck.draw(points_to_convert)
            if evolution_cards:
                for card in evolution_cards:
                    current_player.add_card(card, self.log)
                current_player.evolution_points -= points_to_convert
                self.log(f"{current_player.name} 兑换了{points_to_convert}点进化点数，获得{len(evolution_cards)}张进化卡")
            else:
                self.log("进化牌库已空，无法兑换")
        
        # 使用事件卡
        if current_player.hand[CardType.EVENT] and random.random() < 0.3:
            event_card = random.choice(current_player.hand[CardType.EVENT])
            current_player.hand[CardType.EVENT].remove(event_card)
            self.log(f"{current_player.name} 使用了事件卡: {event_card.get_full_description()}")
            # 这里可以添加事件卡使用效果
        
        # 使用能力卡
        if current_player.abilities and random.random() < 0.3:
            ability = random.choice(current_player.abilities)
            self.log(f"{current_player.name} 发动了能力: {ability.get_full_description()}")
            # 这里可以添加能力卡使用效果
    
    def environment_change(self, current_player: Player):
        """执行环境变化（可选规则）"""
        if random.random() < 0.3 and not self.environment_change_deck.is_empty():
            environment_card = self.environment_change_deck.draw(1)[0]
            self.log(f"{current_player.name} 执行环境变化: {environment_card.get_full_description()}")
            
            # 生态改造能力
            if current_player.has_ability("生态改造") and random.random() < 0.5:
                self.log(f"{current_player.name} 使用生态改造能力，自定义环境变化")
                # 随机改变一个格子的类型
                grid_to_change = random.randint(1, self.board.grid_count - 2)
                new_type = random.choice([gt for gt in GridType if gt not in [GridType.START, GridType.FINISH]])
                result = self.board.change_grid_type(grid_to_change, new_type)
                self.log(result)
            else:
                # 正常执行环境变化卡效果
                if environment_card.name == "干旱降临":
                    # 将地图上最近的一个资源丰富格变为自然灾害格
                    pos = self.board.find_grid_by_type(GridType.RESOURCE_RICH)
                    if pos is not None:
                        result = self.board.change_grid_type(pos, GridType.NATURAL_DISASTER)
                        self.log(result)
                
                elif environment_card.name == "绿洲形成":
                    # 将地图上最近的一个自然灾害格变为资源丰富格
                    pos = self.board.find_grid_by_type(GridType.NATURAL_DISASTER)
                    if pos is not None:
                        result = self.board.change_grid_type(pos, GridType.RESOURCE_RICH)
                        self.log(result)
                
                # 其他环境变化卡效果...
            
            # 触发快速适应能力
            for player in self.players:
                if not player.is_eliminated:
                    self.apply_ability_effects(player, None, "environment_change")
    
    def check_elimination(self):
        """检查是否有玩家被淘汰"""
        for player in self.players:
            if not player.is_eliminated and player.is_eliminated_check(self.log):
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
                abilities = [ability.name for ability in player.abilities]
                ability_str = ", ".join(abilities) if abilities else "无"
                self.log(f"{player.name} ({player.marker}): 位置{player.position}, 进化卡{player.get_evolution_card_count()}张, 进化点数{player.evolution_points}点, 能力: {ability_str}")
    
    def play_turn(self):
        """执行一个完整的回合"""
        current_player = self.get_current_player()
        
        if current_player.is_eliminated:
            self.next_player()
            return
        
        self.log(f"\n=== {current_player.name} 的回合开始 ===")
        self.round_count += 1
        
        # 显示当前地图状态
        self.board.display_map(self.players, self.log)
        self.display_player_status()
        
        # 战术升级能力 - 掷两次骰子选择其一
        dice_roll = self.roll_dice()
        if current_player.has_ability("战术升级") and random.random() < 0.5:
            dice_roll2 = self.roll_dice()
            dice_roll = max(dice_roll, dice_roll2)  # 选择较大的点数
            self.log(f"{current_player.name} 使用战术升级，掷出{dice_roll}和{dice_roll2}，选择{dice_roll}点")
        
        self.log(f"{current_player.name} 掷出 {dice_roll} 点")
        
        # 阶段一：掷骰与移动
        steps = self.move_player(current_player, dice_roll)
        if steps > 0:
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
        self.log(f"\n游戏开始! 共有{len(self.players)}名玩家")
        
        round_count = 1
        while not self.game_over and round_count <= 100:  # 防止无限循环
            self.log(f"\n--- 第 {round_count} 轮 ---")
            self.play_turn()
            round_count += 1
        
        if self.winner:
            self.log(f"\n=== 游戏结束！{self.winner.name} 获胜！ ===")
            self.log(f"游戏进行了 {round_count-1} 轮")
        else:
            self.log("\n=== 游戏结束！没有玩家获胜 ===")
        
        # 显示最终状态
        self.display_player_status()
        
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
