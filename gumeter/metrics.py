from datetime import datetime
import numpy as np


def get_step_values(time_axis, event_times, event_counts):
    values = []
    if not event_times or event_times[0] > 0:
        event_times = [0.0] + event_times
        event_counts = [0] + event_counts

    event_idx = 0
    for t in time_axis:
        while event_idx + 1 < len(event_times) and event_times[event_idx + 1] <= t:
            event_idx += 1
        values.append(event_counts[event_idx])
    return values


def compute_normalized_efficiency_area(C_r, C_p, delta_t=0.1):
    C_r = np.array(C_r)
    C_p = np.array(C_p)

    assert C_r.shape == C_p.shape, "Arrays must be the same length"
    if np.any(C_p > C_r):
        raise ValueError("Cp should not exceed Cr at any point.")

    # Area between the curves
    area_diff = np.sum((C_r - C_p) * delta_t)

    # Max area (i.e., Cr - 0)
    max_area = np.sum(C_r * delta_t)

    # Normalized efficiency
    efficiency_normalized = 1 - (area_diff / max_area) if max_area != 0 else 1
    return efficiency_normalized


def measure_elasticity(backend_data):

    start_time_dt = datetime.fromtimestamp(backend_data['start_time'])
    end_time_dt = datetime.fromtimestamp(backend_data['end_time'])
    duration = (end_time_dt - start_time_dt).total_seconds()
    time_axis = np.arange(0.0, duration + 0.1, 0.1).tolist()
    if time_axis and time_axis[-1] < duration:
        time_axis.append(duration)
    time_axis = [t for t in time_axis if t <= duration + 0.001]

    provisioned_events = []
    for key, stage_workers in backend_data.items():
        if key.startswith('stage') and isinstance(stage_workers, list):
            for worker_stat in stage_workers:
                worker_start_dt = datetime.fromtimestamp(worker_stat['worker_start_tstamp'])
                worker_end_dt = datetime.fromtimestamp(worker_stat['worker_end_tstamp'])
                norm_start = (worker_start_dt - start_time_dt).total_seconds()
                norm_end = (worker_end_dt - start_time_dt).total_seconds()
                provisioned_events.append((norm_start, 1))
                provisioned_events.append((norm_end, -1))
    provisioned_events.sort(key=lambda x: x[0])
    provisioned_times_raw = [0.0]
    provisioned_counts_raw = [0]
    current_provisioned = 0
    for time, change in provisioned_events:
        if time > provisioned_times_raw[-1]:
            provisioned_times_raw.append(time)
            provisioned_counts_raw.append(current_provisioned)
        current_provisioned += change
        provisioned_times_raw.append(time)
        provisioned_counts_raw.append(current_provisioned)
    if provisioned_times_raw[-1] < duration:
        provisioned_times_raw.append(duration)
        provisioned_counts_raw.append(current_provisioned)
    provisioned_cpus_values = get_step_values(time_axis, provisioned_times_raw, provisioned_counts_raw)
    provisioned_cpus_values = [max(0, val) for val in provisioned_cpus_values]

    required_events = []
    for key, stage_workers in backend_data.items():
        if key.startswith('stage') and isinstance(stage_workers, list) and stage_workers:
            stage_start_dt = min(datetime.fromtimestamp(w['worker_start_tstamp']) for w in stage_workers)
            norm_stage_start = (stage_start_dt - start_time_dt).total_seconds()
            required_events.append((norm_stage_start, len(stage_workers)))
            for worker_stat in stage_workers:
                worker_end_dt = datetime.fromtimestamp(worker_stat['worker_end_tstamp'])
                norm_worker_end = (worker_end_dt - start_time_dt).total_seconds()
                required_events.append((norm_worker_end, -1))
    required_events.sort(key=lambda x: x[0])
    required_times_raw = [0.0]
    required_counts_raw = [0]
    current_required = 0
    for time, change in required_events:
        if time > required_times_raw[-1]:
            required_times_raw.append(time)
            required_counts_raw.append(current_required)
        current_required += change
        required_times_raw.append(time)
        required_counts_raw.append(current_required)
    if required_times_raw[-1] < duration:
        required_times_raw.append(duration)
        required_counts_raw.append(current_required)
    required_cpus_values = get_step_values(time_axis, required_times_raw, required_counts_raw)
    required_cpus_values = [max(0, val) for val in required_cpus_values]

    elasticity_coefficient = compute_normalized_efficiency_area(
        np.array(required_cpus_values),
        np.array(provisioned_cpus_values)
    )

    return elasticity_coefficient
