"""CLI: print closed-form r_hat and p_c table over (protocol x r) for a given V."""
import argparse

from imvc_audit.stats import expected_stats


def _format_table(V, rates, protocols):
    cell_w = 17  # width of " r_hat   p_c " block
    lines = [f"V={V}"]

    head1 = " " * 6
    for r in rates:
        head1 += f"{f'r={r:g}':^{cell_w}}"
    lines.append(head1)

    head2 = "Proto "
    for _ in rates:
        head2 += f"{'r_hat':>8}{'p_c':>9}"
    lines.append(head2)

    for proto in protocols:
        row = f"{proto:<6}"
        for r in rates:
            s = expected_stats(V, r, proto)
            row += f"{s['r_hat']:>8.3f}{s['p_c']:>9.3f}"
        lines.append(row)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Print (protocol x r) closed-form r_hat and p_c table.",
    )
    parser.add_argument("--V", type=int, required=True, help="Number of views (>=2).")
    parser.add_argument("--rates", type=str, default="0.1,0.3,0.5,0.7",
                        help="Comma-separated nominal missing rates.")
    parser.add_argument("--protocols", type=str, default="P1,P2,P3,P4",
                        help="Comma-separated protocol names.")
    args = parser.parse_args()

    rates = [float(x) for x in args.rates.split(",")]
    protocols = [p.strip().upper() for p in args.protocols.split(",")]
    print(_format_table(args.V, rates, protocols))


if __name__ == "__main__":
    main()
