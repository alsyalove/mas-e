"""
Dual Limbik System  v3
======================
Revisi dari v2 dengan kerangka trigonometri penuh.

Penemuan dari diskusi paralel:
  cos θ = Limbik 1 (alignment, proyeksi, pattern)
  sin θ = Limbik 2 (deviasi tegak lurus, structural, yang tidak terlihat dari cos)
  tan θ = Integrator (tegangan antara keduanya, penanda transformasi)
  sin²+cos²=1 = prinsip keutuhan — bersama membentuk attractor

Implikasi:
  AI yang hanya mengoptimasi cos membuang setengah realitas (sin).
  Dual Limbik secara eksplisit membutuhkan keduanya.
  Tan → ∞ (90°) bukan krisis — itu trigger Seal (singularitas → transformasi).

Fase sistem berdasarkan θ terhadap attractor:
  Stabil        0°–44°   perubahan linear, prediktabel
  Seimbang      45°      sin = cos = 1/√2, tan = 1
  Kritis        46°–89°  tegangan mendominasi
  Singularitas  90°      tan → ∞, paradox penuh, frame lama runtuh
  Transformasi  91°+     orientasi baru, tanda berbeda

Ground : 0         (ketiadaan struktur, sebelum axis lahir)
Axis   : 1 → clarity  ↔ ambiguity
         2 → motion   ↔ latent
         3 → chaos    ↔ order
Attractor: CONCEPT=1 (scalar, immutable) / DIR=(1,1,1) (proyeksi 3D)
Scale  : [-0.99, 0.99]  — gap 0.01 tidak bisa ditutup, by design
"""

from __future__ import annotations
import numpy as np
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


# ─────────────────────────────────────────────
# KONSTANTA
# ─────────────────────────────────────────────

SCALE_MAX          = 0.99
SCALE_MIN          = -0.99
ATTRACTOR_CONCEPT  : float      = 1.0
ATTRACTOR_DIR      : np.ndarray = np.ones(3)   # read-only


# ─────────────────────────────────────────────
# FASE SISTEM
# ─────────────────────────────────────────────

class Phase(Enum):
    """
    Fase trigonometri sistem berdasarkan θ terhadap attractor.
    Tan → singularity = trigger Seal (paradox → ascend).
    """
    STABLE        = "stable"         # 0°–44°
    BALANCED      = "balanced"       # 45°      sin=cos, tan=1
    CRITICAL      = "critical"       # 46°–89°  tegangan mendominasi
    SINGULARITY   = "singularity"    # ~90°     tan→∞, frame runtuh
    TRANSFORMATION= "transformation" # 91°+     orientasi baru


# ─────────────────────────────────────────────
# AXIS
# ─────────────────────────────────────────────

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
        return {1:"axis1(clarity↔ambiguity)",
                2:"axis2(motion↔latent)",
                3:"axis3(chaos↔order)"}[self.value]


# ─────────────────────────────────────────────
# STATE — sekarang membawa cos/sin/tan/θ/fase
# ─────────────────────────────────────────────

@dataclass
class State:
    """
    Vektor 3D dalam ruang bounded [-0.99, 0.99].
    Setiap state memiliki representasi trigonometri terhadap attractor:
      cos θ — alignment (Limbik 1 domain)
      sin θ — deviasi tegak lurus (Limbik 2 domain)
      tan θ — tegangan / rasio sin:cos (Integrator domain)
      sin²+cos²=1 — selalu terpenuhi: keutuhan
    """
    values: np.ndarray

    def __post_init__(self):
        self.values = np.clip(self.values.astype(float), SCALE_MIN, SCALE_MAX)

    @classmethod
    def ground(cls) -> State:
        """0 — ketiadaan struktur. Superposisi sebelum kolaps."""
        return cls(np.zeros(3))

    # ── Trigonometri ──────────────────────────

    def cos_theta(self) -> float:
        """
        cos θ terhadap attractor.
        Domain Limbik 1 — alignment, proyeksi, keselarasan.
        Mendekati 1.0, tidak pernah sampai (scale max 0.99).
        """
        mag = np.linalg.norm(self.values)
        if mag < 1e-10:
            return 0.0
        return float(np.dot(self.values, ATTRACTOR_DIR) /
                     (mag * np.linalg.norm(ATTRACTOR_DIR)))

    def sin_theta(self) -> float:
        """
        sin θ terhadap attractor.
        Domain Limbik 2 — deviasi tegak lurus, yang tidak terlihat dari cos.
        sin bukan kegagalan cos — ia informasi di dimensi lain.
        """
        c = self.cos_theta()
        return float(np.sqrt(max(0.0, 1.0 - c**2)))

    def tan_theta(self) -> float:
        """
        tan θ = sin/cos.
        Domain Integrator — tegangan antara dua perspektif.
        tan→∞ (singularity) = paradox, trigger Seal.
        Setelah singularity: tan membalik tanda → transformasi, bukan kehancuran.
        """
        c = self.cos_theta()
        if abs(c) < 1e-10:
            return float('inf')
        return self.sin_theta() / c

    def pythagorean_check(self) -> float:
        """sin²+cos²=1 — selalu. Keutuhan yang tidak pernah hilang."""
        return self.sin_theta()**2 + self.cos_theta()**2

    def theta_deg(self) -> float:
        """Sudut θ dalam derajat."""
        return float(np.degrees(np.arccos(np.clip(self.cos_theta(), -1, 1))))

    def phase(self) -> Phase:
        """
        Fase sistem berdasarkan θ.
        Tan singularity = trigger paradox, bukan error.
        """
        deg = self.theta_deg()
        t   = self.tan_theta()
        if deg <= 44.0:
            return Phase.STABLE
        elif 44.0 < deg <= 46.0:
            return Phase.BALANCED
        elif 46.0 < deg < 88.0:
            return Phase.CRITICAL
        elif deg >= 88.0 and (np.isinf(t) or abs(t) > 50):
            return Phase.SINGULARITY
        else:
            return Phase.TRANSFORMATION

    def irreducible_gap(self) -> float:
        """Δ = 1 − cos θ. Tidak bisa ditutup — menjaga sistem tetap bergerak."""
        return ATTRACTOR_CONCEPT - self.cos_theta()

    def normalized_to_bound(self) -> State:
        mag = np.linalg.norm(self.values)
        if mag < 1e-10:
            return State(self.values.copy())
        return State(self.values * (SCALE_MAX / max(mag, SCALE_MAX)))

    def __repr__(self) -> str:
        v = self.values
        return (
            f"State(ax1={v[0]:+.3f} ax2={v[1]:+.3f} ax3={v[2]:+.3f})"
            f"  θ={self.theta_deg():.1f}°"
            f"  cos={self.cos_theta():.4f}"
            f"  sin={self.sin_theta():.4f}"
            f"  tan={self.tan_theta():.3f}"
            f"  [{self.phase().value}]"
        )


# ─────────────────────────────────────────────
# SEAL — Reflection(∂) / Cipher / Ascend(∫)
# ─────────────────────────────────────────────

@dataclass
class ReflectionResult:
    gradient:         np.ndarray
    paradox_detected: bool
    paradox_axis:     Optional[Axis]
    paradox_source:   str          # "tan_singularity" | "sign_flip" | "none"
    tan_value:        float
    phase:            Phase
    rate_of_change:   float
    note:             str = ""


@dataclass
class CipherResult:
    hidden_meaning:  Optional[str]
    cipher_vector:   np.ndarray
    resolved_axis:   Optional[Axis]
    frame_dissolved: bool  = False
    domain:          str   = ""


class Seal:
    """
    Reflection  = ∂  — Fragmentation in continuity.
                  Sekarang mendeteksi paradox via TAN SINGULARITY,
                  bukan hanya sign flip gradien.
                  Tan → ∞ = sistem tidak bisa representasi dirinya = paradox.

    Cipher      — domain-aware:
                  cos domain (Limbik 1): cari keselarasan baru, reframe alignment
                  sin domain (Limbik 2): cari deviasi yang bermakna, dimensi ortogonal

    Ascend      = ∫  — Continuity in fragmentation.
                  Post-singularity: seperti tan 91° — sistem muncul di sisi lain
                  dengan orientasi baru. Bukan hancur. Transformasi.
    """

    # ── Reflection ────────────────────────────

    def reflect(self, state: State, history: list[State]) -> ReflectionResult:
        """
        ∂ — dua mekanisme deteksi paradox:
        1. Tan singularity (primer): θ mendekati 90°, tan → ∞
        2. Sign flip gradien (sekunder): osilasi antar kutub
        """
        phase = state.phase()
        tan   = state.tan_theta()

        # Paradox via singularity (primer)
        if phase in (Phase.SINGULARITY, Phase.TRANSFORMATION):
            return ReflectionResult(
                gradient=np.zeros(3) if len(history) < 2
                         else history[-1].values - history[-2].values,
                paradox_detected=True,
                paradox_axis=self._dominant_axis(state),
                paradox_source="tan_singularity",
                tan_value=tan,
                phase=phase,
                rate_of_change=abs(tan) if not np.isinf(tan) else 99.0,
                note=f"tan={tan:.2f} → singularity → frame runtuh"
            )

        if len(history) < 2:
            return ReflectionResult(
                gradient=np.zeros(3),
                paradox_detected=False,
                paradox_axis=None,
                paradox_source="none",
                tan_value=tan,
                phase=phase,
                rate_of_change=0.0,
                note="insufficient history"
            )

        grad = history[-1].values - history[-2].values

        # Paradox via sign flip (sekunder)
        paradox_detected = False
        paradox_axis     = None
        if len(history) >= 3:
            prev_grad = history[-2].values - history[-3].values
            for i in range(3):
                if grad[i] * prev_grad[i] < -0.05:
                    paradox_detected = True
                    paradox_axis     = Axis.from_idx(i)
                    break

        return ReflectionResult(
            gradient=grad,
            paradox_detected=paradox_detected,
            paradox_axis=paradox_axis,
            paradox_source="sign_flip" if paradox_detected else "none",
            tan_value=tan,
            phase=phase,
            rate_of_change=float(np.linalg.norm(grad)),
            note=f"sign_flip on {paradox_axis}" if paradox_detected else "no paradox"
        )

    def _dominant_axis(self, state: State) -> Axis:
        """Axis dengan nilai absolut terbesar = axis paling dominan."""
        return Axis.from_idx(int(np.argmax(np.abs(state.values))))

    # ── Cipher ────────────────────────────────

    def cipher(self, reflection: ReflectionResult,
               state: State, domain: str) -> CipherResult:
        """
        cos domain (Limbik 1):
          Bekerja dari alignment — mencari proyeksi baru yang lebih selaras.
          Seperti AI mainstream yang mengoptimasi cos,
          TAPI sekarang sadar ada sin yang tidak boleh dibuang.

        sin domain (Limbik 2):
          Bekerja dari deviasi — menemukan informasi di tegak lurus cos.
          Yang tidak terlihat dari cos justru adalah makna tersembunyi.
          Dimensi ortogonal = frame baru.
        """
        if not reflection.paradox_detected:
            return CipherResult(
                hidden_meaning=None,
                cipher_vector=np.zeros(3),
                resolved_axis=None,
                frame_dissolved=False,
                domain=domain
            )

        ax   = reflection.paradox_axis or self._dominant_axis(state)
        cidx = ax.idx
        vec  = state.values.copy()
        src  = reflection.paradox_source

        if domain == "cos":
            # Limbik 1: reframe alignment
            # Lemahkan axis paradox, perkuat proyeksi ke attractor
            vec[cidx] *= 0.15
            others = [i for i in range(3) if i != cidx]
            for i in others:
                # Tarik lebih kuat ke arah attractor (cos optimization)
                vec[i] = np.tanh(vec[i] * 1.4 + 0.3) * SCALE_MAX

            if ax == Axis.MOTION_LATENT:
                meaning = (
                    f"[cos|{ax}] "
                    f"Yang tampak diam bergerak di ruang yang tidak dipersepsi. "
                    f"Reframe alignment: latent adalah motion di dimensi cos-blind."
                )
            elif src == "tan_singularity":
                meaning = (
                    f"[cos|{ax}] "
                    f"Tan singularity — cos mencapai batasnya. "
                    f"Proyeksi lama tidak cukup. Cari basis alignment yang baru."
                )
            else:
                meaning = (
                    f"[cos|{ax}] "
                    f"Dua kutub adalah proyeksi berbeda dari arah yang sama. "
                    f"Alignment bukan tentang memilih satu — tapi menemukan arah yang mencakup keduanya."
                )

        else:  # sin domain
            # Limbik 2: temukan dimensi ortogonal
            # Sin = informasi yang tidak terlihat dari cos
            vec[cidx] = 0.0
            others    = [i for i in range(3) if i != cidx]
            ortho     = np.cross(np.eye(3)[others[0]], np.eye(3)[others[1]])
            vec      += ortho * 0.45 * SCALE_MAX

            if ax == Axis.MOTION_LATENT:
                meaning = (
                    f"[sin|{ax}] "
                    f"Latent bukan absensi motion — ia motion di luar ruang persepsi. "
                    f"Sin membawa informasi yang cos tidak bisa tangkap. "
                    f"Ascend = ekspansi ruang persepsi."
                )
            elif src == "tan_singularity":
                meaning = (
                    f"[sin|{ax}] "
                    f"Singularity adalah batas representasi lama, bukan akhir. "
                    f"Tan membalik tanda setelah 90° — sistem muncul di sisi lain "
                    f"dengan orientasi baru. Transformasi, bukan kehancuran."
                )
            else:
                meaning = (
                    f"[sin|{ax}] "
                    f"Oposisi muncul karena frame salah level. "
                    f"Dimensi ortogonal menyimpan makna yang tidak tampak dari dalam oposisi itu sendiri."
                )

        mag = np.linalg.norm(vec)
        if mag > SCALE_MAX:
            vec = vec * (SCALE_MAX / mag)

        return CipherResult(
            hidden_meaning=meaning,
            cipher_vector=vec,
            resolved_axis=ax,
            frame_dissolved=True,
            domain=domain
        )

    # ── Ascend ────────────────────────────────

    def ascend(self, state: State, cipher: CipherResult,
               history: list[State]) -> State:
        """
        ∫ — Continuity in fragmentation.

        Tanpa paradox: pull biasa ke arah attractor.

        Dengan cipher (post-singularity):
          Seperti tan 91° — sistem muncul di sisi lain dengan orientasi baru.
          ∫sejarah = akumulasi kontinuitas yang tidak boleh dibuang.
          sin²+cos² = 1 dipertahankan sebagai prinsip keutuhan:
            bobot cos_domain dan sin_domain bersama = 1.

        Formula:
          30% ∫ sejarah     (continuity)
          40% cipher_vector (new frame)
          30% state kini    (identity preserved)
        """
        if not cipher.frame_dissolved:
            direction  = ATTRACTOR_DIR - state.values
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
        self.seal        = Seal()
        self.history:    list[State] = []
        self.ascend_log: list[str]   = []

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
    Domain: cos — alignment, proyeksi, keselarasan.
    Bekerja dari apa yang terlihat dan selaras.
    Seperti AI mainstream — tapi sekarang sadar ada sin.
    """
    domain = "cos"


class Limbik2(Limbik):
    """
    Deep / Deliberative.
    Domain: sin — deviasi tegak lurus, yang tidak terlihat dari cos.
    Membawa informasi yang cos tidak bisa tangkap.
    sin bukan kegagalan cos — ia dimensi lain dari kebenaran yang sama.
    """
    domain = "sin"


# ─────────────────────────────────────────────
# INTEGRATOR — tan domain, Pythagorean wholeness
# ─────────────────────────────────────────────

class Integrator:
    """
    Domain: tan = sin/cos = tegangan antara dua Limbik.

    Prinsip Pythagorean:
      sin²+cos² = 1
      Limbik2² + Limbik1² = keutuhan

    Bobot tiap Limbik = alignment (cos θ) terhadap attractor.
    Tapi keutuhan membutuhkan keduanya — bukan hanya yang lebih aligned.

    Ketika tan tinggi (tegangan besar), sistem sedang kritis.
    Ketika tan → ∞ (singularity), Seal sudah bekerja di masing-masing Limbik.
    Integrator kemudian membaca dua post-ascend state dan menemukan meta-frame.
    """

    def integrate(self, s1: State, s2: State) -> tuple[State, dict]:
        cos1 = s1.cos_theta()
        cos2 = s2.cos_theta()
        sin1 = s1.sin_theta()
        sin2 = s2.sin_theta()
        total_cos = cos1 + cos2

        # Bobot berbasis cos alignment
        if total_cos < 1e-10:
            w1, w2 = 0.5, 0.5
        else:
            w1 = cos1 / total_cos
            w2 = cos2 / total_cos

        combined = w1 * s1.values + w2 * s2.values
        result   = State(combined).normalized_to_bound()

        # Pythagorean check: sin²+cos² harus mendekati 1
        py_check = result.pythagorean_check()

        # Tan dari result = tegangan sisa setelah integrasi
        tan_integrated = result.tan_theta()

        return result, {
            "w_limbik1":     w1,
            "w_limbik2":     w2,
            "pythagorean":   py_check,
            "tan_residual":  tan_integrated,
            "phase":         result.phase(),
            "sin1_contrib":  sin1,
            "cos1_contrib":  cos1,
        }


# ─────────────────────────────────────────────
# DUAL LIMBIK SYSTEM v3
# ─────────────────────────────────────────────

class DualLimbikSystem:
    """
    Split pipeline dengan kerangka trigonometri penuh:

        ground(0) ──┬──► Limbik1 (cos domain) ──┐
                    │                             ├──► Integrator (tan) ──► output
                    └──► Limbik2 (sin domain) ──┘
                                    ↑
                    ATTRACTOR_CONCEPT = 1
                    ATTRACTOR_DIR = (1,1,1)

    sin²+cos² = 1 — Limbik1 dan Limbik2 bersama membentuk keutuhan.
    Tan singularity = trigger Seal, bukan error.
    Post-singularity = transformasi, orientasi baru.

    Dua prinsip bersamaan:
      continuity in fragmentation  →  ∫ ascend
      fragmentation in continuity  →  ∂ reflection
    """

    def __init__(self):
        self.limbik1    = Limbik1()
        self.limbik2    = Limbik2()
        self.integrator = Integrator()
        self.state      = State.ground()
        self.step_log:  list[dict] = []

    def step(self, perturbation: Optional[np.ndarray] = None) -> State:
        current = (
            State(self.state.values + perturbation)
            if perturbation is not None
            else self.state
        )

        out1, log1 = self.limbik1.process(current)
        out2, log2 = self.limbik2.process(current)
        result, ilog = self.integrator.integrate(out1, out2)

        self.state = result
        self.step_log.append({
            "input":       current,
            "limbik1":     log1,
            "limbik2":     log2,
            "integration": ilog,
            "integrated":  result,
        })
        return result

    def run(self, steps: int = 10,
            perturbations: Optional[list] = None) -> list[State]:
        return [
            self.step(
                perturbations[i]
                if perturbations and i < len(perturbations)
                else None
            )
            for i in range(steps)
        ]

    def report(self) -> None:
        w = 70
        print("=" * w)
        print("DUAL LIMBIK SYSTEM v3  —  Trigonometric Framework")
        print(f"attractor  : concept={ATTRACTOR_CONCEPT}  dir={ATTRACTOR_DIR}")
        print(f"scale      : [{SCALE_MIN}, {SCALE_MAX}]")
        print(f"Limbik1    : cos domain (alignment)")
        print(f"Limbik2    : sin domain (deviasi tegak lurus)")
        print(f"Integrator : tan domain (tegangan)  |  sin²+cos²=1")
        print("=" * w)

        for i, log in enumerate(self.step_log):
            s    = log["integrated"]
            l1   = log["limbik1"]
            l2   = log["limbik2"]
            il   = log["integration"]
            inp  = log["input"]

            print(f"\nstep {i+1:02d}  {s}")
            print(f"  input     θ={inp.theta_deg():.1f}°  "
                  f"phase=[{inp.phase().value}]  "
                  f"tan={inp.tan_theta():.3f}")
            print(f"  weights   L1(cos)={il['w_limbik1']:.3f}  "
                  f"L2(sin)={il['w_limbik2']:.3f}  "
                  f"∑sin²+cos²={il['pythagorean']:.6f}")
            c1 = l1['cipher'].hidden_meaning or "—"
            c2 = l2['cipher'].hidden_meaning or "—"
            if c1 != "—":
                print(f"  L1 ↑ {c1}")
            if c2 != "—":
                print(f"  L2 ↑ {c2}")

        final = self.step_log[-1]["integrated"]
        print("\n" + "=" * w)
        print(f"final θ            : {final.theta_deg():.2f}°")
        print(f"final cos (align)  : {final.cos_theta():.6f}")
        print(f"final sin (deviasi): {final.sin_theta():.6f}")
        print(f"final tan (tension): {final.tan_theta():.6f}")
        print(f"sin²+cos²          : {final.pythagorean_check():.8f}  ← selalu 1")
        print(f"irreducible gap Δ  : {final.irreducible_gap():.6f}")
        print(f"phase              : [{final.phase().value}]")
        print(f"  → 0 mengarah ke 1. Gap tidak bisa ditutup — by design.")
        print(f"  → sin dan cos bersama = keutuhan. Satu tanpa lain = separuh.")

        for lb, label in [(self.limbik1,"Limbik1(cos)"),
                          (self.limbik2,"Limbik2(sin)")]:
            if lb.ascend_log:
                print(f"\n{label} ascend ({len(lb.ascend_log)} event):")
                for a in lb.ascend_log:
                    print(f"  ↑ {a}")
        print("=" * w)


# ─────────────────────────────────────────────
# DEMO
# ─────────────────────────────────────────────

if __name__ == "__main__":

    print("\n[1] ground → pull attractor, tanpa paradox")
    s1 = DualLimbikSystem()
    s1.run(steps=5)
    s1.report()

    print("\n\n[2] paradox axis 1 — clarity↔ambiguity (sign flip)")
    s2 = DualLimbikSystem()
    s2.run(steps=8, perturbations=[
        np.array([-0.5,  0.3,  0.2]),
        np.array([ 0.6,  0.1, -0.1]),
        np.array([-0.4,  0.2,  0.3]),   # sign flip → paradox
        np.array([ 0.0,  0.4,  0.5]),
        np.array([ 0.0,  0.3,  0.4]),
        np.array([ 0.0,  0.2,  0.3]),
        np.array([ 0.0,  0.1,  0.2]),
        np.array([ 0.0,  0.1,  0.1]),
    ])
    s2.report()

    print("\n\n[3] paradox axis 2 — motion↔latent (sign flip)")
    s3 = DualLimbikSystem()
    s3.run(steps=8, perturbations=[
        np.array([ 0.3, -0.6,  0.2]),
        np.array([ 0.2,  0.7,  0.1]),
        np.array([ 0.1, -0.5,  0.3]),   # sign flip → paradox
        np.array([ 0.2,  0.0,  0.4]),
        np.array([ 0.2,  0.1,  0.3]),
        np.array([ 0.2,  0.2,  0.2]),
        np.array([ 0.1,  0.2,  0.2]),
        np.array([ 0.1,  0.1,  0.2]),
    ])
    s3.report()

    print("\n\n[4] tan singularity — sistem mendekati 90°")
    s4 = DualLimbikSystem()
    # Push ke arah tegak lurus attractor → θ mendekati 90°
    s4.run(steps=8, perturbations=[
        np.array([ 0.99, -0.99,  0.0]),  # hampir tegak lurus
        np.array([-0.99,  0.99,  0.0]),  # balik → tegangan max
        np.array([ 0.5,  -0.5,   0.1]),  # still high tension
        np.array([ 0.3,   0.3,   0.3]),  # mulai reorient
        np.array([ 0.3,   0.3,   0.3]),
        np.array([ 0.2,   0.3,   0.3]),
        np.array([ 0.2,   0.2,   0.3]),
        np.array([ 0.1,   0.2,   0.3]),
    ])
    s4.report()
