#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2009-2010  Gary Burton
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2015-2016  Nick Hall
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
Widgets supporting various sections of the frame.
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
from gramps.gen.lib import Media, MediaRef
from gramps.gen.lib.mediabase import MediaBase
from gramps.gen.utils.file import media_path_full
from gramps.gui.utils import open_file_with_default_application

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..common.common_classes import GrampsConfig, GrampsContext
from ..common.common_const import (
    BUTTON_PRIMARY,
    GROUP_LABELS,
    GROUP_LABELS_SINGLE,
)
from ..common.common_utils import button_pressed, get_bookmarks, pack_icon
from ..services.service_status import StatusIndicatorService
from .frame_utils import get_tag_icon

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# FrameId class
#
# ------------------------------------------------------------------------
class FrameId(Gtk.HBox, GrampsConfig):
    """
    A class to display the id and privacy for a Frame object.
    """

    def __init__(self, grstate, groptions):
        Gtk.HBox.__init__(
            self,
            hexpand=False,
            vexpand=False,
            halign=Gtk.Align.END,
            valign=Gtk.Align.START,
        )
        GrampsConfig.__init__(self, grstate, groptions)

    def load(self, grobject, gramps_id=None):
        """
        Load the id field as needed for the given object.
        """
        if "Ref" in grobject.obj_type and self.groptions.ref_mode == 1:
            self.set_halign(Gtk.Align.START)
            self.add_privacy_indicator(grobject.obj)
            pack_icon(self, "stock_link")
            if grobject.is_primary:
                self.add_gramps_id(obj=grobject.obj)
            elif gramps_id:
                self.add_gramps_id(gramps_id=gramps_id)
        else:
            if grobject.is_primary:
                self.add_gramps_id(obj=grobject.obj)
            elif gramps_id:
                self.add_gramps_id(gramps_id=gramps_id)
            if grobject.has_handle:
                self.add_bookmark_indicator(grobject.obj, grobject.obj_type)
            elif "Ref" in grobject.obj_type:
                pack_icon(self, "stock_link")
            self.add_privacy_indicator(grobject.obj)
            if grobject.obj_type == "Person":
                self.add_home_indicator(grobject.obj)
            self.show_all()

    def reload(self, grobject, gramps_id=None):
        """
        Reload the field.
        """
        list(map(self.remove, self.get_children()))
        self.load(grobject, gramps_id=gramps_id)

    def add_gramps_id(self, obj=None, gramps_id=""):
        """
        Add the gramps id if needed.
        """
        if self.grstate.config.get("indicator.gramps-ids"):
            if obj:
                text = obj.gramps_id
            else:
                text = gramps_id
            label = Gtk.Label(
                use_markup=True,
                label=self.detail_markup.format(escape(text)),
            )
            self.pack_end(label, False, False, 0)

    def add_bookmark_indicator(self, obj, obj_type):
        """
        Add the bookmark indicator if needed.
        """
        if self.grstate.config.get("indicator.bookmarks"):
            for bookmark in get_bookmarks(
                self.grstate.dbstate.db, obj_type
            ).get():
                if bookmark == obj.get_handle():
                    pack_icon(self, "gramps-bookmark", tooltip=_("Bookmarked"))
                    break

    def add_privacy_indicator(self, obj):
        """
        Add privacy mode indicator if needed.
        """
        mode = self.grstate.config.get("indicator.privacy")
        if mode:
            if obj.private:
                if mode in [1, 3]:
                    pack_icon(self, "gramps-lock", tooltip=_("Private"))
            else:
                if mode in [2, 3]:
                    pack_icon(self, "gramps-unlock", tooltip=_("Public"))

    def add_home_indicator(self, obj):
        """
        Add the home indicator if needed.
        """
        if self.grstate.config.get("indicator.home-person"):
            default = self.grstate.dbstate.db.get_default_person()
            if default and default.get_handle() == obj.get_handle():
                pack_icon(self, "go-home", tooltip=_("Home Person"))


# ------------------------------------------------------------------------
#
# FrameGrid class
#
# ------------------------------------------------------------------------
class FrameGrid(Gtk.Grid):
    """
    A simple class to manage a fact grid for a Gramps frame.
    """

    def __init__(self, right=False):
        Gtk.Grid.__init__(
            self,
            row_spacing=2,
            column_spacing=6,
            halign=Gtk.Align.START,
            valign=Gtk.Align.START,
            hexpand=True,
        )
        self.row = 0
        if right:
            self.set_halign(Gtk.Align.END)

    def add_fact(self, fact, label=None):
        """
        Add a simple fact.
        """
        if label:
            self.attach(label, 0, self.row, 1, 1)
            self.attach(fact, 1, self.row, 1, 1)
        else:
            self.attach(fact, 0, self.row, 2, 1)
        self.row = self.row + 1


# ------------------------------------------------------------------------
#
# FrameIcons class
#
# ------------------------------------------------------------------------
class FrameIcons(Gtk.HBox, GrampsConfig):
    """
    A simple class for managing display of the child indicator and tag
    icons for a Gramps object.
    """

    def __init__(self, grstate, groptions, right_justify=False):
        if right_justify:
            justify = Gtk.Align.END
        else:
            justify = Gtk.Align.START
        Gtk.HBox.__init__(self, halign=justify, valign=Gtk.Align.END)
        GrampsConfig.__init__(self, grstate, groptions)
        self.flowbox = Gtk.FlowBox(
            orientation=Gtk.Orientation.HORIZONTAL,
            homogeneous=False,
            valign=Gtk.Align.END,
            halign=justify,
        )
        self.flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        if "active" in self.groptions.option_space:
            size = self.grstate.config.get("display.icons-active-width")
        else:
            size = self.grstate.config.get("display.icons-group-width")
        self.flowbox.set_min_children_per_line(size)
        self.flowbox.set_max_children_per_line(size)
        self.pack_end(self.flowbox, True, True, 0)
        self.grobject = None
        self.title = None

    def load(self, grobject, title=None):
        """
        Load icons for an object.
        """
        self.title = title
        self.grobject = grobject

        self.load_status(grobject)
        if self.grstate.config.get("indicator.child-objects"):
            self.load_indicators(grobject)

        if self.grstate.config.get("indicator.tags") and grobject.has_tags:
            self.load_tags(grobject)
        self.show_all()

    def load_status(self, grobject):
        """
        Load status indicators for an object.
        """
        status_service = StatusIndicatorService()
        for icon in status_service.get_status(self.grstate, grobject.obj):
            self.flowbox.add(icon)

    def load_indicators(self, grobject):
        """
        Load child icon indicators for an object.
        """
        obj = grobject.obj
        obj_type = grobject.obj_type
        check = self.grstate.config.get

        if obj_type == "Person":
            self.__load_person(obj, check)
        elif obj_type == "Family" and check("indicator.children"):
            count = len(obj.get_child_ref_list())
            if count:
                self.__add_icon("gramps-person", "child", count)
        if check("indicator.events") and grobject.has_events:
            count = len(obj.get_event_ref_list())
            if count:
                self.__add_icon("gramps-event", "event", count)
        if check("indicator.ordinances") and grobject.has_ldsords:
            count = len(obj.get_lds_ord_list())
            if count:
                self.__add_icon("emblem-documents", "ldsord", count)
        if check("indicator.attributes") and grobject.has_attributes:
            count = len(obj.get_attribute_list())
            if count:
                self.__add_icon("gramps-attribute", "attribute", count)
        if check("indicator.media") and grobject.has_media:
            count = len(obj.get_media_list())
            if count:
                self.__add_icon("gramps-media", "media", count)
        if check("indicator.citations") and grobject.has_citations:
            count = len(obj.get_citation_list())
            if count:
                self.__add_icon("gramps-citation", "citation", count)
        if check("indicator.notes") and grobject.has_notes:
            count = len(obj.get_note_list())
            if count:
                self.__add_icon("gramps-notes", "note", count)
        if check("indicator.addresses") and grobject.has_addresses:
            count = len(obj.get_address_list())
            if count:
                self.__add_icon("gramps-address", "address", count)
        if check("indicator.urls") and grobject.has_urls:
            count = len(obj.get_url_list())
            if count:
                self.__add_icon("gramps-url", "url", count)

    def __load_person(self, obj, check):
        """
        Examine and load indicators for a person.
        """
        if check("indicator.names"):
            count = len(obj.get_alternate_names())
            if count:
                self.__add_icon("user-info", "name", count)
        if check("indicator.parents"):
            count = len(obj.get_parent_family_handle_list())
            if count:
                self.__add_icon("gramps-family", "parent", count)
        if check("indicator.spouses"):
            count = len(obj.get_family_handle_list())
            if count:
                self.__add_icon("gramps-spouse", "spouse", count)
        if check("indicator.associations"):
            count = len(obj.get_person_ref_list())
            if count:
                self.__add_icon("gramps-person", "association", count)

    def __add_icon(self, icon_name, group_type, count):
        """
        Add an indicator icon.
        """
        icon = Gtk.Image(halign=Gtk.Align.END)
        icon.set_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
        if count == 1:
            text = GROUP_LABELS_SINGLE[group_type]
            if group_type == "parent":
                text = " ".join((_("Set"), _("of"), GROUP_LABELS[group_type]))
        else:
            text = GROUP_LABELS[group_type]
            if group_type == "parent":
                text = " ".join((_("Sets"), _("of"), text))
        tooltip = " ".join((str(count), text))
        eventbox = Gtk.EventBox(tooltip_text=tooltip)
        if self.grstate.config.get("indicator.child-objects-counts"):
            box = Gtk.HBox(hexpand=False, vexpand=False, spacing=2, margin=0)
            label = self.get_label(str(count))
            box.pack_start(label, False, False, 0)
            box.pack_start(icon, False, False, 0)
            eventbox.add(box)
        else:
            eventbox.add(icon)
        eventbox.connect(
            "button-press-event", self.__indicator_press, group_type
        )
        eventbox.connect("button-release-event", self.__indicator_release)
        self.flowbox.add(eventbox)

    def __indicator_press(self, _dummy_obj, event, group_type):
        """
        Launch group dialog.
        """
        if not button_pressed(event, BUTTON_PRIMARY):
            return False
        self.grstate.show_group(
            self.grobject.obj, group_type, title=self.title
        )
        return True

    def __indicator_release(self, *_dummy_args):
        """
        Sink action.
        """
        return True

    def load_tags(self, grobject):
        """
        Load tags for an object.
        """
        tags = []
        for handle in grobject.obj.get_tag_list():
            tag = self.fetch("Tag", handle)
            tags.append(tag)

        if self.grstate.config.get("indicator.tags-sort-by-name"):
            tags.sort(key=lambda x: x.name)
        else:
            tags.sort(key=lambda x: x.priority)

        for tag in tags:
            eventbox = Gtk.EventBox(tooltip_text=tag.name)
            eventbox.add(get_tag_icon(tag))
            eventbox.connect(
                "button-press-event", self.__tag_click, tag.handle
            )
            self.flowbox.add(eventbox)

    def __tag_click(self, _dummy_obj, event, handle):
        """
        Request page for tag.
        """
        if button_pressed(event, BUTTON_PRIMARY):
            tag = self.fetch("Tag", handle)
            page_context = GrampsContext(tag, None, None)
            self.grstate.load_page(page_context.pickled)
            return True
        return False


# ------------------------------------------------------------------------
#
# GrampsImage class
#
# ------------------------------------------------------------------------
class GrampsImage(Gtk.EventBox):
    """
    A simple class for managing display of an image for a Frame object.
    """

    def __init__(self, grstate, obj=None, media_ref=None, active=False):
        Gtk.EventBox.__init__(self)
        self.grstate = grstate
        self.media_ref = None
        self.active = active

        if isinstance(obj, Media):
            self.media = obj
        elif isinstance(media_ref, MediaRef):
            self.media_ref = media_ref
            self.media = grstate.fetch("Media", media_ref.ref)
        elif isinstance(obj, MediaBase) and obj.get_media_list():
            self.media_ref = obj.get_media_list()[0]
            self.media = grstate.fetch("Media", self.media_ref.ref)
        else:
            self.media = None

        if self.media:
            self.path = media_path_full(
                self.grstate.dbstate.db, self.media.get_path()
            )

    def load(self, size=0, crop=True):
        """
        Load or reload an image.
        """
        if self.media:
            list(map(self.remove, self.get_children()))
            thumbnail = self.__get_thumbnail(size, crop)
            if thumbnail:
                self.add(thumbnail)
                self.connect("button-press-event", self.handle_click)

    def __get_thumbnail(self, size, crop):
        """
        Get the thumbnail image.
        """
        if self.media and self.media.get_mime_type()[0:5] == "image":
            rectangle = None
            if self.media_ref and crop:
                rectangle = self.media_ref.get_rectangle()
            pixbuf = self.grstate.thumbnail(self.path, rectangle, size)
            image = Gtk.Image()
            image.set_from_pixbuf(pixbuf)
            return image
        return None

    def handle_click(self, _dummy_obj, event):
        """
        Open the image in the default picture viewer.
        """
        if button_pressed(event, BUTTON_PRIMARY):
            if not self.active and self.grstate.config.get(
                "general.image-page-link"
            ):
                context = GrampsContext(self.media, None, None)
                return self.grstate.load_page(context.pickled)
            open_file_with_default_application(self.path, self.grstate.uistate)
            return True
        return False
