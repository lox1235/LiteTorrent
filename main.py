import libtorrent as lt
import time
import sys
import threading
from tkinter import *
from tkinter import ttk, messagebox, filedialog
import os


class TorrentDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LiteTorrent")
        self.root.geometry("750x510")
        self.root.resizable(width=False, height=False)

        self.root.configure(bg='#1e1e1e')

        self.button_style = {
            'bg': '#1e3a8a',
            'fg': 'white',
            'font': ('Arial', 10, 'bold'),
            'relief': 'raised',
            'bd': 2
        }

        self.red_button_style = {
            'bg': '#dc2626',
            'fg': 'white',
            'font': ('Arial', 10, 'bold'),
            'relief': 'raised',
            'bd': 2
        }

        self.green_button_style = {
            'bg': '#16a34a',
            'fg': 'white',
            'font': ('Arial', 10, 'bold'),
            'relief': 'raised',
            'bd': 2
        }

        self.ses = None
        self.handle = None
        self.downloading = False
        self.update_thread = None

        self.setup_ui()

    def setup_ui(self):
        bg_color = '#1e1e1e'
        fg_color = '#ffffff'
        frame_bg = '#2d2d2d'
        entry_bg = '#3c3c3c'

        control_frame = Frame(self.root, padx=10, pady=10, bg=bg_color)
        control_frame.pack(fill=X)

        Label(control_frame, text="Torrent файл:",
              bg=bg_color, fg=fg_color, font=('Arial', 10)).grid(row=0, column=0, sticky=W)

        self.file_entry = Entry(control_frame, width=50,
                                bg=entry_bg, fg=fg_color,
                                insertbackground=fg_color,
                                font=('Arial', 10))
        self.file_entry.grid(row=0, column=1, padx=5)

        Button(control_frame, text="Выбрать",
               command=self.browse_file,
               **self.button_style).grid(row=0, column=2, padx=5)

        Button(control_frame, text="Начать загрузку",
               command=self.start_download,
               **self.green_button_style).grid(row=1, column=0, pady=10, sticky=W)

        Button(control_frame, text="Остановить",
               command=self.stop_download,
               **self.red_button_style).grid(row=1, column=1, pady=10, padx=5, sticky=W)

        Button(control_frame, text="Пауза/Продолжить",
               command=self.toggle_pause,
               **self.button_style).grid(row=1, column=2, pady=10)

        info_frame = LabelFrame(self.root, text="Информация о торренте",
                                padx=10, pady=10,
                                bg=frame_bg, fg=fg_color,
                                font=('Arial', 10, 'bold'))
        info_frame.pack(fill=X, padx=10, pady=5)

        self.info_text = Text(info_frame, height=6, width=80,
                              bg=entry_bg, fg=fg_color,
                              insertbackground=fg_color,
                              font=('Arial', 10))
        self.info_text.pack()

        progress_frame = LabelFrame(self.root, text="Прогресс загрузки",
                                    padx=10, pady=10,
                                    bg=frame_bg, fg=fg_color,
                                    font=('Arial', 10, 'bold'))
        progress_frame.pack(fill=X, padx=10, pady=5)

        self.progress_label = Label(progress_frame, text="Не запущено",
                                    bg=frame_bg, fg=fg_color,
                                    font=('Arial', 10))
        self.progress_label.pack(anchor=W)

        style = ttk.Style()
        style.theme_use('default')
        style.configure("TProgressbar",
                        thickness=20,
                        background='#3b82f6',
                        troughcolor=entry_bg,
                        bordercolor=frame_bg,
                        lightcolor='#3b82f6',
                        darkcolor='#3b82f6')

        self.progress_bar = ttk.Progressbar(progress_frame, length=700, mode='determinate')
        self.progress_bar.pack(pady=5)

        stats_frame = LabelFrame(self.root, text="Статистика",
                                 padx=10, pady=10,
                                 bg=frame_bg, fg=fg_color,
                                 font=('Arial', 10, 'bold'))
        stats_frame.pack(fill=X, padx=10, pady=5)

        stats_grid = Frame(stats_frame, bg=frame_bg)
        stats_grid.pack()

        self.name_label = Label(stats_grid, text="Название: ",
                                bg=frame_bg, fg=fg_color,
                                font=('Arial', 10))
        self.name_label.grid(row=0, column=0, sticky=W)

        self.size_label = Label(stats_grid, text="Размер: ",
                                bg=frame_bg, fg=fg_color,
                                font=('Arial', 10))
        self.size_label.grid(row=1, column=0, sticky=W)

        self.progress_percent = Label(stats_grid, text="Прогресс: 0%",
                                      bg=frame_bg, fg='#60a5fa',
                                      font=('Arial', 10))
        self.progress_percent.grid(row=2, column=0, sticky=W)

        self.download_speed = Label(stats_grid, text="Скачка: 0 kB/s",
                                    bg=frame_bg, fg='#10b981',
                                    font=('Arial', 10))
        self.download_speed.grid(row=0, column=1, sticky=W, padx=20)

        self.upload_speed = Label(stats_grid, text="Отдача: 0 kB/s",
                                  bg=frame_bg, fg='#f59e0b',
                                  font=('Arial', 10))
        self.upload_speed.grid(row=1, column=1, sticky=W, padx=20)

        self.peers_label = Label(stats_grid, text="Пиры: 0",
                                 bg=frame_bg, fg='#8b5cf6',
                                 font=('Arial', 10))
        self.peers_label.grid(row=2, column=1, sticky=W, padx=20)

        self.status_label = Label(self.root, text="Готов к загрузке",
                                  bg='#374151', fg=fg_color,
                                  anchor=W, relief=SUNKEN,
                                  font=('Arial', 10))
        self.status_label.pack(side=BOTTOM, fill=X, padx=10, pady=5)

    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Выберите torrent файл",
            filetypes=[("Torrent files", "*.torrent"), ("All files", "*.*")]
        )
        if filename:
            self.file_entry.delete(0, END)
            self.file_entry.insert(0, filename)
            self.show_torrent_info(filename)

    def show_torrent_info(self, torrent_path):
        try:
            info = lt.torrent_info(torrent_path)
            self.info_text.delete(1.0, END)

            info_str = f"""
Название: {info.name()}
Размер: {info.total_size() / (1024 * 1024):.2f} MB
Количество файлов: {info.num_files()}
Хэш: {str(info.info_hash())}
Трекеры: {len(info.trackers())}
"""
            self.info_text.insert(1.0, info_str)

            self.name_label.config(text=f"Название: {info.name()}")
            self.size_label.config(text=f"Размер: {info.total_size() / (1024 * 1024):.2f} MB")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать торрент файл: {e}")

    def start_download(self):
        torrent_path = self.file_entry.get()

        if not torrent_path or not os.path.exists(torrent_path):
            messagebox.showerror("Ошибка", "Укажите корректный путь к torrent файлу")
            return

        if self.downloading:
            messagebox.showwarning("Внимание", "Загрузка уже идет")
            return

        try:
            self.ses = lt.session({'listen_interfaces': '0.0.0.0:6881'})
            info = lt.torrent_info(torrent_path)

            save_dir = filedialog.askdirectory(title="Выберите папку для сохранения")
            if not save_dir:
                return

            self.handle = self.ses.add_torrent({'ti': info, 'save_path': save_dir})

            self.downloading = True
            self.status_label.config(text="Загрузка начата", bg='#16a34a', fg='white')

            self.update_thread = threading.Thread(target=self.update_stats, daemon=True)
            self.update_thread.start()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось начать загрузку: {e}")

    def update_stats(self):
        while self.downloading and self.handle and self.handle.is_valid():
            try:
                s = self.handle.status()

                progress = s.progress * 100
                self.progress_bar['value'] = progress
                self.progress_percent.config(text=f"Прогресс: {progress:.2f}%")

                self.progress_label.config(
                    text=f"{s.progress * 100:.2f}% завершено | Состояние: {self.get_state_str(s.state)}")

                self.download_speed.config(text=f"Скачка: {s.download_rate / 1000:.1f} kB/s")
                self.upload_speed.config(text=f"Отдача: {s.upload_rate / 1000:.1f} kB/s")
                self.peers_label.config(text=f"Пиры: {s.num_peers}")

                if s.is_seeding:
                    self.downloading = False
                    self.status_label.config(text="Загрузка завершена!", bg='#3b82f6', fg='white')
                    messagebox.showinfo("Успех", f"'{s.name}' успешно загружен!")
                    break

                time.sleep(1)

            except Exception as e:
                print(f"Ошибка обновления: {e}")
                break

    def get_state_str(self, state):
        states = {
            0: "В очереди",
            1: "Проверка",
            2: "Загрузка метаданных",
            3: "Загрузка",
            4: "Завершено",
            5: "Раздача"
        }
        return states.get(state, f"Неизвестно ({state})")

    def stop_download(self):
        if self.handle and self.handle.is_valid():
            self.ses.remove_torrent(self.handle)
        self.downloading = False
        self.status_label.config(text="Загрузка остановлена", bg='#f59e0b', fg='white')
        self.progress_label.config(text="Остановлено пользователем")

    def toggle_pause(self):
        if self.handle and self.handle.is_valid():
            if self.handle.status().paused:
                self.handle.resume()
                self.status_label.config(text="Загрузка возобновлена", bg='#16a34a', fg='white')
            else:
                self.handle.pause()
                self.status_label.config(text="На паузе", bg='#f59e0b', fg='white')

    def on_closing(self):
        self.downloading = False
        if self.update_thread:
            self.update_thread.join(timeout=2)
        self.root.destroy()


def main():
    root = Tk()
    app = TorrentDownloaderGUI(root)

    root.protocol("WM_DELETE_WINDOW", app.on_closing)

    root.mainloop()


if __name__ == "__main__":
    main()