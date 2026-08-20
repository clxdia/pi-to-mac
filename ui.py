import os
import threading
from urllib.parse import unquote

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, Gdk, GLib

from transfer import FileTransfer


class PiToMac(Gtk.Window):

    def __init__(self):

        super().__init__(
            title="Pi to Mac"
        )

        self.set_default_size(
            500,
            350
        )

        self.set_border_width(20)

        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=15
        )

        self.add(box)

        # Title

        title = Gtk.Label()

        title.set_markup(
            "<big><b>Send Files from Pi to Mac</b></big>"
        )

        box.pack_start(
            title,
            False,
            False,
            0
        )

        # Drop area

        self.drop_area = Gtk.EventBox()

        drop_label = Gtk.Label(
            "Drop files here"
        )

        self.drop_area.add(
            drop_label
        )

        self.drop_area.set_size_request(
            -1,
            130
        )

        box.pack_start(
            self.drop_area,
            True,
            True,
            0
        )

        # Choose files

        choose_button = Gtk.Button(
            label="📁 Choose Files"
        )

        choose_button.connect(
            "clicked",
            self.on_choose_files
        )

        box.pack_start(
            choose_button,
            False,
            False,
            0
        )

        # Current file

        self.file_label = Gtk.Label()

        box.pack_start(
            self.file_label,
            False,
            False,
            0
        )

        # Progress

        self.progress_bar = Gtk.ProgressBar()

        self.progress_bar.set_show_text(
            True
        )

        box.pack_start(
            self.progress_bar,
            False,
            False,
            0
        )

        # Status

        self.info_label = Gtk.Label(
            label="Waiting for files…"
        )

        box.pack_start(
            self.info_label,
            False,
            False,
            0
        )

        # Drag & drop

        self.drop_area.drag_dest_set(
            Gtk.DestDefaults.ALL,
            [],
            Gdk.DragAction.COPY
        )

        self.drop_area.drag_dest_add_uri_targets()

        self.drop_area.connect(
            "drag-data-received",
            self.on_files_dropped
        )

    # -------------------------------------------------
    # Choose files
    # -------------------------------------------------

    def on_choose_files(self, button):

        dialog = Gtk.FileChooserDialog(
            title="Choose files to copy",
            parent=self,
            action=Gtk.FileChooserAction.OPEN
        )

        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK
        )

        dialog.set_select_multiple(True)

        response = dialog.run()

        if response == Gtk.ResponseType.OK:

            files = dialog.get_filenames()

            if files:
                self.start_transfer(files)

        dialog.destroy()

    # -------------------------------------------------
    # Drag & drop
    # -------------------------------------------------

    def on_files_dropped(
        self,
        widget,
        drag_context,
        x,
        y,
        data,
        info,
        timestamp
    ):

        files = []

        for uri in data.get_uris():

            path = uri.replace(
                "file://",
                ""
            )

            path = unquote(path)

            if os.path.isfile(path):
                files.append(path)

        if files:
            self.start_transfer(files)

        else:
            self.info_label.set_text(
                "No files found."
            )

        drag_context.finish(
            True,
            False,
            timestamp
        )

    # -------------------------------------------------
    # Start transfer
    # -------------------------------------------------

    def start_transfer(self, files):

        self.progress_bar.set_fraction(
            0
        )

        self.progress_bar.set_text(
            "0%"
        )

        self.file_label.set_text("")

        self.info_label.set_text(
            f"Preparing {len(files)} file(s)…"
        )

        transfer = FileTransfer(
            on_progress=self.on_progress
        )

        thread = threading.Thread(
            target=self.run_transfer,
            args=(transfer, files),
            daemon=True
        )

        thread.start()

    # -------------------------------------------------
    # Transfer thread
    # -------------------------------------------------

    def run_transfer(
        self,
        transfer,
        files
    ):

        total = len(files)

        for index, file_path in enumerate(files):

            filename = os.path.basename(
                file_path
            )

            GLib.idle_add(
                self.file_label.set_text,
                f"File {index + 1} of {total}: {filename}"
            )

            try:

                transfer.send_file(
                    file_path
                )

            except Exception as error:

                print(error)

                GLib.idle_add(
                    self.info_label.set_text,
                    f"❌ Failed: {filename}"
                )

                continue

        GLib.idle_add(
            self.progress_bar.set_fraction,
            1.0
        )

        GLib.idle_add(
            self.progress_bar.set_text,
            "Complete"
        )

        GLib.idle_add(
            self.info_label.set_text,
            f"✓ Successfully sent {total} file(s)"
        )

    # -------------------------------------------------
    # Progress callback
    # -------------------------------------------------

    def on_progress(
        self,
        percentage,
        speed,
        eta
    ):

        GLib.idle_add(
            self.progress_bar.set_fraction,
            percentage / 100
        )

        GLib.idle_add(
            self.progress_bar.set_text,
            f"{percentage}%"
        )

        GLib.idle_add(
            self.info_label.set_text,
            f"{speed}  •  {eta} remaining"
        )