from tkinter import *
from PIL import Image
from PIL.ImageTk import PhotoImage
from Components import GameField


class MyField(Frame):
    item_choosen = {'num': None}

    def __init__(self, *args, **kargs):
        Frame.__init__(self, *args, **kargs)
        self.parent = args[0]
        self.makeWidgets()
        self.sizex = 3
        self.sizey = 20

    def makeWidgets(self):
        global items
        self.frameField = Frame(self)
        self.frameField.pack(padx=10, pady=10, fill=BOTH, expand=YES)
        self.label = Label(self.frameField, text="Пентамино")

        self.system = Frame(self.frameField, width=200, height=500)
        self.superfield = Frame(self.system, width=220, height=500)
        self.superfield.pack(expand=YES, fill=Y)
        self.shop = Canvas(self.superfield, width=204, height=400, relief=GROOVE, bd=3)
        self.shopCanvasScroll = Scrollbar(self.superfield, orient='vertical', command=self.shop.yview)
        self.shopCanvasScroll.pack(side=RIGHT, fill=Y, expand=True)
        self.shop.configure(yscrollcommand=self.shopCanvasScroll.set)
        self.status = Canvas(self.system, width=200, height=100, relief=GROOVE, bd=3)
        self.field = GameField.GameField(self.frameField, width=500, height=500, bg="#ffffff", relief=GROOVE, bd=3,
                                         status=self.status, items=items)
        self.field.bind('<Configure>', lambda x: self.field.update())
        self.field.bind('<Motion>', lambda x: self.field.overlay(x, self.item_choosen))
        root.bind('<r>', lambda x: self.rotate_item(self.item_choosen))
        root.bind('<f>', lambda x: self.flip_item(x, self.item_choosen))
        self.field.bind('<Button-1>', lambda x: self.field.add_figure(x, self.item_choosen))
        self.field.bind('<Button-3>', lambda x: self.field.delete_figure(x))
        self.shop.bind('<Button-1>', lambda x: self.moveShop(x))
        self.label.pack()
        self.field.pack(side=LEFT, padx=10, expand=YES, fill=BOTH)
        self.system.pack(fill=Y, expand=YES)
        self.shop.pack(expand=YES, fill=Y)
        self.status.pack()
        self.fillShop()

        menubar = Menu(self.parent)
        self.parent.config(menu=menubar)
        file_menu = Menu(menubar, tearoff=0)
        field_sizes = Menu(file_menu, tearoff=0)
        field_sizes.add_command(label="3x20", command=lambda: self.field.set_geometry(3, 20))
        field_sizes.add_command(label="6x10", command=lambda: self.field.set_geometry(6, 10))
        field_sizes.add_command(label="5x12", command=lambda: self.field.set_geometry(5, 12))
        field_sizes.add_command(label="4x15", command=lambda: self.field.set_geometry(4, 15))
        file_menu.add_command(label="Очистить", command=lambda: self.field.clear_field())
        file_menu.add_cascade(label="Изменить размер", menu=field_sizes)
        menubar.add_cascade(label="Поле", menu=file_menu)
        menubar.add_cascade(label="Сохранить", command=lambda: self.field.save_game())
        menubar.add_cascade(label="Заргузить", command=lambda: self.field.load_game())

    """Вращаем элемент"""

    def rotate_item(self, item):
        item['current_rotation'] += 1
        if item['current_rotation'] >= len(item['rotations']):
            item['current_rotation'] = 0
        item['cords'] = item['rotations'][item['current_rotation']]
        self.field.overlay(self.status.event_info_custom, item)

    """Отражаем элемент по горизонтали"""

    def flip_item(self, event, item):
        for cord in item['cords']:
            if cord[0] != 0:
                cord[0] *= -1
        self.field.overlay(self.status.event_info_custom, item)

    """Выбираем элемент"""

    def moveShop(self, event):
        root.update()
        # определяем клеточку. Берем координаты по y и
        yCord = int(self.shop.canvasy(event.y)) // 100
        xCord = int(self.shop.canvasx(event.x)) // 100
        item = yCord * 2 + xCord
        if item < 13:
            if self.item_choosen['num'] != items[item]['num']:
                self.shop.create_rectangle(0, 0, self.shop.winfo_width(), 700, fill="#eeeeee")
                self.fillShop()
                self.shop.create_rectangle(4 + xCord * 102, yCord * 100, xCord * 102 + 100, yCord * 100 + 100,
                                           outline="red")
                self.item_choosen = items[item]
            else:
                self.item_choosen = {'num': None}
                self.fillShop()

    """Хелпер для создания изображения элементов"""

    def create_shop_image(self, path):
        width = self.shop.winfo_width()
        size = (100, 100)
        img = Image.open(path)
        img = img.resize(size)
        return img

    """Заполняет магаз картинками"""

    def fillShop(self):
        self.shop.delete(ALL)
        # Звполняем сетку изображениями
        images = ["./Assets/F.png",
                  "./Assets/I.png",
                  "./Assets/G.png",
                  "./Assets/N.png",
                  "./Assets/P.png",
                  "./Assets/T.png",
                  "./Assets/U.png",
                  "./Assets/V.png",
                  "./Assets/W.png",
                  "./Assets/X.png",
                  "./Assets/Y.png",
                  "./Assets/Z.png",
                  ]
        self.shop_items = ['' for i in images]
        j = 0
        k = 0
        for (i, image) in enumerate(images):
            self.shop_items[i] = PhotoImage(self.create_shop_image(image))
            self.shop.create_image(54 + (i % 2 * 102), 50 + (j * 100), image=self.shop_items[i])
            k += 1
            if k == 2:
                j += 1
                k = 0
        self.shop.configure(scrollregion=self.shop.bbox("all"))


items = [
    {'num': 1,
     'rotations': [
         [[0, 0], [-1, 0], [1, -1], [0, 1], [0, -1]],
         [[0, 0], [0, -1], [1, 0], [1, 1], [-1, 0]],
         [[0, 0], [1, 0], [0, 1], [-1, 1], [0, -1]],
         [[0, 0], [0, 1], [-1, 0], [-1, -1], [1, 0]],
     ],
     'current_rotation': 0,
     'banned': False,
     'cords': [[0, 0], [-1, 0], [1, -1], [0, 1], [0, -1]],
     'color': "#ff4132"
     },
    {'num': 2,
     'rotations': [
         [[0, 0], [0, -1], [0, -2], [0, 1], [0, 2]],
         [[0, 0], [-1, 0], [-2, 0], [1, 0], [2, 0]],
     ],
     'current_rotation': 0,
     'banned': False,
     'cords': [[0, 0], [0, -1], [0, -2], [0, 1], [0, 2]],
     'color': "#9c3cc4"
     },
    {'num': 3,
     'rotations': [
         [[0, 0], [0, -1], [0, 1], [0, 2], [1, 2]],
         [[0, 0], [1, 0], [-1, 0], [-2, 0], [-2, 1]],
         [[0, 0], [0, 1], [0, -1], [0, -2], [-1, -2]],
         [[0, 0], [-1, 0], [1, 0], [2, 0], [2, -1]],
     ],
     'current_rotation': 0,
     'banned': False,
     'cords': [[0, 0], [0, -1], [0, 1], [0, 2], [1, 2]],
     'color': "#6bc43c"
     },
    {'num': 4,
     'rotations': [
         [[0, 0], [0, -1], [0, -2], [-1, 0], [-1, 1]],
         [[0, 0], [1, 0], [2, 0], [-1, -1], [0, -1]],
         [[0, 0], [0, 1], [0, 2], [1, -1], [1, 0]],
         [[0, 0], [-1, 0], [-2, 0], [1, 1], [0, 1]],
     ],
     'current_rotation': 0,
     'banned': False,
     'cords': [[0, 0], [0, -1], [0, -2], [-1, 0], [-1, 1]],
     'color': "#3350b9"
     },
    {'num': 5,
     'rotations': [
         [[0, 0], [0, -1], [0, 1], [1, 0], [1, -1]],
         [[0, 0], [1, 0], [-1, 0], [0, 1], [1, 1]],
         [[0, 0], [1, 0], [1, -1], [1, 1], [0, 1]],
         [[0, 0], [1, 0], [2, 1], [1, 1], [0, 1]],
     ],
     'current_rotation': 0,
     'banned': False,
     'cords': [[0, 0], [0, -1], [0, 1], [1, 0], [1, -1]],
     'color': "#0ff2da"
     },
    {'num': 6,
     'rotations': [
         [[0, 0], [0, -1], [0, 1], [-1, -1], [1, -1]],
         [[0, 0], [1, 0], [1, -1], [-1, 0], [1, 1]],
         [[0, 0], [0, -1], [1, 1], [0, 1], [-1, 1]],
     ],
     'current_rotation': 0,
     'banned': False,
     'cords': [[0, 0], [0, -1], [0, 1], [-1, -1], [1, -1]],
     'color': "#f2ba0f"
     },
    {'num': 7,
     'rotations': [
         [[0, 0], [-1, 0], [-1, -1], [1, 0], [1, -1]],
         [[0, 0], [0, -1], [0, 1], [1, 1], [1, -1]],
         [[0, 0], [-1, 0], [-1, 1], [1, 0], [1, 1]],
     ],
     'current_rotation': 0,
     'banned': False,
     'cords': [[0, 0], [-1, 0], [-1, -1], [1, 0], [1, -1]],
     'color': "#0097f6"
     },
    {'num': 8,
     'rotations': [
         [[0, 0], [0, -1], [0, -2], [1, 0], [2, 0]],
         [[0, 0], [0, 1], [0, 2], [-1, 0], [-2, 0]],
     ],
     'current_rotation': 0,
     'banned': False,
     'cords': [[0, 0], [0, -1], [0, -2], [1, 0], [2, 0]],
     'color': "#697478"
     },
    {'num': 9,
     'rotations': [
         [[0, 0], [-1, 0], [-1, -1], [0, 1], [1, 1]],
         [[0, 0], [-1, 0], [-1, 1], [0, -1], [1, -1]],
     ],
     'current_rotation': 0,
     'banned': False,
     'cords': [[0, 0], [-1, 0], [-1, -1], [0, 1], [1, 1]],
     'color': "#f918c7"
     },
    {'num': 10,
     'rotations': [[[0, 0], [-1, 0], [0, -1], [0, 1], [1, 0]]],
     'banned': False,
     'current_rotation': 0,
     'cords': [[0, 0], [-1, 0], [0, -1], [0, 1], [1, 0]],
     'color': "#ffec12"
     },
    {'num': 11,
     'rotations': [
         [[0, 0], [-1, 0], [0, -1], [0, 1], [0, 2]],
         [[0, 0], [0, -1], [-1, 0], [1, 0], [2, 0]],
         [[0, 0], [-1, 1], [0, -1], [0, 1], [0, 2]],
     ],
     'current_rotation': 0,
     'banned': False,
     'cords': [[0, 0], [-1, 0], [0, -1], [0, 1], [0, 2]],
     'color': "#00bdd6"
     },
    {'num': 12,
     'rotations': [
         [[0, 0], [0, -1], [-1, -1], [0, 1], [1, 1]],
         [[0, 0], [1, 0], [-1, -1], [-1, 0], [1, 1]],
     ],
     'banned': False,
     'current_rotation': 0,
     'cords': [[0, 0], [0, -1], [-1, -1], [0, 1], [1, 1]],
     'color': "#ff9900"
     },

]
if __name__ == '__main__':
    root = Tk()
    root.title("Пентамино")
    root.iconbitmap("icon.ico")

    MyField(root).pack(fill=BOTH, expand=YES)
    root.mainloop()
