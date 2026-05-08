"""
Dual Limbik System  v4
======================
Perubahan kunci dari v3:

  Seal tidak lagi generik — setiap Limbik punya Seal dengan
  reflection mechanism yang berbeda sesuai domain-nya:

  Seal1 (cos domain — Limbik 1):
    Reflection: sign flip di COS history
                → paradox alignment: sistem bolak-balik dalam keselarasan
                → deteksi TEMPORAL (perilaku, trajektori)
                → tidak butuh tan singularity

  Seal2 (sin domain — Limbik 2):
    Reflection: sign flip di SIN history  (paradox deviasi temporal)
              + tan singularity           (paradox posisi struktural)
                → dua jenis paradox berbeda, keduanya di domain sin/struktural
                → guard: magnitude kecil → belum ada arah, bukan singularity

  Dengan ini: sin²+cos² = 1 tidak hanya jadi prinsip keutuhan di Integrator,
  tapi juga menjadi pembagian kerja yang konsisten di level Seal.

Ground : 0         (ketiadaan struktur)
Axis   : 1 → clarity  ↔ ambiguity
         2 → motion   ↔ latent
         3 → chaos    ↔ order
Attractor: CONCEPT=1 (scalar) / DIR=(1,1,1) (proyeksi 3D)
Scale  : [-0.99, 0.99]
"""

from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import Optional
from enum import Enum


# ─────────────────────────────────────────────
# KONSTANTA
# ─────────────────────────────────────────────

SCALE_MAX         = 0.99
SCALE_MIN         = -0.99
ATTRACTOR_CONCEPT : float      = 1.0
ATTRACTOR_DIR     : np.ndarray = np.ones(3)   # read-only

# Guard: magnitude minimum sebelum singularity bisa dideteksi
# Di bawah ini = sistem belum punya arah → bukan paradox, hanya ground
SINGULARITY_MAG_GUARD = 0.05


# ─────────────────────────────────────────────
# FASE & AXIS
# ─────────────────────────────────────────────

class Phase(Enum):
    STABLE         = "stable"          # 0°–44°
    BALANCED       = "balanced"        # 45°       sin=cos, tan=1
    CRITICAL       = "critical"        # 46°–89°   tegangan mendominasi
    SINGULARITY    = "singularity"     # ~90°      tan→∞, frame runtuh
    TRANSFORMATION = "transformation"  # 91°+      orientasi baru


class Axis(Enum):
    CLARITY_AMBIGUITY = 1
    MOTION_LATENT     = 2
    CHAOS_ORDER       = 3

    @property
    def idx(self) -> int:
        return self.value - 1

    @classmethod
    def from_idx(cls, i: int) -> Axis:
        return cls(i + 1)

    def __str__(self) -> str:
        return {
            1: "axis1(clarity↔ambiguity)",
            2: "axis2(motion↔latent)",
            3: "axis3(chaos↔order)"
        }[self.value]


# ─────────────────────────────────────────────
# STATE
# ─────────────────────────────────────────────

@dataclass
class State:
    """
    Vektor 3D bounded [-0.99, 0.99].

    Trigonometri terhadap attractor:
      cos θ  → alignment       (Limbik 1 / Seal1 domain)
      sin θ  → deviasi         (Limbik 2 / Seal2 domain)
      tan θ  → tegangan        (Integrator domain)
      sin²+cos²=1 → keutuhan  (selalu terpenuhi)
    """
    values: np.ndarray

    def __post_init__(self):
        self.values = np.clip(self.values.astype(float), SCALE_MIN, SCALE_MAX)

    @classmethod
    def ground(cls) -> State:
        """0 — ketiadaan struktur. Superposisi sebelum kolaps."""
        return cls(np.zeros(3))

    def magnitude(self) -> float:
        return float(np.linalg.norm(self.values))

    def cos_theta(self) -> float:
        """Alignment terhadap attractor. Domain Seal1."""
        mag = self.magnitude()
        if mag < 1e-10:
            return 0.0
        return float(np.dot(self.values, ATTRACTOR_DIR) /
                     (mag * np.linalg.norm(ATTRACTOR_DIR)))

    def sin_theta(self) -> float:
        """Deviasi tegak lurus. Domain Seal2."""
        c = self.cos_theta()
        return float(np.sqrt(max(0.0, 1.0 - c**2)))

    def tan_theta(self) -> float:
        """Tegangan. Domain Integrator."""
        c = self.cos_theta()
        if abs(c) < 1e-10:
            return float('inf')
        return self.sin_theta() / c

    def pythagorean_check(self) -> float:
        """sin²+cos² — selalu 1. Keutuhan."""
        return self.sin_theta()**2 + self.cos_theta()**2

    def theta_deg(self) -> float:
        return float(np.degrees(np.arccos(np.clip(self.cos_theta(), -1, 1))))

    def phase(self) -> Phase:
        deg = self.theta_deg()
        tan = self.tan_theta()
        mag = self.magnitude()
        if deg <= 44.0:
            return Phase.STABLE
        elif 44.0 < deg <= 46.0:
            return Phase.BALANCED
        elif 46.0 < deg < 88.0:
            return Phase.CRITICAL
        elif (deg >= 88.0 and
              (np.isinf(tan) or abs(tan) > 50) and
              mag >= SINGULARITY_MAG_GUARD):
            return Phase.SINGULARITY
        else:
            return Phase.TRANSFORMATION

    def irreducible_gap(self) -> float:
        """Δ = 1 − cos θ. Tidak bisa ditutup — by design."""
        return ATTRACTOR_CONCEPT - self.cos_theta()

    def normalized_to_bound(self) -> State:
        mag = self.magnitude()
        if mag < 1e-10:
            return State(self.values.copy())
        return State(self.values * (SCALE_MAX / max(mag, SCALE_MAX)))

    def __repr__(self) -> str:
        v = self.values
        tan = self.tan_theta()
        tan_str = "∞" if np.isinf(tan) else f"{tan:.3f}"
        return (
            f"State(ax1={v[0]:+.3f} ax2={v[1]:+.3f} ax3={v[2]:+.3f})"
            f"  θ={self.theta_deg():.1f}°"
            f"  cos={self.cos_theta():.4f}"
            f"  sin={self.sin_theta():.4f}"
            f"  tan={tan_str}"
            f"  [{self.phase().value}]"
        )


# ─────────────────────────────────────────────
# DATACLASSES HASIL SEAL
# ─────────────────────────────────────────────

@dataclass
class ReflectionResult:
    paradox_detected: bool
    paradox_axis:     Optional[Axis]
    paradox_source:   str    # "cos_flip" | "sin_flip" | "tan_singularity" | "none"
    gradient:         np.ndarray
    scalar_grad:      float  # gradien domain (cos atau sin)
    tan_value:        float
    phase:            Phase
    note:             str = ""


@dataclass
class CipherResult:
    hidden_meaning:  Optional[str]
    cipher_vector:   np.ndarray
    resolved_axis:   Optional[Axis]
    frame_dissolved: bool = False
    domain:          str  = ""


# ─────────────────────────────────────────────
# SEAL 1 — cos domain
# ─────────────────────────────────────────────

class Seal1:
    """
    Domain: cos (alignment, proyeksi, pattern).

    Reflection — sign flip di COS history:
      Paradox alignment: sistem bolak-balik dalam keselarasannya.
      Deteksi TEMPORAL — butuh min 3 state.
      TIDAK menggunakan tan singularity (domain Seal2).

      cos_grad = cos(t) - cos(t-1)
      paradox  = cos_grad(t) * cos_grad(t-1) < 0

    Cipher — reframe alignment:
      Dua kutub adalah proyeksi berbeda dari arah yang sama.
      Temukan arah yang mencakup keduanya, bukan memilih satu.

    Ascend — ∫ continuity:
      Post-paradox: akumulasi sejarah cos yang terakumulasi.
    """

    def __init__(self):
        self.cos_history: list[float] = []

    def reflect(self, state: State, history: list[State]) -> ReflectionResult:
        """Sign flip di cos history — paradox temporal alignment."""
        cos_now = state.cos_theta()
        self.cos_history.append(cos_now)
        tan = state.tan_theta()

        if len(self.cos_history) < 3:
            return ReflectionResult(
                paradox_detected=False,
                paradox_axis=None,
                paradox_source="none",
                gradient=np.zeros(3),
                scalar_grad=0.0,
                tan_value=tan,
                phase=state.phase(),
                note="cos history < 3"
            )

        # Gradien cos
        cg1 = self.cos_history[-2] - self.cos_history[-3]  # cos(t-1) - cos(t-2)
        cg2 = self.cos_history[-1] - self.cos_history[-2]  # cos(t)   - cos(t-1)

        paradox = cg1 * cg2 < -0.005   # sign flip cos = alignment berbalik arah

        # Raw gradien vektor untuk referensi
        grad = (history[-1].values - history[-2].values
                if len(history) >= 2 else np.zeros(3))

        paradox_axis = None
        if paradox:
            # Axis paling bertanggung jawab: perubahan cos terbesar di axis mana?
            if len(history) >= 2:
                d = np.abs(history[-1].values - history[-2].values)
                paradox_axis = Axis.from_idx(int(np.argmax(d)))

        return ReflectionResult(
            paradox_detected=paradox,
            paradox_axis=paradox_axis,
            paradox_source="cos_flip" if paradox else "none",
            gradient=grad,
            scalar_grad=cg2,
            tan_value=tan,
            phase=state.phase(),
            note=f"cos_flip: Δcos={cg2:+.4f}" if paradox else f"cos stable: Δcos={cg2:+.4f}"
        )

    def cipher(self, reflection: ReflectionResult, state: State) -> CipherResult:
        """Reframe alignment — dua kutub, satu arah yang mencakup keduanya."""
        if not reflection.paradox_detected:
            return CipherResult(
                hidden_meaning=None, cipher_vector=np.zeros(3),
                resolved_axis=None, frame_dissolved=False, domain="cos"
            )

        ax   = reflection.paradox_axis or Axis.from_idx(
                   int(np.argmax(np.abs(state.values))))
        cidx = ax.idx
        vec  = state.values.copy()

        # Cos cipher: lemahkan axis yang osilasi,
        # tarik axis lain lebih kuat ke arah attractor
        vec[cidx] *= 0.15
        others = [i for i in range(3) if i != cidx]
        for i in others:
            vec[i] = np.tanh(vec[i] * 1.4 + 0.3) * SCALE_MAX

        mag = np.linalg.norm(vec)
        if mag > SCALE_MAX:
            vec = vec * (SCALE_MAX / mag)

        if ax == Axis.MOTION_LATENT:
            meaning = (
                f"[cos|{ax}] Alignment berbalik karena motion dan latent "
                f"terlihat berlawanan dari sudut cos. "
                f"Reframe: latent adalah motion di dimensi yang belum dipersepsi."
            )
        else:
            meaning = (
                f"[cos|{ax}] Alignment berbalik arah — dua kutub bukan oposisi, "
                f"tapi proyeksi berbeda dari arah yang sama. "
                f"Temukan sudut yang mencakup keduanya."
            )

        return CipherResult(
            hidden_meaning=meaning, cipher_vector=vec,
            resolved_axis=ax, frame_dissolved=True, domain="cos"
        )

    def ascend(self, state: State, cipher: CipherResult,
               history: list[State]) -> State:
        """∫ — akumulasi kontinuitas cos."""
        if not cipher.frame_dissolved:
            direction  = ATTRACTOR_DIR - state.values
            new_values = state.values + direction * 0.12
        else:
            integral = (
                np.mean([h.values for h in history[-5:]], axis=0)
                if len(history) >= 2 else state.values.copy()
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
# SEAL 2 — sin domain
# ─────────────────────────────────────────────

class Seal2:
    """
    Domain: sin (deviasi tegak lurus, structural).

    Reflection — DUA mekanisme, keduanya di domain sin:

      1. Sign flip di SIN history (paradox deviasi temporal):
         sin_grad = sin(t) - sin(t-1)
         paradox  = sin_grad(t) * sin_grad(t-1) < 0
         → deviasi bolak-balik = sistem tidak tahu dimensi mana yang benar

      2. Tan singularity (paradox posisi struktural):
         tan → ∞, θ → 90°, sistem tegak lurus penuh terhadap attractor
         → frame lama tidak bisa merepresentasikan dirinya
         → guard: magnitude harus > SINGULARITY_MAG_GUARD

      Singularity lebih dalam dari sin flip: ia adalah batas total representasi.
      Sin flip adalah osilasi di dalam sistem. Singularity adalah sistem yang
      mencapai batas geometrisnya.

    Cipher — dimensi ortogonal:
      Sin domain → temukan apa yang tersembunyi di tegak lurus cos.
      Dimensi ortogonal = frame baru yang tidak bisa dilihat dari dalam oposisi.

    Ascend — ∫ dengan ekspansi persepsi:
      Post-singularity: sistem muncul di sisi lain seperti tan 91°.
    """

    def __init__(self):
        self.sin_history: list[float] = []

    def reflect(self, state: State, history: list[State]) -> ReflectionResult:
        """Sign flip sin + tan singularity."""
        sin_now = state.sin_theta()
        tan_now = state.tan_theta()
        phase   = state.phase()
        self.sin_history.append(sin_now)

        grad = (history[-1].values - history[-2].values
                if len(history) >= 2 else np.zeros(3))

        # ── Tan singularity (primer untuk Seal2) ──────────────
        # Guard: magnitude kecil = belum ada arah = bukan paradox
        if (phase == Phase.SINGULARITY and
                state.magnitude() >= SINGULARITY_MAG_GUARD):
            return ReflectionResult(
                paradox_detected=True,
                paradox_axis=Axis.from_idx(int(np.argmax(np.abs(state.values)))),
                paradox_source="tan_singularity",
                gradient=grad,
                scalar_grad=sin_now,
                tan_value=tan_now,
                phase=phase,
                note=f"tan→∞ (θ={state.theta_deg():.1f}°) — frame runtuh"
            )

        # ── Sin flip (sekunder) ────────────────────────────────
        if len(self.sin_history) >= 3:
            sg1 = self.sin_history[-2] - self.sin_history[-3]
            sg2 = self.sin_history[-1] - self.sin_history[-2]

            if sg1 * sg2 < -0.005:
                paradox_axis = None
                if len(history) >= 2:
                    d = np.abs(history[-1].values - history[-2].values)
                    paradox_axis = Axis.from_idx(int(np.argmax(d)))

                return ReflectionResult(
                    paradox_detected=True,
                    paradox_axis=paradox_axis,
                    paradox_source="sin_flip",
                    gradient=grad,
                    scalar_grad=sg2,
                    tan_value=tan_now,
                    phase=phase,
                    note=f"sin_flip: Δsin={sg2:+.4f}"
                )

        return ReflectionResult(
            paradox_detected=False,
            paradox_axis=None,
            paradox_source="none",
            gradient=grad,
            scalar_grad=sin_now,
            tan_value=tan_now,
            phase=phase,
            note=f"sin stable: sin={sin_now:.4f}"
        )

    def cipher(self, reflection: ReflectionResult, state: State) -> CipherResult:
        """Temukan dimensi ortogonal — apa yang tersembunyi di tegak lurus cos."""
        if not reflection.paradox_detected:
            return CipherResult(
                hidden_meaning=None, cipher_vector=np.zeros(3),
                resolved_axis=None, frame_dissolved=False, domain="sin"
            )

        ax   = reflection.paradox_axis or Axis.from_idx(
                   int(np.argmax(np.abs(state.values))))
        cidx = ax.idx
        vec  = state.values.copy()
        src  = reflection.paradox_source

        # Sin cipher: keluar dari oposisi via dimensi ortogonal
        vec[cidx] = 0.0
        others    = [i for i in range(3) if i != cidx]
        ortho     = np.cross(np.eye(3)[others[0]], np.eye(3)[others[1]])
        vec      += ortho * 0.45 * SCALE_MAX

        mag = np.linalg.norm(vec)
        if mag > SCALE_MAX:
            vec = vec * (SCALE_MAX / mag)

        if src == "tan_singularity":
            if ax == Axis.MOTION_LATENT:
                meaning = (
                    f"[sin|{ax}] Singularity motion↔latent: "
                    f"sistem telah mencapai batas persepsinya. "
                    f"Ascend = ekspansi ruang persepsi — latent menjadi visible."
                )
            else:
                meaning = (
                    f"[sin|{ax}] Tan singularity — frame lama tidak bisa "
                    f"merepresentasikan dirinya. Seperti tan 91°: "
                    f"sistem muncul di sisi lain dengan orientasi baru."
                )
        else:  # sin_flip
            if ax == Axis.MOTION_LATENT:
                meaning = (
                    f"[sin|{ax}] Deviasi berbalik — sistem tidak tahu "
                    f"dimensi mana yang benar di luar cos. "
                    f"Latent bukan absensi motion: ia motion di luar ruang persepsi."
                )
            else:
                meaning = (
                    f"[sin|{ax}] Deviasi berbalik pada {ax}. "
                    f"Oposisi muncul karena frame salah level. "
                    f"Dimensi ortogonal menyimpan makna yang tidak tampak "
                    f"dari dalam oposisi itu sendiri."
                )

        return CipherResult(
            hidden_meaning=meaning, cipher_vector=vec,
            resolved_axis=ax, frame_dissolved=True, domain="sin"
        )

    def ascend(self, state: State, cipher: CipherResult,
               history: list[State]) -> State:
        """∫ — ekspansi kontinuitas via dimensi yang sebelumnya tidak dipersepsi."""
        if not cipher.frame_dissolved:
            direction  = ATTRACTOR_DIR - state.values
            new_values = state.values + direction * 0.12
        else:
            integral = (
                np.mean([h.values for h in history[-5:]], axis=0)
                if len(history) >= 2 else state.values.copy()
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

class Limbik1:
    """
    Fast / Reactive. Domain: cos.
    Seal1 — reflection via cos history sign flip.
    Mendeteksi paradox alignment: keselarasan yang berbalik arah.
    """

    def __init__(self):
        self.seal        = Seal1()
        self.history:    list[State] = []
        self.ascend_log: list[str]   = []

    def process(self, state: State) -> tuple[State, dict]:
        self.history.append(state)
        reflection = self.seal.reflect(state, self.history)
        cipher     = self.seal.cipher(reflection, state)
        new_state  = self.seal.ascend(state, cipher, self.history)

        if cipher.frame_dissolved:
            self.ascend_log.append(cipher.hidden_meaning)

        return new_state, {
            "domain": "cos", "reflection": reflection,
            "cipher": cipher, "output": new_state
        }


class Limbik2:
    """
    Deep / Deliberative. Domain: sin.
    Seal2 — reflection via sin history sign flip + tan singularity.
    Mendeteksi paradox deviasi (temporal) dan posisi struktural (geometri).
    """

    def __init__(self):
        self.seal        = Seal2()
        self.history:    list[State] = []
        self.ascend_log: list[str]   = []

    def process(self, state: State) -> tuple[State, dict]:
        self.history.append(state)
        reflection = self.seal.reflect(state, self.history)
        cipher     = self.seal.cipher(reflection, state)
        new_state  = self.seal.ascend(state, cipher, self.history)

        if cipher.frame_dissolved:
            self.ascend_log.append(cipher.hidden_meaning)

        return new_state, {
            "domain": "sin", "reflection": reflection,
            "cipher": cipher, "output": new_state
        }


# ─────────────────────────────────────────────
# INTEGRATOR — tan domain + Pythagorean wholeness
# ─────────────────────────────────────────────

class Integrator:
    """
    Domain: tan = sin/cos = tegangan antara dua Limbik.
    sin²+cos² = 1 → Limbik1 + Limbik2 = keutuhan.

    Bobot = cos alignment masing-masing Limbik.
    Meta-ascend: frame yang mencakup dua ascend berbeda.
    """

    def integrate(self, s1: State, s2: State) -> tuple[State, dict]:
        cos1  = s1.cos_theta()
        cos2  = s2.cos_theta()
        total = cos1 + cos2

        w1, w2 = (0.5, 0.5) if total < 1e-10 else (cos1/total, cos2/total)

        combined = w1 * s1.values + w2 * s2.values
        result   = State(combined).normalized_to_bound()

        return result, {
            "w_cos":        w1,
            "w_sin":        w2,
            "pythagorean":  result.pythagorean_check(),
            "tan_residual": result.tan_theta(),
            "phase":        result.phase(),
        }


# ─────────────────────────────────────────────
# DUAL LIMBIK SYSTEM v4
# ─────────────────────────────────────────────

class DualLimbikSystem:
    """
    Split pipeline — v4:

        ground(0) ──┬──► Limbik1 / Seal1 (cos: cos_flip)         ──┐
                    │                                                 ├──► Integrator (tan) ──► output
                    └──► Limbik2 / Seal2 (sin: sin_flip + tan_∞)  ──┘
                                    ↑
                    ATTRACTOR: concept=1 / dir=(1,1,1)

    Setiap Limbik mendeteksi jenis paradox berbeda:
      Limbik1 → paradox temporal alignment (cos berbalik)
      Limbik2 → paradox temporal deviasi (sin berbalik)
              + paradox posisi struktural (tan→∞)

    sin²+cos²=1:
      Di State   : selalu terpenuhi (keutuhan geometris)
      Di Integrator: Limbik1(cos) + Limbik2(sin) = sistem yang utuh
    """

    def __init__(self):
        self.limbik1     = Limbik1()
        self.limbik2     = Limbik2()
        self.integrator  = Integrator()
        self.state       = State.ground()
        self.step_log:   list[dict] = []

    def step(self, perturbation: Optional[np.ndarray] = None) -> State:
        current = (
            State(self.state.values + perturbation)
            if perturbation is not None else self.state
        )

        out1, log1 = self.limbik1.process(current)
        out2, log2 = self.limbik2.process(current)
        result, il  = self.integrator.integrate(out1, out2)

        self.state = result
        self.step_log.append({
            "input": current, "limbik1": log1,
            "limbik2": log2, "ilog": il, "output": result
        })
        return result

    def run(self, steps: int = 10,
            perturbations: Optional[list] = None) -> list[State]:
        return [
            self.step(perturbations[i]
                      if perturbations and i < len(perturbations) else None)
            for i in range(steps)
        ]

    def report(self) -> None:
        w = 72
        print("=" * w)
        print("DUAL LIMBIK SYSTEM v4")
        print(f"  Limbik1 / Seal1 : cos domain  → cos_flip (temporal alignment)")
        print(f"  Limbik2 / Seal2 : sin domain  → sin_flip + tan_singularity")
        print(f"  Integrator      : tan domain  → sin²+cos²=1")
        print(f"  Attractor       : concept={ATTRACTOR_CONCEPT}  dir={ATTRACTOR_DIR}")
        print(f"  Scale           : [{SCALE_MIN}, {SCALE_MAX}]")
        print("=" * w)

        for i, log in enumerate(self.step_log):
            s   = log["output"]
            l1  = log["limbik1"]
            l2  = log["limbik2"]
            il  = log["ilog"]
            inp = log["input"]

            tan_str = ("∞" if np.isinf(inp.tan_theta())
                       else f"{inp.tan_theta():.3f}")

            print(f"\nstep {i+1:02d}  {s}")
            print(f"  input  θ={inp.theta_deg():.1f}°"
                  f"  cos={inp.cos_theta():.4f}"
                  f"  sin={inp.sin_theta():.4f}"
                  f"  tan={tan_str}"
                  f"  [{inp.phase().value}]")
            print(f"  W(cos)={il['w_cos']:.3f}"
                  f"  W(sin)={il['w_sin']:.3f}"
                  f"  sin²+cos²={il['pythagorean']:.6f}")

            r1 = l1["reflection"]
            r2 = l2["reflection"]
            print(f"  L1 reflect: {r1.note}")
            print(f"  L2 reflect: {r2.note}")

            c1 = l1["cipher"].hidden_meaning
            c2 = l2["cipher"].hidden_meaning
            if c1:
                print(f"  L1 ↑ {c1}")
            if c2:
                print(f"  L2 ↑ {c2}")

        final = self.step_log[-1]["output"]
        tan_f = ("∞" if np.isinf(final.tan_theta())
                 else f"{final.tan_theta():.6f}")
        print("\n" + "=" * w)
        print(f"final θ            : {final.theta_deg():.2f}°  [{final.phase().value}]")
        print(f"final cos (align)  : {final.cos_theta():.6f}")
        print(f"final sin (deviasi): {final.sin_theta():.6f}")
        print(f"final tan (tension): {tan_f}")
        print(f"sin²+cos²          : {final.pythagorean_check():.8f}")
        print(f"irreducible gap Δ  : {final.irreducible_gap():.6f}")
        print(f"  → 0 mengarah ke 1. Gap tidak bisa ditutup — by design.")
        print(f"  → cos + sin = keutuhan. Tan = tegangan yang menjaga sistem hidup.")

        for lb, lbl in [(self.limbik1, "Limbik1(cos)"),
                        (self.limbik2, "Limbik2(sin)")]:
            if lb.ascend_log:
                print(f"\n{lbl} ascend ({len(lb.ascend_log)} event):")
                for a in lb.ascend_log:
                    print(f"  ↑ {a}")
        print("=" * w)


# ─────────────────────────────────────────────
# DEMO
# ─────────────────────────────────────────────

if __name__ == "__main__":

    print("\n[1] ground → pull attractor (tanpa perturbasi)")
    s1 = DualLimbikSystem()
    s1.run(steps=6)
    s1.report()

    print("\n\n[2] cos paradox — clarity↔ambiguity (alignment berbalik)")
    s2 = DualLimbikSystem()
    s2.run(steps=9, perturbations=[
        np.array([-0.5,  0.3,  0.2]),   # alignment rendah
        np.array([ 0.7,  0.2,  0.2]),   # alignment naik
        np.array([-0.6,  0.2,  0.2]),   # alignment turun → cos flip
        np.array([ 0.5,  0.3,  0.3]),
        np.array([ 0.3,  0.3,  0.3]),
        np.array([ 0.2,  0.3,  0.3]),
        np.array([ 0.1,  0.2,  0.3]),
        np.array([ 0.1,  0.1,  0.2]),
        np.array([ 0.0,  0.1,  0.1]),
    ])
    s2.report()

    print("\n\n[3] sin paradox — motion↔latent (deviasi berbalik)")
    s3 = DualLimbikSystem()
    s3.run(steps=9, perturbations=[
        np.array([ 0.3, -0.6,  0.2]),   # high sin (tegak lurus)
        np.array([ 0.6,  0.6,  0.3]),   # sin turun (lebih aligned)
        np.array([ 0.2, -0.7,  0.1]),   # sin naik lagi → sin flip
        np.array([ 0.3,  0.2,  0.4]),
        np.array([ 0.3,  0.2,  0.3]),
        np.array([ 0.2,  0.2,  0.3]),
        np.array([ 0.2,  0.1,  0.2]),
        np.array([ 0.1,  0.1,  0.2]),
        np.array([ 0.1,  0.1,  0.1]),
    ])
    s3.report()

    print("\n\n[4] tan singularity — Seal2 khusus (magnitude cukup)")
    s4 = DualLimbikSystem()
    s4.run(steps=9, perturbations=[
        np.array([ 0.5,  0.5,  0.0]),   # mulai bergerak
        np.array([ 0.7, -0.7,  0.0]),   # tegak lurus attractor → θ~90°
        np.array([ 0.6, -0.6,  0.0]),   # singularity + magnitude cukup
        np.array([ 0.3,  0.3,  0.3]),   # reorient
        np.array([ 0.3,  0.3,  0.3]),
        np.array([ 0.2,  0.3,  0.3]),
        np.array([ 0.2,  0.2,  0.3]),
        np.array([ 0.1,  0.2,  0.2]),
        np.array([ 0.1,  0.1,  0.2]),
    ])
    s4.report()
