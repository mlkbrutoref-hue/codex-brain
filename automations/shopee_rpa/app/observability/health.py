import math


def health_report(events, **current):
    actions = [e for e in events if e.get('event') == 'action']
    times = sorted(e['latency_ms'] for e in actions if isinstance(e.get('latency_ms'), (int, float)))
    successes = sum(e.get('status') == 'SUCCESS' for e in actions)
    errors = sum(e.get('status') in ('ERROR', 'UNKNOWN') for e in actions)
    consecutive = 0
    for action in reversed(actions):
        if action.get('status') == 'SUCCESS': break
        consecutive += 1
    return dict(actions_total=len(actions), success_rate=successes / len(actions) if actions else None,
        error_rate=errors / len(actions) if actions else None,
        avg_latency_ms=sum(times) / len(times) if times else None,
        p95_latency_ms=times[max(0, math.ceil(.95 * len(times)) - 1)] if times else None,
        consecutive_failures=consecutive, unknown_results=sum(e.get('status') == 'UNKNOWN' for e in events),
        **current)
