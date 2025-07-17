import numpy as np


def elasticity_coefficient(
    cp: np.array,
    cr: np.array,
    step_size: int = 1,
    burst_penalty: float = 1
) -> float:

    time_steps = len(cp) * step_size

    # First term: Efficiency (Integral of C_r(t) / C_p(t))
    efficiency = np.trapezoid(cr / cp, time_steps) / (time_steps[-1] - time_steps[0])

    # Second term: Burst penalty (Integral of |d(C_p/C_r)/dt|)
    C_p_r_ratio = cp / cr
    d_Cp_r = np.gradient(C_p_r_ratio, time_steps)  # Numerical derivative

    penalty = np.trapezoid(np.abs(d_Cp_r), time_steps)

    # Elasticity coefficient
    E = efficiency - burst_penalty * penalty

    return E
