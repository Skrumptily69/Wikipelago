from dataclasses import dataclass

from Options import Choice, PerGameCommonOptions, Range, Toggle


class CheckCount(Range):
    display_name = "Round Count"
    range_start = 10
    range_end = 5000
    default = 50


class RequiredFragments(Range):
    display_name = "Required Fragments"
    range_start = 1
    range_end = 5000
    default = 8


class StartRoundsUnlocked(Range):
    display_name = "Start Rounds Unlocked"
    range_start = 1
    range_end = 100
    default = 8


class RoundsPerUnlock(Range):
    display_name = "Rounds Per Round Access"
    range_start = 1
    range_end = 25
    default = 5


class RandomGoalArticle(Toggle):
    display_name = "Random Goal Article"
    default = 0


class IncludeVideoGames(Toggle):
    display_name = "Include Video Games"
    default = 1


class IncludeBoardGames(Toggle):
    display_name = "Include Board Games"
    default = 1


class IncludeMovies(Toggle):
    display_name = "Include Movies"
    default = 1


class IncludeTVShows(Toggle):
    display_name = "Include TV Shows"
    default = 1


class IncludeAnimeManga(Toggle):
    display_name = "Include Anime and Manga"
    default = 1


class IncludeSports(Toggle):
    display_name = "Include Sports"
    default = 1


class IncludeScienceSpace(Toggle):
    display_name = "Include Science and Space"
    default = 1


class IncludeTechnology(Toggle):
    display_name = "Include Technology and Internet"
    default = 1


class IncludeHistory(Toggle):
    display_name = "Include History"
    default = 1


class IncludeGeography(Toggle):
    display_name = "Include Geography and Landmarks"
    default = 1


class IncludeFoodCuisine(Toggle):
    display_name = "Include Food and Cuisine"
    default = 1


class IncludeArtLiterature(Toggle):
    display_name = "Include Art and Literature"
    default = 1


class IncludeMythologyFolklore(Toggle):
    display_name = "Include Mythology and Folklore"
    default = 1


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
    default = 2


@dataclass
class WikipelagoOptions(PerGameCommonOptions):
    check_count: CheckCount
    required_fragments: RequiredFragments
    start_rounds_unlocked: StartRoundsUnlocked
    rounds_per_unlock: RoundsPerUnlock
    random_goal_article: RandomGoalArticle
    include_video_games: IncludeVideoGames
    include_board_games: IncludeBoardGames
    include_movies: IncludeMovies
    include_tv_shows: IncludeTVShows
    include_anime_manga: IncludeAnimeManga
    include_sports: IncludeSports
    include_science_space: IncludeScienceSpace
    include_technology: IncludeTechnology
    include_history: IncludeHistory
    include_geography: IncludeGeography
    include_food_cuisine: IncludeFoodCuisine
    include_art_literature: IncludeArtLiterature
    include_mythology_folklore: IncludeMythologyFolklore
    goal_article_preset: GoalArticlePreset
