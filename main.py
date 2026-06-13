import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import cv2
from PIL import Image, ImageTk
import numpy as np

class ImageApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Обработка изображений")
        self.root.geometry("1100x750")

        self.cap = None
        self.camera_running = False
        self.camera_job = None

        self.original_image = None
        self.image = None
        self.photo = None

        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=10)

        self.open_button = tk.Button(self.button_frame, text="Открыть изображение", command=self.open_image)
        self.open_button.grid(row=0, column=0, padx=5)

        self.original_button = tk.Button(root, text="Оригинал", command=self.show_original)
        self.original_button.pack(pady=5)

        self.red_button = tk.Button(root, text="Красный канал", command=self.show_red_channel)
        self.red_button.pack(pady=5)

        self.green_button = tk.Button(root, text="Зелёный канал", command=self.show_green_channel)
        self.green_button.pack(pady=5)

        self.blue_button = tk.Button(root, text="Синий канал", command=self.show_blue_channel)
        self.blue_button.pack(pady=5)

        self.gray_button = tk.Button(root, text="Оттенки серого", command=self.show_gray)
        self.gray_button.pack(pady=5)

        self.line_button = tk.Button(root, text="Нарисовать линию", command=self.draw_line)
        self.line_button.pack(pady=5)

        self.line_button = tk.Button(root, text="Размытие по Гауссу", command=self.apply_gaussian_blur)
        self.line_button.pack(pady=5)

        self.camera_shot_button = tk.Button(root, text="Сделать снимок с камеры", command=self.capture_from_camera)
        self.camera_shot_button.pack(pady=5)

        self.status_label = tk.Label(root, text="Изображение не загружено")
        self.status_label.pack(pady=10)

        self.image_label = tk.Label(root, text="")
        self.image_label.pack(expand=True)

    def open_image(self):
        file_path = filedialog.askopenfilename(
            title ="Выберите изображение",
            filetypes=[
            ("PNG files", "*.png"),
            ("JPG files", "*.jpg"),
            ("JPEG files", "*.jpeg"),
            ("All image files", "*.png *.jpg *.jpeg"),
            ("All files", "*.*")
            ]
        )

        if not file_path:
            self.status_label.config(text="Файл не выбран")
            return
        
        try:
            img_array = np.fromfile(file_path, dtype=np.uint8)
            image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        except Exception:
            image = None

        if image is None:
            messagebox.showerror("Ошибка", "Не удалось загрузить изображение.")
            self.status_label.config(text="Ошибка загрузки изображения")
            return

        self.original_image = image
        self.current_image = image.copy()

        self.status_label.config(text=f"Загружено изображение: {file_path}")
        self.show_image(self.current_image)

    def show_image(self, image):

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        height, width = image_rgb.shape[:2]
        max_width, max_height = 800, 500

        scale = min(max_width / width, max_height / height, 1)
        new_width = int(width * scale)
        new_height = int(height * scale)

        resized = cv2.resize(image_rgb, (new_width, new_height))

        pil_image = Image.fromarray(resized)
        self.photo = ImageTk.PhotoImage(pil_image)

        self.image_label.config(image=self.photo, text="")
    def show_original(self):
        if self.original_image is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение.")
            return

        self.current_image = self.original_image.copy()
        self.status_label.config(text="Показано оригинальное изображение")
        self.show_image(self.current_image)

    def show_red_channel(self):
        self.show_channel(2, "Показан красный канал")

    def show_green_channel(self):
        self.show_channel(1, "Показан зелёный канал")

    def show_blue_channel(self):
        self.show_channel(0, "Показан синий канал")

    def draw_line(self):
        if self.original_image is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение.")
            return

        try:
            x1 = simpledialog.askinteger("Линия", "X1 (начало):", minvalue=0)
            if x1 is None:
             return
            y1 = simpledialog.askinteger("Линия", "Y1 (начало):", minvalue=0)
            if y1 is None:
                return
            x2 = simpledialog.askinteger("Линия", "X2 (конец):", minvalue=0)
            if x2 is None:
                return
            y2 = simpledialog.askinteger("Линия", "Y2 (конец):", minvalue=0)
            if y2 is None:
                return
            thickness = simpledialog.askinteger("Линия", "Толщина линии (пиксели):", minvalue=1)
            if thickness is None:
                return
        except Exception:
            messagebox.showerror("Ошибка", "Неверный ввод параметров линии.")
            return

        h, w = self.original_image.shape[:2]
        if not (0 <= x1 < w and 0 <= x2 < w and 0 <= y1 < h and 0 <= y2 < h):
            messagebox.showerror("Ошибка", "Координаты линии выходят за границы изображения.")
            return

        result = self.current_image.copy() if self.current_image is not None else self.original_image.copy()

        color = (0, 255, 0)  # BGR: зелёный
        cv2.line(result, (x1, y1), (x2, y2), color, thickness)

        self.current_image = result
        self.status_label.config(text=f"Нарисована зелёная линия: ({x1}, {y1}) → ({x2}, {y2}), толщина {thickness}")
        self.show_image(self.current_image)

    def apply_gaussian_blur(self):
        if self.original_image is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение.")
            return

        size = simpledialog.askinteger(
            "Размытие по Гауссу",
            "Размер ядра (нечётное число, например 3, 5, 7):",
            minvalue=1
        )
        if size is None:
            return

        if size % 2 == 0:
            messagebox.showerror("Ошибка", "Размер ядра должен быть нечётным числом.")
            return
        
        result = self.current_image.copy() if self.current_image is not None else self.original_image.copy()

        # sigmaX = 0, чтобы OpenCV само подобрало стандартное отклонение
        blurred = cv2.GaussianBlur(result, (size, size), 0)

        self.current_image = blurred
        self.status_label.config(text=f"Применено размытие по Гауссу с ядром {size}x{size}")
        self.show_image(self.current_image)
    
    def show_gray(self):
        if self.original_image is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение.")
            return

        gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        gray_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

        self.current_image = gray_bgr
        self.status_label.config(text="Показано изображение в оттенках серого")
        self.show_image(self.current_image)

    def show_channel(self, channel_index, message):
        if self.original_image is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение.")
            return
    
        channel_image = np.zeros_like(self.original_image)
        channel_image[:, :, channel_index] = self.original_image[:, :, channel_index]

        self.current_image = channel_image
        self.status_label.config(text=message)
        self.show_image(self.current_image)

    def capture_from_camera(self):
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            messagebox.showerror("Ошибка", "Не удалось открыть веб-камеру.")
            return

        ret, frame = cap.read()
        cap.release()

        if not ret:
            messagebox.showerror("Ошибка", "Не удалось получить снимок с веб-камеры.")
            return

        self.original_image = frame.copy()
        self.current_image = frame.copy()

        self.status_label.config(text="Получен фотоснимок с веб-камеры")
        self.show_image(self.current_image)


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageApp(root)
    root.mainloop()