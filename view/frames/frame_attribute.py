#
# Gramps - a GTK+/GNOME based genealogy program
#
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
AttributeGrampsFrame
"""

# ------------------------------------------------------------------------
#
# Python modules
#
# ------------------------------------------------------------------------
from html import escape

# ------------------------------------------------------------------------
#
# GTK modules
#
# ------------------------------------------------------------------------
from gi.repository import Gtk

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.utils.alive import probably_alive

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..common.common_classes import GrampsContext
from ..common.common_utils import get_person_color_css
from .frame_secondary import SecondaryGrampsFrame

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# AttributeGrampsFrame class
#
# ------------------------------------------------------------------------
class AttributeGrampsFrame(SecondaryGrampsFrame):
    """
    The AttributeGrampsFrame exposes facts about an Attribute.
    """

    def __init__(self, grstate, groptions, obj, attribute):
        SecondaryGrampsFrame.__init__(self, grstate, groptions, obj, attribute)

        name = glocale.translation.sgettext(attribute.get_type().xml_str())
        if "Ref" not in self.primary.obj_type:
            label = self.get_link(
                name,
                self.primary.obj_type,
                self.primary.obj.get_handle(),
                callback=self.switch_attribute_page,
            )
        else:
            name = "".join(("<b>", escape(name), "</b>"))
            label = Gtk.Label(
                halign=Gtk.Align.START,
                wrap=True,
                xalign=0.0,
                justify=Gtk.Justification.LEFT,
            )
            label.set_markup(name)
        self.widgets["title"].pack_start(label, False, False, 0)

        if attribute.get_value():
            self.add_fact(self.get_label(attribute.get_value()))

        self.show_all()
        self.enable_drag()
        self.enable_drop()
        self.set_css_style()

    def switch_attribute_page(self, *_dummy_obj):
        """
        Initiate switch to attribute page.
        """
        context = GrampsContext(self.primary.obj, None, self.secondary.obj)
        self.grstate.load_page(context.pickled)

    def build_action_menu(self, _dummy_obj, event):
        """
        Build the action menu for a right click. First action will always be
        edit, then any custom actions of the derived children, then the global
        actions supported for all objects enabled for them.
        """
        if "Ref" not in self.primary.obj_type:
            SecondaryGrampsFrame.build_action_menu(self, _dummy_obj, event)
        return True

    def route_action(self, obj, event):
        """
        Route the action if the frame was clicked on.
        """
        if "Ref" not in self.primary.obj_type:
            SecondaryGrampsFrame.route_action(self, obj, event)

    def edit_secondary_object(self, _dummy_var1=None):
        """
        Override default method to launch the attribute editor.
        """
        self.edit_attribute(None, self.secondary.obj)

    def get_color_css(self):
        """
        Determine color scheme to be used if available."
        """
        if self.grstate.config.get("options.global.use-color-scheme"):
            if self.primary.obj_type == "Person":
                living = probably_alive(
                    self.primary.obj, self.grstate.dbstate.db
                )
                return get_person_color_css(
                    self.primary.obj,
                    living=living,
                )
        return ""
