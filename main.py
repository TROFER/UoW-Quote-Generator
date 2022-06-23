import threading
import math
import time
import tkinter as tk
from tkinter import font, messagebox, ttk

# Global
STORE = "Winchester"


def display_pounds(pence: int) -> str:
    return "£{0:0.2f}".format(pence / 100)


# Data Classes
class Wrap:

    OVERLAP = 3  # Overlap left on each side
    PRICES = {0: 0.4, 1: 0.75}  # Price Per Centimeter (In Pence) Low & High
    COLOURS = [
        "Purple",
        "DarkSlateGray4",
        "Deep Sky Blue",
        "Light Sea Green",
        "VioletRed2",
        "Gold",
    ]
    SHAPE_VECTORS = {
        "Trapezium": [(0, 15), (7.25, 0), (30, 0), (37.25, 15)],
        "Hexagon": [(0, 15), (15, 0), (30, 0), (45, 15), (30, 30), (15, 30)],
    }

    def __init__(self, colour: str = COLOURS[0], quality: int = 0) -> None:
        self.colour = tk.StringVar(value=colour)
        self.quality = tk.IntVar(value=quality)

    def copy(self) -> object:
        """Returns a copy of itself"""
        return Wrap(colour=self.colour.get(), quality=self.quality.get())

    def draw(self, canvas) -> None:
        """Draws the selected paper on a canvas widget"""
        canvas.delete("all")

        if not self.quality.get():
            vectors = Wrap.SHAPE_VECTORS["Trapezium"]
            height = 15
            width = 38
            offset = 0
        else:
            vectors = Wrap.SHAPE_VECTORS["Hexagon"]
            height = 30
            width = 45
            offset = 30

        odd_line = False
        for y in range(0, int(canvas.cget("height")), height):
            for x in range(0, int(canvas.cget("width")), width):

                if odd_line:
                    x -= offset

                vertices = []
                for vector in vectors:
                    vertices.append(vector[0] + x)
                    vertices.append(vector[1] + y)

                canvas.create_polygon(
                    *vertices, fill=self.colour.get(), outline="#000000"
                )
            odd_line = not odd_line


class Gift:

    SHAPES = {0: "Cube", 1: "Cuboid", 2: "Cylinder"}
    MAX_SIZE = 500

    def __init__(
        self, shape: int = 0, x: int = 1, y: int = 1, z: int = 1
    ) -> None:
        self.shape = tk.IntVar(value=shape)
        self.x = tk.StringVar(value=x)
        self.y = tk.StringVar(value=y)
        self.z = tk.StringVar(value=z)

    def copy(self) -> object:
        """Returns a copy of itself"""
        return Gift(
            shape=self.shape.get(),
            x=self.x.get(),
            y=self.y.get(),
            z=self.z.get(),
        )

    def get_dimensions(self) -> list:
        """Returns dimensions as integers, in width, height, depth order"""
        if self.shape.get() == 0:
            dimensions = [self.x]

        elif self.shape.get() == 1:
            dimensions = [self.x, self.y, self.z]

        else:
            dimensions = [self.x, self.y]

        try:
            return [float(value.get()) for value in dimensions]
        except ValueError:
            return ValueError

    def wrap(self) -> float:
        """Returns amount of paper required to wrap the gift in CM2"""
        dimensions = self.get_dimensions()

        # Return 0 if dimensions are currently invalid
        if dimensions is ValueError:
            return 0

        # If Cube
        elif self.shape.get() == 0:
            if 0 in dimensions:
                return 0
            else:
                wrap_width = dimensions[0] * 4
                wrap_height = dimensions[0] * 3

        # If Cuboid
        elif self.shape.get() == 1:
            if dimensions.count(0) > 1:
                return 0
            else:
                wrap_width = (dimensions[0] * 2) + (dimensions[1] * 2)
                wrap_height = (dimensions[1] * 2) + dimensions[2]

        # If Cylinder
        else:
            if 0 in dimensions:
                return 0
            else:
                wrap_width = dimensions[0] * math.pi
                wrap_height = (dimensions[0] * 2) + dimensions[1]

        # Calculate and return sheet area
        overlap = 2 * Wrap.OVERLAP
        return (wrap_width + overlap) * (wrap_height + overlap)


class Quote:

    MAX_LABEL_SUMMARY_LENGTH = (
        20  # Maximum number of label characters visible in quote summary
    )

    def __init__(
        self,
        gift: Gift = None,
        wrap: Wrap = None,
        includes_label: int = 0,
        label_text: str = "",
        includes_bow: int = 0,
    ) -> None:
        self.gift = Gift() if gift is None else gift
        self.wrapping_paper = Wrap() if wrap is None else wrap

        self.includes_label = tk.IntVar(value=includes_label)
        self.label_text = tk.StringVar(value=label_text)
        self.includes_bow = tk.IntVar(value=includes_bow)

    def copy(self) -> object:
        """Returns a copy of itself"""
        return Quote(
            gift=self.gift.copy(),
            wrap=self.wrapping_paper.copy(),
            includes_label=self.includes_label.get(),
            label_text=self.label_text.get(),
            includes_bow=self.includes_bow.get(),
        )

    def get_total(self) -> int:
        """Retuns the quote cost in pence"""
        # Calculate paper cost ensuring to always round half up
        total = math.ceil(
            self.gift.wrap() * Wrap.PRICES[self.wrapping_paper.quality.get()]
        )

        if self.includes_bow.get():
            total += 150

        if self.includes_label.get():
            total += 50 + (2 * len(self.label_text.get()))

        return total

    def __str__(self) -> str:
        """Returns a short string summarising the quote configuration"""
        # Format dimensions as WxHxD string
        dimensions_string = "x".join(
            [str(round(value, 1)) for value in self.gift.get_dimensions()]
        )

        # Check if label is too long for full display
        label_text = self.label_text.get()
        if len(label_text) > Quote.MAX_LABEL_SUMMARY_LENGTH:
            label_text = f"{label_text[:Quote.MAX_LABEL_SUMMARY_LENGTH - 4]}"
            +"..."

        # Price, Shape, Size, Quality, Colour, Bow, Label, Label Text
        data = [
            display_pounds(self.get_total()),
            Gift.SHAPES[self.gift.shape.get()],
            f" {dimensions_string} CM",
            "EXP" if self.wrapping_paper.quality.get() else "CHP",
            self.wrapping_paper.colour.get(),
            "BOW" if self.includes_bow.get() else "NO BOW",
            f"LBL: {label_text}" if self.includes_label.get() else "NO LABEL",
        ]

        return "[Cost: {}] - [Gift: {},{}] - [Wrap: {}, {}] - [{}, {}]".format(
            *data
        )


class Order(list):
    def __init__(self, id: int = 1) -> None:
        super().__init__()
        self.id = id

    def get_total(self) -> int:
        """Returns the order total in pence"""
        return sum([quote.get_total() for quote in self])

    def export(self) -> str:
        """Exports the order to an external text file"""
        datestamp = time.strftime("%d-%m-%y")
        header = [
            f"{'=' * 20} Spence's International - {STORE} {'=' * 20}",
            "Thank you for your purchase!",
            f"Order Number: {self.id}",
            f"Date: {datestamp}",
            f"Items: {len(self)}",
            f"Subtotal: {display_pounds(self.get_total())}",
            f"{'-' * 31} Order Contents {'-' * 31}",
        ]

        filename = f"Export - {datestamp} - Order #{self.id}.txt"
        with open("./" + filename, "w") as export:
            [header.append(str(quote)) for quote in self]
            [export.write(line + "\n") for line in header]
        return filename


class WidgetStore(dict):
    def store(self, group: str, contents) -> None:
        if isinstance(contents, list):
            try:
                self[group] += contents
            except KeyError:
                self[group] = contents
        else:
            try:
                self[group].append(contents)
            except KeyError:
                self[group] = [contents]


# Window Classes
class Overview(tk.Tk):
    """Shows an overview of the current order"""

    def __init__(self) -> None:
        super().__init__()
        self.resizable(False, False)

        # Override Default Font
        font_ = font.nametofont("TkDefaultFont")
        font_.configure(family="Noto Sans", size=11)
        self.option_add("*Font", font_)

        # Create Window Styles
        self.style = ttk.Style(self)
        self.style.configure("TButton", background="#F8F8F8", relief="solid")
        self.style.configure("TRadiobutton", background="##ECECEC")
        self.style.configure("TCheckbutton", background="#F8F8F8")
        self.style.configure("TLabel", background="#F8F8F8")
        self.style.configure("TLabelframe", background="#F8F8F8")
        self.style.configure("TFrame", background="#F8F8F8")
        self.style.configure("Highlight.TFrame", background="#FF9200")

        # Variables
        self.order = Order()

        # Tk Display Variables
        self._quotes = tk.StringVar()
        self._order_total = tk.StringVar()
        self._total_items = tk.StringVar()

        # Set Keybindings
        self.bind("<Control-n>", func=self._add_quote)
        self.bind("<Control-e>", func=self._edit_quote)
        self.bind("<Control-s>", func=self._checkout)

        self._construct()
        self._stylize()
        self._pack()

    def show(self) -> None:
        threading.Thread(target=self._synchronise, daemon=True).start()
        self.mainloop()

    def _export_to_file(self) -> None:
        if not self.order:
            messagebox.showerror("Export Error", "Current order is empty")
        else:
            filename = self.order.export()
            messagebox.showinfo("Export", f"Order Exported as:\n{filename}")

    def _construct(self) -> None:
        # Menu Bar
        self._menubar = tk.Menu(self, bg="#F8F8F8", activebackground="#ff9200")
        file_menu = tk.Menu(
            self._menubar, tearoff=0, bg="#F8F8F8", activebackground="#ff9200"
        )
        edit_menu = tk.Menu(
            self._menubar, tearoff=0, bg="#F8F8F8", activebackground="#ff9200"
        )
        help_menu = tk.Menu(
            self._menubar, tearoff=0, bg="#F8F8F8", activebackground="#ff9200"
        )

        file_menu.add_command(label="Checkout", command=self._checkout)
        file_menu.add_command(
            label="Export to File", command=self._export_to_file
        )
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self._quit)
        edit_menu.add_command(label="Add Quote", command=self._add_quote)
        edit_menu.add_separator()
        edit_menu.add_command(
            label="Edit Selected Quote", command=self._edit_quote
        )
        edit_menu.add_command(
            label="Remove Selected Quote", command=self._remove_quote
        )
        edit_menu.add_separator()
        edit_menu.add_command(label="Clear Order", command=self._clear_order)
        help_menu.add_command(
            label="Shortcuts Guide", command=self._show_shortcuts
        )

        self._menubar.add_cascade(label="File", menu=file_menu)
        self._menubar.add_cascade(label="Edit", menu=edit_menu)
        self._menubar.add_cascade(label="Help", menu=help_menu)

        self.config(menu=self._menubar)

        # Frames
        self._centre_frame = ttk.Frame(self, padding=5)
        self._lower_frame = ttk.Frame(self, padding=5)

        # Widgets
        self._widgets = [
            tk.Listbox(self, listvariable=self._quotes),
            ttk.Label(self._centre_frame, textvariable=self._order_total),
            ttk.Label(self._centre_frame, textvariable=self._total_items),
            ttk.Button(
                self._lower_frame, text="Checkout", command=self._checkout
            ),
            ttk.Button(
                self._lower_frame, text="Add Quote", command=self._add_quote
            ),
        ]

    def _stylize(self) -> None:
        # Frames
        self._lower_frame.configure(style="Highlight.TFrame")

        # Widgets
        self._widgets[0].configure(
            width=95, height=30, borderwidth=0, relief="solid"
        )

    def _pack(self) -> None:
        # Widgets
        self._widgets[0].grid()
        self._widgets[1].pack(side="left")
        self._widgets[2].pack(side="right")
        self._widgets[3].pack(side="left")
        self._widgets[4].pack(side="right")

        # Frames
        self._centre_frame.grid(sticky="NESW")
        self._lower_frame.grid(sticky="NESW")

    def _synchronise(self) -> None:
        """Keeps the display synchronised with the current order object"""
        while True:
            self.title(f"Overview - Order #{self.order.id}")

            self._quotes.set([str(quote) for quote in self.order])

            self._order_total.set(
                f"Subtotal: {display_pounds(self.order.get_total())}"
            )

            self._total_items.set(f"Items: {len(self.order)}")
            time.sleep(0.5)

    def _quit(self) -> None:
        if messagebox.askyesno(
            title="Quit", message="Are you sure you want to quit?"
        ):
            self.quit()

    def _add_quote(self, *args) -> None:
        configurator = Configurator(self)
        self.withdraw()
        configurator.show()

    def _edit_quote(self, *args) -> None:
        try:
            selected_index = self._widgets[0].curselection()[0]
            configurator = Configurator(
                self, self.order[selected_index], selected_index
            )
            self.withdraw()
            configurator.show()

            self.order.pop(selected_index)
            self.active_configurator = True
        except IndexError:
            messagebox.showerror("Configurator", "No quote selected")

    def _remove_quote(self) -> None:
        try:
            index = self._widgets[0].curselection()[0]
            self.order.pop(index)
        except IndexError:
            messagebox.showerror("Configurator", "No quote selected")

    def _clear_order(self) -> None:
        if messagebox.askyesno(
            title="Clear Order",
            message="Are you sure you want to remove all quotes?",
        ):
            self.order.clear()

    def _checkout(self, *args) -> None:
        if not self.order:
            messagebox.showerror(
                "Checkout Error", "Cannot checkout with empty order"
            )
        else:
            Checkout(self)
            self.withdraw()

    def _show_shortcuts(self) -> None:
        ShortcutsGuide(self)
        self.withdraw()


class Configurator(tk.Toplevel):
    def __init__(
        self, parent: Overview, quote: Quote = None, index: int = None
    ) -> None:
        super().__init__()
        self.resizable(False, False)

        # Variables
        self._parent = parent
        self._quote = Quote() if quote is None else quote
        self._quote_index = index

        self._quote_unedited = self._quote.copy()
        self._quote_total = tk.StringVar()
        self._exit_flag = False

        # Base Styling
        self.config(background="#F8F8F8")

        # Set Keybindings
        self.bind("<Control-s>", func=self._add_to_order)

        self.title(f"Quote Configurator - Order #{self._parent.order.id}")
        self._construct()
        self._stylize()
        self._pack()

    def show(self) -> None:
        self._sync_thread = threading.Thread(target=self._synchronise)
        self._sync_thread.start()
        self._validate_spinboxes()
        self._update_preview()

    def destroy(self, revert_changes: bool = True) -> None:
        if revert_changes:
            if self._quote_index is not None:
                self._parent.order.insert(
                    self._quote_index, self._quote_unedited
                )

        elif not self._validate_spinboxes():
            return

        self._exit_flag = True
        self._sync_thread.join()
        self._parent.active_configurator = False
        self._parent.deiconify()
        super().destroy()

    def _construct(self) -> None:
        """Creates frames and widgets"""
        # Frames
        self._left_frame = ttk.Frame(self)
        self._right_frame = ttk.Frame(self)
        self._lower_frame = ttk.Frame(self, padding=2)

        self._shape_frame = ttk.LabelFrame(self._left_frame)
        self._size_frame = ttk.LabelFrame(self._left_frame)
        self._label_frame = ttk.LabelFrame(self._left_frame)
        self._bow_frame = ttk.LabelFrame(self._left_frame)

        self._preview_frame = ttk.LabelFrame(self._right_frame)
        self._wrapping_frame = ttk.LabelFrame(self._right_frame)

        # Widgets
        self._widgets = WidgetStore()

        self._widgets.store(
            "ShapeSelection",
            [
                ttk.Label(self._shape_frame, text="Gift Shape"),
                tk.Radiobutton(
                    self._shape_frame,
                    value=0,
                    text="Cube",
                    variable=self._quote.gift.shape,
                ),
                tk.Radiobutton(
                    self._shape_frame,
                    value=1,
                    text="Cuboid",
                    variable=self._quote.gift.shape,
                ),
                tk.Radiobutton(
                    self._shape_frame,
                    value=2,
                    text="Cylinder",
                    variable=self._quote.gift.shape,
                ),
            ],
        )

        self._widgets.store(
            "DimensionInput",
            [
                ttk.Label(self._size_frame, text="Gift Dimensions (CM)"),
                ttk.Spinbox(self._size_frame, textvariable=self._quote.gift.x),
                ttk.Spinbox(self._size_frame, textvariable=self._quote.gift.y),
                ttk.Spinbox(self._size_frame, textvariable=self._quote.gift.z),
                ttk.Label(self._size_frame, text="Width"),
                ttk.Label(self._size_frame, text="Height"),
                ttk.Label(self._size_frame, text="Depth"),
            ],
        )

        self._widgets.store(
            "LabelControl",
            [
                ttk.Label(self._label_frame, text="Label"),
                ttk.Checkbutton(
                    self._label_frame,
                    text="Include Label",
                    variable=self._quote.includes_label,
                ),
                ttk.Label(self._label_frame, text="Label Text"),
                ttk.Entry(
                    self._label_frame, textvariable=self._quote.label_text
                ),
            ],
        )

        self._widgets.store(
            "BowControl",
            [
                ttk.Label(self._bow_frame, text="Bow"),
                ttk.Checkbutton(
                    self._bow_frame,
                    text="Include Bow",
                    variable=self._quote.includes_bow,
                ),
            ],
        )

        self._widgets.store(
            "WrapPreview",
            [
                ttk.Label(self._preview_frame, text="Preview"),
                tk.Canvas(self._preview_frame),
            ],
        )

        self._widgets.store(
            "WrapSelection",
            [
                ttk.Label(self._wrapping_frame, text="Wrapping Paper"),
                ttk.Label(self._wrapping_frame, text="Paper Quality"),
                tk.Radiobutton(
                    self._wrapping_frame,
                    value=0,
                    text="Cheap",
                    variable=self._quote.wrapping_paper.quality,
                    command=self._update_preview,
                ),
                tk.Radiobutton(
                    self._wrapping_frame,
                    value=1,
                    text="Expensive",
                    variable=self._quote.wrapping_paper.quality,
                    command=self._update_preview,
                ),
                ttk.Label(self._wrapping_frame, text="Paper Colour"),
                ttk.Combobox(
                    self._wrapping_frame,
                    textvariable=self._quote.wrapping_paper.colour,
                    values=Wrap.COLOURS,
                ),
            ],
        )

        self._widgets.store(
            "ControlBar",
            [
                ttk.Button(
                    self._lower_frame, text="Cancel", command=self._cancel
                ),
                ttk.Label(self._lower_frame, textvariable=self._quote_total),
                ttk.Button(
                    self._lower_frame,
                    text="Add to Order",
                    command=self._add_to_order,
                ),
            ],
        )

    def _stylize(self) -> None:
        """Applies style properties"""
        # Frames
        self._shape_frame.configure(
            labelwidget=self._widgets["ShapeSelection"][0]
        )
        self._size_frame.configure(
            labelwidget=self._widgets["DimensionInput"][0]
        )
        self._label_frame.configure(
            labelwidget=self._widgets["LabelControl"][0]
        )
        self._bow_frame.configure(labelwidget=self._widgets["BowControl"][0])
        self._preview_frame.configure(
            labelwidget=self._widgets["WrapPreview"][0]
        )
        self._wrapping_frame.configure(
            labelwidget=self._widgets["WrapSelection"][0]
        )

        self._lower_frame.configure(style="Highlight.TFrame")

        # Widgets
        for widgets in list(self._widgets.values())[:-1]:
            widgets[0].configure(
                font=font.Font(family="Noto Sans", size=11, weight="bold")
            )

        for radiobutton in self._widgets["ShapeSelection"][1:]:
            radiobutton.configure(
                background="#F8F8F8",
                highlightbackground="#F8F8F8",
                activebackground="#F8F8F8",
            )

        for spinbox in self._widgets["DimensionInput"][1:4]:
            spinbox.configure(
                to=Gift.MAX_SIZE,
                width=7,
                validate="focusout",  # Only suitable validation mode
                validatecommand=self._validate_spinboxes,
            )

        self._widgets["LabelControl"][3].configure(width=27)
        self._widgets["WrapPreview"][1].configure(
            width=150, height=150, background="#FFFFFF"
        )

        for radiobutton in self._widgets["WrapSelection"][2:4]:
            radiobutton.configure(
                background="#F8F8F8",
                highlightbackground="#F8F8F8",
                activebackground="#F8F8F8",
            )

        self._widgets["WrapSelection"][5].configure(state="readonly", width=15)

        self._widgets["ControlBar"][1].configure(
            justify=tk.CENTER,
            background="#FF9200",
            font=font.Font(family="Noto Sans", size=12, weight="bold"),
        )

    def _pack(self) -> None:
        """Places all frames and widgets"""
        # Widgets
        x, y = 3, 3
        self._widgets["ShapeSelection"][1].grid(
            row=0, column=0, padx=x, pady=y
        )
        self._widgets["ShapeSelection"][2].grid(
            row=0, column=1, padx=x, pady=y
        )
        self._widgets["ShapeSelection"][3].grid(
            row=0, column=2, padx=x, pady=y
        )
        self._widgets["DimensionInput"][1].grid(
            row=0, column=0, padx=x, pady=y
        )
        self._widgets["DimensionInput"][2].grid(
            row=0, column=1, padx=x, pady=y
        )
        self._widgets["DimensionInput"][3].grid(
            row=0, column=2, padx=x, pady=y
        )
        self._widgets["DimensionInput"][4].grid(
            row=1, column=0, padx=x, pady=y
        )
        self._widgets["DimensionInput"][5].grid(
            row=1, column=1, padx=x, pady=y
        )
        self._widgets["DimensionInput"][6].grid(
            row=1, column=2, padx=x, pady=y
        )

        self._widgets["LabelControl"][1].grid(sticky="W", padx=x)
        self._widgets["LabelControl"][2].grid(sticky="W", padx=x)
        self._widgets["LabelControl"][3].grid(sticky="W", padx=x, pady=y)

        self._widgets["BowControl"][1].grid(sticky="W", padx=x, pady=y)

        self._widgets["WrapPreview"][1].pack(padx=x, pady=y)

        self._widgets["WrapSelection"][1].grid(padx=x, pady=y)
        self._widgets["WrapSelection"][2].grid(row=1, column=0, padx=x, pady=y)
        self._widgets["WrapSelection"][3].grid(row=1, column=1, padx=x, pady=y)
        self._widgets["WrapSelection"][4].grid(row=2, column=0, padx=x, pady=y)
        self._widgets["WrapSelection"][5].grid(row=2, column=1, padx=x, pady=y)

        self._lower_frame.columnconfigure(1, weight=1)
        self._widgets["ControlBar"][0].grid(row=0, column=0, padx=x, pady=y)
        self._widgets["ControlBar"][1].grid(row=0, column=1, padx=x, pady=y)
        self._widgets["ControlBar"][2].grid(row=0, column=2, padx=x, pady=y)

        # Group Frames
        x, y = 0, 3
        self._shape_frame.grid(column=0, sticky="NESW", padx=x, pady=y)
        self._size_frame.grid(column=0, sticky="NESW", padx=x, pady=y)
        self._label_frame.grid(column=0, sticky="NESW", padx=x, pady=y)
        self._bow_frame.grid(column=0, sticky="NESW", padx=x, pady=y)

        self._preview_frame.grid(column=0, sticky="NESW", padx=x, pady=y)
        self._wrapping_frame.grid(column=0, sticky="NESW", padx=x, pady=y)

        # Planes
        x, y = 5, 5
        self._left_frame.grid(row=0, column=0, padx=x, pady=y, sticky="N")
        self._right_frame.grid(row=0, column=1, padx=x, pady=y, sticky="N")
        self._lower_frame.grid(row=1, column=0, columnspan=2, sticky="NESW")

    def _validate_spinboxes(self) -> bool:
        for spinbox in self._widgets["DimensionInput"][1:4]:

            # Check for alpha characters
            if any([char.isalpha() for char in spinbox.get()]):
                messagebox.showerror(
                    "Invalid Dimension",
                    "Gift Dimensions Can't Contain Letters." +
                    "\nPlease Only Enter Numerical Values.",
                )
                return False

            # Check if spinbox is empty
            elif not spinbox.get() or float(spinbox.get()) == 0:
                messagebox.showerror(
                    "Invalid Dimension",
                    "Gift Dimensions Can't be Empty, Zero or Negative." +
                    f"\nPlease Enter a Value Between 1 and {Gift.MAX_SIZE}.",
                )
                return False

            # Check if value is negative
            elif float(spinbox.get()) < 0:
                messagebox.showerror(
                    "Invalid Dimension",
                    "Gift Dimensions Can't be Negative." +
                    f"\nPlease Enter a Value Between 1 and {Gift.MAX_SIZE}.",
                )
                return False

            # Check if value exceeds the maxium size
            elif float(spinbox.get()) > Gift.MAX_SIZE:
                messagebox.showerror(
                    "Invalid Dimension",
                    f"Gift Dimensions Exceed {Gift.MAX_SIZE} cm." +
                    f"\nPlease Enter a Value Between 1 and {Gift.MAX_SIZE}.",
                )
                return False

        return True

    def _update_preview(self) -> None:
        self._quote.wrapping_paper.draw(self._widgets["WrapPreview"][1])

    def _synchronise(self) -> None:
        """Synchronises the quote instance with the display contents"""
        colour_cache = self._quote.wrapping_paper.colour.get()

        while not self._exit_flag:
            self._quote_total.set(
                f"Total: {display_pounds(self._quote.get_total())}"
            )

            # Check if Wrapping Colour has Changed
            if colour_cache != self._quote.wrapping_paper.colour.get():
                self._update_preview()
                colour_cache = self._quote.wrapping_paper.colour.get()

            if self._quote.includes_label.get():
                self._widgets["LabelControl"][3].configure(state=tk.NORMAL)
            else:
                self._widgets["LabelControl"][3].configure(state=tk.DISABLED)

            # Enable and Disable Spinboxes
            if self._quote.gift.shape.get() == 0:
                self._widgets["DimensionInput"][1].configure(state=tk.NORMAL)
                self._widgets["DimensionInput"][2].configure(state=tk.DISABLED)
                self._widgets["DimensionInput"][3].configure(state=tk.DISABLED)

            elif self._quote.gift.shape.get() == 1:
                self._widgets["DimensionInput"][1].configure(state=tk.NORMAL)
                self._widgets["DimensionInput"][2].configure(state=tk.NORMAL)
                self._widgets["DimensionInput"][3].configure(state=tk.NORMAL)

            else:
                self._widgets["DimensionInput"][1].configure(state=tk.NORMAL)
                self._widgets["DimensionInput"][2].configure(state=tk.NORMAL)
                self._widgets["DimensionInput"][3].configure(state=tk.DISABLED)

            time.sleep(0.1)

    def _add_to_order(self, *args) -> None:
        if self._quote_index is None:
            self._parent.order.append(self._quote)
        else:
            self._parent.order.insert(self._quote_index, self._quote)
        self.destroy(revert_changes=False)

    def _cancel(self) -> None:
        self.destroy(revert_changes=True)


class Checkout(tk.Toplevel):
    def __init__(self, parent: Overview) -> None:
        super().__init__()
        self.resizable(False, False)

        # Variables
        self._parent = parent

        # Base Styling
        self.config(background="#F8F8F8")

        self.title(f"Checkout - Order #{self._parent.order.id}")
        self._construct()
        self._stylize()
        self._pack()

    def _construct(self) -> None:
        # Frames
        self._lower_frame = ttk.Frame(
            self, padding=5, style="Highlight.TFrame"
        )

        # Widgets
        self._widgets = [
            ttk.Label(self, text=f"Order Number: {self._parent.order.id}"),
            ttk.Label(self, text=f"Items: {len(self._parent.order)}"),
            ttk.Label(
                self,
                text=f"Subtotal: £0.00",
            ),
            ttk.Button(
                self._lower_frame, text="Quit Application", command=self._quit
            ),
            ttk.Button(
                self._lower_frame,
                text="Start New Order",
                command=self._new_order,
            ),
            ttk.Button(
                self._lower_frame,
                text="Export Order",
                command=self._export_to_file,
            ),
        ]

    def _stylize(self) -> None:
        self._widgets[0].configure(
            justify=tk.LEFT,
            font=font.Font(family="Noto Sans", size=15, weight="bold"),
        )
        self._widgets[1].configure(
            justify=tk.LEFT, font=font.Font(family="Noto Sans", size=13)
        )
        self._widgets[2].configure(
            justify=tk.LEFT, font=font.Font(family="Noto Sans", size=13)
        )

    def _pack(self) -> None:
        self._widgets[0].grid(row=0, column=0, sticky="W", padx=5)
        self._widgets[1].grid(row=1, column=0, sticky="W", padx=5)
        self._widgets[2].grid(row=2, column=0, sticky="W", padx=5)

        self._widgets[3].grid(row=0, column=0, padx=5)
        self._widgets[4].grid(row=0, column=1, padx=5)
        self._widgets[5].grid(row=0, column=2, padx=5)
        self._lower_frame.grid()

    def _quit(self) -> None:
        self._parent.destroy()

    def _export_to_file(self) -> None:
        filename = self._parent.order.export()
        messagebox.showinfo("Export", f"Order Exported as:\n{filename}")

    def _new_order(self) -> None:
        self._parent.order.clear()
        self._parent.order.id += 1
        self._parent.deiconify()
        self.destroy()


class ShortcutsGuide(tk.Toplevel):

    SHORTCUTS = {
        "New Quote (Overview)": "Ctl+N",
        "Edit Quote (Overview)": "Ctl+E",
        "Go to Checkout (Overview)": "Ctl+S",
        "Add to Order (Configurator)": "Ctl+S",
    }

    def __init__(self, parent: Overview) -> None:
        super().__init__()
        self.resizable(False, False)

        # Variables
        self._parent = parent

        self.title("Shortcuts Guide")
        self._construct()
        self._populate_shortcuts()
        self._pack()

    def _construct(self) -> None:
        # Frames
        self._lower_frame = ttk.Frame(
            self, padding=5, style="Highlight.TFrame"
        )

        #  Widgets
        self._shortcut_bindings = tk.Listbox(
            self,
            width=30,
            highlightcolor="#F8F8F8",
            highlightthickness=0,
            selectbackground="#F8F8F8",
        )
        self._shortcut_names = tk.Listbox(
            self,
            width=30,
            highlightcolor="#F8F8F8",
            highlightthickness=0,
            selectbackground="#F8F8F8",
        )
        self._close_button = ttk.Button(
            self._lower_frame, text="Close", command=self.destroy
        )

    def _populate_shortcuts(self) -> None:
        for name, binding in zip(
            ShortcutsGuide.SHORTCUTS.keys(), ShortcutsGuide.SHORTCUTS.values()
        ):
            self._shortcut_names.insert(0, name)
            self._shortcut_bindings.insert(0, binding)

    def _pack(self) -> None:
        self._shortcut_names.grid(row=0, column=0, sticky="NESW")
        self._shortcut_bindings.grid(row=0, column=1, sticky="NESW")

        self._close_button.pack(side="left")
        self._lower_frame.grid(row=1, column=0, sticky="NESW", columnspan=2)

    def destroy(self):
        self._parent.deiconify()
        super().destroy()


# Program Initalisation
if __name__ == "__main__":
    root = Overview()
    root.show()
