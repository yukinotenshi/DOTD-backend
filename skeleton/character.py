from model import User


class BaseCharacter:
    def __init__(self, player, name, skill):
        self.player = player
        self.name = name
        self.skill = skill

    def calc_skill_value(self):
        return 5.00 + (0.1 * self.player.level)


class Police(BaseCharacter):
    def __init__(self, player):
        super().__init__(player, "Police", "Sirine")


class Drunk(BaseCharacter):
    def __init__(self, player):
        super().__init__(player, "Drunk", "Beer Throwing")


class DebtCollector(BaseCharacter):
    def __init__(self, player):
        super().__init__(player, "Debt Collector", "Underground Intel")


class Trickster(BaseCharacter):
    def __init__(self, player):
        super().__init__(player, "Trickster", "Evasion")

    def calc_skill_value(self):
        return 0.25 + (0.05 * self.player.level)


characters_class = {
    "Police": Police,
    "Drunk": Drunk,
    "Debt Collector": DebtCollector,
    "Trickster": Trickster,
}

chasing_characters = ["Police", "Debt Collector"]

hiding_characters = ["Drunk", "Trickster"]
