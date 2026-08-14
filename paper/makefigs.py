"""Regenerate every figure of focus.tex as a vector PDF.

Text is typeset by pdflatex through the matplotlib pgf backend, so the
figures use the same Computer Modern fonts as the manuscript body.  Every
numerical value is the exact one produced by ehrhart_fswa.majorization;
see figdata.py for the generating computations.

Usage:  python makefigs.py
"""

from __future__ import annotations

import matplotlib

matplotlib.use("pgf")

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle  # noqa: E402

matplotlib.rcParams.update({
    "pgf.texsystem": "pdflatex",
    "pgf.rcfonts": False,
    "font.family": "serif",
    "font.size": 8,
    "axes.linewidth": 0.6,
    "lines.linewidth": 0.9,
    "pgf.preamble": r"\usepackage{amsmath}\usepackage{amssymb}",
})

TW = 5.147  # \textwidth in inches

BLUE = "#1f4e79"
ORANGE = "#b8500f"
GRAY = "#666666"
LIGHT = "#b0b0b0"
F_BLUE = "#d9e4f2"
F_ORANGE = "#f7e2d0"
F_GREEN = "#dfeadb"
F_PURPLE = "#e6e0ee"
F_GRAY = "#f1f1f1"


def blank_axes(ax, xlim, ylim, equal=False):
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    if equal:
        ax.set_aspect("equal")
    ax.axis("off")


def box(ax, x, y, w, h, text, fc=F_GRAY, ec="black", fs=8, lw=0.7):
    ax.add_patch(FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0.0,rounding_size=1.6",
        linewidth=lw, edgecolor=ec, facecolor=fc, zorder=2))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, zorder=3)


def arrow(ax, p, q, color="black", lw=0.8, style="-|>", rad=0.0, ms=5):
    ax.annotate("", xy=q, xytext=p, zorder=4, annotation_clip=False,
                arrowprops=dict(arrowstyle=style, color=color, linewidth=lw,
                                mutation_scale=ms,
                                shrinkA=0, shrinkB=0,
                                connectionstyle=f"arc3,rad={rad}"))


def save(fig, path, full=False):
    if full:
        fig.subplots_adjust(left=0.005, right=0.995, top=0.995,
                            bottom=0.005)
    fig.savefig(path, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


# ----------------------------------------------------------------- fig 1
def _body_shape(ax, cx, cy, rx, ry, kind, fc, ec):
    if kind == "diamond":
        verts = [(rx, 0), (0, ry), (-rx, 0), (0, -ry)]
    elif kind == "octagon":
        a = 0.62
        verts = [(rx, a * ry), (a * rx, ry), (-a * rx, ry), (-rx, a * ry),
                 (-rx, -a * ry), (-a * rx, -ry), (a * rx, -ry), (rx, -a * ry)]
    else:
        verts = [(rx, ry), (-rx, ry), (-rx, -ry), (rx, -ry)]
    ax.add_patch(plt.Polygon([(cx + x, cy + y) for x, y in verts],
                             closed=True, facecolor=fc, edgecolor=ec,
                             linewidth=0.9, zorder=3))


def fig_architecture(path="fig-architecture.pdf"):
    height = 2.85
    ar = TW / height           # data units per unit of visual aspect
    fig, ax = plt.subplots(figsize=(TW, height))
    blank_axes(ax, (0, 100), (0, 100))

    cells = (17.0, 50.0, 83.0)
    ax.add_patch(FancyBboxPatch(
        (3, 63), 94, 32,
        boxstyle="round,pad=0.0,rounding_size=1.6",
        linewidth=0.6, edgecolor="#e0e4ea", facecolor="#f8f9fb", zorder=1))
    for x0 in (31.8, 64.0):
        arrow(ax, (x0, 83), (x0 + 3.6, 83), color=GRAY, lw=0.7, ms=4)

    # (a) a centered exchange fiber
    cx, cy, u = cells[0], 83.0, 1.80
    ax.add_patch(plt.Polygon(
        [(cx + 3 * u, cy), (cx, cy + 3 * u * ar), (cx - 3 * u, cy),
         (cx, cy - 3 * u * ar)], closed=True, facecolor=F_BLUE,
        edgecolor=BLUE, linewidth=0.8, zorder=2))
    grid = [(i, j) for i in range(-3, 4) for j in range(-3, 4)
            if abs(i) + abs(j) <= 3]
    ax.plot([cx + u * i for i, j in grid], [cy + u * ar * j for i, j in grid],
            "o", ms=1.4, color=GRAY, zorder=3)
    ax.plot([cx - 1.15 * u, cx + 2.15 * u],
            [cy + 2.15 * u * ar, cy - 1.15 * u * ar], "-", color=ORANGE,
            lw=0.9, zorder=4)
    fiber = [(-1, 2), (0, 1), (1, 0), (2, -1)]
    ax.plot([cx + u * i for i, j in fiber], [cy + u * ar * j for i, j in fiber],
            "o", ms=3.0, color=ORANGE, zorder=5)
    ax.text(cx + 7.6, 91.3, r"$x_i+x_j=r$", fontsize=6.5, color=ORANGE,
            ha="center", va="center")
    ax.text(cx - 7.6, 74.7, r"$w=x_i-x_j$", fontsize=6.5, color=GRAY,
            ha="center", va="center")

    # (b) the atomic exposure of one transfer
    cx, cy, u = cells[1], 83.0, 1.90
    ax.add_patch(Rectangle((cx - 3.6 * u, cy - 0.55 * u * ar), 7.2 * u,
                           1.1 * u * ar, facecolor=F_BLUE, edgecolor="none",
                           zorder=2))
    ax.plot([cx - 6.2 * u, cx + 6.2 * u], [cy, cy], "-", color=LIGHT, lw=0.7,
            zorder=3)
    ax.plot([cx + u * k for k in (-3, -1, 1, 3)], [cy] * 4, "o", ms=2.0,
            color=GRAY, zorder=4)
    arrow(ax, (cx - 5 * u, cy), (cx - 3.25 * u, cy), color=GRAY, lw=0.8, ms=4)
    arrow(ax, (cx + 3.15 * u, cy), (cx + 4.9 * u, cy), color=ORANGE, lw=0.8,
          ms=4)
    ax.plot([cx - 5 * u], [cy], "o", ms=3.2, color=GRAY, zorder=5)
    ax.plot([cx + 5 * u], [cy], "o", ms=3.2, color=ORANGE, zorder=5)
    ax.text(cx - 4.1 * u, cy + 1.15 * u * ar, r"$\varepsilon=0$", fontsize=7,
            color=GRAY, ha="center", va="bottom")
    ax.text(cx + 4.1 * u, cy + 1.15 * u * ar, r"$\varepsilon=1$", fontsize=7,
            color=ORANGE, ha="center", va="bottom")

    # (c) the order it generates on one shell: the majorization Hasse
    # diagram of the partitions of s=6 into at most d=3 parts
    cx, cy = cells[2], 83.5
    place = {
        "600": (cx - 10.6, cy), "510": (cx - 6.4, cy),
        "420": (cx - 2.2, cy), "330": (cx + 2.2, cy + 5.0),
        "411": (cx + 2.2, cy - 5.0), "321": (cx + 6.4, cy),
        "222": (cx + 10.6, cy),
    }
    tags = {"600": 1, "510": -1, "420": 1, "330": 1, "411": -1,
            "321": -1, "222": 1}
    covers = (("600", "510"), ("510", "420"), ("420", "330"), ("420", "411"),
              ("330", "321"), ("411", "321"), ("321", "222"))
    for a, b in covers:
        (x0, y0), (x1, y1) = place[a], place[b]
        dx, dy = x1 - x0, (y1 - y0) / ar
        norm = (dx * dx + dy * dy) ** 0.5
        gap = 1.7 / norm
        arrow(ax, (x0 + gap * dx, y0 + gap * dy * ar),
              (x1 - gap * dx, y1 - gap * dy * ar),
              color=LIGHT, lw=0.7, ms=4)
    for key, (x, y) in place.items():
        colour = {"600": ORANGE, "222": BLUE}.get(key, GRAY)
        ax.plot([x], [y], "o", ms=3.8 if colour is not GRAY else 3.0,
                color=colour, zorder=5)
        ax.text(x + {"420": -1.4, "321": 1.4}.get(key, 0.0),
                y + 3.7 * tags[key],
                "$({0}{{,}}{1}{{,}}{2})$".format(*key), fontsize=6,
                color=colour,
                ha="center", va="center")
    ax.text(cx - 8.6, 71.8, r"$g$ nondecreasing", fontsize=6, color=GRAY,
            ha="center", va="center")

    labels = ("centered exchange fiber",
              r"atomic exposure $\varepsilon\in\{0,1\}$",
              "fixed-shell Schur order")
    for cx, text in zip(cells, labels):
        ax.text(cx, 66.5, text, fontsize=7.5, ha="center", va="center")

    arrow(ax, (50, 62.2), (50, 52.6), color=GRAY, lw=0.9, ms=6)

    bases = (17.0, 50.0, 83.0)
    bodies = (
        (bases[0], 8.8, "diamond", F_ORANGE, ORANGE, "Lee balls",
         r"$d\ge3$, $4\le s\le2t-2$:",
         r"$\lfloor s/2\rfloor-1$ minimizing arcs"),
        (bases[1], 8.4, "octagon", F_PURPLE, "#6a5a8c",
         r"$C_d+bB_\infty^d$", r"$d\ge3$, $b\ge2$, $4\le s\le N$:",
         r"sharp $\kappa_b^{(d)}(s)$ and $\Theta_{d,b}(s)$"),
        (bases[2], 7.7, "square", F_GREEN, "#4a7a44", "cubes",
         r"$d\ge3$, every active shell:", "one minimizing arc"),
    )
    for cx, r, kind, fc, ec, head, first, second in bodies:
        _body_shape(ax, cx, 35, r, r * ar, kind, fc, ec)
        ax.text(cx, 13, head, fontsize=8, ha="center", va="center")
        ax.text(cx, 6.4, first, fontsize=7, ha="center", va="center",
                color=GRAY)
        ax.text(cx, 1.4, second, fontsize=7, ha="center", va="center",
                color=GRAY)
    arrow(ax, (40, 35), (27, 35), color=GRAY, lw=0.8, ms=5)
    arrow(ax, (60, 35), (73, 35), color=GRAY, lw=0.8, ms=5)
    ax.text(33.5, 39, r"$b=0$", fontsize=7, color=GRAY, ha="center",
            va="bottom")
    ax.text(66.5, 39, r"$b\to\infty$", fontsize=7, color=GRAY, ha="center",
            va="bottom")

    ax.text(2.5, 98.5, "universal mechanism", fontsize=7, color=GRAY,
            ha="left", va="center")
    ax.text(2.5, 54, "body-specific quantitative layer", fontsize=7,
            color=GRAY, ha="left", va="center")
    save(fig, path, full=True)


# ----------------------------------------------------------------- fig 2
def fig_exchange_fiber(path="fig-exchange-fiber.pdf"):
    fig, axes = plt.subplots(1, 2, figsize=(1.10 * TW, 2.30),
                             gridspec_kw=dict(width_ratios=[1.0, 1.22],
                                              wspace=0.22))
    ax = axes[0]
    blank_axes(ax, (-3.6, 3.6), (-3.6, 3.6), equal=True)
    verts = [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2),
             (1, -2), (2, -1)]
    ax.add_patch(plt.Polygon(verts, closed=True, facecolor=F_BLUE,
                             edgecolor=BLUE, linewidth=0.9, zorder=1))
    pts = [(x, y) for x in range(-3, 4) for y in range(-3, 4)
           if abs(x) + abs(y) <= 3 and max(abs(x), abs(y)) <= 2]
    on = [(x, y) for (x, y) in pts if x + y == 1]
    off = [p for p in pts if p not in on]
    ax.plot([p[0] for p in off], [p[1] for p in off], "o", ms=1.9,
            color=GRAY, zorder=3)
    ax.plot([-1.4, 2.4], [2.4, -1.4], "-", color=ORANGE, lw=0.9, zorder=2)
    ax.plot([p[0] for p in on], [p[1] for p in on], "o", ms=3.6,
            color=ORANGE, zorder=4)

    ax.plot([2.45, 1.62], [2.25, 1.55], "-", color=BLUE, lw=0.5, zorder=2)
    ax.text(2.62, 2.42, r"$K$", fontsize=8, color=BLUE, ha="left",
            va="bottom")
    ax.plot([-2.25, -1.15], [-2.72, -2.05], "-", color=GRAY, lw=0.5,
            zorder=2)
    ax.text(-2.45, -3.0, r"$K\cap\mathbb Z^d$", fontsize=7, color=GRAY,
            ha="center", va="center")
    ax.text(2.3, -3.0, r"$x_i+x_j=r$", fontsize=7, color=ORANGE,
            ha="center", va="center")
    ax.set_title(r"(a) a fixed coordinate-sum line", fontsize=8, pad=4)

    ax = axes[1]
    blank_axes(ax, (-5.4, 5.4), (-2.05, 2.05))
    ax.add_patch(Rectangle((-3, -0.26), 6, 0.52, facecolor=F_BLUE,
                           edgecolor="none", zorder=1))
    ax.plot([-4.7, 4.6], [0, 0], "-", color="black", lw=0.7, zorder=2)
    arrow(ax, (4.6, 0), (5.05, 0), lw=0.7, ms=5)
    for k in range(-4, 5):
        ax.plot([k, k], [-0.13, 0.13], "-", color=LIGHT, lw=0.6, zorder=2)
        ax.text(k, -0.42, f"${k}$", fontsize=6.5, ha="center", va="top",
                color=GRAY)
    ax.plot([0, 0], [-0.6, 0.6], ":", color=GRAY, lw=0.6, zorder=2)
    ax.plot([-3, -1, 1, 3], [0, 0, 0, 0], "o", ms=4.4, color=ORANGE,
            zorder=4)

    for x in (0, 3):
        ax.plot([x, x], [0.30, 1.12], "-", color=LIGHT, lw=0.5, zorder=2)
    arrow(ax, (0, 0.95), (3, 0.95), color=BLUE, lw=0.7, style="<|-|>", ms=5)
    ax.text(1.5, 1.20, r"$m=3$", fontsize=7, color=BLUE, ha="center",
            va="bottom")
    for x in (-3, -1):
        ax.plot([x, x], [-0.30, -1.12], "-", color=LIGHT, lw=0.5, zorder=2)
    arrow(ax, (-3, -0.95), (-1, -0.95), color=GRAY, lw=0.7, style="<|-|>",
          ms=5)
    ax.text(-2, -1.22, r"spacing $2$", fontsize=7, color=GRAY, ha="center",
            va="top")
    ax.text(4.9, -1.22, r"$\delta=x_i-x_j$", fontsize=7, ha="right",
            va="top")
    ax.set_title(r"(b) its fiber: a centered parity interval",
                 fontsize=8, pad=4)
    save(fig, path)


# ----------------------------------------------------------------- fig 3
def fig_atomic_exposure(path="fig-atomic-exposure.pdf"):
    cases = [
        (3, 3, 4, r"(a) new endpoint in, old out", 1),
        (7, 3, 2, r"(b) both endpoints inside", 0),
        (1, 1, 6, r"(c) both endpoints outside", 0),
    ]
    fig = plt.figure(figsize=(1.05 * TW, 3.75))
    gs = fig.add_gridspec(4, 3, width_ratios=[0.64, 1.0, 0.15],
                          height_ratios=[1, 1, 1, 0.86],
                          hspace=0.30, wspace=0.04)
    yb, ya = 1.30, -1.30
    for row, (alpha, beta, D, tag, eps) in enumerate(cases):
        Ia = list(range(-alpha, alpha + 1, 2))
        before = [k - D for k in range(-beta, beta + 1, 2)]
        after = [k + 2 for k in before]
        hit_b = sorted(set(before) & set(Ia))
        hit_a = sorted(set(after) & set(Ia))

        axl = fig.add_subplot(gs[row, 0])
        blank_axes(axl, (0, 1), (-2.05, 2.25))
        axl.text(0.0, 1.20, tag, fontsize=8.0, ha="left", va="center")
        axl.text(0.0, 0.10, rf"$\alpha={alpha}$, $\beta={beta}$, $D={D}$",
                 fontsize=7.8, ha="left", va="center", color=GRAY)
        axl.text(0.0, -1.00, rf"coincidences ${len(hit_b)}\to{len(hit_a)}$",
                 fontsize=7.8, ha="left", va="center", color=GRAY)

        ax = fig.add_subplot(gs[row, 1])
        blank_axes(ax, (-8.4, 8.4), (-2.05, 2.25))
        lo, hi = -alpha - 0.5, alpha + 0.5
        ax.add_patch(Rectangle((lo, -1.80), hi - lo, 3.60,
                               facecolor="#eaf1f9", edgecolor="none",
                               zorder=0))
        for x in (lo, hi):
            ax.plot([x, x], [-1.80, 1.80], ":", color="#9fb8d4", lw=0.6,
                    zorder=1)
        ax.text(lo, 2.02, r"$-\alpha$", fontsize=7.2, color=BLUE,
                ha="center", va="center")
        ax.text(hi, 2.02, r"$\alpha$", fontsize=7.2, color=BLUE,
                ha="center", va="center")
        ax.plot([-8.1, 8.1], [0, 0], "-", color="#cccccc", lw=0.6, zorder=1)

        for k in hit_b:
            ax.plot([k, k], [yb - 0.16, -0.14], "--", color="#b6b6b6",
                    lw=0.6, zorder=2)
        for k in hit_a:
            ax.plot([k, k], [0.14, ya + 0.16], "--", color="#e0b394",
                    lw=0.6, zorder=2)

        ax.plot(Ia, [0] * len(Ia), "o", ms=3.6, color=BLUE, zorder=4)
        for y, pts, col in ((yb, before, GRAY), (ya, after, ORANGE)):
            inside = [k for k in pts if lo < k < hi]
            outside = [k for k in pts if not lo < k < hi]
            ax.plot(inside, [y] * len(inside), "o", ms=3.6, color=col,
                    zorder=4)
            ax.plot(outside, [y] * len(outside), "o", ms=3.6, mfc="white",
                    mec=col, mew=0.8, zorder=4)
        ax.plot([min(before)], [yb], "o", ms=8.0, mfc="none", mec=GRAY,
                mew=0.7, zorder=3)
        ax.plot([max(after)], [ya], "o", ms=8.0, mfc="none", mec=ORANGE,
                mew=0.7, zorder=3)

        axr = fig.add_subplot(gs[row, 2])
        blank_axes(axr, (0, 1), (-2.05, 2.25))
        axr.text(0.5, 0.0, rf"$\varepsilon={eps}$", fontsize=8.0,
                 ha="center", va="center",
                 bbox=dict(boxstyle="round,pad=0.22", fc="white",
                           ec="black", lw=0.5))

    ax = fig.add_subplot(gs[3, :])
    blank_axes(ax, (-19.0, 13.0), (-2.55, 1.15))
    y, x0, t1, t2, x1 = 0.50, -7.6, -2.0, 4.6, 10.8
    ax.add_patch(Rectangle((t1, y - 0.17), t2 - t1, 0.34, facecolor=F_BLUE,
                           edgecolor="none", zorder=1))
    ax.plot([x0, x1], [y, y], "-", color="black", lw=0.7, zorder=2)
    arrow(ax, (x1, y), (x1 + 0.55, y), lw=0.7, ms=5)
    for t in (t1, t2):
        ax.plot([t, t], [y - 0.30, y + 0.30], "-", color=BLUE, lw=0.8,
                zorder=3)
    ax.text(t1, y + 0.42, r"$|\beta-D+2|$", fontsize=7.8, ha="center",
            va="bottom")
    ax.text(t2, y + 0.42, r"$\beta+D$", fontsize=7.8, ha="center",
            va="bottom")
    for x, txt in (((x0 + t1) / 2, r"(c)\quad$\varepsilon=0$"),
                   ((t1 + t2) / 2, r"(a)\quad$\varepsilon=1$"),
                   ((t2 + x1) / 2, r"(b)\quad$\varepsilon=0$")):
        ax.text(x, y - 0.44, txt, fontsize=7.8, ha="center", va="top")
    ax.text(x1 + 1.0, y, r"$\alpha$", fontsize=8.0, ha="left", va="center")
    ax.text(-18.9, y, r"$\beta$ and $D$ fixed:", fontsize=7.9, ha="left",
            va="center")
    for x, col, txt in ((-13.0, BLUE, r"$I_\alpha$"),
                        (-7.4, GRAY, r"$I_\beta-D$"),
                        (1.6, ORANGE, r"$I_\beta-(D-2)$")):
        ax.plot([x], [-1.45], "o", ms=3.6, color=col, zorder=3)
        ax.text(x + 0.60, -1.45, txt, fontsize=8.0, color=col, ha="left",
                va="center")
    arrow(ax, (-2.6, -1.45), (1.0, -1.45), color=GRAY, lw=0.7, ms=5)
    ax.text(-0.8, -1.22, r"$+2$", fontsize=8.0, color=GRAY, ha="center",
            va="bottom")
    ax.text(-18.9, -2.25,
            r"open markers lie outside the window $|x|\le\alpha$; "
            r"dashed links are the coincidences counted",
            fontsize=7.1, ha="left", va="center", color=GRAY)
    save(fig, path)


# ----------------------------------------------------------------- fig 4
def fig_transfer(path="fig-transfer.pdf"):
    fig, axes = plt.subplots(1, 2, figsize=(0.99 * TW, 1.98),
                             gridspec_kw=dict(width_ratios=[1.0, 0.95],
                                              wspace=0.42))
    ax = axes[0]
    ax.set_xlim(-0.5, 4.7)
    ax.set_ylim(-0.5, 4.9)
    ax.set_aspect("equal")
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xticks(range(5))
    ax.set_yticks(range(5))
    ax.tick_params(labelsize=6.5, length=2, pad=1.5)
    ax.plot([0, 4.5], [0, 4.5], ":", color=LIGHT, lw=0.7)
    ax.text(2.35, 4.55, r"$u_1=u_2$", fontsize=6.5, color=GRAY,
            ha="right", va="center")
    shell = [(4, 0), (3, 1), (2, 2), (1, 3), (0, 4)]
    ax.plot([p[0] for p in shell], [p[1] for p in shell], "-",
            color=LIGHT, lw=0.7, zorder=1)
    ax.plot([p[0] for p in shell], [p[1] for p in shell], "o", ms=3.2,
            color=GRAY, zorder=2)
    ax.plot([3, 2], [1, 2], "o", ms=4.2, color=BLUE, zorder=3)
    arrow(ax, (2.86, 1.14), (2.16, 1.84), color=BLUE, lw=1.0, ms=7)
    ax.text(3.25, 0.55, r"$(3,1)$", fontsize=7, color=BLUE, ha="center")
    ax.text(1.30, 2.20, r"$(2,2)$", fontsize=7, color=BLUE, ha="center")
    ax.set_xlabel(r"$u_1$", fontsize=7.5, labelpad=0.5)
    ax.set_ylabel(r"$u_2$", fontsize=7.5, labelpad=0.5)
    ax.set_title(r"(a) one shell $u_1+u_2=4$", fontsize=8, pad=3)

    ax = axes[1]
    blank_axes(ax, (-0.1, 5.4), (-0.95, 4.5))
    for x, h in [(0.3, 3), (1.2, 1), (3.4, 2), (4.3, 2)]:
        ax.add_patch(Rectangle((x, 0), 0.62, h, facecolor=F_BLUE,
                               edgecolor=BLUE, lw=0.8))
    ax.add_patch(Rectangle((0.3, 2), 0.62, 1, facecolor=F_ORANGE,
                           edgecolor=ORANGE, lw=0.8, zorder=3))
    ax.add_patch(Rectangle((4.3, 1), 0.62, 1, facecolor=F_ORANGE,
                           edgecolor=ORANGE, lw=0.8, zorder=3))
    ax.plot([0.1, 2.0], [0, 0], "-", color="black", lw=0.7)
    ax.plot([3.2, 5.1], [0, 0], "-", color="black", lw=0.7)
    arrow(ax, (0.95, 3.25), (4.3, 2.3), color=ORANGE, lw=0.9, rad=-0.30,
          ms=7)
    ax.text(2.6, 4.05, r"one unit", fontsize=7, color=ORANGE, ha="center")
    ax.text(1.05, -0.32, r"$\lambda=(3,1)$", fontsize=7.5, ha="center",
            va="top")
    ax.text(4.15, -0.32, r"$\mu=(2,2)$", fontsize=7.5, ha="center",
            va="top")
    ax.set_title(r"(b) the same move as a transfer", fontsize=8, pad=3)
    save(fig, path)


# ----------------------------------------------------------------- fig 5
def fig_square_map(path="fig-square-map.pdf"):
    fig, axes = plt.subplots(1, 2, figsize=(1.08 * TW, 2.40),
                             gridspec_kw=dict(wspace=0.55))
    pts = [(x, y) for x in range(-2, 3) for y in range(-2, 3)
           if abs(x) + abs(y) <= 2]

    ax = axes[0]
    blank_axes(ax, (-2.9, 2.9), (-2.9, 2.9), equal=True)
    ax.add_patch(plt.Polygon([(2, 0), (0, 2), (-2, 0), (0, -2)], closed=True,
                             facecolor=F_BLUE, edgecolor=BLUE, lw=0.9))
    for (x, y) in pts:
        even = (x + y) % 2 == 0
        ax.plot([x], [y], "o", ms=3.6, color=BLUE if even else "white",
                mec=BLUE if even else ORANGE, mew=0.8, zorder=3)
    ax.plot([-2.7, 2.7], [0, 0], "-", color=LIGHT, lw=0.5, zorder=0)
    ax.plot([0, 0], [-2.7, 2.7], "-", color=LIGHT, lw=0.5, zorder=0)
    ax.text(2.62, -0.42, r"$x$", fontsize=7, ha="center")
    ax.text(0.34, 2.52, r"$y$", fontsize=7, ha="center")
    ax.set_title(r"(a) $|x|+|y|\le2$", fontsize=8, pad=2)

    ax = axes[1]
    blank_axes(ax, (-2.9, 2.9), (-2.9, 2.9), equal=True)
    ax.add_patch(Rectangle((-2, -2), 4, 4, facecolor=F_BLUE,
                           edgecolor=BLUE, lw=0.9))
    for (x, y) in pts:
        r, ww = x + y, x - y
        even = r % 2 == 0
        ax.plot([r], [ww], "o", ms=3.6, color=BLUE if even else "white",
                mec=BLUE if even else ORANGE, mew=0.8, zorder=3)
    ax.plot([-2.7, 2.7], [0, 0], "-", color=LIGHT, lw=0.5, zorder=0)
    ax.plot([0, 0], [-2.7, 2.7], "-", color=LIGHT, lw=0.5, zorder=0)
    ax.text(2.62, -0.42, r"$r$", fontsize=7, ha="center")
    ax.text(0.34, 2.52, r"$w$", fontsize=7, ha="center")
    ax.set_title(r"(b) $\max\{|r|,|w|\}\le2$", fontsize=8, pad=2)

    fig.text(0.505, 0.615, r"$(x,y)\mapsto(x+y,\,x-y)$", fontsize=7,
             ha="center", va="bottom")
    fig.patches.append(matplotlib.patches.FancyArrowPatch(
        (0.455, 0.575), (0.555, 0.575), transform=fig.transFigure,
        arrowstyle="-|>", mutation_scale=7, color="black", lw=0.8))
    fig.text(0.505, 0.50,
             r"$\bullet$ even channel", fontsize=7, ha="center", va="top",
             color=BLUE)
    fig.text(0.505, 0.415,
             r"$\circ$ odd channel", fontsize=7, ha="center", va="top",
             color=ORANGE)
    save(fig, path)


# ----------------------------------------------------------------- fig 6
def fig_parity_rectangle(path="fig-parity-rectangle.pdf"):
    p, q, R = 3, 2, 4
    fig, axes = plt.subplots(1, 2, figsize=(1.10 * TW, 2.47),
                             gridspec_kw=dict(wspace=0.20))
    for ax, (D, tag) in zip(axes, [(2, r"(a) $D=2$: $M_{p,q}=4$"),
                                   (0, r"(b) $D=0$: $M_{p,q}=5$")]):
        blank_axes(ax, (-7.2, 4.2), (-5.0, 4.3), equal=True)
        ax.plot([-7.0, 4.0], [0, 0], "-", color=LIGHT, lw=0.5, zorder=0)
        ax.plot([0, 0], [-3.5, 4.0], "-", color=LIGHT, lw=0.5, zorder=0)
        ax.add_patch(Rectangle((-p, -p), 2 * p, 2 * p, facecolor=F_BLUE,
                               edgecolor=BLUE, lw=0.9, zorder=1))
        ax.add_patch(Rectangle((-R - q, -D - q), 2 * q, 2 * q,
                               facecolor=F_ORANGE, edgecolor=ORANGE,
                               lw=0.9, alpha=0.85, zorder=2))
        lo_r, hi_r = max(-p, -R - q), min(p, -R + q)
        lo_w, hi_w = max(-p, -D - q), min(p, -D + q)
        ax.add_patch(Rectangle((lo_r - 0.3, lo_w - 0.3),
                               hi_r - lo_r + 0.6, hi_w - lo_w + 0.6,
                               facecolor="none", edgecolor="black", lw=0.8,
                               zorder=4))
        for r in range(-p, p + 1):
            for w in range(-p, p + 1):
                if (r - w) % 2:
                    continue
                inside = lo_r <= r <= hi_r and lo_w <= w <= hi_w
                if inside:
                    ax.plot([r], [w], "o", ms=3.8,
                            color=BLUE if r % 2 == 0 else "white",
                            mec=BLUE, mew=0.8, zorder=5)
                else:
                    ax.plot([r], [w], "o", ms=1.6, color=LIGHT, zorder=3)
        if D == 0:
            ax.add_patch(Rectangle((-R - q, -2 - q), 2 * q, 2 * q,
                                   facecolor="none", edgecolor=ORANGE,
                                   lw=0.6, ls=(0, (2, 1.6)), zorder=6))
            arrow(ax, (-6.6, -3.6), (-6.6, -1.8), color=ORANGE, lw=0.8,
                  ms=6)
            ax.text(-6.6, -1.35, r"$+2$", fontsize=7, color=ORANGE,
                    ha="center", va="center")
        ax.text(0.6, 3.45, r"$\max\{|r|,|w|\}\le p$", fontsize=6.8,
                color=BLUE, ha="center")
        ax.text(-3.3, -4.72,
                r"$\max\{|r+R|,|w+D|\}\le q$", fontsize=6.8, color=ORANGE,
                ha="center")
        ax.set_title(tag, fontsize=8, pad=2)
    fig.subplots_adjust(bottom=0.13)
    fig.text(0.5, 0.10,
             r"lattice $r\equiv w \pmod 2$; \ "
             r"$\bullet$ even channel, $\circ$ odd channel",
             fontsize=7.5, ha="center", va="top")
    save(fig, path)


# ----------------------------------------------------------------- fig 7
def fig_shell_graph(path="fig-shell-graph.pdf"):
    pos = {
        (6, 0, 0): (0.0, 5.0), (5, 1, 0): (0.0, 4.0),
        (4, 2, 0): (0.0, 3.0), (4, 1, 1): (-1.5, 2.0),
        (3, 3, 0): (1.5, 2.0), (3, 2, 1): (0.0, 1.0),
        (2, 2, 2): (0.0, 0.0),
    }
    edges = [
        ((6, 0, 0), (5, 1, 0), 5, 0.0), ((5, 1, 0), (4, 2, 0), 5, 0.0),
        ((5, 1, 0), (4, 1, 1), 8, 0.40), ((4, 2, 0), (4, 1, 1), 3, 0.0),
        ((4, 2, 0), (3, 3, 0), 5, 0.0), ((4, 2, 0), (3, 2, 1), 11, -0.60),
        ((4, 1, 1), (3, 2, 1), 8, 0.0), ((3, 3, 0), (3, 2, 1), 6, 0.0),
        ((3, 2, 1), (2, 2, 2), 3, 0.0),
    ]
    lens = {(6, 0, 0): 7, (5, 1, 0): 12, (4, 2, 0): 17, (4, 1, 1): 20,
            (3, 3, 0): 22, (3, 2, 1): 28, (2, 2, 2): 31}
    sharp = {((4, 2, 0), (4, 1, 1)), ((3, 2, 1), (2, 2, 2))}

    fig, ax = plt.subplots(figsize=(0.80 * TW, 3.05))
    blank_axes(ax, (-2.75, 2.75), (-0.55, 5.95))

    for a, b, wt, rad in edges:
        (x1, y1), (x2, y2) = pos[a], pos[b]
        dx, dy = x2 - x1, y2 - y1
        n = (dx ** 2 + dy ** 2) ** 0.5
        sh = 0.34
        pa = (x1 + dx / n * sh, y1 + dy / n * sh)
        pb = (x2 - dx / n * sh, y2 - dy / n * sh)
        hot = (a, b) in sharp
        arrow(ax, pa, pb, color=BLUE if hot else LIGHT,
              lw=1.5 if hot else 0.7, rad=rad, ms=6)
        mx = (pa[0] + pb[0]) / 2 + 0.5 * rad * (pb[1] - pa[1])
        my = (pa[1] + pb[1]) / 2 - 0.5 * rad * (pb[0] - pa[0])
        ux, uy = -dy / n, dx / n
        off = 0.20 if rad == 0 else 0.0
        ax.text(mx + ux * off, my + uy * off, f"${wt}$", fontsize=7,
                color=BLUE if hot else GRAY, ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.06", fc="white", ec="none"),
                zorder=6)

    for node, (x, y) in pos.items():
        lab = "(" + ",".join(str(v) for v in node) + ")"
        ax.text(x, y, f"${lab}$\n$J={lens[node]}$", fontsize=7,
                ha="center", va="center", linespacing=1.25,
                bbox=dict(boxstyle="round,pad=0.24", fc="white",
                          ec="black", lw=0.6), zorder=7)

    ax.text(-2.7, 5.80, r"$\mathcal P_3(6)$ with $t=4$: $\kappa_{3,4,6}=3$",
            fontsize=8, ha="left", va="center")
    ax.plot([-2.62, -2.24], [5.42, 5.42], "-", color=BLUE, lw=1.5)
    ax.text(-2.14, 5.42, r"arc attaining $\kappa$", fontsize=7,
            va="center", color=BLUE)
    save(fig, path)


# ----------------------------------------------------------------- fig 8
def fig_middle_section(path="fig-middle-section.pdf"):
    fig, ax = plt.subplots(figsize=(0.95 * TW, 1.60))
    blank_axes(ax, (-1.1, 6.6), (-0.95, 1.85), equal=True)
    ax.add_patch(Rectangle((0, 0), 3, 1, facecolor=F_GRAY,
                           edgecolor="none", zorder=0))
    ax.plot([0.65, 2.4], [1.35, -0.4], "--", color=ORANGE, lw=0.9,
            zorder=1)
    ax.plot([0, 3], [0, 0], "-", color=BLUE, lw=1.8, zorder=2)
    ax.plot([0, 3], [1, 1], "-", color=BLUE, lw=1.8, zorder=2)
    ax.plot([0, 0], [0, 1], color=LIGHT, lw=1.4, ls=(0, (2.5, 1.5)),
            zorder=2)
    ax.plot([3, 3], [0, 1], color=LIGHT, lw=1.4, ls=(0, (2.5, 1.5)),
            zorder=2)
    for x in range(4):
        for y in range(2):
            hit = x + y == 2
            ax.plot([x], [y], "o", ms=4.4 if hit else 2.6,
                    color=ORANGE if hit else GRAY, zorder=4)
    for x in range(4):
        ax.text(x, -0.30, f"${x}$", fontsize=6.3, color=GRAY, ha="center",
                va="top")
    for y in range(2):
        ax.text(-0.22, y, f"${y}$", fontsize=6.3, color=GRAY, ha="right",
                va="center")
    ax.text(1.5, -0.52, r"$q_1$", fontsize=7, ha="center", va="top")
    ax.text(-0.62, 0.5, r"$q_2$", fontsize=7, ha="center", va="center")
    ax.text(0.52, 1.42, r"$\Lambda_2$", fontsize=7.5, color=ORANGE,
            ha="right", va="center")
    ax.text(1.9, 1.58, r"$w=(3,1)$, \ $a=2$", fontsize=7.5, ha="center")
    ax.plot([3.8, 4.4], [0.92, 0.92], "-", color=BLUE, lw=1.8)
    ax.text(4.55, 0.92, r"meets $\Lambda_2$", fontsize=7, va="center")
    ax.plot([3.8, 4.4], [0.50, 0.50], color=LIGHT, lw=1.4,
            ls=(0, (2.5, 1.5)))
    ax.text(4.55, 0.50, r"misses", fontsize=7, va="center")
    ax.text(3.8, 0.06, r"$F_1=2$ of $4$ facets", fontsize=7, va="center")
    save(fig, path, full=True)


# ----------------------------------------------------------------- fig 9
def fig_case_partition(path="fig-case-partition.pdf"):
    fig, ax = plt.subplots(figsize=(0.92 * TW, 2.35))
    blank_axes(ax, (-1.45, 7.05), (-2.35, 6.15))
    cols = [r"$2$", r"$3$", r"$4$", r"$\ge5$"]
    rows = [r"$0$", r"$1$", r"$2$", r"$3$", r"$\ge4$"]
    fills = {"I": F_BLUE, "II": F_GREEN, "III": F_PURPLE, "IV": F_ORANGE}
    for j in range(len(rows)):
        for i in range(len(cols)):
            if j == 0:
                case = "II"
            elif i == 0:
                case = "II" if j == 1 else "I"
            else:
                case = "IV"
            ax.add_patch(Rectangle((i, j), 1, 1, facecolor=fills[case],
                                   edgecolor="black", lw=0.5))
            ax.text(i + 0.5, j + 0.5, case, fontsize=7.5, ha="center",
                    va="center")
    for i, lab in enumerate(cols):
        ax.text(i + 0.5, -0.20, lab, fontsize=7, ha="center", va="top")
    for j, lab in enumerate(rows):
        ax.text(-0.16, j + 0.5, lab, fontsize=7, ha="right", va="center")
    ax.text(2.0, -0.72, r"gap $D=a-b$", fontsize=7.5, ha="center",
            va="top")
    ax.text(-1.15, 2.5, r"residual mass $c=\|w\|_1$", fontsize=7.5,
            rotation=90, ha="center", va="center")
    ax.text(2.0, 5.30, r"concentrated residual $w=c\,e_1$", fontsize=7.5,
            ha="center", va="center")

    ax.add_patch(Rectangle((5.3, 0), 1.5, 5, facecolor=fills["III"],
                           edgecolor="black", lw=0.5))
    ax.text(6.05, 2.5, "III", fontsize=7.5, ha="center", va="center")
    ax.text(6.05, 5.30, r"spread residual", fontsize=7.5, ha="center",
            va="center")
    ax.text(6.05, -0.20, r"any $D$, any $c$", fontsize=7, ha="center",
            va="top")
    ax.plot([4.85, 4.85], [-0.3, 5.7], ":", color=GRAY, lw=0.7)

    labels = [("I", "family shape"), ("II", "outer arcs"),
              ("III", "spread residual"), ("IV", "wide gap")]
    for k, (name, desc) in enumerate(labels):
        x = -1.4 + (k % 2) * 3.7
        y = -1.55 - (k // 2) * 0.50
        ax.add_patch(Rectangle((x, y - 0.15), 0.32, 0.30,
                               facecolor=fills[name], edgecolor="black",
                               lw=0.5))
        ax.text(x + 0.46, y, f"{name}: {desc}", fontsize=7, va="center")
    save(fig, path, full=True)


# ----------------------------------------------------------------- fig 10
def fig_rigidity(path="fig-rigidity.pdf"):
    fig, axes = plt.subplots(1, 2, figsize=(0.96 * TW, 1.36),
                             gridspec_kw=dict(width_ratios=[1.0, 1.30],
                                              wspace=0.16))
    ax = axes[0]
    blank_axes(ax, (-0.55, 3.75), (-1.15, 1.35))
    xs = [0.25, 1.6, 2.95]
    labs = [r"$(4,3,1)$", r"$(4,2,2)$", r"$(3,3,2)$"]
    for x, lab in zip(xs, labs):
        ax.text(x, 0.55, lab, fontsize=7.5, ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.20", fc="white",
                          ec="black", lw=0.6), zorder=5)
    for a, b in zip(xs, xs[1:]):
        arrow(ax, (a + 0.50, 0.55), (b - 0.50, 0.55), color=BLUE, lw=1.5,
              ms=6)
        ax.text((a + b) / 2, 0.80, r"$3$", fontsize=7, color=BLUE,
                ha="center")
    arrow(ax, (0.25, 0.22), (2.95, 0.22), color=ORANGE, lw=0.9, rad=0.34,
          ms=6)
    ax.text(1.6, -0.45, r"$6$", fontsize=7, color=ORANGE, ha="center")
    ax.text(1.6, -0.78, r"$d_M=1$: no extremal pair", fontsize=7,
            color=ORANGE, ha="center", va="top")
    ax.text(1.6, 1.20, r"interior shell: $t=5$, $s=8$, $\kappa=3$",
            fontsize=7.5, ha="center")

    ax = axes[1]
    blank_axes(ax, (-0.70, 5.30), (-1.15, 1.35))
    xs = [0.25, 1.7, 3.15, 4.6]
    labs = [r"$(6,0,0)$", r"$(5,1,0)$", r"$(4,2,0)$", r"$(3,3,0)$"]
    for x, lab in zip(xs, labs):
        ax.text(x, 0.55, lab, fontsize=7.5, ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.20", fc="white",
                          ec="black", lw=0.6), zorder=5)
    for a, b in zip(xs, xs[1:]):
        arrow(ax, (a + 0.50, 0.55), (b - 0.50, 0.55), color=BLUE, lw=1.5,
              ms=6)
        ax.text((a + b) / 2, 0.80, r"$1$", fontsize=7, color=BLUE,
                ha="center")
    ax.plot([0.25, 0.25, 4.6, 4.6], [0.15, -0.25, -0.25, 0.15], "-",
            color=BLUE, lw=0.7)
    ax.text(2.42, -0.70, r"$d_M=3$, deficit $=3=\kappa\,d_M$: extremal",
            fontsize=7, color=BLUE, ha="center", va="top")
    ax.text(2.42, 1.20, r"outermost shell: $t=3$, $s=6$, $\kappa=1$",
            fontsize=7.5, ha="center")
    save(fig, path, full=True)


# ----------------------------------------------------------------- fig 11
def fig_sharp_constants(path="fig-sharp-constants.pdf"):
    fig, axes = plt.subplots(1, 2, figsize=(TW, 1.95),
                             gridspec_kw=dict(wspace=0.30))
    ax = axes[0]
    s_lee = list(range(2, 11))
    v_lee = [41, 20, 7, 6, 5, 4, 3, 2, 1]
    s_cube = list(range(2, 12))
    v_cube = [11, 10, 9, 8, 7, 6, 5, 4, 3, 2]
    ax.semilogy(s_lee, v_lee, "o-", color=BLUE, ms=3.0, lw=0.9,
                label=r"Lee $\kappa_{3,5,s}$")
    ax.semilogy(s_cube, v_cube, "s--", color=ORANGE, ms=3.0, lw=0.9,
                label=r"cube $\kappa^{\square}_{3,5,s}$")
    ax.axvline(10.5, color=BLUE, lw=0.6, ls=":")
    ax.axvline(11.5, color=ORANGE, lw=0.6, ls=":")
    ax.text(10.2, 30, r"$s=2t$", fontsize=6.5, color=BLUE, ha="right")
    ax.text(11.8, 30, r"$2t+1$", fontsize=6.5, color=ORANGE, ha="left")
    ax.set_xlabel(r"shell weight $s$", fontsize=7.5, labelpad=1.5)
    ax.set_ylabel(r"sharp constant", fontsize=7.5, labelpad=1.5)
    ax.set_xlim(1.2, 13.2)
    ax.set_xticks([2, 4, 6, 8, 10, 12])
    ax.tick_params(labelsize=6.5, length=2, pad=1.5)
    ax.legend(fontsize=6.8, frameon=False, loc="lower left",
              handlelength=1.6, borderpad=0.1)
    ax.set_title(r"(a) Lee ball versus cube, $d=3$, $t=5$", fontsize=8,
                 pad=3)
    ax.spines[["top", "right"]].set_visible(False)

    ax = axes[1]
    c = 4
    ts = list(range(1, 2 * c + 1))
    vals = [min(2 * t - 1, 4 * c - 2 * t + 1) for t in ts]
    ax.plot(ts, vals, "o-", color=BLUE, ms=3.0, lw=1.1)
    ax.axhline(2 * c - 1, color=ORANGE, lw=0.6, ls="--")
    ax.text(8.4, 2 * c - 1 + 0.35, r"$2c-1$", fontsize=6.8, color=ORANGE,
            ha="right")
    ax.text(1.9, 5.4, r"$2t-1$", fontsize=6.8, color=BLUE, ha="center")
    ax.text(6.7, 5.4, r"$4c-2t+1$", fontsize=6.8, color=BLUE, ha="center")
    ax.set_xlabel(r"radius $t$ \quad ($c=4$)", fontsize=7.5, labelpad=1.5)
    ax.set_ylabel(r"transfer increment", fontsize=7.5, labelpad=1.5)
    ax.set_xlim(0.4, 8.6)
    ax.set_ylim(0, 9.2)
    ax.set_xticks(range(1, 9))
    ax.set_yticks([1, 3, 5, 7])
    ax.tick_params(labelsize=6.5, length=2, pad=1.5)
    ax.set_title(r"(b) capped cross-polytope crossover", fontsize=8, pad=3)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, path)


# ----------------------------------------------------------------- fig 12
def _candidates(b, d, s):
    """Recipient-one weight, recipient-zero weight, and the threshold."""
    N, e = 2 * b + 1, d - 2

    def gamma(r):
        value = (N + 2 - r) * N ** (e - 1)
        if e >= 2:
            value += 2 * (e - 1) * (N - r) * N ** (e - 2)
        return value

    return (gamma(s - 4),
            gamma(s - 2) + 2 * N ** (e - 1) * (2 * N - s),
            N * (2 * N - s - 1) - 2 * (d - 3))


def fig_threshold(path="fig-threshold.pdf"):
    fig, axes = plt.subplots(1, 2, figsize=(1.02 * TW, 1.72),
                             gridspec_kw=dict(width_ratios=[0.86, 1.14],
                                              wspace=0.40))

    ax = axes[0]
    blank_axes(ax, (-0.4, 9.3), (-2.9, 5.3))
    step, width = 1.16, 0.62
    groups = [(0.3, [3, 1, 2.4], [r"$3$", r"$1$", r"$s-4$"]),
              (5.3, [2, 0, 3.0], [r"$2$", r"$0$", r"$s-2$"])]
    for x0, heights, labels in groups:
        for k, (h, lab) in enumerate(zip(heights, labels)):
            x = x0 + step * k
            if h > 0:
                ax.add_patch(Rectangle((x, 0), width, h, facecolor=F_BLUE,
                                       edgecolor=BLUE, lw=0.8))
            if k < 2:
                ax.text(x + width / 2, -0.30, lab, fontsize=6.8, ha="center",
                        va="top")
            else:
                ax.text(x + width / 2, h + 0.22, lab, fontsize=6.8,
                        ha="center", va="bottom")
        ax.add_patch(Rectangle((x0, heights[0] - 1), width, 1,
                               facecolor=F_ORANGE, edgecolor=ORANGE, lw=0.8,
                               zorder=3))
        ax.plot([x0 - 0.18, x0 + 2 * step + width + 0.18], [0, 0], "-",
                color="black", lw=0.7)
        arrow(ax, (x0 + width - 0.04, heights[0] - 0.35),
              (x0 + step + 0.10, heights[1] + 0.30),
              color=ORANGE, lw=0.9, rad=-0.42, ms=6.5)
    centers = [x0 + step + width / 2 for x0, _, _ in groups]
    ax.text(centers[0], 4.55, r"recipient one", fontsize=7, ha="center",
            color=GRAY)
    ax.text(centers[1], 4.55, r"recipient zero", fontsize=7, ha="center",
            color=GRAY)
    ax.text(centers[0], -1.40, r"$\Gamma_b^{(e)}(s-4)$", fontsize=7.5,
            ha="center")
    ax.text(centers[1], -1.40, r"$\Gamma_b^{(e)}(s-2)$", fontsize=7.5,
            ha="center")
    ax.text(centers[1], -2.20, r"$+\,2N^{e-1}(2N-s)$", fontsize=7.5,
            ha="center", color=ORANGE)
    ax.set_title(r"(a) the two competing arcs", fontsize=8, pad=2)

    ax = axes[1]
    ds = list(range(3, 41))
    curves = [(2, 5, BLUE, "o", 13), (3, 7, ORANGE, "s", 24),
              (3, 5, GRAY, "^", 31)]
    for b, s, color, marker, tie in curves:
        theta = [_candidates(b, d, s)[2] for d in ds]
        ax.plot(ds, theta, "-", color=color, lw=1.0)
        ax.plot([tie], [0], marker, color=color, ms=3.6, zorder=4)
        ax.text(41.2, theta[-1], rf"$b={b}$, $s={s}$", fontsize=6.8,
                color=color, ha="left", va="center")
    ax.axhline(0, color="black", lw=0.6, ls="--")
    ax.text(48.5, 40, "$\\Theta>0$:\nrecipient one", fontsize=6.5,
            ha="right", va="center", linespacing=1.35)
    ax.text(3.6, -50, "$\\Theta<0$:\ncanonical edge", fontsize=6.5,
            ha="left", va="center", linespacing=1.35)
    ax.set_xlabel(r"dimension $d$", fontsize=7.5, labelpad=1.5)
    ax.set_ylabel(r"$\Theta_{d,b}(s)$", fontsize=7.5, labelpad=1.5)
    ax.set_xlim(2, 49)
    ax.set_ylim(-62, 78)
    ax.set_xticks([3, 13, 24, 31, 40])
    ax.set_yticks([-40, 0, 40])
    ax.tick_params(labelsize=6.5, length=2, pad=1.5)
    ax.set_title(r"(b) the threshold in every dimension", fontsize=8, pad=2)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, path)


if __name__ == "__main__":
    fig_architecture()
    fig_exchange_fiber()
    fig_atomic_exposure()
    fig_transfer()
    fig_square_map()
    fig_parity_rectangle()
    fig_shell_graph()
    fig_middle_section()
    fig_case_partition()
    fig_rigidity()
    fig_sharp_constants()
    fig_threshold()
    print("all figures written")
