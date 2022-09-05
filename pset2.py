#!/usr/bin/env python3

import sys
import math
import base64
import tkinter

from io import BytesIO
from PIL import Image as PILImage

## NO ADDITIONAL IMPORTS ALLOWED!

class Image:
    def __init__(self, width, height, pixels):
        self.width = width
        self.height = height
        self.pixels = pixels

    def get_pixel(self, x, y):
        index = x + self.width * y
        return self.pixels[index]

    def set_pixel(self, x, y, c):
        index = x + self.width * y
        self.pixels[index] = c

    def apply_per_pixel(self, func):
        result = Image.new(self.width, self.height)

        for x in range(result.width):
            for y in range(result.height):
                color = self.get_pixel(x, y)
                newcolor = func(color)
                result.set_pixel(x, y, newcolor)
        return result

    def apply_kernel_per_pixel(self, k):
        result = [[0 for x in range(self.width)] for y in range(self.height)]
        count = 0

        for h in range(self.height):
            for w in range(self.width):
                result[h][w] = self.pixels[count]
                count = count + 1

        aux, extra_kernels = self.add_extra_borders(k, result)
        result, image_pixels_list = self.use_kernel(k, aux, result, extra_kernels)

        image = Image(self.width, self.height, image_pixels_list)
        return image, result

    def add_extra_borders(self, k, result):
        result_height = self.height
        aux = result.copy()
        tamanho_kernel = len(k[0])
        extra_kernels = tamanho_kernel // 2
        for lt in range(result_height + (2 * extra_kernels)):
            for k_size in range(extra_kernels):
                if lt == 0:
                    aux.insert(lt, aux[lt].copy())
                elif lt == result_height - 1:
                    aux.insert(lt, aux[lt].copy())
                aux[lt].insert(0, aux[lt][0])
                line_size = len(aux[lt])
                aux[lt].append(aux[lt][line_size - 1])
                # Inserindo Linha Inicial e Linha Final
        return aux, extra_kernels

    def use_kernel(self, k, aux, result, extra_kernels):
        #Função para Aplicar o Kernel de fato

        image_pixels_list = []
        #Realizando um Loop na parte original da matrix "result" contida dentro da matrix aux
        for h in range(extra_kernels, self.height + (extra_kernels)):
            for w in range(extra_kernels, self.width + (extra_kernels)):
                value = 0
                meio_kernel = (len(k) // 2)
                for i in range(1, extra_kernels + 1):
                    #Pegando valores da linha acima do pixel selecionado
                    value += aux[h - extra_kernels][w - extra_kernels] * k[meio_kernel - extra_kernels][
                        meio_kernel - extra_kernels]
                    value += aux[h - extra_kernels][w] * k[meio_kernel - extra_kernels][meio_kernel]
                    value += aux[h - extra_kernels][w + extra_kernels] * k[meio_kernel - extra_kernels][
                        meio_kernel + extra_kernels]

                    #Pegando valores da mesma linha do pixel selecionado
                    value += aux[h][w - extra_kernels] * k[meio_kernel][meio_kernel - extra_kernels]
                    value += aux[h][w] * k[meio_kernel][meio_kernel]
                    value += aux[h][w + extra_kernels] * k[meio_kernel][meio_kernel + extra_kernels]

                    #Pegando valores da linha abaixo do pixel selecionado
                    value += aux[h + extra_kernels][w - extra_kernels] * k[meio_kernel + extra_kernels][
                        meio_kernel - extra_kernels]
                    value += aux[h + extra_kernels][w] * k[meio_kernel + extra_kernels][meio_kernel]
                    value += aux[h + extra_kernels][w + extra_kernels] * k[meio_kernel + extra_kernels][
                        meio_kernel + extra_kernels]
                value = round(value)

                # Realizando recorte [0:255]
                if value > 255:
                    value = 255
                elif value < 0:
                    value = 0

                # Atualizando matrix Rresult
                result[h - extra_kernels][w - extra_kernels] = value
                image_pixels_list.append(value)

        return result, image_pixels_list

    def inverted(self):
        image = self.apply_per_pixel(lambda c: 256-c)
        return image

    def blurred(self, kernel):
        image, result = self.apply_kernel_per_pixel(kernel)
        return image

    def sharpened(self, kernel):
        blurred = self.blurred(kernel)

        for i in range(len(blurred.pixels)):
            self.pixels[i] = round((image.pixels[i] * 2) - blurred.pixels[i])
        return self

    def edges(self, kernel):
        image, result = self.apply_kernel_per_pixel(kernel)
        return result


    # Below this point are utilities for loading, saving, and displaying
    # images, as well as for testing.

    def __eq__(self, other):
        return all(getattr(self, i) == getattr(other, i)
                   for i in ('height', 'width', 'pixels'))

    def __repr__(self):
        return "Image(%s, %s, %s)" % (self.width, self.height, self.pixels)

    @classmethod
    def load(cls, fname):
        """
        Loads an image from the given file and returns an instance of this
        class representing that image.  This also performs conversion to
        grayscale.

        Invoked as, for example:
           i = Image.load('test_images/cat.png')
        """
        with open(fname, 'rb') as img_handle:
            img = PILImage.open(img_handle)
            img_data = img.getdata()
            if img.mode.startswith('RGB'):
                pixels = [round(.299*p[0] + .587*p[1] + .114*p[2]) for p in img_data]
            elif img.mode == 'LA':
                pixels = [p[0] for p in img_data]
            elif img.mode == 'L':
                pixels = list(img_data)
            else:
                raise ValueError('Unsupported image mode: %r' % img.mode)
            w, h = img.size
            return cls(w, h, pixels)

    @classmethod
    def new(cls, width, height):
        """
        Creates a new blank image (all 0's) of the given height and width.

        Invoked as, for example:
            i = Image.new(640, 480)
        """
        return cls(width, height, [0 for i in range(width*height)])

    def save(self, fname, mode='PNG'):
        """
        Saves the given image to disk or to a file-like object.  If fname is
        given as a string, the file type will be inferred from the given name.
        If fname is given as a file-like object, the file type will be
        determined by the 'mode' parameter.
        """
        out = PILImage.new(mode='L', size=(self.width, self.height))
        out.putdata(self.pixels)
        if isinstance(fname, str):
            out.save(fname)
        else:
            out.save(fname, mode)
        out.close()

    def gif_data(self):
        """
        Returns a base 64 encoded string containing the given image as a GIF
        image.

        Utility function to make show_image a little cleaner.
        """
        buff = BytesIO()
        self.save(buff, mode='GIF')
        return base64.b64encode(buff.getvalue())

    def show(self):
        """
        Shows the given image in a new Tk window.
        """
        global WINDOWS_OPENED
        if tk_root is None:
            # if tk hasn't been properly initialized, don't try to do anything.
            return
        WINDOWS_OPENED = True
        toplevel = tkinter.Toplevel()
        # highlightthickness=0 is a hack to prevent the window's own resizing
        # from triggering another resize event (infinite resize loop).  see
        # https://stackoverflow.com/questions/22838255/tkinter-canvas-resizing-automatically
        canvas = tkinter.Canvas(toplevel, height=self.height,
                                width=self.width, highlightthickness=0)
        canvas.pack()
        canvas.img = tkinter.PhotoImage(data=self.gif_data())
        canvas.create_image(0, 0, image=canvas.img, anchor=tkinter.NW)
        def on_resize(event):
            # handle resizing the image when the window is resized
            # the procedure is:
            #  * convert to a PIL image
            #  * resize that image
            #  * grab the base64-encoded GIF data from the resized image
            #  * put that in a tkinter label
            #  * show that image on the canvas
            new_img = PILImage.new(mode='L', size=(self.width, self.height))
            new_img.putdata(self.pixels)
            new_img = new_img.resize((event.width, event.height), PILImage.NEAREST)
            buff = BytesIO()
            new_img.save(buff, 'GIF')
            canvas.img = tkinter.PhotoImage(data=base64.b64encode(buff.getvalue()))
            canvas.configure(height=event.height, width=event.width)
            canvas.create_image(0, 0, image=canvas.img, anchor=tkinter.NW)
        # finally, bind that function so that it is called when the window is
        # resized.
        canvas.bind('<Configure>', on_resize)
        toplevel.bind('<Configure>', lambda e: canvas.configure(height=e.height, width=e.width))

        # when the window is closed, the program should stop
        toplevel.protocol('WM_DELETE_WINDOW', tk_root.destroy)


try:
    tk_root = tkinter.Tk()
    tk_root.withdraw()
    tcl = tkinter.Tcl()
    def reafter():
        tcl.after(500,reafter)
    tcl.after(500,reafter)
except:
    tk_root = None
WINDOWS_OPENED = False

if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.
    print("Bem-Vindo ao Pseudo-Photoshop!")
    path = input("Insira o Caminho da Imagem que Deseja Alterar "
                 "\npor exemplo 'test_images/chess.png' "
                 "\nCaminho: ")

    image = Image.load(path)
    if image is None: print("Falha ao Carregar Imagem. Encerrando o Programa...")
    else:
        print("Imagem Carregada com Sucesso!")
        effect = input("Selecione o Efeito que Gostaria de Aplicar: "
                       "\n1 - Inversão "
                       "\n2 - Desfoque de Caixa"
                       "\n3 - Nitidez"
                       "\n4 - Detecção de Borda"
                       "\nEscolha: ")

        if effect == '1':
            image = image.inverted()
            image.show()

        elif effect == '2':
            tamanho_kernel = int(input("Insira o Tamanho Desejado do Kernel: "))
            key = 1/(tamanho_kernel*tamanho_kernel)
            kernel = []

            for k2 in range(tamanho_kernel):
                line = []
                for k in range(tamanho_kernel):
                    line.append(key)
                kernel.append(line)

            image = image.blurred(kernel)
            image.show()

        elif effect == '3':
            tamanho_kernel = int(input("Insira o Tamanho Desejado do Kernel: "))
            key = 1 / (tamanho_kernel * tamanho_kernel)
            kernel = []

            for k2 in range(tamanho_kernel):
                line = []
                for k in range(tamanho_kernel):
                    line.append(key)
                kernel.append(line)

            image.sharpened(kernel)
            image.show()

        elif effect == '4':
            pixels = []
            kernel_x = [[-1, 0, 1],
                        [-2, 0, 2],
                        [-1, 0, 1]]

            image_x = image.edges(kernel_x)

            kernel_y = [[1, 2, 1],
                        [0, 0, 0],
                        [-1, -2, -1]]

            image_y = image.edges(kernel_y)

            for i in range(0, image.height):
                for j in range(1, image.width+1):
                    x = pow(image_x[i][j], 2)
                    y = pow(image_y[i][j], 2)
                    value = round(pow(x + y, 0.5))

                    if value > 255:
                        value = 255
                    elif value < 0:
                        value = 0

                    pixels.append(value)

            result = Image(image.width, image.height, pixels)
            result.show()




    # the following code will cause windows from Image.show to be displayed
    # properly, whether we're running interactively or not:
    if WINDOWS_OPENED and not sys.flags.interactive:
        tk_root.mainloop()
