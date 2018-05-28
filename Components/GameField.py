from tkinter import *
from tkinter import messagebox
from PIL import Image
from PIL.ImageTk import PhotoImage
import time
import pickle
from tkinter import filedialog


class GameField(Canvas):
    def __init__(self, *args, **kvargs):
        self.status = kvargs['status']
        self.items = kvargs['items']
        self.message = ""
        del kvargs['status']
        del kvargs['items']
        Canvas.__init__(self, *args, **kvargs)
        self.set_geometry(3, 20)

    """Функция задает размер поля возврощает пустоту"""

    def set_geometry(self, size_x, size_y):
        self.size_x = size_x
        self.size_y = size_y
        # Создаем модель поля
        self.field_model = self.create_field_model()
        # Обновляем все поле
        self.update()

    """Обновляет все поле"""

    def update(self):
        self.width = self.winfo_width()  # Более удобный вариант для ширины поля
        self.height = self.winfo_height()  # Более удобный вариант для высоты поля
        self.cell_width = self.height // self.size_y  # Шаг сетки
        self.start_grid_position = self.width // 2 - self.cell_width * self.size_x // 2  # Начальная позиция скоторой будем рисовать стеку
        self.spy = (self.height - self.size_y * self.cell_width)  # Хз зачем ето, но пусть будет
        self.fast_update()

    """Быстренько просто перересовываем"""

    def fast_update(self):
        self.delete(ALL)
        self.set_fone()
        self.drawGrid()
        self.draw_cells()

    """Рисует сетку на поле Части сетки всегда квадраты при любой ширине"""

    def drawGrid(self):
        # Ставим изображение
        # Затираем сетку перед перерисовкой
        self.create_rectangle(self.start_grid_position - 2, 0,
                              self.start_grid_position + self.size_x * self.cell_width + 2, self.height, fill="#ffffff",
                              width=0)
        # Рисуем сетку, для этого нам надо взять размеры из параметров
        for i in range(self.size_y + 1):  # сначала сделаем палочки по x
            self.create_line(self.start_grid_position, i * self.cell_width + self.spy // 2,
                             self.start_grid_position + self.size_x * self.cell_width,
                             i * self.cell_width + self.spy // 2, fill="#999999")
        for i in range(self.size_x + 1):  # теперь палочки по y
            self.create_line(self.start_grid_position + i * self.cell_width, self.spy // 2,
                             self.start_grid_position + i * self.cell_width, self.height - self.spy // 2,
                             fill="#999999")

    """Рисует клетки нужным цветом"""

    def draw_cells(self):
        # Обходим всю модель и рисуем
        for i, row in enumerate(self.field_model):
            for j, item in enumerate(row):
                if self.field_model[i][j] != 0:
                    start_x = i * self.cell_width + self.start_grid_position
                    end_x = (i + 1) * self.cell_width + self.start_grid_position
                    start_y = j * self.cell_width + self.spy // 2
                    end_y = (j + 1) * self.cell_width + self.spy // 2
                    # Рисуем квадратик нужного цвета
                    self.create_rectangle(start_x, start_y, end_x, end_y,
                                          fill=self.items[self.field_model[i][j] - 1]['color'])

    """Показывает куда будем ставить фигурку"""

    def overlay(self, event, item):
        # Определяем текущие координаты
        self.fast_update()
        xCord, yCord = self.get_cords(event)
        if xCord != -1 or yCord != -1:
            self.status.create_rectangle(0, 0, self.status.winfo_width(), self.status.winfo_height(), fill="#ffffff")
            self.status.create_text(30, 10, text="X: {} Y: {}".format(xCord + 1, yCord + 1))
            self.status.create_text(70, 25, text=self.message)
            self.status.event_info_custom = event
            filled_cells = []
            if item['num'] != None:
                # Теперь надо проверить, выходит оно все за рамки, или нет, и если нет, то нарисовать оверлей
                # Клетки которые мы будем заполнять полностью
                for i in item['cords']:
                    filled_cells.append((xCord + i[0], yCord + i[1]))
                self.fill_cell(filled_cells, "#ffc0cb")

    """Заполняем все клетки при наведении"""

    def fill_cell(self, array, collor):
        for cell_x_cord, cell_y_cord in array:
            start_x = cell_x_cord * self.cell_width + self.start_grid_position
            end_x = (cell_x_cord + 1) * self.cell_width + self.start_grid_position
            start_y = cell_y_cord * self.cell_width
            end_y = (cell_y_cord + 1) * self.cell_width
            # Рисуем квадратик нужного цвета
            self.create_rectangle(start_x, start_y, end_x, end_y, **{'fill': collor})

    """Размещаем фигуру на поле"""

    def add_figure(self, event, item):
        xCord, yCord = self.get_cords(event)
        if xCord != -1 or yCord != -1:
            if item['num'] != None and self.check_item(item, xCord, yCord) and not item['banned']:
                for i in item['cords']:
                    self.field_model[xCord + i[0]][yCord + i[1]] = item['num']
                    self.draw_cells()
                    if self.check_win():
                        self.status.create_rectangle(0, 0, self.status.winfo_width(), self.status.winfo_height(),
                                                     fill="#ffffff")
                        messagebox.showinfo("Победа!!!", "Вы заполнили все поле, вы молодец")
                item['banned'] = True
                self.message = "Фигура добавленна"
            elif item['banned']:
                self.message = "Уже используется"
            else:
                self.message = "Нельзя поставить сюда"

    """Удаляем фигуру с поля"""

    def delete_figure(self, event):
        xCord, yCord = self.get_cords(event)
        # Находим значение в модели поля, и удаляем все эти значения
        value = self.field_model[xCord][yCord]
        for i in range(self.size_x):
            for j in range(self.size_y):
                if self.field_model[i][j] == value:
                    self.field_model[i][j] = 0
                    self.message = "Фигура Удалена"
                    print(value)
                    self.items[value - 1]['banned'] = False

    """Сохраняем игру"""

    def save_game(self):
        game = {'field': self.field_model, 'geometry': (self.size_x, self.size_y)}
        filename = f"./saves/game_{time.time()}.save"
        with open(filename, 'wb') as f:
            pickle.dump(game, f)
            self.message = "Успешно сохранено"

    """Загружаем игру"""

    def load_game(self):
        filename = filedialog.askopenfilename()
        with open(filename, 'rb') as f:
            try:
                game = pickle.load(f)
                self.set_geometry(*game['geometry'])
                self.field_model = game['field']
                self.fast_update()
            except:
                self.message = "Неудалось загрузиться, попробуйте другой файл"

    """Создаем модель поля"""

    def create_field_model(self):
        field_model = [[] for i in range(self.size_x)]
        for item in field_model:
            for i in range(self.size_y):
                item.append(0)
        return field_model

    """Очищаем поле"""

    def clear_field(self):
        self.field_model = self.create_field_model()
        for item in self.items:
            item['banned'] = False
        self.fast_update()

    """Получем кординаты по пикселям"""

    def get_cords(self, event):
        if (event.x >= self.start_grid_position and event.x < self.start_grid_position + self.size_x * self.cell_width):
            yCord = event.y // (self.winfo_height() // self.size_y)
            xCord = (event.x - self.start_grid_position) // (self.cell_width)
        else:
            xCord = yCord = -1
        return xCord, yCord

    """Ставит фоновое изображение"""

    def set_fone(self):
        self.fone = PhotoImage(self.create_thumb())
        self.create_image(0, 0, image=self.fone, anchor="nw")

    """Создаем изображение и делаем так чтоб оно нормально ресайзилось"""

    def create_thumb(self):
        # Получаем высоту и ширину канваса
        size = (int(self.height * 1.7), self.height)
        img = Image.open("./fone.jpg")
        img = img.resize(size)
        return img

    """Проверка победы"""

    def check_win(self):
        for i, row in enumerate(self.field_model):
            for j, item in enumerate(row):
                if self.field_model[i][j] == 0:
                    return False
        return True

    """Проверяем объект, на возможность разместить его на поле"""

    def check_item(self, item, xCord, yCord):
        for i in item['cords']:
            # Проверяем координаты на соответствие
            if (xCord + i[0] >= 0
                    and xCord + i[0] < self.size_x
                    and yCord + i[1] >= 0
                    and yCord + i[1] < self.size_y
                    and self.field_model[xCord + i[0]][yCord + i[1]] == 0):
                pass
            else:
                return False
        return True
