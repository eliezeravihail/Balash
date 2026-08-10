"""Team members and the team that knows them.

A Member pairs a stable id with a display name. The Team is the one authority on
*which* members exist: it is the only place that decides whether a given member id is
real, and it is the thing that can turn a member id into the display name shown when a
task is listed. Because membership questions have exactly one owner, "you may only
assign a task to a member the team knows" is enforced in a single place that every
real assignment path passes through.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Iterator, List

from .errors import UnknownMemberError
from .ids import MemberId


@dataclass(frozen=True)
class Member:
    id: MemberId
    display_name: str

    def __post_init__(self) -> None:
        if not self.display_name or not self.display_name.strip():
            raise ValueError("a member needs a display name")


class Team:
    """The set of people work can be assigned to. Ask it to confirm a member or to
    name one; it answers, or raises UnknownMemberError. It never exposes a way to
    'assign' anything -- that decision belongs to a Task."""

    def __init__(self, members: Iterable[Member] = ()) -> None:
        self._members: Dict[MemberId, Member] = {m.id: m for m in members}

    def knows(self, member_id: MemberId) -> bool:
        return member_id in self._members

    def member(self, member_id: MemberId) -> Member:
        """Resolve a member id to the Member, or refuse if the team has no such
        member. This is the single gate the assign rule funnels through."""
        try:
            return self._members[member_id]
        except KeyError:
            raise UnknownMemberError(
                f"no team member has id {member_id.value!r}; add them first"
            ) from None

    def display_name_for(self, member_id: MemberId) -> str:
        """The name to show for an assignee id."""
        return self.member(member_id).display_name

    def __iter__(self) -> Iterator[Member]:
        return iter(self._members.values())

    def roster(self) -> List[Member]:
        return list(self._members.values())
