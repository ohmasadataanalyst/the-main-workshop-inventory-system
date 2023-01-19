import tkinter as tk
import sqlite3
from tkinter import messagebox
import qrcode
from PIL import Image, ImageTk
import cv2
import csv
import os


def create_database():
    conn = sqlite3.connect('barcodes.db')
    c = conn.cursor()

    # Create barcodes table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS barcodes (data text,product_name text,quantity text,qr_code BLOB)''')
    conn.commit()
    conn.close()
if not os.path.isfile('barcodes.db'):
    create_database()

def submit_details(barcode_entry, product_name_entry, quantity_entry,new_form):
    barcode_data = barcode_entry.get()
    product_name = product_name_entry.get()
    quantity = quantity_entry.get()

    # Generate QR code from barcode data
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(barcode_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Convert image to byte array
    img_bytes = img.tobytes()
    # Insert data into database
    conn = sqlite3.connect('barcodes.db')
    c = conn.cursor()
    c.execute("INSERT INTO barcodes (data,product_name,quantity,qr_code) VALUES (?,?,?,?)", (barcode_data,product_name,quantity,sqlite3.Binary(img_bytes)))
    conn.commit()

    # Save QR code as JPEG file
    img.save("barcode.jpeg", "JPEG")

    # Open the saved image
    os.startfile("barcode.jpeg")

    # Close the new form
    new_form.destroy()

def generate_barcode():
    # Create a new form
    new_form = tk.Toplevel(root)
    new_form.title("Product Details")
    new_form.geometry("300x200")

    # Create label and entry widgets for barcode
    barcode_label = tk.Label(new_form, text="Barcode:")
    barcode_label.pack()
    barcode_entry = tk.Entry(new_form)
    barcode_entry.pack()

    # Create label and entry widgets for product name
    product_name_label = tk.Label(new_form, text="Product Name:")
    product_name_label.pack()
    product_name_entry = tk.Entry(new_form)
    product_name_entry.pack()

    # Create label and entry widgets for quantity
    quantity_label = tk.Label(new_form, text="Quantity:")
    quantity_label.pack()
    quantity_entry = tk.Entry(new_form)
    quantity_entry.pack()

    # Create a button to submit the product details
    submit_button = tk.Button(new_form, text="Submit",
                              command=lambda: submit_details(barcode_entry, product_name_entry, quantity_entry,
                                                             new_form))
    submit_button.pack()





def read_qr():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        cv2.imshow("Webcam QR reader", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    # use cv2.QRCodeDetector() function to detect the QRcode
    # and decode the QRcode content
    qrDecoder = cv2.QRCodeDetector()
    data,bbox,rectifiedImage = qrDecoder.detectAndDecode(frame)
    if len(data)>0:
        print("Decoded Data : {}".format(data))
        messagebox.showinfo("Webcam QR reader", "QR code data : {}".format(data))
        conn = sqlite3.connect("barcodes.db")
        c = conn.cursor()
        # check if the barcode exists in the table
        c.execute("SELECT * FROM barcodes WHERE data=?", (data,))
        row = c.fetchone()
        if row is not None:
            # barcode exists in the table
            # prompt the user to enter the new quantity
            quantity = tk.simpledialog.askinteger("Update Quantity", "Enter the new quantity:", minvalue=0)
            if quantity is not None:
                # update the row with the new quantity
                c.execute("UPDATE barcodes SET quantity=? WHERE data=?", (quantity, data))
                conn.commit()
                messagebox.showinfo("Webcam QR reader", "Quantity updated successfully!")
            else:
                messagebox.showwarning("Webcam QR reader", "Quantity not updated!")
        else:
            messagebox.showwarning("Webcam QR reader", "Barcode not found in the table!")
        conn.close()
    else:
        print("QR Code not detected")
        messagebox.showwarning("Webcam QR reader", "QR code not detected")


def export_to_csv():
    conn = sqlite3.connect('barcodes.db')
    c = conn.cursor()

    c.execute("SELECT data,product_name,quantity FROM barcodes")
    rows = c.fetchall()

    with open('barcodes.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Barcode','Product Name','Quantity'])
        writer.writerows(rows)

    messagebox.showinfo("Export to CSV", "Data exported to barcodes.csv successfully!")
    conn.close()




# Create the main window
from PIL import Image, ImageTk
from tkinter import ttk
root = tk.Tk()
root.title("مخازن الورشة الرئيسيةللخدمات الطبية ")
root.geometry("450x450")

# Open the background image
image = Image.open("Kobry_el_kobba_hospital_logo.png")

# Create a PhotoImage object from the background image
photo_image = ImageTk.PhotoImage(image)

# Create a label to display the background image
background_label = tk.Label(root, image=photo_image)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

# Create a label for the title
title_label = tk.Label(root, text="Barcode Generator", font=("Arial", 20))
title_label.place(relx=0.5, rely=0.1, anchor='center')


# Create a button to generate the barcode
generate_button = tk.Button(root, text="Generate Barcode", command=generate_barcode)
generate_button.place(relx=0.5, rely=0.3, anchor='center')

# Create a button to read QR code using webcam
read_button = tk.Button(root, text="Read QR Code", command=read_qr)
read_button.place(relx=0.5, rely=0.35, anchor='center')

# Create a button to export data to CSV
export_button = tk.Button(root, text="Export to CSV", command=export_to_csv)
export_button.place(relx=0.5, rely=0.4, anchor='center')

# Create a label to display the barcode image
label = tk.Label(root)
label.place(relx=0.5, rely=0.5, anchor='center')

# Run the main loop
root.mainloop()
