# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2008       Raphael Ackermann
# Copyright (C) 2009-2010  Gary Burton
# Copyright (C) 2010       Benny Malengier
# Copyright (C) 2012       Doug Blank <doug.blank@gmail.com>
# Copyright (C) 2015-2016  Nick Hall
# Copyright (C) 2015       Serge Noiraud
# Copyright (C) 2021       Christopher Horn
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
Global configuration dialog functions
"""

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale


# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from ..frames.frame_utils import ConfigReset
from .page_const import (
    MEDIA_IMAGE_DISPLAY_MODES,
    PRIVACY_DISPLAY_MODES,
)
from .page_utils import create_grid, add_config_reset

_ = glocale.translation.sgettext


def build_global_grid(configdialog, grstate):
    """
    Build global option configuration section.
    """
    grid = create_grid()
    configdialog.add_text(grid, _("Global Options"), 0, bold=True)
    configdialog.add_checkbox(
        grid,
        _("Pin active header so it does not scroll"),
        1,
        "options.global.pin-header",
        tooltip=_(
            "Enabling this option pins the header so it will not scroll with the rest of the view."
        ),
    )
    configdialog.add_checkbox(
        grid,
        _("Enable coloring schemes"),
        2,
        "options.global.use-color-scheme",
        tooltip=_(
            "Enabling this option enables coloring schemes for the rendered frames. People and families currently use the default Gramps color scheme defined in the global preferences. This view also supports other user customizable color schemes to choose from for some of the object groups such as the timeline and citations."
        ),
    )
    configdialog.add_checkbox(
        grid,
        _("Use smaller font for details"),
        3,
        "options.global.use-smaller-detail-font",
        tooltip=_(
            "Indicates whether to use a smaller font for the details than used for the title."
        ),
    )
    configdialog.add_spinner(
        grid,
        _("Desired border width"),
        4,
        "options.global.border-width",
        (0, 5),
    )
    configdialog.add_checkbox(
        grid,
        _("Enable gramps ids"),
        10,
        "options.global.enable-gramps-ids",
        tooltip=_(
            "Indicates whether to show the Gramps id for primary objects or not."
        ),
    )
    configdialog.add_combo(
        grid,
        _("Privacy display mode"),
        11,
        "options.global.privacy-mode",
        PRIVACY_DISPLAY_MODES,
    )
    configdialog.add_checkbox(
        grid,
        _("Enable bookmark support"),
        12,
        "options.global.enable-bookmarks",
        tooltip=_("Indicates whether to enable bookmark support or not."),
    )
    configdialog.add_checkbox(
        grid,
        _("Link citation title to source page"),
        13,
        "options.global.link-citation-title-to-source",
        tooltip=_(
            "Indicates whether the source title link in a citation record links to the source page instead of the citation page."
        ),
    )
    configdialog.add_checkbox(
        grid,
        _("Include notes on child objects"),
        14,
        "options.global.include-child-notes",
        tooltip=_(
            "Enabling this option will include notes on children of the primary object in the Notes edit selection section of the action menu if any are present."
        ),
    )
    configdialog.add_checkbox(
        grid,
        _("Include urls from notes"),
        15,
        "options.global.include-note-urls",
        tooltip=_(
            "Enabling this option will parse the notes for the primary object and extract any identifiable urls for inclusion in the url group list."
        ),
    )
    configdialog.add_checkbox(
        grid,
        _("Sort tags by name not priority"),
        16,
        "options.global.sort-tags-by-name",
        tooltip=_(
            "Indicates if tags should be sorted by name and not priority. By default they sort by the priority in which they are organized in the tag organization tool."
        ),
    )
    configdialog.add_spinner(
        grid,
        _("Maximum citations per group"),
        17,
        "options.global.max-citations-per-group",
        (1, 500),
    )
    configdialog.add_spinner(
        grid,
        _("Maximum references per group"),
        18,
        "options.global.max-references-per-group",
        (1, 500),
    )
    configdialog.add_checkbox(
        grid,
        _("Enable warnings"),
        19,
        "options.global.enable-warnings",
        tooltip=_(
            "Indicates to show a warning dialog asking for confirmation before performing an action that removes or deletes data as a safeguard."
        ),
    )

    configdialog.add_text(grid, _("Media Bar Options"), 20, bold=True)
    configdialog.add_combo(
        grid,
        _("Media bar display mode"),
        21,
        "options.global.media-bar-display-mode",
        MEDIA_IMAGE_DISPLAY_MODES,
    )
    configdialog.add_checkbox(
        grid,
        _("Sort media by date"),
        22,
        "options.global.media-bar-sort-by-date",
        tooltip=_("Indicates whether to sort media items by date."),
    )
    configdialog.add_checkbox(
        grid,
        _("Group media by type"),
        23,
        "options.global.media-bar-group-by-type",
        tooltip=_(
            "Indicates whether to group like media, based on Media-Type."
        ),
    )
    configdialog.add_checkbox(
        grid,
        _("Filter out non-photos"),
        24,
        "options.global.media-bar-filter-non-photos",
        tooltip=_(
            "Indicates only photos should be displayed, based on Media-Type."
        ),
    )
    configdialog.add_checkbox(
        grid,
        _("Link image to media page"),
        25,
        "options.global.media-bar-page-link",
        tooltip=_(
            "Indicates left click should open the media page instead of the media viewer."
        ),
    )

    return add_config_reset(configdialog, grstate, "options.global", grid)
