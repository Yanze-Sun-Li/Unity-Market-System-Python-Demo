import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import json
import os
import shutil

# 默认文件路径
default_file_path = "data.json"

# 定义字段名
fields = {
    "id": "ID",
    "name": "Name",
    "description": "Description",
    "default_price": "Default Price",
    "type": "Type",
    "stack_number": "Stack Number",
}

# 载入已有的JSON文件
def load_json_file():
    global data_list, file_path
    file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if not file_path:  # 如果用户没有选择文件，则使用默认路径
        file_path = default_file_path
    
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            try:
                data_list = json.load(file)
                messagebox.showinfo("Success", "File loaded successfully!")
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Failed to load JSON file.")
                data_list = []
    else:
        data_list = []
        messagebox.showinfo("Info", "File not found. A new file will be created.")

# 检查id是否重复
def check_duplicate_id(new_id):
    for item in data_list:
        if item["id"] == new_id:
            return True
    return False

# 将新数据添加到已有文件中
def add_data_to_json():
    new_data = {
        "id": id_entry.get(),
        "name": name_entry.get(),
        "description": description_entry.get(),
        "default_price": default_price_entry.get(),
        "type": type_entry.get(),
        "stack_number": stack_number_entry.get(),
    }
    
    if check_duplicate_id(new_data["id"]):
        messagebox.showerror("Error", "ID already exists! Please use a unique ID.")
    else:
        data_list.append(new_data)
        sort_data_by_id()  # 在保存之前对data_list进行排序
        save_json_file()
        messagebox.showinfo("Success", "Data added successfully!")

# 对data_list进行排序，按数值顺序排序id
def sort_data_by_id():
    global data_list
    data_list.sort(key=lambda x: int(x["id"]))  # 将id转为整数进行排序

# 保存数据到原有的JSON文件中
def save_json_file():
    with open(file_path, "w") as file:
        json.dump(data_list, file, indent=4)

# 复制JSON文件的功能
def copy_json_file():
    original_file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    
    if not original_file_path:
        messagebox.showerror("Error", "No file selected!")
        return

    new_file_name = simpledialog.askstring("Input", "Enter the new file name (without extension):")
    
    if not new_file_name:
        messagebox.showerror("Error", "No name provided for the new file!")
        return
    
    directory = os.path.dirname(original_file_path)
    new_file_path = os.path.join(directory, new_file_name + ".json")
    
    try:
        shutil.copyfile(original_file_path, new_file_path)
        messagebox.showinfo("Success", f"File copied successfully as {new_file_name}.json!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to copy the file: {e}")

# 创建主窗口
root = tk.Tk()
root.title("Market Simulator Data Manager")

# 创建和布局标签和输入框
entries = {}
for i, (key, value) in enumerate(fields.items()):
    label = tk.Label(root, text=value)
    label.grid(row=i, column=0, padx=10, pady=5, sticky=tk.W)

    entry = tk.Entry(root)
    entry.grid(row=i, column=1, padx=10, pady=5)
    entries[key] = entry

# 将输入框保存到相应的变量中
id_entry = entries["id"]
name_entry = entries["name"]
description_entry = entries["description"]
default_price_entry = entries["default_price"]
type_entry = entries["type"]
stack_number_entry = entries["stack_number"]

# 创建按钮
load_button = tk.Button(root, text="Load JSON File", command=load_json_file)
load_button.grid(row=len(fields), column=0, columnspan=2, pady=10)

add_button = tk.Button(root, text="Add Data", command=add_data_to_json)
add_button.grid(row=len(fields)+1, column=0, columnspan=2, pady=10)

# 创建复制文件的按钮
copy_button = tk.Button(root, text="Copy JSON File", command=copy_json_file)
copy_button.grid(row=len(fields)+2, column=0, columnspan=2, pady=10)

# 初始化数据列表和文件路径
data_list = []
file_path = default_file_path

# 运行主循环
root.mainloop()
