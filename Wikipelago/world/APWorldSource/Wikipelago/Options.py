from dataclasses import dataclass

from Options import Choice, PerGameCommonOptions, Range, Toggle


class CheckCount(Range):
    display_name = "Round Count"
    range_start = 10
    range_end = 5000
    default = 100


class RequiredFragments(Range):
    display_name = "Required Fragments"
    range_start = 1
    range_end = 5000
    default = 8


class StartRoundsUnlocked(Range):
    display_name = "Start Rounds Unlocked"
    range_start = 1
    range_end = 100
    default = 5


class RoundsPerUnlock(Range):
    display_name = "Rounds Per Round Access"
    range_start = 1
    range_end = 25
    default = 5


class RandomGoalArticle(Toggle):
    display_name = "Random Goal Article"
    default = 0


class GoalArticlePreset(Choice):
    display_name = "Goal Article Preset (used when random goal is off)"
    option_minecraft = 0
    option_the_legend_of_zelda = 1
    option_dark_souls = 2
    option_elden_ring = 3
    option_super_mario_bros = 4
    option_pokemon_red_and_blue = 5
    option_chess = 6
    option_catan = 7
    option_the_dark_knight = 8
    option_star_wars_film = 9
    option_lord_of_the_rings_fellowship = 10
    option_the_matrix = 11
    option_avatar_the_last_airbender = 12
    option_breaking_bad = 13
    option_stranger_things = 14
    option_game_of_thrones = 15
    option_the_simpsons = 16
    option_spongebob_squarepants = 17
    option_super_smash_bros_ultimate = 18
    option_halo_combat_evolved = 19
    default = 0


@dataclass
class WikipelagoOptions(PerGameCommonOptions):
    check_count: CheckCount
    required_fragments: RequiredFragments
    start_rounds_unlocked: StartRoundsUnlocked
    rounds_per_unlock: RoundsPerUnlock
    random_goal_article: RandomGoalArticle
    goal_article_preset: GoalArticlePreset
