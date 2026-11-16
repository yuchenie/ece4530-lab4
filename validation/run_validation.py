#!/usr/bin/env python3
"""Reproduce the validated Lab 4 testbenches with Cadence Spectre."""
from pathlib import Path
import argparse
import os
import re
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
CASES = ["dcac", "rout", "swing1", "swing10", "swing15", "swing20",
         "swing25", "swing30", "swing40", "gain10", "unity"]

def replace_line(text, name, line):
    text, count = re.subn(r"^" + re.escape(name) + r"\s+.*$",
                         lambda match: line, text, flags=re.M)
    if count != 1:
        raise ValueError("Expected one {} instance; found {}".format(name, count))
    return text

def make_cases(base):
    cases = {"dcac": base}
    text = replace_line(base, "V0", r"V0 (in\+ 0) vsource dc=Vbias mag=0 type=dc")
    if "\nac ac " not in text:
        raise ValueError("Expected the AC analysis named 'ac'.")
    cases["rout"] = text.replace("\nac ac ",
        "\nITEST (0 out) isource dc=0 mag=1\nac ac ", 1)
    for amplitude in [1, 10, 15, 20, 25, 30, 40]:
        text = replace_line(base, "V0",
            r"V0 (in\+ 0) vsource dc=Vbias type=sine ampl={}u freq=100".format(amplitude))
        text = re.sub(r"^ac ac .*$",
            "tran tran stop=30m maxstep=10u errpreset=conservative", text, flags=re.M)
        cases["swing{}".format(amplitude)] = text
    for kind in ["gain10", "unity"]:
        text = base
        for name in ["E1", "E2", "R0", "R1", "R2", "R3", "C1", "V1"]:
            text = re.sub(r"^" + name + r"\s+.*$\n?", "", text, flags=re.M)
        if kind == "gain10":
            source = r"V0 (in\+ 0) vsource type=pulse val0=1.35 val1=1.45 delay=100n rise=1n fall=1n width=400n period=1u"
            feedback = "\n".join([r"VREF (ref 0) vsource dc=1.4",
                r"RF (out in\-) resistor r=9K", r"RG (in\- ref) resistor r=1K"])
        else:
            source = r"V0 (in\+ 0) vsource type=pulse val0=1.39 val1=1.41 delay=100n rise=200p fall=200p width=400n period=1u"
            feedback = r"RF (out in\-) resistor r=1m"
        text = replace_line(text, "V0", source)
        text = re.sub(r"^ac ac .*$", lambda match: feedback +
            "\ntran tran stop=1.2u maxstep=200p errpreset=conservative", text, flags=re.M)
        cases[kind] = text
    return cases

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--netlist", type=Path, default=HERE / "reference/input.scs",
                        help="ADE input.scs; adjacent .scs includes are copied too")
    parser.add_argument("--output", type=Path, default=HERE / "runs")
    parser.add_argument("--case", choices=CASES, help="Run only this test")
    parser.add_argument("--model", type=Path, help="Override the gpdk045.scs model path")
    parser.add_argument("--spectre", default=os.environ.get("SPECTRE", "spectre"))
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    source = args.netlist.expanduser().resolve()
    root = args.output.expanduser().resolve()
    base = source.read_text()
    if args.model:
        base, count = re.subn(r'include\s+"[^"]*gpdk045\.scs"',
            lambda match: 'include "{}"'.format(args.model.expanduser().resolve()), base)
        if count != 1:
            parser.error("Expected exactly one gpdk045.scs include.")
    cases = make_cases(base)
    selected = [args.case] if args.case else CASES
    root.mkdir(parents=True, exist_ok=True)
    failed = False
    with (root / "validation_status.txt").open("w") as status:
        for name in selected:
            directory = root / name
            directory.mkdir(exist_ok=True)
            for extra in source.parent.glob("*.scs"):
                if extra.name != source.name:
                    shutil.copy2(str(extra), str(directory / extra.name))
            (directory / "input.scs").write_text(cases[name])
            if args.prepare_only:
                message = "{} prepared\n".format(name)
            else:
                with (directory / "stdout.log").open("w") as log:
                    result = subprocess.run([args.spectre, "input.scs", "-raw",
                        "psf", "+log", "spectre.out"], cwd=str(directory),
                        stdout=log, stderr=subprocess.STDOUT)
                failed = failed or result.returncode != 0
                message = "{} exit={}\n".format(name, result.returncode)
            status.write(message)
            status.flush()
            print(message, end="", flush=True)
    return 1 if failed else 0

if __name__ == "__main__":
    raise SystemExit(main())
