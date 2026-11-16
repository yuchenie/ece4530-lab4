# ECE 4530 Lab 4

Cadence Virtuoso library for Lab 4. This whole folder is one Cadence library
named **`lab4`**.

## Contents

| Path | What it is |
| --- | --- |
| `lab4_v1/` | Lab 4 circuit (schematic + symbol) |
| `lab4_testbench/` | Testbench for `lab4_v1` (schematic + Maestro setup) |
| `nmos_characterization/` | NMOS characterization testbench (schematic + Maestro setup) |
| `cdsinfo.tag`, `.oalib`, `data.dm` | Cadence library files. Leave these alone. |

## Setup

1. Clone the repo next to your other Cadence libraries (the folder that has your `cds.lib`):

   ```
   cd ~/ece4530
   git clone git@github.com:yuchenie/ece4530-lab4.git lab4
   ```

2. Add this line to your `cds.lib`, using the full path to the folder you just cloned:

   ```
   DEFINE lab4 /home/<netid>/ece4530/lab4
   ```

   The library name must be `lab4`, because the schematics refer to their cells
   as `lab4/...`. The folder itself can be called anything.

3. Restart Virtuoso, or use View -> Refresh in Library Manager. `lab4` should show up.

4. Before the first simulation, open `lab4_testbench/schematic` and run
   **Check and Save** (Shift+X). Then run `lab4_testbench/maestro`.

## Workflow

```
git pull                      # before you start working
# ...make changes in Cadence, then Check and Save...
git add .
git commit -m "Describe what you changed"
git push
```

- Save (or close) a cellview in Cadence before committing it.
- `.oa` files are binary, so git cannot merge them. If two people edit the same
  cellview at the same time, one person's changes get lost. Coordinate before
  editing a shared cell, work on separate branches, or make your own copy with
  your NetID in the name.
- `.gitignore` keeps Cadence lock files (`*.cdslck*`), `.bak` files, and
  Maestro `results/` and `history/` folders out of the repo.

## Validated circuit handoff

The November 15 version is described in [HANDOFF.txt](HANDOFF.txt).
It includes the final device sizes, operating conditions, measured results,
verification methods, and remaining team tasks.

- Use `lab4_v1/schematic` for the circuit and `lab4_testbench/maestro`
  for the saved DC/AC setup.
- Set Maestro's simulation directory to a writable path under your own
  account. The saved `projectDir` is session-specific.
- [validation/README.txt](validation/README.txt) explains the reference
  netlist, standalone checks, and recorded measurements.
- The PDK, licenses, raw PSF results, and recovery files are not distributed.
  The reference netlist uses Cornell's installed gpdk045 model.

Once the update is available on `main`, an existing clean checkout on that
branch can be updated with:

```
git pull --ff-only origin main
```

For a fresh checkout, use the clone and `cds.lib` steps above.
The library name must remain `lab4`.
