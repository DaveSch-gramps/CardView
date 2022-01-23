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

register(
    GENERAL,
    id="status_todo",
    name=_("To Do Indicator"),
    description=_("A To Do note status indicator."),
    category="STATUS",
    version="0.9",
    gramps_target_version="5.1",
    status=STABLE,
    fname="status_todo.py",
    load_on_reg=True,
    authors=["Christopher Horn"],
    authors_email=["https://gramps-project.org"],
)
