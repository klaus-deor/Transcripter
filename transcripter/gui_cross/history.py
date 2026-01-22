"""Cross-platform History window using tkinter."""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from ..clipboard import ClipboardHistory, ClipboardManager, format_timestamp


class HistoryWindow:
    """Cross-platform history window using tkinter."""

    def __init__(
        self,
        clipboard_history: ClipboardHistory,
        clipboard_manager: ClipboardManager,
        max_items: int = 50
    ):
        """
        Initialize the history window.

        Args:
            clipboard_history: ClipboardHistory instance
            clipboard_manager: ClipboardManager for copying text
            max_items: Maximum number of history items to display
        """
        self.clipboard_history = clipboard_history
        self.clipboard_manager = clipboard_manager
        self.max_items = max_items
        self.window: Optional[tk.Toplevel] = None
        self.tree: Optional[ttk.Treeview] = None
        self.text_display: Optional[tk.Text] = None

    def show(self) -> None:
        """Show the history window."""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            self.window.focus_force()
            self._refresh_history()
            return

        self._create_window()

    def _create_window(self) -> None:
        """Create the history window and its widgets."""
        self.window = tk.Toplevel()
        self.window.title("Transcription History")
        self.window.geometry("600x500")
        self.window.resizable(True, True)

        # Center the window
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'+{x}+{y}')

        # Main frame
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill='x', pady=(0, 10))

        ttk.Label(header_frame, text="Recent Transcriptions", font=('', 12, 'bold')).pack(side='left')
        ttk.Button(header_frame, text="Refresh", command=self._refresh_history).pack(side='right')

        # Create paned window for list and preview
        paned = ttk.PanedWindow(main_frame, orient='vertical')
        paned.pack(fill='both', expand=True)

        # Top: Treeview for history list
        tree_frame = ttk.Frame(paned)

        # Create Treeview
        columns = ('timestamp', 'preview', 'length')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', selectmode='browse')

        self.tree.heading('timestamp', text='Time')
        self.tree.heading('preview', text='Text Preview')
        self.tree.heading('length', text='Length')

        self.tree.column('timestamp', width=150, minwidth=120)
        self.tree.column('preview', width=300, minwidth=200)
        self.tree.column('length', width=80, minwidth=60)

        # Scrollbar for treeview
        tree_scroll = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)

        self.tree.pack(side='left', fill='both', expand=True)
        tree_scroll.pack(side='right', fill='y')

        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        self.tree.bind('<Double-1>', self._on_double_click)

        paned.add(tree_frame, weight=1)

        # Bottom: Text display for full content
        text_frame = ttk.LabelFrame(paned, text="Full Text")

        self.text_display = tk.Text(text_frame, wrap='word', height=8)
        text_scroll = ttk.Scrollbar(text_frame, orient='vertical', command=self.text_display.yview)
        self.text_display.configure(yscrollcommand=text_scroll.set)

        self.text_display.pack(side='left', fill='both', expand=True)
        text_scroll.pack(side='right', fill='y')

        paned.add(text_frame, weight=1)

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(10, 0))

        ttk.Button(button_frame, text="Close", command=self._on_close).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Clear History", command=self._on_clear).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Copy Selected", command=self._on_copy).pack(side='right', padx=5)

        # Load history
        self._refresh_history()

    def _refresh_history(self) -> None:
        """Refresh the history display."""
        if not self.tree:
            return

        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Get history
        history = self.clipboard_history.get_recent(self.max_items)

        if not history:
            # Show empty message in text display
            self.text_display.config(state='normal')
            self.text_display.delete('1.0', 'end')
            self.text_display.insert('1.0', "No transcriptions yet.\n\nUse the hotkey to record and transcribe audio.")
            self.text_display.config(state='disabled')
            return

        # Add items (newest first)
        for i, item in enumerate(reversed(history)):
            timestamp = format_timestamp(item['timestamp'])
            text = item['text']
            preview = text[:50] + "..." if len(text) > 50 else text
            preview = preview.replace('\n', ' ')
            length = f"{item['length']} chars"

            # Store original index for retrieval
            original_idx = len(history) - 1 - i
            self.tree.insert('', 'end', iid=str(original_idx), values=(timestamp, preview, length))

        # Select first item
        if history:
            first_item = self.tree.get_children()[0]
            self.tree.selection_set(first_item)
            self._show_text(len(history) - 1)

    def _on_select(self, event) -> None:
        """Handle selection change."""
        selection = self.tree.selection()
        if selection:
            idx = int(selection[0])
            self._show_text(idx)

    def _on_double_click(self, event) -> None:
        """Handle double-click to copy."""
        self._on_copy()

    def _show_text(self, index: int) -> None:
        """Show the full text for the selected item."""
        item = self.clipboard_history.get_item(index)
        if item:
            self.text_display.config(state='normal')
            self.text_display.delete('1.0', 'end')
            self.text_display.insert('1.0', item['text'])
            self.text_display.config(state='disabled')

    def _on_copy(self) -> None:
        """Copy selected item to clipboard."""
        selection = self.tree.selection()
        if not selection:
            return

        idx = int(selection[0])
        item = self.clipboard_history.get_item(idx)
        if item:
            self.clipboard_manager.copy_text(item['text'])
            messagebox.showinfo("Copied", "Text copied to clipboard!")

    def _on_clear(self) -> None:
        """Clear all history."""
        if messagebox.askyesno(
            "Clear History",
            "This will remove all transcription history.\nThis action cannot be undone.\n\nContinue?"
        ):
            self.clipboard_history.clear_history()
            self._refresh_history()

    def _on_close(self) -> None:
        """Close the window."""
        self.window.destroy()
        self.window = None
