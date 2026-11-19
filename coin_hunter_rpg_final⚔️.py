import json
import random
import tkinter as tk
from tkinter import messagebox
from pathlib import Path


SAVE_FILE = Path.home() / ".coin_hunter_rpg_save.json"


class CoinHunterRPG:
    """COIN HUNTER RPG - 코인 수집과 장비 성장, 몬스터 전투를 합친 버전"""

    BG = "#101827"
    PANEL = "#1c2b43"
    PANEL_DARK = "#172338"
    PANEL_LIGHT = "#263952"
    GOLD = "#facc15"
    TEXT = "#f8fafc"
    MUTED = "#cbd5e1"
    GREEN = "#22c55e"
    RED = "#ef4444"
    BLUE = "#475569"

    def __init__(self, root):
        self.root = root
        self.root.title("COIN HUNTER RPG")
        self.root.geometry("1120x790")
        self.root.minsize(1000, 720)
        self.root.configure(bg=self.BG)

        # 기본 재화와 성장 능력치
        self.coins = 100
        self.gems = 10
        self.power = 1
        self.level = 1
        self.xp = 0
        self.max_exp = 50
        self.base_hp = 100
        self.player_hp = 100
        self.potions = 5

        # 스킨
        self.skin = "기본 용사"
        self.owned_skins = ["기본 용사"]
        self.skin_icons = {
            "기본 용사": "🧙",
            "빛의 용사": "🦸",
            "그림자 용사": "🥷",
        }

        # 무기와 갑옷
        self.weapons = {
            "나무 검": {"attack": 10, "price": 0},
            "철 검": {"attack": 20, "price": 150},
            "불꽃 검": {"attack": 35, "price": 350},
            "얼음 창": {"attack": 50, "price": 600},
            "용의 검": {"attack": 80, "price": 1200},
        }
        self.weapon = "나무 검"
        self.weapon_level = 0
        self.owned_weapons = ["나무 검"]

        self.armors = {
            "낡은 갑옷": {"hp": 0, "price": 0},
            "철 갑옷": {"hp": 30, "price": 200},
            "기사 갑옷": {"hp": 60, "price": 500},
            "용의 갑옷": {"hp": 100, "price": 1000},
        }
        self.armor = "낡은 갑옷"
        self.owned_armors = ["낡은 갑옷"]
        self.inventory = []
        self.stage = 1

        # 전투 상태
        self.enemy = None
        self.enemy_hp = 0
        self.enemy_max_hp = 0
        self.enemy_attack = 0
        self.battle_active = False
        self.is_boss = False

        self.status_text = "보물 상자를 클릭하거나 몬스터와 전투해 보세요!"
        self._load_saved_data(silent=True)
        self.build_ui()
        self.refresh()
        self.root.protocol("WM_DELETE_WINDOW", self.close_game)

    # -------------------- 능력치 --------------------

    def max_hp(self):
        return self.base_hp + self.armors[self.armor]["hp"]

    def attack_power(self):
        return self.weapons[self.weapon]["attack"] + self.weapon_level * 5

    def set_status(self, text):
        self.status_text = text
        if hasattr(self, "status") and self.status.winfo_exists():
            self.status.config(text=text)

    # -------------------- UI 공통 --------------------

    def make_button(self, parent, text, command, color="#475569", **kwargs):
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=("맑은 고딕", 9, "bold"),
            bg=color,
            fg="white",
            activebackground="#64748b",
            activeforeground="white",
            relief="flat",
            padx=10,
            pady=7,
            cursor="hand2",
            **kwargs,
        )

    def make_panel(self, parent, **kwargs):
        return tk.Frame(parent, bg=self.PANEL, **kwargs)

    def make_bar(self, parent, color, width=360):
        bar = tk.Canvas(
            parent,
            width=width,
            height=13,
            bg="#475569",
            highlightthickness=0,
            bd=0,
        )
        bar.create_rectangle(0, 0, width, 13, fill=color, outline="", tags="value")
        return bar

    def draw_bar(self, canvas, current, maximum, color):
        canvas.delete("all")
        width = int(canvas.cget("width"))
        ratio = current / maximum if maximum > 0 else 0
        ratio = max(0, min(1, ratio))
        canvas.create_rectangle(0, 0, width, 13, fill="#475569", outline="")
        if ratio > 0:
            canvas.create_rectangle(0, 0, width * ratio, 13, fill=color, outline="")

    # -------------------- 메인 화면 --------------------

    def build_ui(self):
        header = tk.Frame(self.root, bg=self.PANEL_DARK, height=68)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="⚔ COIN HUNTER RPG",
            font=("Arial", 22, "bold"),
            fg=self.GOLD,
            bg=self.PANEL_DARK,
        ).pack(side="left", padx=20, pady=13)

        self.level_label = tk.Label(
            header, text="LV. 1", font=("Arial", 13, "bold"),
            fg="#c4b5fd", bg=self.PANEL_DARK
        )
        self.level_label.pack(side="right", padx=12)
        self.gem_label = tk.Label(
            header, text="💎 10", font=("맑은 고딕", 12, "bold"),
            fg="#67e8f9", bg=self.PANEL_DARK
        )
        self.gem_label.pack(side="right", padx=8)
        self.coin_label = tk.Label(
            header, text="🪙 100", font=("맑은 고딕", 12, "bold"),
            fg="#fde68a", bg=self.PANEL_DARK
        )
        self.coin_label.pack(side="right", padx=(8, 20))

        body = tk.Frame(self.root, bg=self.BG)
        body.pack(fill="both", expand=True, padx=14, pady=12)

        left = tk.Frame(body, bg=self.PANEL, width=690)
        left.pack(side="left", fill="both", expand=True, padx=(0, 12))
        left.pack_propagate(False)

        tk.Label(
            left, text="모험가의 훈련장", font=("맑은 고딕", 17, "bold"),
            fg="white", bg=self.PANEL
        ).pack(pady=(10, 5))

        top_cards = tk.Frame(left, bg=self.PANEL)
        top_cards.pack(fill="x", padx=14)
        top_cards.columnconfigure(0, weight=1)
        top_cards.columnconfigure(1, weight=1)

        character_card = tk.Frame(top_cards, bg=self.PANEL_LIGHT, height=142)
        character_card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        character_card.pack_propagate(False)
        tk.Label(
            character_card, text="나의 캐릭터", font=("맑은 고딕", 10, "bold"),
            fg=self.MUTED, bg=self.PANEL_LIGHT
        ).pack(pady=(7, 0))
        self.character = tk.Label(
            character_card, text="🧙", font=("Segoe UI Emoji", 39),
            fg="white", bg=self.PANEL_LIGHT
        )
        self.character.pack(pady=0)
        self.skin_label = tk.Label(
            character_card, text=self.skin, font=("맑은 고딕", 9, "bold"),
            fg="#fcd34d", bg=self.PANEL_LIGHT
        )
        self.skin_label.pack()

        chest_card = tk.Frame(top_cards, bg="#3b2b26", height=142)
        chest_card.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        chest_card.pack_propagate(False)
        tk.Label(
            chest_card, text="보물 상자", font=("맑은 고딕", 10, "bold"),
            fg="#fed7aa", bg="#3b2b26"
        ).pack(pady=(9, 5))
        self.make_button(
            chest_card, "🎁 보물 상자 클릭!", self.collect, "#9a3412"
        ).pack(pady=4)
        self.power_label = tk.Label(
            chest_card, text="클릭당 골드: 1", font=("맑은 고딕", 9, "bold"),
            fg="#fde68a", bg="#3b2b26"
        )
        self.power_label.pack(pady=4)

        battle = tk.Frame(left, bg=self.PANEL_LIGHT, padx=12, pady=7)
        battle.pack(fill="both", expand=True, padx=14, pady=(10, 8))
        tk.Label(
            battle, text="⚔ 몬스터 전투", font=("맑은 고딕", 14, "bold"),
            fg="#fca5a5", bg=self.PANEL_LIGHT
        ).pack(pady=(1, 3))

        self.stage_label = tk.Label(
            battle, text="현재 스테이지: 1", font=("맑은 고딕", 9, "bold"),
            fg="#fde68a", bg=self.PANEL_LIGHT
        )
        self.stage_label.pack()
        self.enemy_name = tk.Label(
            battle, text="몬스터를 찾아보세요!", font=("맑은 고딕", 11, "bold"),
            fg="white", bg=self.PANEL_LIGHT
        )
        self.enemy_name.pack(pady=(3, 0))
        self.enemy_art = tk.Label(
            battle, text="❔", font=("Segoe UI Emoji", 31),
            fg="white", bg=self.PANEL_LIGHT
        )
        self.enemy_art.pack(pady=0)
        self.enemy_hp_label = tk.Label(
            battle, text="몬스터 HP: -", font=("맑은 고딕", 9),
            fg="#fca5a5", bg=self.PANEL_LIGHT
        )
        self.enemy_hp_label.pack()
        self.enemy_bar = self.make_bar(battle, self.RED, width=370)
        self.enemy_bar.pack(pady=(3, 5))

        self.player_hp_label = tk.Label(
            battle, text="내 HP: 100 / 100", font=("맑은 고딕", 9, "bold"),
            fg="#86efac", bg=self.PANEL_LIGHT
        )
        self.player_hp_label.pack(pady=(2, 0))
        self.player_bar = self.make_bar(battle, self.GREEN, width=370)
        self.player_bar.pack(pady=(3, 5))

        controls = tk.Frame(battle, bg=self.PANEL_LIGHT)
        controls.pack(pady=3)
        self.start_button = self.make_button(
            controls, "일반 몬스터 찾기", self.start_battle, "#6d28d9"
        )
        self.start_button.grid(row=0, column=0, padx=4, pady=3)
        self.boss_button = self.make_button(
            controls, "👑 보스 도전", self.start_boss, "#991b1b"
        )
        self.boss_button.grid(row=0, column=1, padx=4, pady=3)
        self.attack_button = self.make_button(
            controls, "⚔ 공격하기", self.attack, "#b91c1c", state="disabled"
        )
        self.attack_button.grid(row=1, column=0, padx=4, pady=3)
        self.potion_button = self.make_button(
            controls, "🧪 물약 사용", self.use_potion, "#047857", state="disabled"
        )
        self.potion_button.grid(row=1, column=1, padx=4, pady=3)

        self.status = tk.Label(
            left, text=self.status_text, font=("맑은 고딕", 9),
            fg="#93c5fd", bg=self.PANEL, wraplength=640, justify="center"
        )
        self.status.pack(fill="x", padx=12, pady=(0, 8))

        right = tk.Frame(body, bg=self.PANEL, width=310)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        tk.Label(
            right, text="🏪 모험가 상점", font=("맑은 고딕", 16, "bold"),
            fg="white", bg=self.PANEL
        ).pack(pady=(12, 8))

        self.make_shop_item(right, "강화된 곡괭이", "클릭당 골드 +1", "25 골드",
                            lambda: self.buy_power(25, 1))
        self.make_shop_item(right, "황금 곡괭이", "클릭당 골드 +5", "100 골드",
                            lambda: self.buy_power(100, 5))
        self.make_shop_item(right, "체력 강화", "기본 최대 HP +20", "80 골드",
                            self.buy_health_upgrade)
        self.make_shop_item(right, "회복 물약 1개", "전투 중 HP 40 회복", "50 골드",
                            self.buy_potion)

        tk.Label(
            right, text="💎 보석 상점 (무료 테스트)",
            font=("맑은 고딕", 11, "bold"), fg="#67e8f9", bg=self.PANEL
        ).pack(pady=(10, 4))
        self.make_shop_item(right, "보석 10개 체험팩", "무료 테스트 지급", "받기",
                            lambda: self.test_purchase(10))
        self.make_shop_item(right, "보석 30개 체험팩", "무료 테스트 지급", "받기",
                            lambda: self.test_purchase(30))

        tk.Label(
            right, text="🎭 스킨", font=("맑은 고딕", 11, "bold"),
            fg="#fcd34d", bg=self.PANEL
        ).pack(pady=(8, 3))
        self.make_shop_item(right, "빛의 용사", "보석 20개", "구매/장착",
                            lambda: self.buy_skin("빛의 용사", 20))
        self.make_shop_item(right, "그림자 용사", "보석 35개", "구매/장착",
                            lambda: self.buy_skin("그림자 용사", 35))

        footer = tk.Frame(self.root, bg=self.PANEL_DARK)
        footer.pack(fill="x", side="bottom")
        nav_items = [
            ("⚔ 무기 / 강화", self.weapon_page),
            ("🛡 장비 / 인벤토리", self.inventory_page),
            ("💎 아이템 뽑기", self.gacha_page),
            ("🗺 던전 정보", self.dungeon_page),
            ("💾 저장", self.save_game),
            ("불러오기", self.load_game),
            ("초기화", self.reset_game),
        ]
        for text, command in nav_items:
            self.make_button(footer, text, command, "#334155").pack(
                side="left", padx=4, pady=8, expand=True, fill="x"
            )
        tk.Label(
            self.root, text="테스트 버전 · 보석 체험팩은 무료이며 실제 결제 기능은 없음",
            font=("맑은 고딕", 8), fg="#94a3b8", bg=self.BG
        ).pack(side="bottom", pady=(0, 3))

    def make_shop_item(self, parent, title, detail, price, command):
        frame = tk.Frame(parent, bg="#293b56", padx=8, pady=5)
        frame.pack(fill="x", padx=9, pady=3)
        tk.Label(
            frame, text=title, font=("맑은 고딕", 9, "bold"),
            fg="white", bg="#293b56", anchor="w"
        ).pack(fill="x")
        row = tk.Frame(frame, bg="#293b56")
        row.pack(fill="x", pady=(2, 0))
        tk.Label(
            row, text=detail, font=("맑은 고딕", 8),
            fg="#cbd5e1", bg="#293b56"
        ).pack(side="left")
        self.make_button(row, price, command, "#475569").pack(side="right")

    # -------------------- 코인 / 상점 --------------------

    def collect(self):
        self.coins += self.power
        self.set_status(f"보물 상자에서 골드 {self.power}개를 획득했습니다!")
        self.refresh()

    def buy_power(self, cost, increase):
        if self.coins < cost:
            self.set_status(f"골드가 부족합니다. {cost}골드가 필요합니다.")
            return
        self.coins -= cost
        self.power += increase
        self.set_status(f"곡괭이 강화 성공! 클릭당 골드가 {self.power}개가 되었습니다.")
        self.refresh()

    def buy_health_upgrade(self):
        if self.coins < 80:
            self.set_status("골드가 부족합니다. 체력 강화에는 80골드가 필요합니다.")
            return
        self.coins -= 80
        self.base_hp += 20
        self.player_hp = min(self.max_hp(), self.player_hp + 20)
        self.set_status("최대 HP가 20 증가했습니다!")
        self.refresh()

    def buy_potion(self):
        if self.coins < 50:
            self.set_status("골드가 부족합니다. 물약 구매에는 50골드가 필요합니다.")
            return
        self.coins -= 50
        self.potions += 1
        self.set_status(f"회복 물약 1개를 구매했습니다. 보유 물약: {self.potions}개")
        self.refresh()

    def test_purchase(self, amount):
        if messagebox.askyesno(
            "무료 테스트 보석",
            f"테스트용 보석 {amount}개를 무료로 받을까요?\n실제 결제는 없습니다."
        ):
            self.gems += amount
            self.set_status(f"무료 테스트 보석 {amount}개를 받았습니다!")
            self.refresh()

    def buy_skin(self, name, cost):
        if name in self.owned_skins:
            self.skin = name
            self.set_status(f"{name} 스킨을 장착했습니다!")
        elif self.gems >= cost:
            self.gems -= cost
            self.owned_skins.append(name)
            self.skin = name
            self.set_status(f"{name} 스킨을 구매하고 장착했습니다!")
        else:
            self.set_status(f"보석이 부족합니다. {cost}개가 필요합니다.")
        self.refresh()

    # -------------------- 전투 --------------------

    def start_battle(self):
        if self.battle_active:
            self.set_status("이미 몬스터와 전투 중입니다!")
            return
        if self.player_hp <= 0:
            self.player_hp = max(1, self.max_hp() // 2)

        monsters = [
            ("초록 슬라임", "🟢", 35, 7, 15),
            ("숲의 고블린", "👺", 55, 10, 22),
            ("불꽃 박쥐", "🦇", 70, 13, 30),
            ("바위 골렘", "🗿", 100, 16, 45),
            ("어둠의 마법사", "🧙", 125, 19, 60),
        ]
        if self.level < 2:
            choices = monsters[:2]
        elif self.level < 4:
            choices = monsters[:3]
        else:
            choices = monsters

        name, art, hp, damage, reward = random.choice(choices)
        scale = 1 + (self.stage - 1) * 0.12 + (self.level - 1) * 0.04
        self.enemy = {
            "name": name,
            "art": art,
            "damage": max(1, int(damage * scale)),
            "reward": max(1, int(reward * scale)),
        }
        self.enemy_max_hp = max(1, int(hp * scale))
        self.enemy_hp = self.enemy_max_hp
        self.enemy_attack = self.enemy["damage"]
        self.battle_active = True
        self.is_boss = False
        self.enemy_name.config(text=name)
        self.enemy_art.config(text=art)
        self.set_status(f"{name} 등장! 공격하기 버튼을 눌러 전투하세요.")
        self.refresh()

    def start_boss(self):
        if self.battle_active:
            self.set_status("현재 전투를 먼저 끝내세요!")
            return
        if self.player_hp <= 0:
            self.player_hp = max(1, self.max_hp() // 2)

        bosses = [
            ("슬라임 킹", "👑", 150, 16),
            ("어둠의 기사", "🛡️", 210, 22),
            ("고대 드래곤", "🐉", 280, 28),
        ]
        name, art, hp, damage = bosses[(self.stage - 1) % len(bosses)]
        scale = 1 + (self.stage - 1) * 0.18 + (self.level - 1) * 0.04
        self.enemy = {
            "name": name,
            "art": art,
            "damage": max(1, int(damage * scale)),
            "reward": 100 + self.stage * 30,
        }
        self.enemy_max_hp = max(1, int(hp * scale))
        self.enemy_hp = self.enemy_max_hp
        self.enemy_attack = self.enemy["damage"]
        self.battle_active = True
        self.is_boss = True
        self.enemy_name.config(text=f"👑 보스: {name}")
        self.enemy_art.config(text=art)
        self.set_status(f"보스 {name} 등장! 쓰러뜨리면 보석 5개와 다음 스테이지가 열립니다.")
        self.refresh()

    def attack(self):
        if not self.battle_active or self.enemy is None:
            return
        damage = self.attack_power() + random.randint(0, max(4, self.level * 2 + 4))
        self.enemy_hp = max(0, self.enemy_hp - damage)
        if self.enemy_hp <= 0:
            self.win_battle(damage)
            return

        enemy_damage = random.randint(max(1, self.enemy_attack - 3), self.enemy_attack + 3)
        self.player_hp = max(0, self.player_hp - enemy_damage)
        if self.player_hp <= 0:
            self.lose_battle()
            return

        self.set_status(
            f"공격 성공! {self.enemy['name']}에게 {damage} 피해!\n"
            f"반격을 받아 HP가 {enemy_damage} 감소했습니다."
        )
        self.refresh()

    def win_battle(self, last_damage):
        defeated = self.enemy["name"]
        was_boss = self.is_boss
        reward = self.enemy["reward"]
        gained_xp = 20 + self.level * 5 + self.stage * 2

        self.coins += reward
        self.xp += gained_xp
        self.battle_active = False
        self.enemy_hp = 0

        if was_boss:
            self.gems += 5
            self.stage += 1
            result = (
                f"보스 {defeated} 처치 성공!\n골드 {reward}개, 보석 5개, "
                f"경험치 {gained_xp} 획득!\n스테이지 {self.stage}로 이동했습니다!"
            )
        else:
            result = (
                f"{defeated} 처치!\n골드 {reward}개와 경험치 {gained_xp} 획득!"
            )

        level_messages = self.check_level_up()
        if level_messages:
            result += "\n" + "\n".join(level_messages)
        self.set_status(result)
        self.refresh()

    def lose_battle(self):
        self.battle_active = False
        self.player_hp = max(1, self.max_hp() // 2)
        self.set_status(
            f"{self.enemy['name']}에게 패배했습니다.\n"
            f"체력을 절반으로 회복했습니다. 장비를 강화한 뒤 다시 도전하세요."
        )
        self.refresh()

    def use_potion(self):
        if not self.battle_active:
            self.set_status("물약은 전투 중에만 사용할 수 있습니다.")
            return
        if self.potions <= 0:
            self.set_status("물약이 없습니다. 상점에서 구매하세요.")
            return
        if self.player_hp >= self.max_hp():
            self.set_status("체력이 이미 가득 찼습니다!")
            return

        self.potions -= 1
        healed = min(40, self.max_hp() - self.player_hp)
        self.player_hp += healed
        enemy_damage = random.randint(max(1, self.enemy_attack - 3), self.enemy_attack + 3)
        self.player_hp = max(0, self.player_hp - enemy_damage)
        if self.player_hp <= 0:
            self.lose_battle()
            return
        self.set_status(
            f"물약 사용! HP {healed} 회복, 남은 물약 {self.potions}개.\n"
            f"몬스터의 반격으로 HP {enemy_damage} 피해를 입었습니다."
        )
        self.refresh()

    def check_level_up(self):
        messages = []
        while self.xp >= self.max_exp:
            self.xp -= self.max_exp
            self.level += 1
            self.max_exp = max(self.max_exp + 1, int(self.max_exp * 1.3))
            self.base_hp += 10
            self.player_hp = self.max_hp()
            messages.append(
                f"레벨 업! 현재 레벨 {self.level}. 기본 최대 HP가 10 증가했습니다!"
            )
        return messages

    # -------------------- 무기 / 강화 --------------------

    def weapon_page(self):
        win = tk.Toplevel(self.root)
        win.title("무기 / 강화")
        win.geometry("560x590")
        win.configure(bg=self.BG)
        win.transient(self.root)

        tk.Label(
            win, text="⚔ 무기 / 강화", font=("맑은 고딕", 20, "bold"),
            fg="white", bg=self.BG
        ).pack(pady=12)
        current = tk.Label(
            win,
            text=f"현재 무기: {self.weapon} +{self.weapon_level}\n공격력: {self.attack_power()}\n보유 골드: {self.coins}",
            font=("맑은 고딕", 12, "bold"), fg=self.GOLD, bg=self.BG
        )
        current.pack(pady=8)

        list_frame = tk.Frame(win, bg=self.BG)
        list_frame.pack(fill="both", expand=True, padx=18)
        for name, data in self.weapons.items():
            owned = name in self.owned_weapons
            if name == self.weapon:
                button_text = f"{name} (장착 중) · 공격력 {data['attack']}"
                color = "#166534"
            elif owned:
                button_text = f"{name} 장착 · 공격력 {data['attack']}"
                color = "#334155"
            else:
                button_text = f"{name} 구매 · 공격력 {data['attack']} · {data['price']}골드"
                color = "#475569"
            self.make_button(
                list_frame, button_text,
                lambda n=name, w=win: self.buy_or_equip_weapon(n, w), color
            ).pack(fill="x", pady=5)

        upgrade_price = 100 + self.weapon_level * 100
        self.make_button(
            win,
            f"현재 무기 강화 +1 ({upgrade_price}골드)",
            lambda w=win: self.upgrade_weapon(w),
            "#9a6423"
        ).pack(pady=10, ipadx=15)
        self.make_button(win, "닫기", win.destroy, "#334155").pack(pady=(0, 12))

    def buy_or_equip_weapon(self, name, window):
        if name in self.owned_weapons:
            self.weapon = name
            self.weapon_level = 0
            self.set_status(f"{name}을(를) 장착했습니다!")
        else:
            price = self.weapons[name]["price"]
            if self.coins < price:
                self.set_status(f"골드가 부족합니다. {price}골드가 필요합니다.")
                self.refresh()
                return
            self.coins -= price
            self.owned_weapons.append(name)
            self.weapon = name
            self.weapon_level = 0
            self.set_status(f"{name} 구매 및 장착 완료!")
        self.refresh()
        window.destroy()
        self.weapon_page()

    def upgrade_weapon(self, window=None):
        price = 100 + self.weapon_level * 100
        if self.weapon_level >= 10:
            self.set_status("무기가 최대 강화 단계(+10)에 도달했습니다!")
            return
        if self.coins < price:
            self.set_status(f"골드가 부족합니다. 강화에는 {price}골드가 필요합니다.")
            self.refresh()
            return
        self.coins -= price
        self.weapon_level += 1
        self.set_status(f"강화 성공! {self.weapon} +{self.weapon_level}")
        self.refresh()
        if window is not None and window.winfo_exists():
            window.destroy()
            self.weapon_page()

    # -------------------- 갑옷 / 인벤토리 --------------------

    def inventory_page(self):
        win = tk.Toplevel(self.root)
        win.title("장비 / 인벤토리")
        win.geometry("560x620")
        win.configure(bg=self.BG)
        win.transient(self.root)

        tk.Label(
            win, text="🛡 장비 / 인벤토리", font=("맑은 고딕", 20, "bold"),
            fg="white", bg=self.BG
        ).pack(pady=12)
        tk.Label(
            win,
            text=f"현재 갑옷: {self.armor}\n최대 HP: {self.max_hp()}   현재 HP: {self.player_hp}\n보유 물약: {self.potions}개",
            font=("맑은 고딕", 11, "bold"), fg=self.GOLD, bg=self.BG
        ).pack(pady=5)

        tk.Label(
            win, text="보유 갑옷", font=("맑은 고딕", 13, "bold"),
            fg="white", bg=self.BG
        ).pack(pady=(10, 4))
        armor_frame = tk.Frame(win, bg=self.BG)
        armor_frame.pack(fill="x", padx=20)
        for name in self.owned_armors:
            suffix = " (장착 중)" if name == self.armor else " 장착"
            self.make_button(
                armor_frame,
                f"{name}{suffix} · 최대 HP +{self.armors[name]['hp']}",
                lambda n=name, w=win: self.equip_armor(n, w),
                "#166534" if name == self.armor else "#334155"
            ).pack(fill="x", pady=3)

        tk.Label(
            win, text="갑옷 상점", font=("맑은 고딕", 12, "bold"),
            fg="#fcd34d", bg=self.BG
        ).pack(pady=(10, 3))
        armor_shop = tk.Frame(win, bg=self.BG)
        armor_shop.pack(fill="x", padx=20)
        unowned_armors = [name for name in self.armors if name not in self.owned_armors]
        if not unowned_armors:
            tk.Label(
                armor_shop, text="모든 갑옷을 보유하고 있습니다!",
                font=("맑은 고딕", 9), fg="white", bg=self.BG
            ).pack(pady=3)
        else:
            for name in unowned_armors:
                data = self.armors[name]
                self.make_button(
                    armor_shop,
                    f"{name} 구매 · HP +{data['hp']} · {data['price']}골드",
                    lambda n=name, w=win: self.buy_armor(n, w),
                    "#475569"
                ).pack(fill="x", pady=2)

        tk.Label(
            win, text="희귀 아이템", font=("맑은 고딕", 13, "bold"),
            fg=self.GOLD, bg=self.BG
        ).pack(pady=(14, 4))
        item_frame = tk.Frame(win, bg="#1c2b43")
        item_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        if not self.inventory:
            tk.Label(
                item_frame, text="아직 획득한 희귀 아이템이 없습니다.",
                font=("맑은 고딕", 10), fg="white", bg="#1c2b43"
            ).pack(pady=12)
        else:
            item_text = "\n".join(f"💎 {item}" for item in self.inventory)
            tk.Label(
                item_frame, text=item_text, font=("맑은 고딕", 10),
                fg="white", bg="#1c2b43", justify="left", anchor="nw"
            ).pack(fill="both", expand=True, padx=10, pady=8)

        self.make_button(win, "닫기", win.destroy, "#334155").pack(pady=(0, 10))

    def equip_armor(self, name, window=None):
        old_max = self.max_hp()
        self.armor = name
        new_max = self.max_hp()
        self.player_hp = min(new_max, self.player_hp + (new_max - old_max))
        self.set_status(f"{name}을(를) 장착했습니다!")
        self.refresh()
        if window is not None and window.winfo_exists():
            window.destroy()
            self.inventory_page()

    def buy_armor(self, name, window=None):
        if name in self.owned_armors:
            self.set_status(f"이미 보유한 갑옷입니다: {name}")
            return
        price = self.armors[name]["price"]
        if self.coins < price:
            self.set_status(f"골드가 부족합니다. {price}골드가 필요합니다.")
            self.refresh()
            return
        self.coins -= price
        self.owned_armors.append(name)
        old_max = self.max_hp()
        self.armor = name
        self.player_hp = min(self.max_hp(), self.player_hp + self.max_hp() - old_max)
        self.set_status(f"{name} 구매 및 장착 완료!")
        self.refresh()
        if window is not None and window.winfo_exists():
            window.destroy()
            self.inventory_page()

    # -------------------- 희귀 아이템 뽑기 --------------------

    def gacha_page(self):
        win = tk.Toplevel(self.root)
        win.title("희귀 아이템 뽑기")
        win.geometry("470x440")
        win.configure(bg=self.BG)
        win.transient(self.root)

        tk.Label(
            win, text="💎 희귀 아이템 뽑기", font=("맑은 고딕", 20, "bold"),
            fg="white", bg=self.BG
        ).pack(pady=16)
        gems_label = tk.Label(
            win, text=f"보유 보석: {self.gems}개", font=("맑은 고딕", 14, "bold"),
            fg="#67e8f9", bg=self.BG
        )
        gems_label.pack(pady=8)
        tk.Label(
            win, text="1회 뽑기: 보석 5개\n10회 뽑기: 보석 45개",
            font=("맑은 고딕", 11), fg="white", bg=self.BG
        ).pack(pady=8)
        result_label = tk.Label(
            win, text="뽑기 결과가 여기에 표시됩니다.",
            font=("맑은 고딕", 10), fg=self.GOLD, bg=self.BG,
            wraplength=420, justify="center"
        )
        result_label.pack(pady=12)

        def do_draw(count):
            results = self.draw_gacha(count, show_popup=False)
            gems_label.config(text=f"보유 보석: {self.gems}개")
            if results is not None:
                result_label.config(text="\n".join(results))

        self.make_button(win, "1회 뽑기 (5 보석)", lambda: do_draw(1), "#6d28d9").pack(pady=5)
        self.make_button(win, "10회 뽑기 (45 보석)", lambda: do_draw(10), "#7e22ce").pack(pady=5)
        self.make_button(win, "닫기", win.destroy, "#334155").pack(pady=12)

    def draw_gacha(self, count, show_popup=True):
        price = 5 if count == 1 else 45
        if self.gems < price:
            self.set_status(f"보석이 부족합니다. 뽑기에는 보석 {price}개가 필요합니다.")
            self.refresh()
            if show_popup:
                messagebox.showwarning("보석 부족", f"보석 {price}개가 필요합니다!")
            return None

        self.gems -= price
        items = [
            ("희귀한 보석", 40),
            ("전사의 반지", 25),
            ("마법의 목걸이", 20),
            ("불멸의 부적", 10),
            ("전설의 왕관", 5),
        ]
        results = []
        for _ in range(count):
            item = random.choices(
                [entry[0] for entry in items],
                weights=[entry[1] for entry in items],
                k=1,
            )[0]
            self.inventory.append(item)
            results.append(item)

        self.set_status(f"희귀 아이템 {count}개를 뽑았습니다!")
        self.refresh()
        if show_popup:
            messagebox.showinfo("뽑기 결과", "\n".join(results))
        return results

    # -------------------- 던전 정보 --------------------

    def dungeon_page(self):
        win = tk.Toplevel(self.root)
        win.title("던전 / 스테이지")
        win.geometry("480x390")
        win.configure(bg=self.BG)
        win.transient(self.root)

        tk.Label(
            win, text="🗺 던전 / 스테이지", font=("맑은 고딕", 20, "bold"),
            fg="white", bg=self.BG
        ).pack(pady=18)
        tk.Label(
            win,
            text=f"현재 스테이지: {self.stage}\n레벨: {self.level}\n무기: {self.weapon} +{self.weapon_level}\n갑옷: {self.armor}",
            font=("맑은 고딕", 12, "bold"), fg=self.GOLD, bg=self.BG,
            justify="center"
        ).pack(pady=10)
        tk.Label(
            win,
            text="일반 몬스터를 처치해 골드와 경험치를 모으세요.\n"
                 "보스를 처치하면 보석 5개를 얻고 다음 스테이지가 열립니다.",
            font=("맑은 고딕", 10), fg="white", bg=self.BG,
            justify="center"
        ).pack(pady=10)

        def begin_normal():
            win.destroy()
            self.start_battle()

        def begin_boss():
            win.destroy()
            self.start_boss()

        self.make_button(win, "일반 몬스터 찾기", begin_normal, "#166534").pack(pady=6)
        self.make_button(win, "보스 몬스터 도전", begin_boss, "#991b1b").pack(pady=6)
        self.make_button(win, "닫기", win.destroy, "#334155").pack(pady=10)

    # -------------------- 저장 / 불러오기 --------------------

    def save_game(self, show_message=True):
        data = {
            "version": 2,
            "coins": self.coins,
            "gems": self.gems,
            "power": self.power,
            "skin": self.skin,
            "owned_skins": self.owned_skins,
            "level": self.level,
            "xp": self.xp,
            "max_exp": self.max_exp,
            "base_hp": self.base_hp,
            "player_hp": self.player_hp,
            "potions": self.potions,
            "weapon": self.weapon,
            "weapon_level": self.weapon_level,
            "owned_weapons": self.owned_weapons,
            "armor": self.armor,
            "owned_armors": self.owned_armors,
            "inventory": self.inventory,
            "stage": self.stage,
        }
        try:
            SAVE_FILE.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            self.set_status(f"게임 저장 완료! 저장 위치: {SAVE_FILE}")
            if show_message:
                messagebox.showinfo("저장 완료", "게임 진행 상황을 저장했습니다!")
            self.refresh()
            return True
        except OSError as error:
            self.set_status(f"저장 실패: {error}")
            if show_message:
                messagebox.showerror("저장 오류", str(error))
            return False

    def _load_saved_data(self, silent=False):
        # 새 저장 파일이 없으면 이전 두 버전의 저장 파일도 찾아봅니다.
        candidates = [
            SAVE_FILE,
            Path.cwd() / "coin_hunter_rpg_save.json",
            Path.home() / ".coin_hunter_save.json",
        ]
        save_path = next((path for path in candidates if path.exists()), None)
        if save_path is None:
            return False

        try:
            data = json.loads(save_path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("저장 파일 형식이 올바르지 않습니다.")

            self.coins = max(0, int(data.get("coins", data.get("gold", self.coins))))
            self.gems = max(0, int(data.get("gems", self.gems)))
            self.power = max(1, int(data.get("power", self.power)))
            self.level = max(1, int(data.get("level", self.level)))
            self.xp = max(0, int(data.get("xp", data.get("exp", self.xp))))
            default_max_exp = self.level * 50 if "xp" in data and "max_exp" not in data else self.max_exp
            self.max_exp = max(1, int(data.get("max_exp", default_max_exp)))
            if "base_hp" in data:
                self.base_hp = max(1, int(data["base_hp"]))
            elif "player_max_hp" in data:
                self.base_hp = max(1, int(data["player_max_hp"]))
            self.potions = max(0, int(data.get("potions", self.potions)))
            self.stage = max(1, int(data.get("stage", self.stage)))

            skin = str(data.get("skin", self.skin))
            owned_skins = data.get("owned_skins", self.owned_skins)
            if not isinstance(owned_skins, list):
                owned_skins = ["기본 용사"]
            self.owned_skins = [str(item) for item in owned_skins]
            if "기본 용사" not in self.owned_skins:
                self.owned_skins.append("기본 용사")
            self.skin = skin if skin in self.owned_skins else "기본 용사"

            weapon = str(data.get("weapon", self.weapon))
            self.weapon = weapon if weapon in self.weapons else "나무 검"
            owned_weapons = data.get("owned_weapons", ["나무 검"])
            if not isinstance(owned_weapons, list):
                owned_weapons = ["나무 검"]
            self.owned_weapons = [name for name in owned_weapons if name in self.weapons]
            if "나무 검" not in self.owned_weapons:
                self.owned_weapons.insert(0, "나무 검")
            if self.weapon not in self.owned_weapons:
                self.weapon = "나무 검"
            self.weapon_level = max(0, min(10, int(data.get("weapon_level", 0))))

            armor = str(data.get("armor", self.armor))
            self.armor = armor if armor in self.armors else "낡은 갑옷"
            owned_armors = data.get("owned_armors", ["낡은 갑옷"])
            if not isinstance(owned_armors, list):
                owned_armors = ["낡은 갑옷"]
            self.owned_armors = [name for name in owned_armors if name in self.armors]
            if "낡은 갑옷" not in self.owned_armors:
                self.owned_armors.insert(0, "낡은 갑옷")
            if self.armor not in self.owned_armors:
                self.armor = "낡은 갑옷"

            inventory = data.get("inventory", [])
            self.inventory = [str(item) for item in inventory] if isinstance(inventory, list) else []
            saved_hp = data.get("player_hp", data.get("hp", self.max_hp()))
            self.player_hp = max(1, min(self.max_hp(), int(saved_hp)))

            self.battle_active = False
            self.enemy = None
            self.enemy_hp = 0
            self.enemy_max_hp = 0
            self.enemy_attack = 0
            self.is_boss = False
            self.status_text = f"저장된 게임을 불러왔습니다. ({save_path.name})"
            return True
        except (OSError, ValueError, TypeError, json.JSONDecodeError) as error:
            if not silent:
                messagebox.showerror("불러오기 오류", f"저장 파일을 읽지 못했습니다.\n{error}")
            self.status_text = f"불러오기 실패: {error}"
            return False

    def load_game(self):
        loaded = self._load_saved_data(silent=False)
        if not loaded:
            if not any(path.exists() for path in [
                SAVE_FILE,
                Path.cwd() / "coin_hunter_rpg_save.json",
                Path.home() / ".coin_hunter_save.json",
            ]):
                messagebox.showwarning("불러오기 실패", "저장된 게임 파일이 없습니다.")
                self.set_status("저장된 게임 파일이 없습니다.")
            self.refresh()
            return
        self.set_status("저장된 게임을 불러왔습니다!")
        self.refresh()

    def reset_game(self):
        if not messagebox.askyesno("게임 초기화", "모든 진행 상황을 초기화할까요?"):
            return

        self.coins = 100
        self.gems = 10
        self.power = 1
        self.level = 1
        self.xp = 0
        self.max_exp = 50
        self.base_hp = 100
        self.player_hp = 100
        self.potions = 5
        self.skin = "기본 용사"
        self.owned_skins = ["기본 용사"]
        self.weapon = "나무 검"
        self.weapon_level = 0
        self.owned_weapons = ["나무 검"]
        self.armor = "낡은 갑옷"
        self.owned_armors = ["낡은 갑옷"]
        self.inventory = []
        self.stage = 1
        self.enemy = None
        self.enemy_hp = 0
        self.enemy_max_hp = 0
        self.enemy_attack = 0
        self.battle_active = False
        self.is_boss = False
        self.enemy_name.config(text="몬스터를 찾아보세요!")
        self.enemy_art.config(text="❔")
        self.set_status("초기화 완료! 새로운 모험을 시작하세요!")
        self.refresh()
        self.save_game(show_message=False)

    def close_game(self):
        self.save_game(show_message=False)
        self.root.destroy()

    # -------------------- 화면 갱신 --------------------

    def refresh(self):
        self.coin_label.config(text=f"🪙 {self.coins:,}")
        self.gem_label.config(text=f"💎 {self.gems:,}")
        self.level_label.config(text=f"LV. {self.level}")
        self.power_label.config(text=f"클릭당 골드: {self.power}")
        self.skin_label.config(text=self.skin)
        self.character.config(text=self.skin_icons.get(self.skin, "🧙"))
        self.player_hp_label.config(text=f"내 HP: {self.player_hp} / {self.max_hp()}")
        self.draw_bar(self.player_bar, self.player_hp, self.max_hp(), self.GREEN)
        self.stage_label.config(text=f"현재 스테이지: {self.stage}")

        if self.enemy is not None:
            self.enemy_hp_label.config(text=f"몬스터 HP: {self.enemy_hp} / {self.enemy_max_hp}")
            self.draw_bar(self.enemy_bar, self.enemy_hp, self.enemy_max_hp, self.RED)
        else:
            self.enemy_hp_label.config(text="몬스터 HP: -")
            self.draw_bar(self.enemy_bar, 0, 1, self.RED)

        self.attack_button.config(state="normal" if self.battle_active else "disabled")
        self.potion_button.config(
            state="normal" if self.battle_active and self.potions > 0 else "disabled"
        )
        self.start_button.config(state="disabled" if self.battle_active else "normal")
        self.boss_button.config(state="disabled" if self.battle_active else "normal")
        self.status.config(text=self.status_text)


if __name__ == "__main__":
    root = tk.Tk()
    app = CoinHunterRPG(root)
    root.mainloop()
