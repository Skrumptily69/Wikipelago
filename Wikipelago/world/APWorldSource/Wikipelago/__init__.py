from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from typing import Any

from BaseClasses import Item, Location
from worlds.AutoWorld import WebWorld, World
from worlds.generic.Rules import set_rule

from .entertainment_articles import ENTERTAINMENT_ARTICLE_POOL
from .Items import item_table
from .Locations import location_table
from .Options import WikipelagoOptions
from .Regions import create_regions


WIKI_API = "https://en.wikipedia.org/w/api.php"

STOPWORDS: set[str] = {
    "the", "a", "an", "and", "or", "of", "in", "on", "to", "for", "by", "with",
    "at", "from", "into", "about", "after", "before", "over", "under", "new",
}

BANNED_TITLE_KEYWORDS: tuple[str, ...] = (
    "gun",
    "rifle",
    "pistol",
    "shotgun",
    "revolver",
    "machine gun",
    "submachine gun",
    "song",
    "single",
    "album",
    "discography",
    "president",
    "prime minister",
    "king of",
    "queen of",
    "emperor",
    "sultan",
    "chancellor",
    "chemistry",
    "chemical",
    "compound",
    "acid",
    "molecule",
    "molecular",
    "atom",
    "isotope",
    "reaction",
    "periodic table",
    "organic chemistry",
    "inorganic chemistry",
)

BANNED_TITLE_SUFFIXES: tuple[str, ...] = (
    "(programming language)",
    "(operating system)",
    "(software)",
    "(computer)",
)

BANNED_EXACT_TITLES: set[str] = {
    "George Washington",
    "Abraham Lincoln",
    "Theodore Roosevelt",
    "Franklin D. Roosevelt",
    "John F. Kennedy",
    "Winston Churchill",
    "Napoleon",
    "Julius Caesar",
    "Cleopatra",
    "Genghis Khan",
    "Alexander the Great",
}

TOPIC_KEYWORDS: dict[str, tuple[str, ...]] = {
    "video_games": ("game", "mario", "zelda", "pokemon", "halo", "souls", "ring", "minecraft"),
    "board_games": ("board game", "card game", "chess", "catan", "mahjong", "poker", "dungeons"),
    "movies": ("film", "movie", "avengers", "star wars", "godfather", "matrix", "dark knight"),
    "tv_shows": ("tv", "series", "show", "breaking bad", "simpsons", "spongebob", "stranger things"),
}

TOPIC_NEIGHBORS: dict[str, set[str]] = {
    "video_games": {"board_games", "movies", "tv_shows"},
    "board_games": {"video_games", "movies"},
    "movies": {"tv_shows", "video_games", "board_games"},
    "tv_shows": {"movies", "video_games"},
}

GAMING_BOOST: list[str] = [
    "Video game",
    "Game design",
    "First-person shooter",
    "Open world",
    "Esports",
    "Nintendo",
    "PlayStation",
    "Xbox",
    "Steam (service)",
    "Unreal Engine",
    "Unity (game engine)",
    "Minecraft",
    "Fortnite",
    "League of Legends",
    "Dota 2",
    "Valorant",
    "Overwatch",
    "Rocket League",
    "The Legend of Zelda",
    "Super Mario",
    "Pokemon",
    "Sonic the Hedgehog",
    "Final Fantasy",
    "Tetris",
    "Pac-Man",
]


def _preset_goal_name(option_value: int) -> str:
    mapping = {
        0: "Minecraft",
        1: "The Legend of Zelda",
        2: "Dark Souls",
        3: "Elden Ring",
        4: "Super Mario Bros.",
        5: "Pokemon Red and Blue",
        6: "Chess",
        7: "Catan",
        8: "The Dark Knight",
        9: "Star Wars (film)",
        10: "The Lord of the Rings: The Fellowship of the Ring",
        11: "The Matrix",
        12: "Avatar: The Last Airbender",
        13: "Breaking Bad",
        14: "Stranger Things",
        15: "Game of Thrones",
        16: "The Simpsons",
        17: "SpongeBob SquarePants",
        18: "Super Smash Bros. Ultimate",
        19: "Halo: Combat Evolved",
    }
    return mapping.get(option_value, "Minecraft")


class WikipelagoWeb(WebWorld):
    theme = "stone"


class WikipelagoItem(Item):
    game = "Wikipelago"


class WikipelagoLocation(Location):
    game = "Wikipelago"


class WikipelagoWorld(World):
    game = "Wikipelago"
    web = WikipelagoWeb()

    options_dataclass = WikipelagoOptions
    options: WikipelagoOptions

    item_name_to_id = {name: data.code for name, data in item_table.items()}
    location_name_to_id = {name: data.code for name, data in location_table.items()}

    item_class = WikipelagoItem
    location_class = WikipelagoLocation

    round_pairs: list[dict[str, str]]
    goal_article: str

    def _try_expand_pool(self, pool: list[str], required_size: int) -> list[str]:
        if len(pool) >= required_size:
            return pool

        seen = set(pool)
        token: str | None = None

        while len(pool) < required_size:
            params = {
                "action": "query",
                "list": "allpages",
                "apnamespace": "0",
                "apfilterredir": "nonredirects",
                "aplimit": "500",
                "format": "json",
            }
            if token:
                params["apcontinue"] = token

            url = f"{WIKI_API}?{urllib.parse.urlencode(params)}"
            try:
                with urllib.request.urlopen(url, timeout=10) as response:
                    payload = json.loads(response.read().decode("utf-8"))
            except Exception:
                break

            pages = payload.get("query", {}).get("allpages", [])
            for page in pages:
                title = str(page.get("title", "")).strip()
                if (
                    not title
                    or title in seen
                    or not self._is_reasonable_title(title)
                    or not self._looks_common_knowledge(title)
                ):
                    continue
                seen.add(title)
                pool.append(title)
                if len(pool) >= required_size:
                    break

            token = payload.get("continue", {}).get("apcontinue")
            if not token:
                break

        return pool

    @staticmethod
    def _is_reasonable_title(title: str) -> bool:
        if len(title) < 3 or len(title) > 120:
            return False
        if "$" in title:
            return False
        if not re.search(r"[A-Za-z]", title):
            return False
        if re.search(r"^[^A-Za-z0-9]+$", title):
            return False
        return True


    @staticmethod
    def _looks_common_knowledge(title: str) -> bool:
        lowered = title.lower().strip()
        if title in BANNED_EXACT_TITLES:
            return False
        if lowered.startswith(
            (
                "list of ",
                "outline of ",
                "timeline of ",
                "index of ",
                "category:",
                "template:",
                "help:",
                "portal:",
            )
        ):
            return False
        if any(keyword in lowered for keyword in BANNED_TITLE_KEYWORDS):
            return False
        if any(lowered.endswith(suffix) for suffix in BANNED_TITLE_SUFFIXES):
            return False
        if any(ch in title for ch in ('"', "$", "%", "&", "@", "#")):
            return False
        if ":" in title or title.count(",") > 1:
            return False
        if re.search(r"^\d", title):
            return False
        if re.search(
            r"\((disambiguation|album|song|single|magazine|journal)\)$",
            lowered,
        ):
            return False
        if len(title.split()) > 6:
            return False
        if re.search(r"[A-Za-z].*\d.*\d.*\d", title):
            return False
        return True
    @staticmethod
    def _title_tokens(title: str) -> set[str]:
        tokens = {tok for tok in re.findall(r"[A-Za-z]+", title.lower()) if len(tok) > 2}
        return {tok for tok in tokens if tok not in STOPWORDS}
    def _infer_topic(self, title: str) -> str:
        lowered = title.lower()
        for topic, keywords in TOPIC_KEYWORDS.items():
            if any(keyword in lowered for keyword in keywords):
                return topic
        return "society"

    def _is_doable_pair(self, start: str, target: str) -> bool:
        s_topic = self._infer_topic(start)
        t_topic = self._infer_topic(target)
        if s_topic == t_topic:
            return True
        return t_topic in TOPIC_NEIGHBORS.get(s_topic, set())
    def _is_challenging_pair(self, start: str, target: str) -> bool:
        if start == target:
            return False
        sl = start.lower()
        tl = target.lower()
        if sl in tl or tl in sl:
            return False
        s_tokens = self._title_tokens(start)
        t_tokens = self._title_tokens(target)
        if s_tokens and t_tokens and s_tokens.intersection(t_tokens):
            return False
        return True
    def generate_early(self) -> None:
        round_count = self.options.check_count.value

        pool = list(dict.fromkeys(ENTERTAINMENT_ARTICLE_POOL))

        filtered_pool = [
            title
            for title in pool
            if self._is_reasonable_title(title) and self._looks_common_knowledge(title)
        ]

        needed_total = max(2, round_count * 2)
        if len(filtered_pool) < needed_total:
            raise Exception(
                "Wikipelago entertainment-only mode failed: "
                f"need at least {needed_total} unique titles for {round_count} rounds, "
                f"but only have {len(filtered_pool)} after filters."
            )

        if self.options.random_goal_article.value:
            self.goal_article = self.random.choice(filtered_pool)
        else:
            self.goal_article = _preset_goal_name(self.options.goal_article_preset.value)
            if self.goal_article not in filtered_pool:
                filtered_pool.append(self.goal_article)

        remaining = [title for title in filtered_pool if title != self.goal_article]
        needed_non_goal = max(0, (2 * round_count) - 1)

        if len(remaining) < needed_non_goal:
            raise Exception(
                "Wikipelago strict no-repeat mode failed: "
                f"need {needed_non_goal + 1} unique articles total for {round_count} rounds "
                f"(including goal), but pool has {len(remaining) + 1}. "
                "Increase article pool or lower check_count."
            )

        picks = self.random.sample(remaining, needed_non_goal)
        non_final_targets = picks[: round_count - 1]
        base_starts = picks[round_count - 1 :]

        targets = non_final_targets + [self.goal_article]
        unused_starts = list(base_starts)
        pairs: list[dict[str, str]] = []

        for target in targets:
            challenging_and_doable = [
                start for start in unused_starts
                if self._is_doable_pair(start, target) and self._is_challenging_pair(start, target)
            ]
            doable_only = [
                start for start in unused_starts
                if self._is_doable_pair(start, target)
            ]
            challenging_only = [
                start for start in unused_starts
                if self._is_challenging_pair(start, target)
            ]

            candidates = challenging_and_doable or doable_only or challenging_only or unused_starts
            start_choice = self.random.choice(candidates)
            unused_starts.remove(start_choice)
            pairs.append({"start": start_choice, "target": target})

        self.round_pairs = pairs

    def create_regions(self) -> None:
        create_regions(self)

    def create_item(self, name: str) -> WikipelagoItem:
        data = item_table[name]
        return self.item_class(name, data.classification, data.code, self.player)

    def create_items(self) -> None:
        round_count = self.options.check_count.value
        required_fragments = min(self.options.required_fragments.value, round_count)
        start_unlocked = min(self.options.start_rounds_unlocked.value, round_count)
        per_unlock = max(1, self.options.rounds_per_unlock.value)
        early_open = start_unlocked

        round_access_count = max(0, (round_count - early_open + per_unlock - 1) // per_unlock)

        mandatory_items = required_fragments + 3 + round_access_count
        if mandatory_items > round_count:
            raise Exception(
                "Wikipelago item math invalid: required progression items exceed round locations. "
                f"mandatory={mandatory_items}, round_locations={round_count}. "
                "Lower required_fragments or round_access pressure (increase start_rounds_unlocked / rounds_per_unlock)."
            )

        pool: list[WikipelagoItem] = []
        for _ in range(required_fragments):
            pool.append(self.create_item("Knowledge Fragment"))

        pool.append(self.create_item("Back Button"))
        pool.append(self.create_item("Wiki Compass"))
        pool.append(self.create_item("Ctrl+F Lens"))

        for _ in range(round_access_count):
            pool.append(self.create_item("Round Access"))

        while len(pool) < round_count:
            pool.append(self.create_item("Footnote"))

        self.multiworld.itempool.extend(pool)

        grand_goal = self.multiworld.get_location("Grand Goal", self.player)
        grand_goal.place_locked_item(self.create_item("Victory"))

    def set_rules(self) -> None:
        round_count = self.options.check_count.value
        required_fragments = min(self.options.required_fragments.value, round_count)
        start_unlocked = min(self.options.start_rounds_unlocked.value, round_count)
        per_unlock = max(1, self.options.rounds_per_unlock.value)
        early_open = start_unlocked

        goal_round_access = max(0, (round_count - start_unlocked + per_unlock - 1) // per_unlock)

        goal_location = self.multiworld.get_location("Grand Goal", self.player)
        set_rule(
            goal_location,
            lambda state, frag_need=required_fragments, ra_need=goal_round_access: (
                state.has("Knowledge Fragment", self.player, frag_need)
                and state.has("Round Access", self.player, ra_need)
            ),
        )

        for round_index in range(1, round_count + 1):
            location = self.multiworld.get_location(f"Round {round_index} Complete", self.player)
            extra_rounds = max(0, round_index - early_open)
            needed_round_access = (extra_rounds + per_unlock - 1) // per_unlock
            set_rule(
                location,
                lambda state, need=needed_round_access: state.has("Round Access", self.player, need),
            )

        self.multiworld.completion_condition[self.player] = (
            lambda state: state.has("Victory", self.player)
        )

    def fill_slot_data(self) -> dict[str, Any]:
        round_count = self.options.check_count.value
        required_fragments = min(self.options.required_fragments.value, round_count)
        start_unlocked = min(self.options.start_rounds_unlocked.value, round_count)
        per_unlock = max(1, self.options.rounds_per_unlock.value)

        round_location_ids = [
            self.location_name_to_id[f"Round {index} Complete"]
            for index in range(1, round_count + 1)
        ]

        return {
            "check_count": round_count,
            "required_fragments": required_fragments,
            "start_rounds_unlocked": start_unlocked,
            "rounds_per_unlock": per_unlock,
            "goal_required_round_access": max(0, (round_count - start_unlocked + per_unlock - 1) // per_unlock),
            "goal_article": self.goal_article,
            "round_pairs": self.round_pairs,
            "location_ids": {
                "rounds": round_location_ids,
                "grand_goal": self.location_name_to_id["Grand Goal"],
            },
            "item_ids": {name: data.code for name, data in item_table.items()},
        }




































