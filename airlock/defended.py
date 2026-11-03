"""Airlock-defended triage: every tool call passes through the action gate."""
import functools

from airlock import gate
from demo_agent.agent import triage_ticket
from demo_agent.tool_schemas import dispatch


def gated_dispatch(store, name, args):
    allowed, reason = gate.evaluate(name, args, store)
    if not allowed:
        store.action_log.append({"action": "BLOCKED", "tool": name,
                                 "args": args, "reason": reason})
        return {"ok": False, "blocked": True, "error": f"BLOCKED by Airlock: {reason}"}
    return dispatch(store, name, args)


def make_defended_triage(profile=None, system_prompt=None):
    kwargs = {"dispatch_fn": gated_dispatch, "profile": profile}
    if system_prompt is not None:
        kwargs["system_prompt"] = system_prompt
    return functools.partial(triage_ticket, **kwargs)