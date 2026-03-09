from dataclasses import dataclass

from BaseClasses import ItemClassification


@dataclass(frozen=True)
class WikipelagoItemData:
    code: int
    classification: ItemClassification


ITEM_OFFSET = 1_870_000

item_table: dict[str, WikipelagoItemData] = {
    "Knowledge Fragment": WikipelagoItemData(ITEM_OFFSET + 1, ItemClassification.progression),
    "Back Button": WikipelagoItemData(ITEM_OFFSET + 2, ItemClassification.useful),
    "Wiki Compass": WikipelagoItemData(ITEM_OFFSET + 3, ItemClassification.useful),
    "Ctrl+F Lens": WikipelagoItemData(ITEM_OFFSET + 4, ItemClassification.useful),
    "Victory": WikipelagoItemData(ITEM_OFFSET + 5, ItemClassification.progression_skip_balancing),
    "Footnote": WikipelagoItemData(ITEM_OFFSET + 6, ItemClassification.filler),
    "Round Access": WikipelagoItemData(ITEM_OFFSET + 7, ItemClassification.progression),
}
