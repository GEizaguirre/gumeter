import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.lines import Line2D

T = 10
t = np.linspace(0, 5, 1000)

peaks = [1000, 400, 700, 200]
peak_times = [0.5, 1.5, 2.5, 4.0]
peak_intervals = [0.5, 0.5, 1.0, 0.5]
wait = 0.25


def smooth_cr(t, peaks, peak_times, peak_intervals, wait):
    n = len(peaks)

    for i in range(n):
        start_time = peak_times[i]
        end_time = peak_times[i] + peak_intervals[i]

        if start_time <= t < end_time:

            if t < end_time:
                return peaks[i]  # Abruptly reach maximum and stay for the wait time
            else:
                return 1 + (peaks[i] - 1) * np.exp(-25 * (t - end_time))  # Exponential decay after wait

    return 1

Cr = np.array([smooth_cr(time, peaks, peak_times, peak_intervals, wait) for time in t])

Cp = np.zeros_like(t)
Cp[0] = 1

adaptation_rate = 0.06

for i in range(1, len(t)):
    Cp[i] = Cp[i-1] + adaptation_rate * (Cr[i] - Cp[i-1])

integral = np.trapezoid(Cr / Cp, t) / T

print(integral)

# Set font and style for Elsevier journals
plt.rcParams["font.size"] = 18
plt.rcParams["axes.linewidth"] = 1.5  # Thicker axes lines
plt.rcParams["lines.linewidth"] = 3  # Thicker plot lines
# plt.rcParams["font.family"] = "serif"

# Define time array and example data (replace with your actual data)
t = np.linspace(0, 5, 1000)

arrowstyle='<->'
arrow_color='#36b700'
lw=1.5
mutation_scale=6
num_arrows = 3
arrow_distance = 12
start_distance = 10

labeled = False

line_colors = [ "#776bcd", "#ffb400" ]
fill_color = "white"

# Create the plot
with PdfPages('elasticity_burst.pdf') as pdf:
    plt.figure(figsize=(10, 4))  # Slightly taller for better proportions

    # Plot the lines
    h1, = plt.plot(t, Cr, label='Required', color=line_colors[0], solid_capstyle='round')  # Blue for Required
    h2, = plt.plot(t, Cp, label='Provided', color=line_colors[1], linestyle="--")  # Orange for Provided

    # Fill the area between the lines with a hatch pattern
    plt.fill_between(t, Cr, Cp, where=(Cr > Cp) | (Cp > Cr), interpolate=True, color=fill_color, alpha=0.3)

    # Customize ticks and labels
    plt.xticks([0, 1, 2, 3, 4, 5], fontsize=12)
    plt.yticks([0, 500, 1000], fontsize=1)
    plt.ylabel("Resources", fontsize=16)
    plt.xlabel("Time", fontsize=16)

    # Add grid for better readability
    plt.grid(True, linestyle='--', alpha=0.6)

    # Find the indexes where Cr changes from 1 to another number
    change_indexes = np.where(Cr[:-1] != Cr[1:])[0] + 1
    # Get the pair values of change indexes
    down_indexes = change_indexes[1::2]
    up_indexes = change_indexes[::2]

    for ui in up_indexes:
        ui += start_distance
        for _ in range(num_arrows):
            ta = t[ui]
            ys = Cp[ui] + 8
            ye = Cr[ui] + 8
            if ye - ys > 70:

                plt.annotate('',
                    xy=(ta, ys),
                    xytext=(ta, ye),
                    arrowprops=dict(arrowstyle=arrowstyle,
                                    lw=lw,
                                    color=arrow_color,
                                    mutation_scale=mutation_scale),
                    )

            ui += arrow_distance

    for ui in down_indexes:
        ui += start_distance
        for _ in range(num_arrows):
            ta = t[ui]
            ys = Cr[ui] - 8
            ye = Cp[ui] - 15
            if ye - ys > 70:
                plt.annotate('', 
                    xy=(ta, ys),
                    xytext=(ta, ye),
                    arrowprops=dict(arrowstyle=arrowstyle,
                                    lw=lw,
                                    color=arrow_color,
                                    mutation_scale=mutation_scale))
            ui += arrow_distance

    h3 = Line2D([], [], color=arrow_color, label='Stiffness', lw=4)

    # Add legend        
    plt.legend(
        handles=[h1,h2, h3],
        labels=['Required', 'Provided', 'Stiffness'],
        loc='upper center', bbox_to_anchor=(0.5, 1.25), ncol=3, fontsize=16, frameon=False)

    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)

    plt.tight_layout()
    pdf.savefig()
    plt.close()