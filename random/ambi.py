import requests
from pathlib import Path


players = [
    "Quizky",
    "BompkinFTW",
    "Neleo_",
    "Starchomper",
    "A__Mango",
    "AllAdvancements",
    "Qmbi",
    "Bribition",
    "Burawoy",
    "Lenged",
    "Akimaster",
    "Danterus",
    "Yisuntauri",
    "BurgerReviewerr",
    "DVRG_",
    "Tssal",
    "Saltron_mp4",
    "L9_JAKEINGITTOBR",
    "oWinny",
    "Benemies",
    "Redandblack1832",
    "Buzzaboo",
    "PalestineNoodles",
    "Goreay",
    "Spacse",
    "_hpx",
    "Goldam",
    "Whislored",
    "Sfren",
    "Frigbob",
    "MaybeSoul",
    "Yubbawubba8",
    "MuhammadPro5741",
    "Iluvcobblestone",
    "N0tJim",
    "Gradientgray",
    "Linksbasher",
    "Aquacorde",
    "Magmania",
    "Snowdeerjulie",
    "SuperC_",
    "Prince_01",
    "Bbiddd",
    "_pizu",
    "NOHACKSJUSTTIGER",
    "Nottantoo",
    "Czelco",
    "thecamo6",
    "kohout135",
    "Dolqhin",
]


ASSETS_DIR = Path(__file__).parent / "assets"


for player in players:
    resp = requests.get(f"https://mc-heads.net/avatar/{player}/128")
    with open(ASSETS_DIR / f"{player}.png", "wb") as f:
        f.write(resp.content)
