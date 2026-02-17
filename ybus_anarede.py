import numpy as np
import pandas as pd


def add_ramo(Y, de, para, r_pct, x_pct, b_pct=0.0, tap=1.0, shift_deg=0.0, status=1):
    if status == 0:
        return

    i = de - 1
    k = para - 1

    r = r_pct / 100.0
    x = x_pct / 100.0
    b = b_pct / 100.0

    z = complex(r, x)
    if abs(z) == 0:
        raise ValueError(f"Impedancia nula no ramo {de}-{para}")

    y = 1 / z
    ysh = 1j * (b / 2.0)
    a = tap * np.exp(1j * np.deg2rad(shift_deg))

    Y[i, i] += (y + ysh) / (abs(a) ** 2)
    Y[k, k] += (y + ysh)
    Y[i, k] += -y / np.conj(a)
    Y[k, i] += -y / a


def montar_ybus(n_barras, linhas, transformadores):
    Y = np.zeros((n_barras, n_barras), dtype=complex)

    for ln in linhas:
        add_ramo(
            Y,
            de=ln["de"],
            para=ln["para"],
            r_pct=ln["r_pct"],
            x_pct=ln["x_pct"],
            b_pct=ln.get("b_pct", 0.0),
            tap=ln.get("tap", 1.0),
            shift_deg=ln.get("shift_deg", 0.0),
            status=ln.get("status", 1),
        )

    for tr in transformadores:
        add_ramo(
            Y,
            de=tr["de"],
            para=tr["para"],
            r_pct=tr.get("r_pct", 0.0),
            x_pct=tr["x_pct"],
            b_pct=tr.get("b_pct", 0.0),
            tap=tr.get("tap", 1.0),
            shift_deg=tr.get("shift_deg", 0.0),
            status=tr.get("status", 1),
        )

    return Y


def fmt_br(z, casas=5, tol=1e-10):
    if abs(z) < tol:
        return ""
    re = f"{z.real:.{casas}f}".replace(".", ",")
    im_abs = f"{abs(z.imag):.{casas}f}".replace(".", ",")
    sinal = "+" if z.imag >= 0 else "-"
    return f"{re} {sinal} j{im_abs}"


def imprimir_ybus_em_blocos(Y, casas=5):
    n = Y.shape[0]
    idx = [f"Barra {i}" for i in range(1, n + 1)]
    cols = [f"Barra {j}" for j in range(1, n + 1)]
    dados = [[fmt_br(Y[i, j], casas=casas) for j in range(n)] for i in range(n)]
    df = pd.DataFrame(dados, index=idx, columns=cols)

    print("\nYbus (pu):\n")

    # Config para quebrar em blocos, como no formato da sua imagem
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 95)               # controla quebra em blocos
    pd.set_option("display.expand_frame_repr", True) # mostra com "\" na quebra
    pd.set_option("display.max_colwidth", 26)

    print(df)


if __name__ == "__main__":
    n_barras = 9

    linhas = [
        {"de": 3, "para": 5, "r_pct": 1.7,  "x_pct": 9.2,  "b_pct": 15.8},
        {"de": 3, "para": 8, "r_pct": 1.0,  "x_pct": 8.5,  "b_pct": 17.6},
        {"de": 4, "para": 6, "r_pct": 0.85, "x_pct": 7.2,  "b_pct": 14.9},
        {"de": 4, "para": 7, "r_pct": 0.9,  "x_pct": 7.9,  "b_pct": 16.2},
        {"de": 5, "para": 7, "r_pct": 3.2,  "x_pct": 16.1, "b_pct": 30.6},
        {"de": 6, "para": 8, "r_pct": 1.1,  "x_pct": 8.4,  "b_pct": 25.6},
        {"de": 7, "para": 9, "r_pct": 1.19, "x_pct": 10.08, "b_pct": 20.9},
        {"de": 8, "para": 9, "r_pct": 3.9,  "x_pct": 17.0, "b_pct": 35.8},
    ]

    transformadores = [
        {"de": 1, "para": 3, "r_pct": 0.0, "x_pct": 5.34, "tap": 1.0},
        {"de": 2, "para": 4, "r_pct": 0.0, "x_pct": 7.68, "tap": 1.0},
    ]

    Ybus = montar_ybus(n_barras, linhas, transformadores)
    imprimir_ybus_em_blocos(Ybus, casas=5)
