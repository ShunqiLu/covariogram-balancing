"""Regenerate every main-text figure as a vector PDF.

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

# House style shared by every figure.  Three text sizes, three marker sizes,
# and one meaning per colour: blue is the set under discussion, orange the
# second body or the moved object, grey the ambient lattice.
FS_MAIN = 8.0    # panel titles and primary labels
FS_SUB = 7.2     # secondary annotation
FS_TINY = 6.6    # tick numbers and dense labels
MS_ON = 3.6      # a lattice point that belongs to the set in question
MS_OFF = 2.4     # an ambient lattice point that does not
MS_RING = 8.0    # highlight ring drawn around a marker
FW = 0.924 * TW  # every figure is trimmed to this printed width

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


def box(ax, x, y, w, h, text, fc=F_GRAY, ec="black", fs=FS_MAIN, lw=0.7):
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
    width, height = FW, 2.66
    ar = width / height        # data units per unit of visual aspect
    fig, ax = plt.subplots(figsize=(width, height))
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
            "o", ms=MS_OFF, mfc="white", mec="#9a9a9a", mew=0.6, zorder=3)
    ax.plot([cx - 1.15 * u, cx + 2.15 * u],
            [cy + 2.15 * u * ar, cy - 1.15 * u * ar], "-", color=ORANGE,
            lw=0.9, zorder=4)
    fiber = [(-1, 2), (0, 1), (1, 0), (2, -1)]
    ax.plot([cx + u * i for i, j in fiber], [cy + u * ar * j for i, j in fiber],
            "o", ms=MS_ON, color=ORANGE, zorder=5)
    ax.text(cx + 7.6, 91.3, r"$x_i+x_j=r$", fontsize=FS_TINY, color=ORANGE,
            ha="center", va="center")
    ax.text(cx - 7.6, 74.7, r"$w=x_i-x_j$", fontsize=FS_TINY, color=GRAY,
            ha="center", va="center")

    # (b) the atomic exposure of one transfer
    cx, cy, u = cells[1], 83.0, 1.90
    ax.add_patch(Rectangle((cx - 3.6 * u, cy - 0.55 * u * ar), 7.2 * u,
                           1.1 * u * ar, facecolor=F_BLUE, edgecolor="none",
                           zorder=2))
    ax.plot([cx - 6.2 * u, cx + 6.2 * u], [cy, cy], "-", color=LIGHT, lw=0.7,
            zorder=3)
    ax.plot([cx + u * k for k in (-3, -1, 1, 3)], [cy] * 4, "o", ms=MS_ON,
            color=GRAY, zorder=4)
    arrow(ax, (cx - 5 * u, cy), (cx - 3.25 * u, cy), color=GRAY, lw=0.8, ms=4)
    arrow(ax, (cx + 3.15 * u, cy), (cx + 4.9 * u, cy), color=ORANGE, lw=0.8,
          ms=4)
    ax.plot([cx - 5 * u], [cy], "o", ms=MS_ON, color=GRAY, zorder=5)
    ax.plot([cx + 5 * u], [cy], "o", ms=MS_ON, color=ORANGE, zorder=5)
    ax.text(cx - 4.1 * u, cy + 1.15 * u * ar, r"$\varepsilon=0$", fontsize=FS_SUB,
            color=GRAY, ha="center", va="bottom")
    ax.text(cx + 4.1 * u, cy + 1.15 * u * ar, r"$\varepsilon=1$", fontsize=FS_SUB,
            color=ORANGE, ha="center", va="bottom")

    # (c) the order it generates on one shell: the majorization Hasse
    # diagram of the partitions of s=6 into at most d=3 parts
    cx, cy = cells[2] - 1.5, 83.5
    place = {
        "600": (cx - 11.7, cy), "510": (cx - 7.0, cy),
        "420": (cx - 2.3, cy), "330": (cx + 2.4, cy + 5.0),
        "411": (cx + 2.4, cy - 5.0), "321": (cx + 7.1, cy),
        "222": (cx + 11.8, cy),
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
        ax.plot([x], [y], "o", ms=MS_ON, color=colour, zorder=5)
        ax.text(x + {"420": -1.4, "321": 1.4}.get(key, 0.0),
                y + 3.7 * tags[key],
                "$({0}{{,}}{1}{{,}}{2})$".format(*key), fontsize=FS_TINY,
                color=colour,
                ha="center", va="center")
    ax.text(cx - 8.6, 71.8, r"$g$ nondecreasing", fontsize=FS_TINY, color=GRAY,
            ha="center", va="center")

    labels = ("centered exchange fiber",
              r"atomic exposure $\varepsilon\in\{0,1\}$",
              "fixed-shell Schur order")
    for cx, text in zip(cells, labels):
        ax.text(cx, 66.5, text, fontsize=FS_MAIN, ha="center", va="center")

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
        ax.text(cx, 13, head, fontsize=FS_MAIN, ha="center", va="center")
        ax.text(cx, 6.4, first, fontsize=FS_SUB, ha="center", va="center",
                color=GRAY)
        ax.text(cx, 1.4, second, fontsize=FS_SUB, ha="center", va="center",
                color=GRAY)
    arrow(ax, (40, 35), (27, 35), color=GRAY, lw=0.8, ms=5)
    arrow(ax, (60, 35), (73, 35), color=GRAY, lw=0.8, ms=5)
    ax.text(33.5, 39, r"$b=0$", fontsize=FS_SUB, color=GRAY, ha="center",
            va="bottom")
    ax.text(66.5, 39, r"$b\to\infty$", fontsize=FS_SUB, color=GRAY, ha="center",
            va="bottom")

    ax.text(2.5, 98.5, "universal mechanism", fontsize=FS_SUB, color=GRAY,
            ha="left", va="center")
    ax.text(2.5, 54, "body-specific quantitative layer", fontsize=FS_SUB,
            color=GRAY, ha="left", va="center")
    save(fig, path, full=True)


# ----------------------------------------------------------------- fig 2
def fig_exchange_fiber(path="fig-exchange-fiber.pdf"):
    fig, axes = plt.subplots(1, 2, figsize=(1.182 * TW, 2.472),
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
    ax.plot([p[0] for p in off], [p[1] for p in off], "o", ms=MS_OFF,
            mfc="white", mec="#9a9a9a", mew=0.6, zorder=3)
    ax.plot([-1.4, 2.4], [2.4, -1.4], "-", color=ORANGE, lw=0.9, zorder=2)
    ax.plot([p[0] for p in on], [p[1] for p in on], "o", ms=MS_ON,
            color=ORANGE, zorder=4)

    ax.plot([2.45, 1.62], [2.25, 1.55], "-", color=BLUE, lw=0.5, zorder=2)
    ax.text(2.62, 2.42, r"$K$", fontsize=FS_MAIN, color=BLUE, ha="left",
            va="bottom")
    ax.plot([-2.25, -1.15], [-2.72, -2.05], "-", color=GRAY, lw=0.5,
            zorder=2)
    ax.text(-2.45, -3.0, r"$K\cap\mathbb Z^d$", fontsize=FS_SUB, color=GRAY,
            ha="center", va="center")
    ax.text(2.3, -3.0, r"$x_i+x_j=r$", fontsize=FS_SUB, color=ORANGE,
            ha="center", va="center")
    ax.set_title(r"(a) a fixed coordinate-sum line", fontsize=FS_MAIN, pad=4)

    ax = axes[1]
    blank_axes(ax, (-5.4, 5.4), (-2.05, 2.05))
    ax.add_patch(Rectangle((-3, -0.26), 6, 0.52, facecolor=F_BLUE,
                           edgecolor="none", zorder=1))
    ax.plot([-4.7, 4.6], [0, 0], "-", color="black", lw=0.7, zorder=2)
    arrow(ax, (4.6, 0), (5.05, 0), lw=0.7, ms=5)
    for k in range(-4, 5):
        ax.plot([k, k], [-0.13, 0.13], "-", color=LIGHT, lw=0.6, zorder=2)
        ax.text(k, -0.42, f"${k}$", fontsize=FS_TINY, ha="center", va="top",
                color=GRAY)
    ax.plot([0, 0], [-0.6, 0.6], ":", color=GRAY, lw=0.6, zorder=2)
    ax.plot([-3, -1, 1, 3], [0, 0, 0, 0], "o", ms=MS_ON, color=ORANGE,
            zorder=4)

    for x in (0, 3):
        ax.plot([x, x], [0.30, 1.12], "-", color=LIGHT, lw=0.5, zorder=2)
    arrow(ax, (0, 0.95), (3, 0.95), color=BLUE, lw=0.7, style="<|-|>", ms=5)
    ax.text(1.5, 1.20, r"$m=3$", fontsize=FS_SUB, color=BLUE, ha="center",
            va="bottom")
    for x in (-3, -1):
        ax.plot([x, x], [-0.30, -1.12], "-", color=LIGHT, lw=0.5, zorder=2)
    arrow(ax, (-3, -0.95), (-1, -0.95), color=GRAY, lw=0.7, style="<|-|>",
          ms=5)
    ax.text(-2, -1.22, r"spacing $2$", fontsize=FS_SUB, color=GRAY, ha="center",
            va="top")
    ax.text(4.9, -1.22, r"$\delta=x_i-x_j$", fontsize=FS_SUB, ha="right",
            va="top")
    ax.set_title(r"(b) its fiber: a centered parity interval",
                 fontsize=FS_MAIN, pad=4)
    save(fig, path)


# ----------------------------------------------------------------- fig 3
def fig_atomic_exposure(path="fig-atomic-exposure.pdf"):
    cases = [
        (3, 3, 4, r"(a)", 1),
        (7, 3, 2, r"(b)", 0),
        (1, 1, 6, r"(c)", 0),
    ]
    fig = plt.figure(figsize=(1.178 * TW, 3.550))
    gs = fig.add_gridspec(5, 3, width_ratios=[0.46, 1.0, 0.24],
                          height_ratios=[0.34, 1, 1, 1, 0.62],
                          hspace=0.30, wspace=0.04)

    axk = fig.add_subplot(gs[0, 1])
    blank_axes(axk, (-8.4, 8.4), (-1.0, 1.0))
    for x, col, txt in ((-8.2, BLUE, r"$I_\alpha$"),
                        (-5.2, GRAY, r"$I_\beta-D$"),
                        (1.4, ORANGE, r"$I_\beta-(D-2)$")):
        axk.plot([x], [0], "o", ms=MS_ON, color=col, zorder=3)
        axk.text(x + 0.45, 0, txt, fontsize=FS_SUB, color=col, ha="left",
                 va="center")
    arrow(axk, (-1.1, 0), (0.9, 0), color=GRAY, lw=0.7, ms=5)
    axk.text(-0.1, 0.30, r"$+2$", fontsize=FS_SUB, color=GRAY, ha="center",
             va="bottom")

    yb, ya = 1.30, -1.30
    for row, (alpha, beta, D, tag, eps) in enumerate(cases, start=1):
        Ia = list(range(-alpha, alpha + 1, 2))
        before = [k - D for k in range(-beta, beta + 1, 2)]
        after = [k + 2 for k in before]
        hit_b = sorted(set(before) & set(Ia))
        hit_a = sorted(set(after) & set(Ia))

        axl = fig.add_subplot(gs[row, 0])
        blank_axes(axl, (0, 1), (-2.05, 2.25))
        axl.text(0.0, 0.62, tag, fontsize=FS_MAIN, ha="left", va="center")
        axl.text(0.0, -0.52, rf"$\alpha={alpha}$, $\beta={beta}$, $D={D}$",
                 fontsize=FS_MAIN, ha="left", va="center", color=GRAY)

        ax = fig.add_subplot(gs[row, 1])
        blank_axes(ax, (-8.4, 8.4), (-2.05, 2.25))
        lo, hi = -alpha - 0.5, alpha + 0.5
        ax.add_patch(Rectangle((lo, -1.80), hi - lo, 3.60,
                               facecolor="#eaf1f9", edgecolor="none",
                               zorder=0))
        for x in (lo, hi):
            ax.plot([x, x], [-1.80, 1.80], ":", color="#9fb8d4", lw=0.6,
                    zorder=1)
        ax.text(lo, 2.02, r"$-\alpha$", fontsize=FS_SUB, color=BLUE,
                ha="center", va="center")
        ax.text(hi, 2.02, r"$\alpha$", fontsize=FS_SUB, color=BLUE,
                ha="center", va="center")
        ax.plot([-8.1, 8.1], [0, 0], "-", color="#cccccc", lw=0.6, zorder=1)

        for k in hit_b:
            ax.plot([k, k], [yb - 0.16, -0.14], "--", color="#b6b6b6",
                    lw=0.6, zorder=2)
        for k in hit_a:
            ax.plot([k, k], [0.14, ya + 0.16], "--", color="#e0b394",
                    lw=0.6, zorder=2)

        ax.plot(Ia, [0] * len(Ia), "o", ms=MS_ON, color=BLUE, zorder=4)
        for y, pts, col in ((yb, before, GRAY), (ya, after, ORANGE)):
            inside = [k for k in pts if lo < k < hi]
            outside = [k for k in pts if not lo < k < hi]
            ax.plot(inside, [y] * len(inside), "o", ms=MS_ON, color=col,
                    zorder=4)
            ax.plot(outside, [y] * len(outside), "o", ms=MS_OFF, mfc="white",
                    mec=col, mew=0.7, zorder=4)
        ax.plot([min(before)], [yb], "o", ms=MS_RING, mfc="none", mec=GRAY,
                mew=0.7, zorder=3)
        ax.plot([max(after)], [ya], "o", ms=MS_RING, mfc="none", mec=ORANGE,
                mew=0.7, zorder=3)

        axr = fig.add_subplot(gs[row, 2])
        blank_axes(axr, (0, 1), (-2.05, 2.25))
        axr.text(0.42, 0.62, rf"${len(hit_b)}\to{len(hit_a)}$", fontsize=FS_MAIN,
                 ha="center", va="center", color=GRAY)
        axr.text(0.42, -0.62, rf"$\varepsilon={eps}$", fontsize=FS_MAIN,
                 ha="center", va="center",
                 bbox=dict(boxstyle="round,pad=0.22", fc="white",
                           ec="black", lw=0.5))

    ax = fig.add_subplot(gs[4, :])
    blank_axes(ax, (-19.0, 13.0), (-1.30, 1.30))
    y, x0, t1, t2, x1 = 0.30, -7.6, -2.0, 4.6, 10.8
    ax.add_patch(Rectangle((t1, y - 0.17), t2 - t1, 0.34, facecolor=F_BLUE,
                           edgecolor="none", zorder=1))
    ax.plot([x0, x1], [y, y], "-", color="black", lw=0.7, zorder=2)
    arrow(ax, (x1, y), (x1 + 0.55, y), lw=0.7, ms=5)
    for t in (t1, t2):
        ax.plot([t, t], [y - 0.30, y + 0.30], "-", color=BLUE, lw=0.8,
                zorder=3)
    ax.text(t1, y + 0.42, r"$|\beta-D+2|$", fontsize=FS_MAIN, ha="center",
            va="bottom")
    ax.text(t2, y + 0.42, r"$\beta+D$", fontsize=FS_MAIN, ha="center",
            va="bottom")
    for x, txt in (((x0 + t1) / 2, r"(c)\quad$\varepsilon=0$"),
                   ((t1 + t2) / 2, r"(a)\quad$\varepsilon=1$"),
                   ((t2 + x1) / 2, r"(b)\quad$\varepsilon=0$")):
        ax.text(x, y - 0.44, txt, fontsize=FS_MAIN, ha="center", va="top")
    ax.text(x1 + 1.0, y, r"$\alpha$", fontsize=FS_MAIN, ha="left", va="center")
    ax.text(-18.9, y, r"(d)", fontsize=FS_MAIN, ha="left", va="center")
    save(fig, path)


# ----------------------------------------------------------------- fig 4
def _clip_halfplane(poly, a, b, c):
    """Keep the part of the convex polygon with a*x + b*y <= c."""
    out, n = [], len(poly)
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        fp = a * p[0] + b * p[1] - c
        fq = a * q[0] + b * q[1] - c
        if fp <= 1e-12:
            out.append(p)
        if (fp < -1e-12 < fq) or (fq < -1e-12 < fp):
            t = fp / (fp - fq)
            out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    return out


def fig_transfer(path="fig-transfer.pdf"):
    r = 2
    lattice = [(i, j) for i in range(-r, r + 1) for j in range(-r, r + 1)
               if abs(i) + abs(j) <= r]
    cases = [((2, 0), r"(a)\quad$u=2e_1$"), ((1, 1), r"(b)\quad$u=e_1+e_2$")]

    fig = plt.figure(figsize=(1.178 * TW, 3.005))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 0.30, 1.0], wspace=0.05)
    for col, (u, tag) in zip((0, 2), cases):
        ax = fig.add_subplot(gs[0, col])
        blank_axes(ax, (-4.7, 2.7), (-3.95, 2.85), equal=True)
        cx, cy = -u[0], -u[1]
        dia_a = [(r, 0), (0, r), (-r, 0), (0, -r)]
        dia_b = [(cx + r, cy), (cx, cy + r), (cx - r, cy), (cx, cy - r)]
        lens = dia_a
        for s1 in (1, -1):
            for s2 in (1, -1):
                lens = _clip_halfplane(lens, s1, s2,
                                       r + s1 * cx + s2 * cy)
        ax.add_patch(plt.Polygon(dia_a, closed=True, facecolor=F_BLUE,
                                 edgecolor=BLUE, lw=0.9, zorder=1))
        ax.add_patch(plt.Polygon(dia_b, closed=True, facecolor=F_ORANGE,
                                 edgecolor=ORANGE, lw=0.9, alpha=0.85,
                                 zorder=2))
        ax.add_patch(plt.Polygon(lens, closed=True, facecolor="#b4c8de",
                                 edgecolor="none", zorder=3))
        shifted = [(i + cx, j + cy) for i, j in lattice]
        common = sorted(set(lattice) & set(shifted))
        rest = sorted((set(lattice) | set(shifted)) - set(common))
        ax.plot([p[0] for p in rest], [p[1] for p in rest], "o", ms=MS_OFF,
                mfc="white", mec="#9a9a9a", mew=0.6, zorder=4)
        ax.plot([p[0] for p in common], [p[1] for p in common], "o", ms=MS_ON,
                color=BLUE, zorder=5)
        ax.text(-1.0, -3.66, tag, fontsize=FS_MAIN, ha="center", va="center")
        ax.text(-1.0, 2.58, rf"${len(common)}$ common points", fontsize=FS_MAIN,
                color=BLUE, ha="center", va="center")

    axm = fig.add_subplot(gs[0, 1])
    blank_axes(axm, (0, 1), (0, 1))
    arrow(axm, (0.06, 0.52), (0.94, 0.52), color=GRAY, lw=0.8, ms=6)
    axm.text(0.5, 0.60, r"$-e_1+e_2$", fontsize=FS_MAIN, color=GRAY,
             ha="center", va="bottom")
    save(fig, path)


# ----------------------------------------------------------------- fig 5
def fig_square_map(path="fig-square-map.pdf"):
    pts = [(x, y) for x in range(-2, 3) for y in range(-2, 3)
           if abs(x) + abs(y) <= 2]
    image = {(x + y, x - y) for (x, y) in pts}

    fig = plt.figure(figsize=(1.181 * TW, 2.316))
    gs = fig.add_gridspec(2, 3, width_ratios=[1.0, 0.34, 1.0],
                          height_ratios=[1.0, 0.18], wspace=0.05,
                          hspace=0.05)

    ax = fig.add_subplot(gs[0, 0])
    blank_axes(ax, (-2.9, 2.9), (-2.9, 2.9), equal=True)
    ax.add_patch(plt.Polygon([(2, 0), (0, 2), (-2, 0), (0, -2)], closed=True,
                             facecolor=F_BLUE, edgecolor=BLUE, lw=0.9))
    ax.plot([-2.7, 2.7], [0, 0], "-", color=LIGHT, lw=0.5, zorder=0)
    ax.plot([0, 0], [-2.7, 2.7], "-", color=LIGHT, lw=0.5, zorder=0)
    for (x, y) in pts:
        even = (x + y) % 2 == 0
        ax.plot([x], [y], "o" if even else "s", ms=MS_ON, color=BLUE,
                zorder=3)
    ax.text(2.62, -0.42, r"$x$", fontsize=FS_SUB, ha="center")
    ax.text(0.34, 2.52, r"$y$", fontsize=FS_SUB, ha="center")
    ax.set_title(r"(a) $|x|+|y|\le2$ in $\mathbb Z^2$", fontsize=FS_MAIN,
                 pad=2)

    ax = fig.add_subplot(gs[0, 2])
    blank_axes(ax, (-2.9, 2.9), (-2.9, 2.9), equal=True)
    ax.add_patch(Rectangle((-2, -2), 4, 4, facecolor=F_BLUE,
                           edgecolor=BLUE, lw=0.9))
    ax.plot([-2.7, 2.7], [0, 0], "-", color=LIGHT, lw=0.5, zorder=0)
    ax.plot([0, 0], [-2.7, 2.7], "-", color=LIGHT, lw=0.5, zorder=0)
    for r in range(-2, 3):
        for w in range(-2, 3):
            if (r + w) % 2:
                ax.plot([r], [w], "x", ms=3.0, color="#9a9a9a", mew=0.7,
                        zorder=3)
    for (r, w) in sorted(image):
        ax.plot([r], [w], "o" if r % 2 == 0 else "s", ms=MS_ON, color=BLUE,
                zorder=4)
    ax.text(2.62, -0.42, r"$r$", fontsize=FS_SUB, ha="center")
    ax.text(0.34, 2.52, r"$w$", fontsize=FS_SUB, ha="center")
    ax.set_title(r"(b) $\max\{|r|,|w|\}\le2$ in $\Lambda$",
                 fontsize=FS_MAIN, pad=2)

    axm = fig.add_subplot(gs[0, 1])
    blank_axes(axm, (0, 1), (0, 1))
    arrow(axm, (0.05, 0.52), (0.95, 0.52), lw=0.8, ms=6)
    axm.text(0.5, 0.585, r"$T$", fontsize=FS_MAIN, ha="center", va="bottom")

    axk = fig.add_subplot(gs[1, :])
    blank_axes(axk, (0, 1), (0, 1))
    for x, col, mk, txt in ((0.115, BLUE, "o", r"even channel"),
                            (0.395, BLUE, "s", r"odd channel"),
                            (0.665, "#9a9a9a", "x",
                             r"integer point outside $\Lambda$")):
        axk.plot([x], [0.5], mk, ms=MS_ON if mk != "x" else 3.0, color=col,
                 mew=0.7, zorder=3)
        axk.text(x + 0.018, 0.5, txt, fontsize=FS_SUB, color=col, ha="left",
                 va="center")
    save(fig, path)


# ----------------------------------------------------------------- fig 6
def fig_parity_rectangle(path="fig-parity-rectangle.pdf"):
    p, q, R = 3, 2, 4
    fig, axes = plt.subplots(1, 2, figsize=(1.180 * TW, 2.649),
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
                    ax.plot([r], [w], "o" if r % 2 == 0 else "s", ms=MS_ON,
                            color=BLUE, zorder=5)
                else:
                    ax.plot([r], [w], "o", ms=MS_OFF, mfc="white",
                            mec="#9a9a9a", mew=0.6, zorder=3)
        if D == 0:
            ax.add_patch(Rectangle((-R - q, -2 - q), 2 * q, 2 * q,
                                   facecolor="none", edgecolor=ORANGE,
                                   lw=0.6, ls=(0, (2, 1.6)), zorder=6))
            arrow(ax, (-6.6, -3.6), (-6.6, -1.8), color=ORANGE, lw=0.8,
                  ms=6)
            ax.text(-6.6, -1.35, r"$+2$", fontsize=FS_SUB, color=ORANGE,
                    ha="center", va="center")
        ax.text(0.6, 3.45, r"$\max\{|r|,|w|\}\le p$", fontsize=FS_SUB,
                color=BLUE, ha="center")
        ax.text(-3.3, -4.72,
                r"$\max\{|r+R|,|w+D|\}\le q$", fontsize=FS_SUB, color=ORANGE,
                ha="center")
        ax.set_title(tag, fontsize=FS_MAIN, pad=2)
    fig.subplots_adjust(bottom=0.13)
    fig.text(0.5, 0.10,
             r"lattice $\Lambda$: $r\equiv w \pmod 2$; \ "
             r"$\bullet$ even channel, $\blacksquare$ odd channel",
             fontsize=FS_SUB, ha="center", va="top")
    save(fig, path)


# ----------------------------------------------------------------- fig 7
def fig_shell_graph(path="fig-shell-graph.pdf"):
    pos = {
        (6, 0, 0): (0.0, 5.0), (5, 1, 0): (0.0, 4.0),
        (4, 2, 0): (0.0, 3.0), (4, 1, 1): (-2.05, 2.0),
        (3, 3, 0): (2.05, 2.0), (3, 2, 1): (0.0, 1.0),
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

    fig, ax = plt.subplots(figsize=(1.180 * TW, 3.00))
    blank_axes(ax, (-3.40, 3.40), (-0.20, 6.05))

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
        ax.text(mx + ux * off, my + uy * off, f"${wt}$", fontsize=FS_SUB,
                color=BLUE if hot else GRAY, ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.06", fc="white", ec="none"),
                zorder=6)

    for node, (x, y) in pos.items():
        lab = "(" + ",".join(str(v) for v in node) + ")"
        ax.text(x, y, f"${lab}$\n$J={lens[node]}$", fontsize=FS_SUB,
                ha="center", va="center", linespacing=1.25,
                bbox=dict(boxstyle="round,pad=0.24", fc="white",
                          ec="black", lw=0.6), zorder=7)

    ax.text(0.0, 5.80, r"$\mathcal P_3(6)$ with $t=4$: $\kappa_{3,4,6}=3$",
            fontsize=FS_MAIN, ha="center", va="center")
    ax.plot([-3.30, -2.92], [0.32, 0.32], "-", color=BLUE, lw=1.5)
    ax.text(-2.82, 0.32, r"arc attaining $\kappa$", fontsize=FS_SUB,
            va="center", color=BLUE)
    save(fig, path)


# ----------------------------------------------------------------- fig 8
def fig_middle_section(path="fig-middle-section.pdf"):
    fig, ax = plt.subplots(figsize=(1.026 * TW, 1.482))
    blank_axes(ax, (-1.1, 6.6), (-0.85, 1.55), equal=True)
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
            if hit:
                ax.plot([x], [y], "o", ms=MS_ON, color=ORANGE, zorder=4)
            else:
                ax.plot([x], [y], "o", ms=MS_OFF, mfc="white", mec="#9a9a9a",
                        mew=0.6, zorder=4)
    for x in range(4):
        ax.text(x, -0.30, f"${x}$", fontsize=FS_TINY, color=GRAY, ha="center",
                va="top")
    for y in range(2):
        ax.text(-0.22, y, f"${y}$", fontsize=FS_TINY, color=GRAY, ha="right",
                va="center")
    ax.text(1.5, -0.52, r"$q_1$", fontsize=FS_SUB, ha="center", va="top")
    ax.text(-0.62, 0.5, r"$q_2$", fontsize=FS_SUB, ha="center", va="center")
    ax.text(0.52, 1.42, r"$\Lambda_2$", fontsize=FS_MAIN, color=ORANGE,
            ha="right", va="center")
    ax.text(1.9, 1.36, r"$w=(3,1)$, \ $a=2$", fontsize=FS_MAIN, ha="center")
    ax.plot([3.8, 4.4], [0.92, 0.92], "-", color=BLUE, lw=1.8)
    ax.text(4.55, 0.92, r"meets $\Lambda_2$", fontsize=FS_SUB, va="center")
    ax.plot([3.8, 4.4], [0.50, 0.50], color=LIGHT, lw=1.4,
            ls=(0, (2.5, 1.5)))
    ax.text(4.55, 0.50, r"misses", fontsize=FS_SUB, va="center")
    ax.text(3.8, 0.06, r"$F_1=2$ of $4$ facets", fontsize=FS_SUB, va="center")
    save(fig, path, full=True)


# ----------------------------------------------------------------- fig 9
def fig_case_partition(path="fig-case-partition.pdf"):
    fig, ax = plt.subplots(figsize=(0.924 * TW, 2.220))
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
            ax.text(i + 0.5, j + 0.5, case, fontsize=FS_MAIN, ha="center",
                    va="center")
    for i, lab in enumerate(cols):
        ax.text(i + 0.5, -0.20, lab, fontsize=FS_SUB, ha="center", va="top")
    for j, lab in enumerate(rows):
        ax.text(-0.16, j + 0.5, lab, fontsize=FS_SUB, ha="right", va="center")
    ax.text(2.0, -0.72, r"gap $D=a-b$", fontsize=FS_MAIN, ha="center",
            va="top")
    ax.text(-1.15, 2.5, r"residual mass $c=\|w\|_1$", fontsize=FS_MAIN,
            rotation=90, ha="center", va="center")
    ax.text(2.0, 5.30, r"concentrated residual $w=c\,e_1$", fontsize=FS_MAIN,
            ha="center", va="center")

    ax.add_patch(Rectangle((5.3, 0), 1.5, 5, facecolor=fills["III"],
                           edgecolor="black", lw=0.5))
    ax.text(6.05, 2.5, "III", fontsize=FS_MAIN, ha="center", va="center")
    ax.text(6.05, 5.30, r"spread residual", fontsize=FS_MAIN, ha="center",
            va="center")
    ax.text(6.05, -0.20, r"any $D$, any $c$", fontsize=FS_SUB, ha="center",
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
        ax.text(x + 0.46, y, f"{name}: {desc}", fontsize=FS_SUB, va="center")
    save(fig, path, full=True)


# ----------------------------------------------------------------- fig 10
def fig_rigidity(path="fig-rigidity.pdf"):
    fig, axes = plt.subplots(1, 2, figsize=(0.925 * TW, 1.360),
                             gridspec_kw=dict(width_ratios=[1.0, 1.30],
                                              wspace=0.16))
    ax = axes[0]
    blank_axes(ax, (-0.55, 3.75), (-1.15, 1.35))
    xs = [0.25, 1.6, 2.95]
    labs = [r"$(4,3,1)$", r"$(4,2,2)$", r"$(3,3,2)$"]
    for x, lab in zip(xs, labs):
        ax.text(x, 0.55, lab, fontsize=FS_MAIN, ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.20", fc="white",
                          ec="black", lw=0.6), zorder=5)
    for a, b in zip(xs, xs[1:]):
        arrow(ax, (a + 0.50, 0.55), (b - 0.50, 0.55), color=BLUE, lw=1.5,
              ms=6)
        ax.text((a + b) / 2, 0.80, r"$3$", fontsize=FS_SUB, color=BLUE,
                ha="center")
    arrow(ax, (0.25, 0.22), (2.95, 0.22), color=ORANGE, lw=0.9, rad=0.34,
          ms=6)
    ax.text(1.6, -0.45, r"$6$", fontsize=FS_SUB, color=ORANGE, ha="center")
    ax.text(1.6, -0.78, r"$d_M=1$: no extremal pair", fontsize=FS_SUB,
            color=ORANGE, ha="center", va="top")
    ax.text(1.6, 1.20, r"interior shell: $t=5$, $s=8$, $\kappa=3$",
            fontsize=FS_MAIN, ha="center")

    ax = axes[1]
    blank_axes(ax, (-0.70, 5.30), (-1.15, 1.35))
    xs = [0.25, 1.7, 3.15, 4.6]
    labs = [r"$(6,0,0)$", r"$(5,1,0)$", r"$(4,2,0)$", r"$(3,3,0)$"]
    for x, lab in zip(xs, labs):
        ax.text(x, 0.55, lab, fontsize=FS_MAIN, ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.20", fc="white",
                          ec="black", lw=0.6), zorder=5)
    for a, b in zip(xs, xs[1:]):
        arrow(ax, (a + 0.50, 0.55), (b - 0.50, 0.55), color=BLUE, lw=1.5,
              ms=6)
        ax.text((a + b) / 2, 0.80, r"$1$", fontsize=FS_SUB, color=BLUE,
                ha="center")
    ax.plot([0.25, 0.25, 4.6, 4.6], [0.15, -0.25, -0.25, 0.15], "-",
            color=BLUE, lw=0.7)
    ax.text(2.42, -0.70, r"$d_M=3$, deficit $=3=\kappa\,d_M$: extremal",
            fontsize=FS_SUB, color=BLUE, ha="center", va="top")
    ax.text(2.42, 1.20, r"outermost shell: $t=3$, $s=6$, $\kappa=1$",
            fontsize=FS_MAIN, ha="center")
    save(fig, path, full=True)


# ----------------------------------------------------------------- fig 11
def fig_sharp_constants(path="fig-sharp-constants.pdf"):
    fig, axes = plt.subplots(1, 2, figsize=(1.098 * TW, 1.950),
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
    ax.text(10.35, 1.0, r"$s=2t$", fontsize=FS_TINY, color=BLUE,
            va="center", ha="left")
    ax.text(11.35, 2.0, r"$s=2t+1$", fontsize=FS_TINY, color=ORANGE,
            va="center", ha="left")
    ax.set_xlabel(r"shell weight $s$", fontsize=FS_MAIN, labelpad=1.5)
    ax.set_ylabel(r"sharp constant", fontsize=FS_MAIN, labelpad=1.5)
    ax.set_xlim(1.2, 13.2)
    ax.set_xticks([2, 4, 6, 8, 10, 12])
    ax.tick_params(labelsize=6.5, length=2, pad=1.5)
    ax.legend(fontsize=FS_SUB, frameon=False, loc="lower left",
              handlelength=1.6, borderpad=0.1)
    ax.set_title(r"(a) Lee ball versus cube, $d=3$, $t=5$", fontsize=FS_MAIN,
                 pad=3)
    ax.spines[["top", "right"]].set_visible(False)

    ax = axes[1]
    c = 4
    ts = list(range(1, 2 * c + 1))
    vals = [min(2 * t - 1, 4 * c - 2 * t + 1) for t in ts]
    ax.plot(ts, vals, "o-", color=BLUE, ms=3.0, lw=1.1)
    ax.axhline(2 * c - 1, color=ORANGE, lw=0.6, ls="--")
    ax.text(8.4, 2 * c - 1 + 0.35, r"$2c-1$", fontsize=FS_SUB, color=ORANGE,
            ha="right")
    ax.text(1.75, 5.2, r"$2t-1$", fontsize=FS_SUB, color=BLUE, ha="center")
    ax.text(7.05, 5.2, r"$4c-2t+1$", fontsize=FS_SUB, color=BLUE, ha="center")
    ax.set_xlabel(r"radius $t$ \quad ($c=4$)", fontsize=FS_MAIN, labelpad=1.5)
    ax.set_ylabel(r"transfer increment", fontsize=FS_MAIN, labelpad=1.5)
    ax.set_xlim(0.4, 8.6)
    ax.set_ylim(0, 9.2)
    ax.set_xticks(range(1, 9))
    ax.set_yticks([1, 3, 5, 7])
    ax.tick_params(labelsize=6.5, length=2, pad=1.5)
    ax.set_title(r"(b) capped cross-polytope crossover", fontsize=FS_MAIN, pad=3)
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
    fig, axes = plt.subplots(1, 2, figsize=(1.123 * TW, 1.52),
                             gridspec_kw=dict(width_ratios=[0.86, 1.14],
                                              wspace=0.40))

    ax = axes[0]
    unit = 1.30                       # printed height of one coordinate unit
    blank_axes(ax, (-0.4, 9.3), (-0.30, 5.75))
    step, width = 1.16, 0.62
    groups = [(0.52, [3, 1, 2.4], [r"$3$", r"$1$", r"$s-4$"]),
              (5.52, [2, 0, 3.0], [r"$2$", r"$0$", r"$s-2$"])]
    for x0, heights, labels in groups:
        for k, (h, lab) in enumerate(zip(heights, labels)):
            x = x0 + step * k
            if h > 0:
                ax.add_patch(Rectangle((x, 0), width, unit * h,
                                       facecolor=F_BLUE, edgecolor=BLUE,
                                       lw=0.8))
            if k < 2:
                ax.text(x + width / 2, -0.24, lab, fontsize=FS_SUB, ha="center",
                        va="top")
            else:
                ax.text(x + width / 2, unit * h + 0.16, lab, fontsize=FS_SUB,
                        ha="center", va="bottom")
        ax.add_patch(Rectangle((x0, unit * (heights[0] - 1)), width, unit,
                               facecolor=F_ORANGE, edgecolor=ORANGE, lw=0.8,
                               zorder=3))
        ax.add_patch(Rectangle((x0 + step, unit * heights[1]), width, unit,
                               facecolor="none", edgecolor=ORANGE, lw=0.8,
                               ls=(0, (2.2, 1.4)), zorder=3))
        ax.plot([x0 - 0.18, x0 + 2 * step + width + 0.18], [0, 0], "-",
                color="black", lw=0.7)
        arrow(ax, (x0 + width - 0.04, unit * heights[0] - 0.45),
              (x0 + step + 0.10, unit * (heights[1] + 1) + 0.20),
              color=ORANGE, lw=0.9, rad=-0.42, ms=6.5)
    centers = [x0 + step + width / 2 for x0, _, _ in groups]
    ax.text(centers[0], 5.34, r"recipient one", fontsize=FS_SUB, ha="center",
            color=GRAY)
    ax.text(centers[1], 5.34, r"recipient zero", fontsize=FS_SUB, ha="center",
            color=GRAY)
    ax.text(centers[0], -0.98, r"$\Gamma_b^{(e)}(s-4)$", fontsize=FS_SUB,
            ha="center", va="top")
    ax.text(centers[1], -0.98, r"$\Gamma_b^{(e)}(s-2)$", fontsize=FS_SUB,
            ha="center", va="top")
    ax.text(centers[1], -1.66, r"$+\,2N^{e-1}(2N-s)$", fontsize=FS_SUB,
            ha="center", va="top", color=ORANGE)
    ax.set_title(r"(a) the two competing arcs", fontsize=FS_MAIN, pad=2)

    ax = axes[1]
    ds = list(range(3, 41))
    curves = [(2, 5, BLUE, "o", 13), (3, 7, ORANGE, "s", 24),
              (3, 5, GRAY, "^", 31)]
    for b, s, color, marker, tie in curves:
        theta = [_candidates(b, d, s)[2] for d in ds]
        ax.plot(ds, theta, "-", color=color, lw=0.6, alpha=0.5, zorder=2)
        ax.plot(ds, theta, ".", color=color, ms=1.6, zorder=3)
        ax.plot([tie], [0], marker, color=color, ms=3.6, zorder=4)
        ax.text(41.2, theta[-1], rf"$b={b}$, $s={s}$", fontsize=FS_SUB,
                color=color, ha="left", va="center")
    ax.axhline(0, color="black", lw=0.6, ls="--")
    ax.text(48.5, 40, "$\\Theta>0$:\nrecipient one", fontsize=FS_TINY,
            ha="right", va="center", linespacing=1.35)
    ax.text(3.6, -50, "$\\Theta<0$:\ncanonical edge", fontsize=FS_TINY,
            ha="left", va="center", linespacing=1.35)
    ax.set_xlabel(r"dimension $d\in\mathbb Z_{\ge3}$", fontsize=FS_MAIN,
                  labelpad=1.5)
    ax.set_ylabel(r"$\Theta_{d,b}(s)$", fontsize=FS_MAIN, labelpad=1.5)
    ax.set_xlim(2, 49)
    ax.set_ylim(-62, 78)
    ax.set_xticks([3, 13, 24, 31, 40])
    ax.set_yticks([-40, 0, 40])
    ax.tick_params(labelsize=6.5, length=2, pad=1.5)
    ax.set_title(r"(b) the threshold in every dimension", fontsize=FS_MAIN, pad=2)
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
