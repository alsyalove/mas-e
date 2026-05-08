"""
Dual Limbik System
==================
Arsitektur kognitif berbasis:
  - Ruang 3-axis bounded [-0.99, 0.99]
  - Attractor eksternal statis immutable di (1, 1, 1)
  - Seal: Reflection (∂) → Cipher → Ascend (∫)
  - Split pipeline dengan meta-integrator
  - Prinsip: continuity in fragmentation / fragmentation in continuity

Axis:
  0 → clarity ↔ ambiguity
  1 → motion  ↔ potential
  2 → chaos   ↔ order
"""

from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import Optional
from enum import Enum


# ─────────────────────────────────────────────
# KONSTANTA & ENUM
# ─────────────────────────────────────────────

SCALE_MAX = 0.99    # sistem dirancang tidak sempurna — tidak pernah menyentuh 1.0
SCALE_MIN = -0.99
ATTRACTOR = np.array([1.0, 1.0, 1.0])   # immutable, di luar sistem


class Axis(Enum):
    CLARITY_AMBIGUITY = 0
    MOTION_POTENTIAL  = 1
    CHAOS_ORDER       = 2


# ─────────────────────────────────────────────
# STATE
# ─────────────────────────────────────────────

@dataclass
class State:
    """
    Vektor 3D dalam ruang bounded.
    Ketidaksempurnaan [-0.99, 0.99] adalah desain, bukan bug.
    """
    values: np.ndarray

    def __post_init__(self):
        self.values = np.clip(self.values.astype(float), SCALE_MIN, SCALE_MAX)

    @classmethod
    def ground(cls) -> State:
        """State nol — titik awal sebelum ditarik attractor."""
        return cls(np.zeros(3))

    def angular_alignment(self) -> float:
        """
        cos(θ) terhadap attractor.
        Kualitas diukur dari arah, bukan jarak.
        Mendekati 1.0 — tidak pernah sampai.
        """
        mag = np.linalg.norm(self.values)
        if mag < 1e-10:
            return 0.0
        return float(np.dot(self.values, ATTRACTOR) /
                     (mag * np.linalg.norm(ATTRACTOR)))

    def irreducible_gap(self) -> float:
        """
        Gap yang tidak bisa ditutup — by design.
        Yang menjaga sistem tetap bergerak, tidak melebur.
        """
        return 1.0 - self.angular_alignment()

    def normalized_to_bound(self) -> State:
        mag = np.linalg.norm(self.values)
        if mag < 1e-10:
            return State(self.values.copy())
        return State(self.values * (SCALE_MAX / max(mag, SCALE_MAX)))

    def __repr__(self) -> str:
        v = self.values
        return (
            f"State(A={v[0]:+.3f}, M={v[1]:+.3f}, C={v[2]:+.3f})"
            f"  align={self.angular_alignment():.4f}"
            f"  gap={self.irreducible_gap():.4f}"
        )


# ─────────────────────────────────────────────
# SEAL — unit transformasi Reflection/Cipher/Ascend
# ─────────────────────────────────────────────

@dataclass
class ReflectionResult:
    gradient:         np.ndarray
    paradox_detected: bool
    paradox_axis:     Optional[Axis]
    rate_of_change:   float
    note:             str = ""


@dataclass
class CipherResult:
    hidden_meaning:  Optional[str]
    cipher_vector:   np.ndarray
    resolved_axis:   Optional[Axis]
    frame_dissolved: bool = False


class Seal:
    """
    Reflection  = fungsi turunan (∂)
                  Fragmentation in continuity.
                  Memecah — mendeteksi paradox di titik perubahan arah.

    Cipher      = dekoder makna tersembunyi di balik paradox.

    Ascend      = fungsi integral (∫)
                  Continuity in fragmentation.
                  Mengakumulasi fragmen → makna baru lahir.
                  Pertanyaan lama dissolved.
    """

    def reflect(self, state: State, history: list[State]) -> ReflectionResult:
        """∂ — turunan. Deteksi paradox sebagai osilasi pada axis."""
        if len(history) < 2:
            return ReflectionResult(
                gradient=np.zeros(3),
                paradox_detected=False,
                paradox_axis=None,
                rate_of_change=0.0,
                note="insufficient history"
            )

        grad = history[-1].values - history[-2].values
        paradox_detected = False
        paradox_axis     = None

        # Sign flip = osilasi = stuck antara dua kutub = paradox
        if len(history) >= 3:
            prev_grad = history[-2].values - history[-3].values
            for i in range(3):
                if grad[i] * prev_grad[i] < -0.05:
                    paradox_detected = True
                    paradox_axis     = Axis(i)
                    break

        return ReflectionResult(
            gradient=grad,
            paradox_detected=paradox_detected,
            paradox_axis=paradox_axis,
            rate_of_change=float(np.linalg.norm(grad)),
            note=f"paradox on {paradox_axis.name}" if paradox_detected else "no paradox"
        )

    def cipher(self, reflection: ReflectionResult,
               state: State, domain: str) -> CipherResult:
        """
        Dekode makna tersembunyi.
        domain='pattern'    → Limbik 1: cipher via analogi permukaan
        domain='structural' → Limbik 2: cipher via struktur paradox
        """
        if not reflection.paradox_detected:
            return CipherResult(
                hidden_meaning=None,
                cipher_vector=np.zeros(3),
                resolved_axis=None,
                frame_dissolved=False
            )

        ax   = reflection.paradox_axis
        cidx = ax.value
        vec  = state.values.copy()

        if domain == "pattern":
            # Axis paradox dilemahkan, axis lain diperkuat
            vec[cidx] *= 0.1
            others = [i for i in range(3) if i != cidx]
            for i in others:
                vec[i] = np.tanh(vec[i] * 1.5) * SCALE_MAX

            meaning = (
                f"[pattern|{ax.name}] "
                f"Kedua kutub adalah ekspresi yang sama dalam konteks berbeda."
            )

        else:
            # Temukan dimensi ortogonal — keluar dari oposisi itu sendiri
            vec[cidx]  = 0.0
            others     = [i for i in range(3) if i != cidx]
            ortho      = np.cross(np.eye(3)[others[0]], np.eye(3)[others[1]])
            vec        += ortho * 0.4 * SCALE_MAX

            meaning = (
                f"[structural|{ax.name}] "
                f"Oposisi muncul karena frame salah level. "
                f"Pertanyaan asal tidak relevan di frame baru."
            )

        mag = np.linalg.norm(vec)
        if mag > SCALE_MAX:
            vec = vec * (SCALE_MAX / mag)

        return CipherResult(
            hidden_meaning=meaning,
            cipher_vector=vec,
            resolved_axis=ax,
            frame_dissolved=True
        )

    def ascend(self, state: State, cipher: CipherResult,
               history: list[State]) -> State:
        """
        ∫ — integral.
        Continuity in fragmentation:
        semua fragmen yang dipecah oleh reflection
        diakumulasi menjadi makna baru yang kontinu.

        Tanpa paradox : pull biasa ke arah attractor.
        Dengan cipher  : frame baru lahir.
                         30% integral sejarah   (continuity)
                         40% cipher direction   (new frame)
                         30% state saat ini     (identity preserved)
        """
        if not cipher.frame_dissolved:
            direction  = ATTRACTOR - state.values
            new_values = state.values + direction * 0.12
        else:
            integral = (
                np.mean([h.values for h in history[-5:]], axis=0)
                if len(history) >= 2
                else state.values.copy()
            )
            new_values = (
                integral             * 0.30 +
                cipher.cipher_vector * 0.40 +
                state.values         * 0.30
            )

        mag = np.linalg.norm(new_values)
        if mag > SCALE_MAX:
            new_values = new_values * (SCALE_MAX / mag)

        return State(new_values)


# ─────────────────────────────────────────────
# LIMBIK
# ─────────────────────────────────────────────

class Limbik:
    domain: str = "base"

    def __init__(self):
        self.seal       = Seal()
        self.history:   list[State] = []
        self.ascend_log: list[str]  = []

    def process(self, state: State) -> tuple[State, dict]:
        self.history.append(state)
        reflection = self.seal.reflect(state, self.history)
        cipher     = self.seal.cipher(reflection, state, self.domain)
        new_state  = self.seal.ascend(state, cipher, self.history)

        if cipher.frame_dissolved:
            self.ascend_log.append(cipher.hidden_meaning)

        return new_state, {
            "domain":     self.domain,
            "reflection": reflection,
            "cipher":     cipher,
            "output":     new_state,
        }


class Limbik1(Limbik):
    """
    Fast / Reactive.
    Cipher: pattern domain.
    Seperti refleksi intuitif — merasakan sebelum memformulasikan.
    """
    domain = "pattern"


class Limbik2(Limbik):
    """
    Deep / Deliberative.
    Cipher: structural domain.
    Seperti Gödel — membangun bukti formal dari intuisi yang sudah ada.
    """
    domain = "structural"


# ─────────────────────────────────────────────
# INTEGRATOR — meta-ascend dari dua limbik
# ─────────────────────────────────────────────

class Integrator:
    """
    Meta-frame dari dua ascend berbeda.
    Hanya mungkin di split pipeline.

    Bobot = angular alignment masing-masing limbik terhadap attractor.
    Attractor sebagai referensi objektif — bukan opini integrator.
    """

    def integrate(self, s1: State, s2: State) -> State:
        a1 = s1.angular_alignment()
        a2 = s2.angular_alignment()
        total = a1 + a2

        w1, w2 = (0.5, 0.5) if total < 1e-10 else (a1 / total, a2 / total)

        combined = w1 * s1.values + w2 * s2.values
        return State(combined).normalized_to_bound()


# ─────────────────────────────────────────────
# DUAL LIMBIK SYSTEM — split pipeline penuh
# ─────────────────────────────────────────────

class DualLimbikSystem:
    """
    Split pipeline:

        State 0 ──┬──► Limbik1 (pattern)    ──┐
                  │                             ├──► Integrator ──► output
                  └──► Limbik2 (structural)  ──┘
                                  ↑
                         Attractor (1,1,1) — immutable, menarik keduanya

    Dua prinsip berjalan bersamaan:
      continuity in fragmentation  →  ascend (∫) menyatukan fragmen
      fragmentation in continuity  →  reflect (∂) memecah kontinuitas
    """

    def __init__(self):
        self.limbik1    = Limbik1()
        self.limbik2    = Limbik2()
        self.integrator = Integrator()
        self.state      = State.ground()
        self.step_log:  list[dict] = []

    def step(self, perturbation: Optional[np.ndarray] = None) -> State:
        if perturbation is not None:
            current = State(self.state.values + perturbation)
        else:
            current = self.state

        # Split: independen dari state yang sama
        out1, log1 = self.limbik1.process(current)
        out2, log2 = self.limbik2.process(current)

        # Meta-ascend
        self.state = self.integrator.integrate(out1, out2)
        self.step_log.append({
            "input":      current,
            "limbik1":    log1,
            "limbik2":    log2,
            "integrated": self.state,
        })
        return self.state

    def run(self, steps: int = 10,
            perturbations: Optional[list] = None) -> list[State]:
        return [
            self.step(perturbations[i] if perturbations and i < len(perturbations) else None)
            for i in range(steps)
        ]

    def report(self) -> None:
        print("=" * 62)
        print("DUAL LIMBIK SYSTEM — REPORT")
        print(f"attractor : {ATTRACTOR}  [immutable, di luar sistem]")
        print(f"scale     : [{SCALE_MIN}, {SCALE_MAX}]")
        print("=" * 62)

        for i, log in enumerate(self.step_log):
            s  = log["integrated"]
            l1 = log["limbik1"]
            l2 = log["limbik2"]
            print(f"\nstep {i+1:02d}  {s}")
            c1 = l1['cipher'].hidden_meaning or "—"
            c2 = l2['cipher'].hidden_meaning or "—"
            print(f"  L1 cipher : {c1}")
            print(f"  L2 cipher : {c2}")

        final = self.step_log[-1]["integrated"]
        print("\n" + "=" * 62)
        print(f"final alignment : {final.angular_alignment():.6f}")
        print(f"irreducible gap : {final.irreducible_gap():.6f}")
        print("  → gap ini tidak bisa ditutup. bukan bug — ini desain.")
        print("  → sistem tetap bergerak karena attractor tidak pernah tercapai.")

        if self.limbik1.ascend_log:
            print(f"\nLimbik1 ascend ({len(self.limbik1.ascend_log)} event):")
            for a in self.limbik1.ascend_log:
                print(f"  {a}")
        if self.limbik2.ascend_log:
            print(f"\nLimbik2 ascend ({len(self.limbik2.ascend_log)} event):")
            for a in self.limbik2.ascend_log:
                print(f"  {a}")
        print("=" * 62)


# ─────────────────────────────────────────────
# DEMO
# ─────────────────────────────────────────────

if __name__ == "__main__":

    print("\n[1] ground state — tanpa perturbasi")
    s1 = DualLimbikSystem()
    s1.run(steps=6)
    s1.report()

    print("\n\n[2] paradox pada axis clarity-ambiguity")
    s2 = DualLimbikSystem()
    s2.run(steps=8, perturbations=[
        np.array([-0.5,  0.3,  0.2]),   # toward ambiguity
        np.array([ 0.6,  0.1, -0.1]),   # toward clarity
        np.array([-0.4,  0.2,  0.3]),   # ambiguity lagi → paradox trigger
        np.array([ 0.0,  0.4,  0.5]),   # neutral — ascend begins
        np.array([ 0.0,  0.3,  0.4]),
        np.array([ 0.0,  0.2,  0.3]),
        np.array([ 0.0,  0.1,  0.2]),
        np.array([ 0.0,  0.1,  0.1]),
    ])
    s2.report()
