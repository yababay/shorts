#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp, GObject, GLib, Gio, Gtk
gi.require_version('Gegl', '0.4')
import sys
import os
import glob

shorts_dir = '/home/mabel/.3f-lab/_projects/shorts'

def select_photo(parent_window=None):
    # Create file selection window
    dialog = Gtk.FileChooserDialog(
        title="Выберите картинку для видео",
        action=Gtk.FileChooserAction.OPEN,
        buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                 Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
    )

    # Filters for .txt files
    filter_img = Gtk.FileFilter()
    filter_img.set_name("Изображения из Телеграм")
    filter_img.add_pattern("photo_*.jpg")
    filter_img.add_pattern("photo_*.jpeg")
    filter_img.add_pattern("photo_*.png")
    dialog.add_filter(filter_img)

    # Run dialog and get response
    response = dialog.run()
    filename = None

    if response == Gtk.ResponseType.OK:
        filename = dialog.get_filename()

    dialog.destroy()

    return filename

def run_prepare_short(procedure, run_mode, image, drawables, config, data):

    try:

        photo_path = select_photo()

        if not os.path.exists(photo_path):
            Gimp.message(f"❌ Не выбран файл с префиксом photo_")
            return procedure.new_return_values(Gimp.PDBStatusType.CALLING_ERROR, GLib.Error())

        dir_name = os.path.dirname(photo_path)

        readme_path = os.path.join(dir_name, "README.md")
        if not os.path.exists(readme_path):
            Gimp.message(f"❌ Не найден README.md в:\n{dir_name}")
            return procedure.new_return_values(Gimp.PDBStatusType.CALLING_ERROR, GLib.Error())

        # Безопасно извлекаем config (и run_data, если он есть)
        # config = args[0] if len(args) > 0 else None
        
        #if config is None:
        #    Gimp.message("❌ Ошибка: не передан объект config")
        #    return procedure.new_return_values(Gimp.PDBStatusType.CALLING_ERROR, GLib.Error())

        # 1. Получаем строку с именем директории
        #dir_name = config.get_property("dir-path")
        
        #if not dir_name:
        #    Gimp.message("❌ Имя директории не указано")
        #    return procedure.new_return_values(Gimp.PDBStatusType.CALLING_ERROR, GLib.Error())
        
        # 2. Формируем путь (ИСПРАВЛЕНО: dir_name — это строка, у неё нет .get_path())
        #dir_path = os.path.join(shorts_dir, str(dir_name))
        
        # 3. Проверяем, что это директория
        #if not os.path.isdir(dir_path):
        #    Gimp.message(f"❌ Не является директорией:\n{dir_path}")
        #    return procedure.new_return_values(Gimp.PDBStatusType.CALLING_ERROR, GLib.Error())
        
        # 4. Ищем README.md
        #readme_path = os.path.join(dir_path, "README.md")
        #if not os.path.exists(readme_path):
        #    Gimp.message(f"❌ Не найден README.md в:\n{dir_path}")
        #    return procedure.new_return_values(Gimp.PDBStatusType.CALLING_ERROR, GLib.Error())
        
        # 5. Ищем файл с префиксом photo_
        #photo_files = glob.glob(os.path.join(dir_path, "photo_*"))
        #if not photo_files:
        #    Gimp.message(f"❌ Не найдены файлы с префиксом photo_ в:\n{dir_path}")
        #    return procedure.new_return_values(Gimp.PDBStatusType.CALLING_ERROR, GLib.Error())
        
        #photo_path = photo_files[0]
        
        # 6. Успех!
        Gimp.message(f"✅ Найдено:\n\nREADME: {readme_path}\nPhoto:  {photo_path}")

        image = Gimp.get_images()[0]
        for layer in image.get_layers():
             if isinstance(layer, Gimp.TextLayer):
                  with open(readme_path, 'r', encoding='utf-8') as f:
                      new_text = f.read().strip()
        
                  # Устанавливаем текст
                  layer.set_text(new_text)
        
                  # Обновляем отображение
                  Gimp.displays_flush()

        source_layer = Gimp.file_load_layer(0, image, Gio.File.new_for_path(photo_path))
        image.insert_layer(source_layer, None, 0)

        src_height = source_layer.get_height()
        src_width = source_layer.get_width()
        img_width = image.get_width()
        img_height = image.get_height()

        scale = 1850 / src_height
        new_width = int(src_width * scale)
        new_height = int(src_height * scale)
        source_layer.scale(new_width, new_height, True)
        offset_x = (img_width - new_width) // 2
        offset_y = (img_height - new_height) // 2
        source_layer.set_offsets(offset_x, offset_y)
        
        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

    except Exception as e:
        import traceback
        # Выводим ошибку и в GIMP, и в терминал (чтобы вы точно её увидели)
        error_msg = f"❌ Критическая ошибка в плагине:\n{e}\n\n{traceback.format_exc()}"
        print(error_msg, file=sys.stderr)
        Gimp.message(error_msg)
        return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())


class PrepareShortPlugin(Gimp.PlugIn):
    def do_query_procedures(self):
        return ['prepare-short-interactive']
    
    def do_create_procedure(self, name):
        p = Gimp.ImageProcedure.new(
            self, name,
            Gimp.PDBProcType.PLUGIN,
            run_prepare_short, None
        )
        
        # Правильный метод для GIMP 3.0
        #p.add_string_argument(
        #    "dir-path",
        #    "Имя директории",
        #    "Например: 2026-10-28",
        #    # "2026-10-28",  # значение по умолчанию
        #    '.current',
        #    GObject.ParamFlags.READWRITE
        #)
        
        p.set_documentation(
            "Ищет картинку и текст в выбранной директории",
            "Ищет photo_* и README.md в указанной папке",
            None
        )
        p.set_attribution("Author", "Yababay", "2026")
        p.set_image_types("*")
        p.set_menu_label("Подготовить Short из файлов...")
        p.add_menu_path('<Image>/Filters/')
        
        return p

Gimp.main(PrepareShortPlugin.__gtype__, sys.argv)

