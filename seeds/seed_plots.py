import json
import math
import os
from functools import lru_cache
from pathlib import Path
import sys

from manim import *
from rankedutils import numb

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"

# Must match seed_map.py
IRON_STEP = 2000
IRON_CAP = 120000
FORT_STEP = 5000
FORT_CAP = 600000
DISCOVERY_STEP = 1000

MIN_O_LEVEL_SEEDS = 100
MIN_SCORE_COMPLETIONS = 5
MIN_REPEAT_BIN_PLAYERS = 20
MIN_COMPLETION_BIN_SEEDS = 20
REPEAT_BIN = 20
REPEAT_MAX_PLAYS = 1000

OVERWORLDS = ("BURIED_TREASURE", "DESERT_TEMPLE", "RUINED_PORTAL", "SHIPWRECK", "VILLAGE")
SHIP_TYPES = ("full", "normal", "sideways", "upsidedown")
FORTRESS_BIOMES = ("basalt_deltas", "crimson_forest", "nether_wastes", "soul_sand_valley", "warped_forest")
BASTIONS = ("STABLES", "BRIDGE", "HOUSING")
BASTION_KEYS = ("triples", "singles", "small_singles")


# ---------------------------------------------------------------- data
@lru_cache(maxsize=None)
def load(name):
    with open(DATA_DIR / f"{name}.json", "r") as f:
        return json.load(f)


def pretty(name):
    return name.replace("_", " ").title()


def digital(ms):
    return numb.digital_time(int(ms))


def bins(dist):
    return {key: value for key, value in dist.items() if key != "avg"}


def percentages(dist, categories):
    total = sum(bins(dist).values())
    return [100 * dist.get(str(category), 0) / total for category in categories]


def merge(dists):
    merged = {}
    for dist in dists:
        for key, value in bins(dist).items():
            merged[key] = merged.get(key, 0) + value
    return merged


def average_of(dist):
    return dist["avg"] if "avg" in dist else None


# ---------------------------------------------------------------- chart helpers
def nice_range(max_value):
    raw = max_value / 5
    magnitude = 10 ** math.floor(math.log10(raw))
    step = next(m * magnitude for m in (1, 2, 5, 10) if m * magnitude >= raw)
    top = math.ceil(max_value / step) * step
    return [0, top, step]


def tex_labels(chart, x_title, y_title):
    _, y_label = chart.get_axis_labels(Tex(x_title).scale(0.5), Tex(y_title).scale(0.5))
    x_label = Tex(x_title).scale(0.5).next_to(chart, DOWN, buff=0.25)
    return VGroup(x_label, y_label)


def histogram_chart(values, names, y_rng, x_title, y_title=r"Share (\%)"):
    chart = BarChart(
        values,
        bar_names=names,
        y_range=y_rng,
        x_length=12,
        y_length=4.5,
        bar_width=1,
        bar_stroke_width=0.5,
        axis_config={"font_size": 16},
    )
    chart.shift(DOWN * 0.4)
    half_bar = chart.bars[0].width / 2
    [name.shift(LEFT * half_bar) for name in chart.x_axis.labels]
    return chart, tex_labels(chart, x_title, y_title)


def shrink_names(chart, scale=0.55):
    [name.scale(scale) for name in chart.x_axis.labels]


def category_chart(names, values, y_rng, x_title, y_title=r"Share (\%)", width=10, label_fmt=None, bar_width=0.6):
    chart = BarChart(
        values,
        bar_names=names,
        y_range=y_rng,
        x_length=width,
        y_length=4.5,
        bar_width=bar_width,
        axis_config={"font_size": 20},
        x_axis_config={"label_constructor": Text},
    )
    shrink_names(chart)
    chart.shift(DOWN * 0.4)
    labels = tex_labels(chart, x_title, y_title)
    return chart, labels


def value_labels(chart, values, fmt):
    return VGroup(*[
        Text(fmt(value), font_size=18).next_to(bar, UP, buff=0.1)
        for value, bar in zip(values, chart.bars)
    ])


def line_through(axes, xs, ys, color, width=4):
    line = VMobject(color=color, stroke_width=width)
    line.set_points_as_corners([axes.c2p(x, y) for x, y in zip(xs, ys)])
    return line


class SeedScene(Scene):

    def setup(self):
        Text.set_default(font="Minecraft")

    @staticmethod
    def make_title(text):
        return Text(text, font_size=24).move_to(UP * 3.3)

    @staticmethod
    def make_note(text):
        return Text(text, font_size=18).move_to(UP * 2.8)

    def play_stages(self, chart, axis_labels, stages, label_fmt=None, hold=1.5):
        title = self.make_title(stages[0]["title"])
        note = self.make_note(stages[0]["note"]) if stages[0].get("note") else None

        self.play(Write(title))
        self.play(Write(chart), Write(axis_labels))
        if note:
            self.play(FadeIn(note))
        labels = None
        if label_fmt:
            labels = value_labels(chart, stages[0]["values"], label_fmt)
            self.play(FadeIn(labels))
        self.wait(hold)

        for stage in stages[1:]:
            animations = [
                Transform(title, self.make_title(stage["title"])),
                chart.animate.change_bar_values(stage["values"]),
            ]
            if note:
                animations.append(Transform(note, self.make_note(stage["note"])))
            if labels:
                animations.append(FadeOut(labels))
            self.play(*animations)
            if label_fmt:
                labels = value_labels(chart, stage["values"], label_fmt)
                self.play(FadeIn(labels))
            self.wait(hold)

    def play_groups(self, stages, hold=1.5):
        title = self.make_title(stages[0][0])
        group = stages[0][1]
        self.play(Write(title))
        self.play(Write(group))
        self.wait(hold)
        for new_title, new_group in stages[1:]:
            self.play(Transform(title, self.make_title(new_title)), FadeTransform(group, new_group))
            group = new_group
            self.wait(hold)


def category_group(names, values, y_rng, x_title, y_title, label_fmt, **kwargs):
    chart, labels = category_chart(names, values, y_rng, x_title, y_title, **kwargs)
    return VGroup(chart, labels, value_labels(chart, values, label_fmt))


# ---------------------------------------------------------------- biomes
class BiomeDistribution(SeedScene):

    def construct(self):
        dists = load("distributions")
        bastion = percentages(dists["bastion_biomes"], FORTRESS_BIOMES)
        fortress = percentages(dists["fortress_biomes"], FORTRESS_BIOMES)

        y_rng = nice_range(max(bastion + fortress))
        chart, labels = category_chart([pretty(b) for b in FORTRESS_BIOMES], bastion, y_rng, "Biome", r"Share of seeds (\%)")
        stages = [
            {"title": "Bastion Biome Distribution", "values": bastion},
            {"title": "Fortress Biome Distribution", "values": fortress},
        ]
        self.play_stages(chart, labels, stages, label_fmt=lambda v: f"{v:.1f}%")


class VillageBiomes(SeedScene):

    def construct(self):
        dist = load("distributions")["village_biomes"]
        biomes = sorted(dist, key=lambda b: -dist[b])
        values = percentages(dist, biomes)

        chart, labels = category_chart(
            [pretty(b) for b in biomes], values, nice_range(max(values)),
            "Biome", r"Share of village seeds (\%)"
        )
        self.play_stages(chart, labels, [{"title": "Village Biome Distribution", "values": values}], label_fmt=lambda v: f"{v:.1f}%")


# ---------------------------------------------------------------- seed counts
class PlaycountDistribution(SeedScene):

    def construct(self):
        dist = load("distributions")["seed_playcount_distribution"]
        plays = range(1, max(int(k) for k in dist) + 1)
        values = percentages(dist, plays)

        chart, labels = histogram_chart(
            values,
            [str(p) if p % 10 == 0 else "" for p in plays],
            nice_range(max(values)),
            "Times Seed Was Rolled", r"Share of seeds (\%)"
        )
        [name.shift(RIGHT * chart.bars[0].width / 2) for name in chart.x_axis.labels]
        self.play_stages(chart, labels, [{"title": "Seed Play Count Distribution", "values": values}])


class OLevelDistribution(SeedScene):

    def construct(self):
        dist = {k: v for k, v in load("distributions")["o_level_distribution"].items() if k != "null"}
        levels = range(min(int(k) for k in dist), max(int(k) for k in dist) + 1)
        values = percentages(dist, levels)

        chart, labels = histogram_chart(
            values,
            [str(level) if level % 4 == 0 else "" for level in levels],
            nice_range(max(values)),
            "Overworld Level", r"Share of seeds (\%)"
        )
        [name.shift(RIGHT * chart.bars[0].width / 2) for name in chart.x_axis.labels]
        self.play_stages(chart, labels, [{"title": "Overworld Level Distribution", "values": values}])


class BastionVariants(SeedScene):

    def construct(self):
        dists = load("distributions")["bastion_distribution"]
        categories = ("null", "1", "2", "3")
        names = ["None", "1", "2", "3"]

        def stage_values(key):
            return {b: percentages(dists[b][key], categories) for b in BASTIONS}

        stages = {key: stage_values(key) for key in BASTION_KEYS}
        y_rng = [0, 100, 20]

        charts = VGroup()
        headings = VGroup()
        for bastion in BASTIONS:
            chart = BarChart(
                stages["triples"][bastion],
                bar_names=names,
                y_range=y_rng,
                x_length=3.4,
                y_length=3.5,
                axis_config={"font_size": 14},
                x_axis_config={"label_constructor": Text},
            )
            charts.add(chart)
        for chart in charts:
            shrink_names(chart)
        charts.arrange(RIGHT, buff=0.9).shift(DOWN * 0.5)
        heading_y = charts[0].y_axis.get_top()[1] + 0.4
        for bastion, chart in zip(BASTIONS, charts):
            heading = Text(pretty(bastion), font_size=20)
            headings.add(heading.move_to([chart.x_axis.get_center()[0], heading_y, 0]))

        def title(key):
            return f"Bastion {key.replace('_', ' ').title()} Distribution"

        title_text = self.make_title(title("triples"))
        y_label = Tex(r"Share of seeds (\%)").scale(0.5).next_to(charts, DOWN, buff=0.4)

        self.play(Write(title_text))
        self.play(Write(charts), Write(headings), Write(y_label))
        self.wait(1.5)
        for key in BASTION_KEYS[1:]:
            self.play(
                Transform(title_text, self.make_title(title(key))),
                *[
                    chart.animate.change_bar_values(stages[key][bastion])
                    for bastion, chart in zip(BASTIONS, charts)
                ]
            )
            self.wait(1.5)


# ---------------------------------------------------------------- iron
def iron_stages(entries):
    bands = list(range(0, IRON_CAP, IRON_STEP))
    stages = []
    for title, dist in entries:
        stage = {"title": title, "values": percentages(dist, bands)}
        avg = average_of(dist)
        stage["note"] = f"Average: {digital(avg)}" if avg is not None else "Average: -"
        stages.append(stage)
    return bands, stages


def iron_histogram(bands, stages):
    y_rng = nice_range(max(max(stage["values"]) for stage in stages))
    return histogram_chart(
        stages[0]["values"],
        [digital(band) if i % 5 == 0 else "" for i, band in enumerate(bands)],
        y_rng,
        "Time to Smelt Iron", r"Share of runs (\%)"
    )


class IronDistribution(SeedScene):

    def construct(self):
        dists = load("distributions")
        entries = [("Iron Acquisition Time - All Overworlds", dists["iron_distribution"])]
        entries += [(f"Iron Acquisition Time - {pretty(ow)}", dists["iron_overworld"][ow]) for ow in OVERWORLDS]
        bands, stages = iron_stages(entries)
        chart, labels = iron_histogram(bands, stages)
        self.play_stages(chart, labels, stages)


class IronShipwreck(SeedScene):

    def construct(self):
        dists = load("distributions")
        entries = [("Iron Acquisition Time - Shipwreck", dists["iron_overworld"]["SHIPWRECK"])]
        entries += [(f"Iron Acquisition Time - {pretty(s)} Shipwreck", dists["iron_shipwreck"][s]) for s in SHIP_TYPES]
        bands, stages = iron_stages(entries)
        chart, labels = iron_histogram(bands, stages)
        self.play_stages(chart, labels, stages)


class IronAverages(SeedScene):

    def construct(self):
        dists = load("distributions")
        overworld = [dists["iron_overworld"][ow]["avg"] for ow in OVERWORLDS]
        shipwreck = [dists["iron_shipwreck"][s]["avg"] for s in SHIP_TYPES]
        y_rng = nice_range(max(overworld + shipwreck) / 1000)

        def group(names, avgs):
            return category_group(
                [pretty(n) for n in names], [a / 1000 for a in avgs], y_rng,
                "Type", "Average Time (s)", lambda v: digital(v * 1000), width=11
            )

        self.play_groups([
            ("Average Iron Time by Overworld", group(OVERWORLDS, overworld)),
            ("Average Iron Time by Shipwreck Type", group(SHIP_TYPES, shipwreck)),
        ])


# ---------------------------------------------------------------- fortress
class FortressSplits(SeedScene):

    def construct(self):
        dists = load("distributions")["fortress_biome_splits"]
        bands = list(range(0, FORT_CAP, FORT_STEP))
        entries = [("Fortress to Stronghold Split - All Biomes", merge(dists.values()))]
        entries += [(f"Fortress to Stronghold Split - {pretty(b)}", dists[b]) for b in FORTRESS_BIOMES]

        stages = []
        for title, dist in entries:
            stage = {"title": title, "values": percentages(dist, bands)}
            avg = average_of(dist)
            stage["note"] = f"Average: {digital(avg)}" if avg is not None else "Average: -"
            stages.append(stage)

        weights = {b: sum(bins(dists[b]).values()) for b in FORTRESS_BIOMES}
        overall = sum(dists[b]["avg"] * weights[b] for b in FORTRESS_BIOMES) / sum(weights.values())
        stages[0]["note"] = f"Average: {digital(overall)}"

        chart, labels = histogram_chart(
            stages[0]["values"],
            [digital(band) if i % 12 == 0 else "" for i, band in enumerate(bands)],
            nice_range(max(max(stage["values"]) for stage in stages)),
            "Fortress to Stronghold Time", r"Share of runs (\%)"
        )
        self.play_stages(chart, labels, stages)


# ---------------------------------------------------------------- end fight
class EndRates(SeedScene):

    def construct(self):
        o_level_seeds = load("distributions")["o_level_distribution"]
        stats = load("graphs")["o_level_stats"]
        levels = sorted(
            int(k) for k, v in stats.items()
            if k != "null"
            and v["zero_cycle_rate"] is not None
            and v["end_choke_rate"] is not None
            and o_level_seeds.get(k, 0) >= MIN_O_LEVEL_SEEDS
        )
        zero = [100 * stats[str(level)]["zero_cycle_rate"] for level in levels]
        choke = [100 * stats[str(level)]["end_choke_rate"] for level in levels]

        y_rng = nice_range(max(zero + choke))
        axes = Axes(
            x_range=[levels[0], levels[-1], 4],
            y_range=y_rng,
            x_length=11,
            y_length=4.5,
            axis_config={"include_tip": False, "include_numbers": True, "font_size": 20},
        ).shift(DOWN * 0.4)
        axis_labels = tex_labels(axes, "Overworld Level", r"Rate (\%)")

        zero_line = line_through(axes, levels, zero, YELLOW)
        choke_line = line_through(axes, levels, choke, RED)

        title = self.make_title("Zero Cycle Rate by Overworld Level")
        self.play(Write(title))
        self.play(Write(axes), Write(axis_labels))
        self.play(Create(zero_line), run_time=3)
        self.wait(1.5)
        self.play(
            Transform(title, self.make_title("End Choke Rate by Overworld Level")),
            Transform(zero_line, choke_line),
        )
        self.wait(1.5)


# ---------------------------------------------------------------- history
class DiscoveryHistory(SeedScene):

    def construct(self):
        history = {int(k): v for k, v in load("graphs")["discovery_history"].items()}
        first, last = min(history), max(history)
        group = 10
        xs, rate, total = [], [], []
        running = 0
        for start in range(first, last + 1, DISCOVERY_STEP * group):
            counts = [history.get(start + i * DISCOVERY_STEP, 0) for i in range(group)]
            running += sum(counts)
            xs.append((start + DISCOVERY_STEP * group / 2) / 1_000_000)
            rate.append(sum(counts) / group)
            total.append(running)

        x_range = [math.floor(first / 1e6), math.ceil(last / 1e6), 2]

        def make_axes(y_values):
            return Axes(
                x_range=x_range,
                y_range=nice_range(max(y_values)),
                x_length=11,
                y_length=4.5,
                axis_config={"include_tip": False, "include_numbers": True, "font_size": 20},
            ).shift(DOWN * 0.4)

        rate_axes, total_axes = make_axes(rate), make_axes(total)
        rate_labels = tex_labels(rate_axes, "Match ID (millions)", "New seeds per 1000 matches")
        total_labels = tex_labels(total_axes, "Match ID (millions)", "Total seeds discovered")
        rate_line = line_through(rate_axes, xs, rate, YELLOW, width=3)
        total_line = line_through(total_axes, xs, total, YELLOW, width=3)

        title = self.make_title("Seed Discovery Rate")
        self.play(Write(title))
        self.play(Write(rate_axes), Write(rate_labels))
        self.play(Create(rate_line), run_time=5)
        self.wait(2)
        self.play(
            Transform(title, self.make_title("Cumulative Seeds Discovered")),
            Transform(rate_axes, total_axes),
            Transform(rate_labels, total_labels),
            Transform(rate_line, total_line),
            run_time=3,
        )
        self.wait(2)


class RepeatsByPlayCount(SeedScene):

    def construct(self):
        points = load("graphs")["repeats_play_count"]
        totals = {}
        for plays, repeats in points:
            if plays >= REPEAT_MAX_PLAYS:
                continue
            band = plays // REPEAT_BIN * REPEAT_BIN
            players, play_sum, repeat_sum = totals.get(band, (0, 0, 0))
            totals[band] = (players + 1, play_sum + plays, repeat_sum + repeats)

        bands = sorted(b for b, (players, _, _) in totals.items() if players >= MIN_REPEAT_BIN_PLAYERS)
        xs = [b + REPEAT_BIN / 2 for b in bands]
        ys = [100 * totals[b][2] / totals[b][1] for b in bands]

        axes = Axes(
            x_range=[0, REPEAT_MAX_PLAYS, 200],
            y_range=nice_range(max(ys)),
            x_length=11,
            y_length=4.5,
            axis_config={"include_tip": False, "include_numbers": True, "font_size": 20},
        ).shift(DOWN * 0.4)
        axis_labels = tex_labels(axes, "Matches Played", r"Repeat seeds (\% of matches)")
        line = line_through(axes, xs, ys, YELLOW)

        title = self.make_title("Repeat Seed Rate by Player Experience")
        self.play(Write(title))
        self.play(Write(axes), Write(axis_labels))
        self.play(Create(line), run_time=3)
        self.wait(2)


class SeedScores(SeedScene):

    def construct(self):
        scores = [score for score, completions in load("graphs")["seed_scores"] if completions > MIN_SCORE_COMPLETIONS]
        classes = 20
        counts = [0] * classes
        for score in scores:
            counts[min(int(score * classes), classes - 1)] += 1
        values = [100 * count / len(scores) for count in counts]

        chart, labels = histogram_chart(
            values,
            [f"{i / classes:.1f}" if i % 2 == 0 else "" for i in range(classes)],
            nice_range(max(values)),
            "Seed Score", r"Share of seeds (\%)"
        )
        self.play_stages(chart, labels, [{
            "title": "Seed Score Distribution",
            "values": values,
            "note": f"Seeds with more than {MIN_SCORE_COMPLETIONS} completions",
        }])


class SeedScoreVsCompletions(SeedScene):

    def construct(self):
        data = np.array(load("graphs")["seed_scores"])
        scores, completions = data[:, 0], data[:, 1]
        r = np.corrcoef(scores, completions)[0, 1]
        slope, intercept = np.polyfit(completions, scores, 1)

        # one point per completion count
        points = []
        for count in np.unique(completions):
            in_bin = scores[completions == count]
            if len(in_bin) >= MIN_COMPLETION_BIN_SEEDS:
                points.append((count, in_bin.mean(), len(in_bin)))
        max_x = int(max(count for count, _, _ in points))
        max_n = max(n for _, _, n in points)

        axes = Axes(
            x_range=[0, max_x + 1, 2],
            y_range=[0, 1, 0.2],
            x_length=11,
            y_length=4.5,
            axis_config={"include_tip": False, "include_numbers": True, "font_size": 20},
        ).shift(DOWN * 0.4)
        axis_labels = tex_labels(axes, "Completions", "Mean seed score")

        dots = VGroup(*[
            Dot(axes.c2p(count, mean), radius=0.05 + 0.1 * math.sqrt(n / max_n), color=YELLOW)
            for count, mean, n in points
        ])
        fit = line_through(axes, [0, max_x + 1], [intercept, intercept + slope * (max_x + 1)], RED)

        title = self.make_title("Seed Score vs Completions")
        note = self.make_note(f"Pearson r = {r:.3f}  (n = {len(scores):,} seeds)")
        self.play(Write(title))
        self.play(Write(axes), Write(axis_labels))
        self.play(LaggedStart(*[FadeIn(dot) for dot in dots], lag_ratio=0.05), run_time=3)
        self.play(Create(fit), run_time=2)
        self.play(FadeIn(note))
        self.wait(2)


# ---------------------------------------------------------------- items
class ItemTimes(SeedScene):

    def construct(self):
        per_item = load("graphs")["avg_per_item"]
        deltas = {}
        for overworld in OVERWORLDS:
            items = {
                item: (times["absent"] - times["present"]) / 1000
                for item, times in per_item[overworld].items()
                if times["present"] is not None and times["absent"] is not None
            }
            if items:
                deltas[overworld] = items

        y_rng = nice_range(max(max(items.values()) for items in deltas.values()))
        stages = [
            (
                f"Time Saved by Structure Item - {pretty(overworld)}",
                category_group(
                    [pretty(item) for item in items], list(items.values()), y_rng,
                    "Item In Structure", "Average Time Saved (s)",
                    lambda v: f"{v:+.0f}s", width=8
                ),
            )
            for overworld, items in deltas.items()
        ]
        self.play_groups(stages)


SCENES = [
    "BiomeDistribution",
    "VillageBiomes",
    "PlaycountDistribution",
    "OLevelDistribution",
    "BastionVariants",
    "IronDistribution",
    "IronShipwreck",
    "IronAverages",
    "FortressSplits",
    "EndRates",
    "DiscoveryHistory",
    "RepeatsByPlayCount",
    "SeedScores",
    "SeedScoreVsCompletions",
    "ItemTimes",
]


if __name__ == "__main__":
    name = os.path.basename(__file__)[:-3]
    for scene in sys.argv[1:] or SCENES:
        os.system(fr"{sys.executable} -m manim render -qp -o {scene}.mp4 {name}.py {scene}")
