"""Reproduce selected Java behavior without changing the original checkout.

Usage: python tools/legacy_probe.py /path/to/legacy-checkout > tests/fixtures/legacy-results.json
Requires Java 17+ with the jdk.compiler module. No JUnit or external JARs needed.
Encoding normalization occurs only in a temporary copy (the repo mixes encodings).
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

PROBE = r"""
import util.hypercomplex.ultracomplex.Ultra;
class LegacyProbe {
    static void show(String name, Ultra value) {
        System.out.print(name + "|");
        for (int k = 0; k < 8; k++) {
            if (k > 0) System.out.print(",");
            System.out.print(value.getDouble(k));
        }
        System.out.println();
    }
    public static void main(String[] args) {
        Ultra a = new Ultra(1, 1, 1, -1, 0, 0, 0, 0);
        show("invertible_inverse", a.inverse());
        show("invertible_conjugate", a.conjugate());
        show("negative_real_log", new Ultra(-1).ln());
        show("zero_squared", Ultra.ZERO.pow(new Ultra(2)));
        Ultra d = new Ultra(0, 0, 0, 0, 1, 0, 0, 0);
        show("eps_squared", d.pow(new Ultra(2)));
        Ultra oldBug = new Ultra(.2, .2, .2, .2, 0, 0, 0, 0);
        show("old_bug_csc", oldBug.csc());
        Ultra x = new Ultra(2, 3, 5, 7, 11, 13, 17, 19);
        Ultra y = new Ultra(3, 5, 7, 11, 13, 17, 19, 2);
        show("addition", x.plus(y));
        show("multiplication", x.times(y));
        show("small_inverse", x.times(1e-10).inverse());
        show("large_inverse", x.times(1e10).inverse());
        for (int i=0; i<8; ++i) for (int j=0; j<8; ++j)
            show("basis_"+i+"_"+j, Ultra.unit(i).times(Ultra.unit(j)));
    }
}
"""


def main():
    legacy = Path(sys.argv[1]).resolve()
    commit = subprocess.check_output(
        ["git", "-C", str(legacy), "rev-parse", "HEAD"], text=True
    ).strip()
    encodings = {}
    with tempfile.TemporaryDirectory() as directory:
        temp = Path(directory)
        for path in (legacy / "src").rglob("*.java"):
            data = path.read_bytes()
            try:
                text = data.decode("utf-8")
                encoding = "utf-8"
            except UnicodeDecodeError:
                text = data.decode("cp1252")
                encoding = "cp1252"
            encodings[encoding] = encodings.get(encoding, 0) + 1
            target = temp / path.relative_to(legacy)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
        probe = temp / "LegacyProbe.java"
        probe.write_text(PROBE, encoding="utf-8")
        subprocess.run(
            [
                "java",
                "-m",
                "jdk.compiler/com.sun.tools.javac.Main",
                "-encoding",
                "UTF-8",
                "-d",
                str(temp / "classes"),
                "-sourcepath",
                str(temp / "src"),
                str(probe),
            ],
            check=True,
            timeout=60,
        )
        output = subprocess.check_output(
            ["java", "-cp", str(temp / "classes"), "LegacyProbe"], text=True, timeout=60
        )
    cases = {}
    for line in output.splitlines():
        name, numbers = line.split("|")
        cases[name] = [
            float(x) if x not in ("NaN", "Infinity", "-Infinity") else x for x in numbers.split(",")
        ]
    print(
        json.dumps(
            {"source_commit": commit, "source_encodings": encodings, "cases": cases},
            indent=2,
            allow_nan=False,
        )
    )


if __name__ == "__main__":
    main()
