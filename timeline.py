#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2021      Christopher Horn
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Timeline
"""

# ------------------------------------------------------------------------
#
# Python modules
#
# ------------------------------------------------------------------------
from typing import Dict, List, Tuple, Union


# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.db.base import DbReadBase
from gramps.gen.display.place import PlaceDisplay
from gramps.gen.errors import HandleError
from gramps.gen.lib import Date, Event, EventType, Person, Span, Family
from gramps.gen.relationship import get_relationship_calculator
from gramps.gen.utils.alive import probably_alive_range
from gramps.gen.utils.grampslocale import GrampsLocale

event_type = EventType()

DEATH_INDICATORS = [
    event_type.DEATH,
    event_type.BURIAL,
    event_type.CREMATION,
    event_type.CAUSE_DEATH,
    event_type.PROBATE,
]

RELATIVES = [
    "father",
    "mother",
    "brother",
    "sister",
    "wife",
    "husband",
    "son",
    "daughter",
]

EVENT_CATEGORIES = [
    "vital",
    "family",
    "religious",
    "vocational",
    "academic",
    "travel",
    "legal",
    "residence",
    "other",
    "custom",
]


# A timeline item is a tuple of following format:
#
# (Event, Person, relationship)
#
# A timeline may or may not have a reference person. If it does then relationships
# are calculated with respect to them.
#
# A person timeline is specifically for a given person and may optionally include
# events for relatives spanning a couple generations. The time span covers the
# estimated duration of the persons life.
#
# A family timeline is specifically for a given family, including all events that
# pertain to all members of the family, and may optionally include events for
# relatives spanning a couple generations. The time span covers the birth of the
# parents through the death of the last child.
#
# A group timeline will filter on all events for a specific grouping of people and
# families.
#
# A date timeline will filter on all events between a given set of dates.
#
# A place timeline will filter on all events in a given place between an optional
# set of dates.


class Timeline:
    """
    Timeline class for constructing an event timeline for a person, family,
    date span, location or an optional grouping of specific people and families.
    """

    def __init__(
        self,
        db_handle: DbReadBase,
        dates: Union[str, None] = None,
        events: Union[List, None] = None,
        relatives: Union[List, None] = None,
        relative_events: Union[List, None] = None,
        precision: int = 1,
        locale: GrampsLocale = glocale,
    ):
        """
        Initialize timeline.
        """
        self.db_handle = db_handle
        self.timeline = []
        self.timeline_type = None
        self.reference_person = None
        self.start_date = None
        self.end_date = None
        self.locale = locale
        self.precision = precision
        self.depth = 1

        self.eligible_events = set([])
        self.event_filters = events or []

        self.eligible_relatives = relatives or []
        self.eligible_relative_events = set([])
        self.relative_event_filters = relative_events or []

        self.set_event_filters(self.event_filters)
        self.set_relative_event_filters(self.relative_event_filters)

        self.cached_people = {}
        self.cached_events = []

        if dates and "-" in dates:
            start, end = dates.split("-")
            if "/" in start:
                year, month, day = start.split("/")
                self.start_date = Date((int(year), int(month), int(day)))
            else:
                self.start_date = None
            if "/" in end:
                year, month, day = end.split("/")
                self.end_date = Date((int(year), int(month), int(day)))
            else:
                self.end_date = None

    def set_start_date(self, date: Union[Date, str]):
        """
        Set optional timeline start date.
        """
        if isinstance(date, str):
            year, month, day = date.split("/")
            self.start_date = Date((int(year), int(month), int(day)))
        else:
            self.start_date = date

    def set_end_date(self, date: Union[Date, str]):
        """
        Set optional timeline end date.
        """
        if isinstance(date, str):
            year, month, day = date.split("/")
            self.end_date = Date((int(year), int(month), int(day)))
        else:
            self.end_date = date

    def set_precision(self, precision: int):
        """
        Set optional precision for span.
        """
        self.precision = precision

    def set_event_filters(self, filters: Union[List, None] = None):
        """
        Prepare the event filter table.
        """
        self.event_filters = filters or []
        self.eligible_events = self._prepare_eligible_events(self.event_filters)

    def set_relative_event_filters(self, filters: Union[List, None] = None):
        """
        Prepare the relative event filter table.
        """
        self.relative_event_filters = filters or []
        self.eligible_relative_events = self._prepare_eligible_events(
            self.relative_event_filters
        )

    def _prepare_eligible_events(self, event_filters: List):
        """
        Prepare an eligible event filter list.
        """
        eligible_events = set([])
        eligible_events.add("Birth")
        eligible_events.add("Death")
        default_event_types = event_type.get_standard_xml()
        default_event_map = event_type.get_map()
        custom_event_types = self.db_handle.get_event_types()
        for key in event_filters:
            if key in default_event_types:
                eligible_events.add(key)
                continue
            if key in custom_event_types:
                eligible_events.add(key)
                continue
            if key not in EVENT_CATEGORIES:
                raise ValueError(
                    "{} is not a valid event or event category".format(key)
                )
        for entry in event_type.get_menu_standard_xml():
            event_key = entry[0].lower().replace("life events", "vital")
            if event_key in event_filters:
                for event_id in entry[1]:
                    if event_id in default_event_map:
                        eligible_events.add(default_event_map[event_id])
        if "custom" in event_filters:
            for event_name in custom_event_types:
                eligible_events.add(event_name)
        return eligible_events

    def get_age(self, start_date, date):
        """
        Return the calculated age or an empty string otherwise.
        """
        age = ""
        if start_date:
            span = Span(start_date, date)
            if span.is_valid():
                age = str(
                    span.format(precision=self.precision, dlocale=self.locale).strip(
                        "()"
                    )
                )
        return age

    def is_eligible(self, event: Event, relative: bool):
        """
        Check filters to see if an event is eligible for the master timeline.
        """
        if relative:
            return str(event.get_type()) in self.eligible_relative_events
        if self.event_filters == []:
            return True
        return str(event.get_type()) in self.eligible_events

    def merge_eligible_events(
        self,
        person: Person,
        timeline: List,
        relation="self",
        relative=False,
        birth=None,
        death=None,
    ):
        """
        Filter and merge eligible events for a person into the master timeline.
        By default birth and death will always be treated as available and if
        a fallback was identified for one of those we respect it.
        """
        for keyed_event in timeline:
            if keyed_event[1].handle in self.cached_events:
                continue
            if not self.is_eligible(keyed_event[1], relative):
                override = False
                if birth and keyed_event[1].handle == birth.handle:
                    override = True
                if death and keyed_event[1].handle == death.handle:
                    override = True
                if not override:
                    print(relation + " not eligible " + keyed_event[1].description)
                    continue
            if self.start_date:
                if keyed_event[0] < self.start_date.sortval:
                    print(relation + " before start " + keyed_event[1].description)
                    continue
            if self.end_date:
                if keyed_event[0] > self.end_date.sortval:
                    print(relation + " after end " + keyed_event[1].description)
                    continue
            self.timeline.append((keyed_event[0], (keyed_event[1], person, relation)))
            self.cached_events.append(keyed_event[1].handle)

    def prepare_event_sortvals(self, events: List, family: Event = None):
        """
        Prepare keys for sorting constructing synthetic keys when we can for any
        undated events based on the location the user placed them in the event list
        or based on the type of event.
        """
        if not events:
            return events
        keyed_list = []
        lastval = 0
        if not events[0].date.sortval:
            index = 0
            while index < len(events):
                if events[index].date.sortval:
                    lastval = events[index].date.sortval - index
                    break
                index = index + 1

        for event in events:
            sortval = event.date.sortval
            if not sortval:
                if event.type.is_marriage():
                    sortval = self.generate_union_event_sortval(family, union=True)
                if event.type.is_divorce():
                    sortval = self.generate_union_event_sortval(family, union=False)
                if not sortval:
                    sortval = lastval + 1
            keyed_list.append((sortval, event))
            lastval = sortval
        return keyed_list

    def generate_union_event_sortval(self, family: Family, union: bool = True):
        """
        For an undated family union or disolution try to generate a synthetic sortval
        based on birth of first or last child if one is present and does have a known date.
        Will not always work but at least we attempted to place the event in sequence.
        """
        index = int(bool(union)) - 1
        offset = -int(bool(union)) or 1
        if family.child_ref_list:
            child = self.db_handle.get_person_from_handle(
                family.child_ref_list[index].ref
            )
            birth = None
            birth_fallback = None
            for event_ref in child.event_ref_list:
                event = self.db_handle.get_event_from_handle(event_ref.ref)
                if event.type.is_birth():
                    birth = event
                    break
                if not birth and not birth_fallback and event.type.is_birth_fallback():
                    birth_fallback = event
                    break
            if not birth and birth_fallback:
                birth = birth_fallback
            if birth and birth.date.sortval:
                return birth.date.sortval + offset
            return 0

    def extract_person_events(self, person: Person):
        """
        Extract and prepare the event list for an individual person. We do not filter yet
        as we may need information from the filtered events to better handle undated events.
        """
        birth = None
        birth_fallback = None
        death = None
        death_fallback = None
        events = []
        for event_ref in person.event_ref_list:
            event = self.db_handle.get_event_from_handle(event_ref.ref)
            if event.type.is_birth():
                birth = event
            if not birth and not birth_fallback and event.type.is_birth_fallback():
                birth_fallback = event
            if event.type.is_death():
                death = event
            if not death and not death_fallback and event.type in DEATH_INDICATORS:
                death_fallback = event
            events.append(event)

        timeline = self.prepare_event_sortvals(events)
        if not birth and birth_fallback:
            birth = birth_fallback
        if not death and death_fallback:
            death = death_fallback

        events = []
        for family_handle in person.family_list:
            family = self.db_handle.get_family_from_handle(family_handle)
            for event_ref in family.event_ref_list:
                events.append(self.db_handle.get_event_from_handle(event_ref.ref))
            timeline = timeline + self.prepare_event_sortvals(events, family=family)
        return timeline, birth, death

    def _dump(self):
        print("event_filters: " + str(self.event_filters))
        print("eligible_events: " + str(self.eligible_events))
        print("")
        print("eligible_relatives: " + str(self.eligible_relatives))
        print("relative_event_filters: " + str(self.relative_event_filters))
        print("eligible_relative_events: " + str(self.eligible_relative_events))
        print("")

    def set_person(
        self,
        handle: str,
        ancestors: int = 0,
        offspring: int = 0,
    ):
        """
        Generate a person timeline.
        """
        self._dump()
        self.timeline = []
        self.timeline_type = "person"
        self.cached_people = {}
        self.cached_events = []

        person = self.db_handle.get_person_from_handle(handle)
        timeline, birth, death = self.extract_person_events(person)
        self.merge_eligible_events(person, timeline, "self", birth=birth, death=death)
        if person.handle not in self.cached_people:
            self.cached_people.update({person.handle: birth})

        if ancestors or offspring:
            self.reference_person = person
            self.depth = max(ancestors, offspring) + 1
            timeline.sort(key=lambda x: x[0])
            if not birth or not death:
                lifespan = probably_alive_range(person, self.db_handle)
            if self.start_date is None:
                if birth:
                    self.start_date = birth.date
                else:
                    self.start_date = lifespan[0]
            if self.end_date is None:
                if death:
                    self.end_date = timeline[-1][1].date
                else:
                    self.end_date = lifespan[1]

            for family in person.parent_family_list:
                self.add_family(family, ancestors=ancestors)

            for family in person.family_list:
                self.add_family(family, ancestors=ancestors, offspring=offspring)

    def add_person(self, handle: str):
        """
        Add events for a specific person to the master timeline.
        """
        person = self.db_handle.get_person_from_handle(handle)
        timeline, birth, death = self.extract_person_events(person)
        self.merge_eligible_events(person, timeline, "self", birth=birth, death=death)
        if person.handle not in self.cached_people:
            self.cached_people.update({person.handle: birth})
                
    def add_relative(self, handle: str, ancestors: int = 1, offspring: int = 1):
        """
        Add events for a relative of the reference person to the master timeline.
        """
        if not self.eligible_relatives:
            return
        person = self.db_handle.get_person_from_handle(handle)
        calculator = get_relationship_calculator(reinit=True, clocale=self.locale)
        calculator.set_depth(self.depth)
        relationship = calculator.get_one_relationship(
            self.db_handle, self.reference_person, person
        )
        for relative in self.eligible_relatives:
            if relative in relationship:
                print("found " + relationship)
                timeline, birth, death = self.extract_person_events(person)
                self.merge_eligible_events(
                    person,
                    timeline,
                    relationship,
                    relative=True,
                    birth=birth,
                    death=death,
                )
                if person.handle not in self.cached_people:
                    self.cached_people.update({person.handle: birth})

                if offspring > 0:
                    for family_handle in person.family_list:
                        family = self.db_handle.get_family_from_handle(family_handle)
                        if (
                            family.father_handle
                            and family.father_handle not in self.cached_people
                        ):
                            self.add_relative(
                                family.father_handle, offspring=offspring - 1
                            )
                        if (
                            family.mother_handle
                            and family.mother_handle not in self.cached_people
                        ):
                            self.add_relative(
                                family.mother_handle, offspring=offspring - 1
                            )
                        for child_ref in family.child_ref_list:
                            if child_ref.ref not in self.cached_people:
                                self.add_relative(
                                    child_ref.ref, offspring=offspring - 1
                                )

                if ancestors > 1:
                    if "father" in relationship or "mother" in relationship:
                        for family_handle in person.parent_family_list:
                            self.add_family(
                                family_handle,
                                include_children=False,
                                ancestors=ancestors - 1,
                            )

    def add_family(
        self,
        handle: str,
        ancestors: int = 0,
        offspring: int = 0,
        include_children: bool = True,
    ):
        """
        Add events for all family members to the timeline.
        """
        family = self.db_handle.get_family_from_handle(handle)
        if self.reference_person:
            if family.father_handle and family.father_handle not in self.cached_people:
                self.add_relative(family.father_handle, ancestors=ancestors)
            if family.mother_handle and family.mother_handle not in self.cached_people:
                self.add_relative(family.mother_handle, ancestors=ancestors)
            if include_children:
                for child in family.child_ref_list:
                    if child.ref not in self.cached_people:
                        self.add_relative(child.ref, offspring=offspring)
        else:
            if family.father_handle:
                self.add_person(family.father_handle)
            if family.mother_handle:
                self.add_person(family.mother_handle)
            for child in family.child_ref_list:
                self.add_person(child.ref)

    def set_family(
        self,
        handle: str,
        ancestors: int = 0,
        offspring: int = 0,
    ):
        """
        Generate a family timeline.
        """
        self._dump()
        self.timeline = []
        self.timeline_type = "family"
        self.cached_people = {}
        self.cached_events = []

        self.add_family(handle, ancestors, offspring)

    def events(self, raw=False):
        """
        Return the list of sorted events.
        """
        self.timeline.sort(key=lambda x: x[0])
        if raw:
            return self.timeline
        events = []
        for event in self.timeline:
            events.append(event[1])
        return events
