import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

import os
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.models import load_model

# --- Configuración ---
IMAGE_SIZE = (128, 128)
THRESHOLD = 0.5

# Rutas modelos
MATURITY_MODEL_PATH = 'tomato_maturity_model.h5'
QUALITY_MODEL_PATH  = 'tomato_quality_model.h5'

# Mapas etiquetas
MATURITY_LABELS = {0: 'Inmaduro', 1: 'Maduro'}
QUALITY_LABELS  = {0: 'Podrido',   1: 'Fresco'}

# --- Funciones ---
def preprocess_image(img_path, target_size=IMAGE_SIZE):
    img = load_img(img_path, target_size=target_size)
    x = img_to_array(img) / 255.0
    return np.expand_dims(x, axis=0)

def predict_tomato(img_path, maturity_model, quality_model):
    x = preprocess_image(img_path)
    m_pred = maturity_model.predict(x)[0][0]
    q_pred = quality_model.predict(x)[0][0]
    m_cls = 1 if m_pred > THRESHOLD else 0
    q_cls = 1 if q_pred > THRESHOLD else 0
    return MATURITY_LABELS[m_cls], QUALITY_LABELS[q_cls], m_cls, q_cls

# --- Carga modelos ---
if not os.path.exists(MATURITY_MODEL_PATH) or not os.path.exists(QUALITY_MODEL_PATH):
    raise FileNotFoundError("Faltan los archivos .h5 en el mismo directorio que este script.")

maturity_model = load_model(MATURITY_MODEL_PATH)
quality_model = load_model(QUALITY_MODEL_PATH)

# --- Ventana principal ---
root = tk.Tk()
root.title("Clasificador de Tomates 🍅")

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
root.resizable(False, False)
root.configure(bg="#000000")

# Banner
BANNER_IMAGE_PATH = "C://Users//urbin//PROYECTO IA//TOMACOIA.COM.png"
try:
    banner_img = Image.open(BANNER_IMAGE_PATH).resize((WINDOW_WIDTH, 220))
    banner_photo = ImageTk.PhotoImage(banner_img)
    banner_label = tk.Label(root, image=banner_photo, bg="#333333")
    banner_label.pack(pady=10)
except Exception:
    banner_label = tk.Label(root, text="Clasificador de Tomates 🍅", font=("Roboto", 28, "bold"), bg="#333333", fg="white")
    banner_label.pack(pady=20)

main_frame = tk.Frame(root, bg="#B72424")
main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

# Columna izquierda
left_frame = tk.Frame(main_frame, bg="#B72424")
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
img_container = tk.Frame(left_frame, bg="#B72424")
img_container.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1)

TOMATO_SAD_IMAGE_PATH = "C://Users//urbin//PROYECTO IA//tomate_triste.png"
try:
    sad_img = Image.open(TOMATO_SAD_IMAGE_PATH).resize((350, 350))
    sad_img_tk = ImageTk.PhotoImage(sad_img)
except Exception:
    sad_img_tk = None

sad_img_label = tk.Label(img_container, image=sad_img_tk, bg="#B72424", relief="flat")
if sad_img_tk:
    sad_img_label.place(relx=0.5, rely=0.5, anchor="center")
else:
    sad_img_label.config(text="Tomate triste (no encontrado)", fg="white", font=("Segoe UI", 14))
    sad_img_label.place(relx=0.5, rely=0.5, anchor="center")

img_label = tk.Label(img_container, bg="#B72424")
img_label.place_forget()

# Columna derecha
right_frame = tk.Frame(main_frame, bg="#B72424")
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(20, 0))

# Resultado con Text en lugar de Label para aplicar negritas
resultado_textbox = tk.Text(right_frame, font=("Segoe UI Semibold", 16), bg="#B72424", fg="white", wrap="word", bd=0)
resultado_textbox.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.6)
resultado_textbox.tag_configure("bold", font=("Segoe UI Semibold", 16, "bold"))
resultado_textbox.config(state="disabled")

# Botón
btn_seleccionar = tk.Button(root, text="Seleccionar imagen", font=("Segoe UI", 18), bg="#882828", fg="white",
                            activebackground="#FF9A00", relief="flat", bd=5, padx=20, pady=10, cursor="hand2")
btn_seleccionar.pack(side=tk.BOTTOM, pady=30)

# --- Función principal ---
def seleccionar_imagen():
    file_path = filedialog.askopenfilename(
        title="Selecciona una imagen",
        filetypes=[("Archivos de imagen", "*.jpg *.jpeg *.png *.bmp *.gif")]
    )
    if file_path:
        try:
            madurez, calidad, m_cls, q_cls = predict_tomato(file_path, maturity_model, quality_model)

            # Preparar texto con etiquetas
            resultado_textbox.config(state="normal")
            resultado_textbox.delete("1.0", tk.END)

            resultado_textbox.insert(tk.END, "Madurez: ", "bold")
            resultado_textbox.insert(tk.END, f"{madurez}\n")

            resultado_textbox.insert(tk.END, "Calidad: ", "bold")
            resultado_textbox.insert(tk.END, f"{calidad}\n\n")

            if q_cls == 0:
                resultado_textbox.insert(tk.END, "⚠️ Recomendación: ", "bold")
                resultado_textbox.insert(tk.END, "NO utilizar este tomate como alimento. Está en mal estado.")
            elif m_cls == 1:
                resultado_textbox.insert(tk.END, "✅ Recomendación: ", "bold")
                resultado_textbox.insert(tk.END, "Comerlo. Está perfecto para consumir.")
            else:
                resultado_textbox.insert(tk.END, "⌛ Recomendación: ", "bold")
                resultado_textbox.insert(tk.END, "Esperar a que madure antes de consumirlo.")

            resultado_textbox.config(state="disabled")

            img = Image.open(file_path)
            img.thumbnail((350, 350), Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            img_label.config(image=img_tk)
            img_label.image = img_tk
            img_label.place(relx=0.5, rely=0.5, anchor="center")
            sad_img_label.place_forget()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo procesar la imagen:\n{str(e)}")
            resultado_textbox.config(state="normal")
            resultado_textbox.delete("1.0", tk.END)
            resultado_textbox.config(state="disabled")
            img_label.config(image="")
            img_label.place_forget()
            if sad_img_tk:
                sad_img_label.place(relx=0.5, rely=0.5, anchor="center")

btn_seleccionar.config(command=seleccionar_imagen)

# Centrar ventana
def centrar_ventana(ventana, ancho, alto):
    ancho_pantalla = ventana.winfo_screenwidth()
    alto_pantalla = ventana.winfo_screenheight()
    x = (ancho_pantalla // 2) - (ancho // 2)
    y = (alto_pantalla // 2) - (alto // 2)
    ventana.geometry(f'{ancho}x{alto}+{x}+{y}')

centrar_ventana(root, WINDOW_WIDTH, WINDOW_HEIGHT)
root.mainloop()
