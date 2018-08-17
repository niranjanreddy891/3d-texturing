import tkinter
from tkinter import ttk, filedialog

import mimetypes, os, re, subprocess, tempfile

from threading import Thread

from ToolTip import createToolTip
#===================================================================

####  @ author: @niranjanreddy891@gmail.com

win = tkinter.Tk()

# Change the main windows icon
win.iconbitmap('Iconsmind-Outline-Dress.ico')  # filename

# Add a title
win.title("Render Texture Batch")

# We are creating a container frame
# to basically hold files and folders fields
fileFrame = ttk.LabelFrame(win, text=' Files and Folders ')
fileFrame.grid(sticky='WE', padx=10, pady=5)

# file / folder field width
widthFileDefault = 40

def enableDisableRender():
    if (os.path.isdir(objectFolder.get())
        and (os.path.isdir(texture.get())
        or os.path.isfile(texture.get()))
        and os.path.isfile(blender.get())):
            if (os.path.isfile(texture.get())):
                mimetype = mimetypes.guess_type(texture.get())
                if (mimetype[0] and mimetype[0].startswith('image')):
                    render.configure(state='enabled')
                else:
                    render.configure(state='disabled')
            else:
                render.configure(state='enabled')
    else:
        render.configure(state='disabled')

# Button Callback
def getObjectFolder():
    if (objectFolder.get().strip()):
        if (os.path.isdir(objectFolder.get().strip())):
            initDir  = objectFolder.get().strip()
        else:
            initDir = os.path.dirname(objectFolder.get().strip())
    else:
        initDir  = os.path.dirname(os.path.realpath(__file__))
    fName = filedialog.askdirectory(parent=fileFrame, initialdir=initDir,
        title='Select folder containing object files')
    if (fName):
        objectFolder.set(fName)

browseObjectFolder = ttk.Button(fileFrame, text="Objects...", command=getObjectFolder)
browseObjectFolder.grid(column=0, row=0, sticky=tkinter.W)
createToolTip(browseObjectFolder, 'Browse for folder containing objects')

objectFolder = tkinter.StringVar()
objectFolderEntry = ttk.Entry(fileFrame, textvariable=objectFolder, width=widthFileDefault)
objectFolderEntry.grid(column=1, row=0, sticky=tkinter.W)
createToolTip(objectFolderEntry, 'Folder containing objects')

# Place cursor into object folder Entry
objectFolderEntry.focus()

# Button Callback
def getTexture():
    if (texture.get().strip()):
        if (os.path.isdir(texture.get().strip())):
            initDir  = texture.get().strip()
        else:
            initDir  = os.path.dirname(texture.get().strip())
    else:
        initDir  = os.path.dirname(os.path.realpath(__file__))

    if (singleTexture.get()):
        fName = filedialog.askopenfilename(parent=fileFrame, initialdir=initDir,
            title='Select ' + browseTextureFile)
    else:
        fName = filedialog.askdirectory(parent=fileFrame, initialdir=initDir,
            title='Select ' + browseTextureFolder)
    if (fName):
        texture.set(fName)

browseTextureFile = "Texture file"
browseTextureFolder = "Texture folder"

browseTextureText = tkinter.StringVar()
browseTexture = ttk.Button(fileFrame, textvariable=browseTextureText, command=getTexture)
browseTexture.grid(column=0, row=1, sticky=tkinter.W)
createToolTip(browseTexture, 'Browse for texture')

texture = tkinter.StringVar()
textureEntry = ttk.Entry(fileFrame, textvariable=texture, width=widthFileDefault)
textureEntry.grid(column=1, row=1, sticky=tkinter.W)
createToolTip(textureEntry, 'Texture')

# Button Callback
def getMap():
    if (map.get().strip()):
        if (os.path.isdir(map.get().strip())):
            initDir  = map.get().strip()
        else:
            initDir  = os.path.dirname(map.get().strip())
    else:
        initDir  = os.path.dirname(os.path.realpath(__file__))
    fName = filedialog.askopenfilename(parent=fileFrame, initialdir=initDir,
        title='Select map')
    if (fName):
        map.set(fName)

browseMap = ttk.Button(fileFrame, text="Map file...", command=getMap)
browseMap.grid(column=0, row=2, sticky=tkinter.W)
createToolTip(browseMap, 'Browse for map')

map = tkinter.StringVar()
mapEntry = ttk.Entry(fileFrame, textvariable=map, width=widthFileDefault)
mapEntry.grid(column=1, row=2, sticky=tkinter.W)
createToolTip(mapEntry, 'Map')

# browse button Callback
def getRender():
    if (renderFolder.get().strip()):
        if (os.path.isdir(renderFolder.get().strip())):
            initDir  = renderFolder.get().strip()
        else:
            initDir  = os.path.dirname(renderFolder.get().strip())
    else:
        initDir  = os.path.dirname(os.path.realpath(__file__))
    fName = filedialog.askdirectory(parent=fileFrame, initialdir=initDir,
        title='Select folder to render in')
    if (fName):
        renderFolder.set(fName)

browseRender = ttk.Button(fileFrame, text="Render folder...", command=getRender)
browseRender.grid(column=0, row=3, sticky=tkinter.W)
createToolTip(browseRender, 'Browse for folder to save renders in')

renderFolder = tkinter.StringVar()
renderFolderEntry = ttk.Entry(fileFrame, textvariable=renderFolder, width=widthFileDefault)
renderFolderEntry.grid(column=1, row=3, sticky=tkinter.W)
createToolTip(renderFolderEntry, 'Folder to save renders in')

# begin batch rendering
def renderStart():
    global itemsProcessed, renderingsProcessed
    itemsProcessed = 0
    renderingsProcessed = 0
    objects.set(itemsProcessed)
    renderings.set(renderingsProcessed)

    renderBatch = {'objectFolder': objectFolder.get(), 'texture': texture.get()
        , 'renderFolder': renderFolder.get(), 'cameras': cameras.get()
        , 'width': width.get(), 'height': height.get()
        , 'renderFormat': renderFormat.get()
        , 'transparent': transparent.get()
        , 'single_texture': singleTexture.get()
        , 'smartUVProject': smartUVProject.get()
        , 'orthographicCamera': orthographicCamera.get()
        , 'cameraAngleStart': cameraAngleStart.get()
        , 'before': before.get()
    }

    blenderExecutable = blender.get()

    batchArgs = ('r"{objectFolder}", r"{texture}", r"{renderFolder}", "{cameras}", {width}, {height}, "{renderFormat}", {transparent}, {single_texture}, {smartUVProject}, {orthographicCamera}, {cameraAngleStart}, {before}').format_map(renderBatch)

    batch = subprocess.Popen([blenderExecutable, "-b", "--python-expr", "import sys;sys.path.append('.');import render_texture_batch; render_texture_batch.renderTextureBatch(" + batchArgs + ")"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    renderCount(batch, itemsProcessed, renderingsProcessed, stdout.get(), stderr.get())

def renderCount(batch, itemsProcessed, renderingsProcessed, stdout, stderr):    
    while True:
        stdoutLine = batch.stdout.readline()
        if stdoutLine == '' and batch.poll() is not None:
            break
        if stdoutLine:
            if stdout:
                print(stdoutLine)
            itemsProcessedLine = re.match('itemsProcessed:\s+(\d+)', stdoutLine)
            if (itemsProcessedLine):
                itemsProcessedValue = int(itemsProcessedLine.group(1))
                if (itemsProcessed < itemsProcessedValue):
                    itemsProcessed = itemsProcessedValue
                    objects.set(itemsProcessed)
            else:
                renderingsProcessedLine = re.match('renderingsProcessed:\s+(\d+)', stdoutLine)
                if (renderingsProcessedLine):
                    renderingsProcessedValue = int(renderingsProcessedLine.group(1))
                    if (renderingsProcessed < renderingsProcessedValue):
                        renderingsProcessed = renderingsProcessedValue
                        renderings.set(renderingsProcessed)

    while True:
        stderrLine = batch.stderr.readline()
        if stderrLine == '' and batch.poll() is not None:
            break
        if stderr and stderrLine:
            print(stderrLine)

# Adding Render Button
render = ttk.Button(fileFrame, text="Render", state='disabled', command=renderStart)
render.grid(column=2, row=3)
createToolTip(render, 'Start batch rendering')

for child in fileFrame.winfo_children():
    child.grid_configure(padx=8, pady=4)

# We are creating a container frame to hold options
optionFrame = ttk.LabelFrame(win, text=' Options ')
optionFrame.grid(sticky='WE', padx=10, pady=5)

ttk.Label(optionFrame, text="Camera angles").grid(column=0, row=4, sticky='W')
cameras = tkinter.IntVar()
cameras.set(4)
camera1 = tkinter.Radiobutton(optionFrame, text='One', variable=cameras, value=1)
camera1.grid(column=1, row=4, sticky=tkinter.W)
createToolTip(camera1, 'Front view only')
camera2 = tkinter.Radiobutton(optionFrame, text='Two', variable=cameras, value=2)
camera2.grid(column=2, row=4, sticky=tkinter.W)
createToolTip(camera2, 'Front and Back views')
camera4 = tkinter.Radiobutton(optionFrame, text='Four', variable=cameras, value=4)
camera4.grid(column=3, row=4, sticky=tkinter.W)
createToolTip(camera4, 'Front, back and side views')
camera8 = tkinter.Radiobutton(optionFrame, text='Eight', variable=cameras, value=8)
camera8.grid(column=4, row=4, sticky=tkinter.W)
createToolTip(camera8, 'Eight camera angles')
camera16 = tkinter.Radiobutton(optionFrame, text='Sixteen', variable=cameras, value=16)
camera16.grid(column=5, row=4, sticky=tkinter.W)
createToolTip(camera16, 'Sixteen camera angles')

ttk.Label(optionFrame, text="Render width").grid(column=0, row=5, sticky='W')
width = tkinter.StringVar()
width.set(1800)
widthEntry = ttk.Entry(optionFrame, width=4, textvariable=width)
widthEntry.grid(column=1, row=5, sticky='W')
createToolTip(widthEntry, 'Width of render')

ttk.Label(optionFrame, text="Render height").grid(column=2, row=5, sticky='W')
height = tkinter.StringVar()
height.set(1200)
heightEntry = ttk.Entry(optionFrame, width=4, textvariable=height)
heightEntry.grid(column=3, row=5, sticky='W')
createToolTip(heightEntry, 'Height of render')

transparent = tkinter.IntVar()
transparentWidget = tkinter.Checkbutton(optionFrame, text="Transparent", variable=transparent)
transparentWidget.grid(column=4, row=5, sticky=tkinter.W)
createToolTip(transparentWidget, 'Sets alpha mode to Transparent or Sky')

def singleTextureHandler():
    if (singleTexture.get()):
        browseTextureText.set(browseTextureFile + "...")
    else:
        browseTextureText.set(browseTextureFolder + "...")

singleTexture = tkinter.IntVar()
singleTexture.trace("w", lambda name, index, mode: singleTextureHandler())
singleTexture.set(1)
singleTextureWidget = tkinter.Checkbutton(optionFrame, text="Single texture", variable=singleTexture)
singleTextureWidget.grid(column=5, row=5, sticky=tkinter.W)
createToolTip(singleTextureWidget, 'Use single texture')

# create three Radiobuttons using one variable
renderFormat = tkinter.StringVar()
renderFormat.set('JPEG')

renderFormatJPEG = tkinter.Radiobutton(optionFrame, text='JPEG', variable=renderFormat, value='JPEG')
renderFormatJPEG.grid(column=6, row=5, sticky=tkinter.W)

renderFormatPng = tkinter.Radiobutton(optionFrame, text='PNG', variable=renderFormat, value='PNG')
renderFormatPng.grid(column=7, row=5, sticky=tkinter.W)

def transparentHandler():
    if (transparent.get()):
        renderFormat.set('PNG')

transparent.trace("w", lambda name, index, mode: transparentHandler())
transparent.set(0)

for child in optionFrame.winfo_children():
    child.grid_configure(padx=8, pady=4)

# We are creating a container frame to hold render progress
progressFrame = ttk.LabelFrame(win, text=' Progress ')
progressFrame.grid(sticky='WE', padx=10, pady=5)

ttk.Label(progressFrame, text="Number of Wavefronts (Obj) processed: ").grid(column=0, row=6, sticky='W')
objects = tkinter.StringVar()
itemsProcessed = 0
objects.set(itemsProcessed)
objectsEntry = ttk.Entry(progressFrame, textvariable=objects, state='disabled')
objectsEntry.grid(column=1, row=6, sticky='W')
createToolTip(objectsEntry, 'Objects processed so far')

ttk.Label(progressFrame, text="Render count: ").grid(column=2, row=6, sticky='W')
renderings = tkinter.StringVar()
renderingsProcessed = 0
renderings.set(renderingsProcessed)
renderingsEntry = ttk.Entry(progressFrame, textvariable=renderings, state='disabled')
renderingsEntry.grid(column=3, row=6, sticky='W')
createToolTip(renderingsEntry, 'Images rendered so far')

for child in progressFrame.winfo_children():
    child.grid_configure(padx=8, pady=4)

# We are creating a container frame to hold misc
miscFrame = ttk.LabelFrame(win, text=' Misc ')
miscFrame.grid(sticky='WE', padx=10, pady=5)

# browse button Callback
def getBlender():
    if (blender.get().strip()):
        initDir  = os.path.dirname(blender.get())
    else:
        initDir  = os.path.dirname(__file__)
    fName = filedialog.askopenfilename(parent=miscFrame, initialdir=initDir,
        title='Select Blender executable')
    if (fName):
        blender.set(fName)

browseBlender = ttk.Button(miscFrame, text="Blender executable...", command=getBlender)
browseBlender.grid(column=0, row=8, sticky=tkinter.W)
createToolTip(browseBlender, 'Browse for Blender .exe file')

blender = tkinter.StringVar()
blender.trace("w", lambda name, index, mode : enableDisableRender())

blenderExecutable = os.path.join(os.path.join('C:', os.sep), 'Program Files', 'Blender Foundation', 'Blender', 'blender.exe')
if (not os.path.isfile(blenderExecutable)):
    blenderExecutable = os.path.join(os.path.expanduser('~'), 'dev', os.path.relpath(blenderExecutable, os.path.join(os.path.join(os.path.splitdrive(blenderExecutable)[0], os.sep))))

blender.set(blenderExecutable)
blenderEntry = ttk.Entry(miscFrame, width=widthFileDefault, textvariable=blender)
blenderEntry.grid(column=1, row=8, columnspan=4)
createToolTip(blenderEntry, 'File Path of Blender executable')

objectFolder.trace("w", lambda name, index, mode : enableDisableRender())
objectFolder.set(os.path.dirname(os.path.realpath(__file__)))
texture.trace("w", lambda name, index, mode : enableDisableRender())
texture.set(objectFolder.get())
renderFolder.set(tempfile.mkdtemp(prefix='render_texture_batch'))

smartUVProject = tkinter.IntVar()
smartUVProject.set(1)
smartUVProjectWidget = tkinter.Checkbutton(miscFrame, text="Smart UV project", variable=smartUVProject)
smartUVProjectWidget.grid(column=0, row=9, sticky=tkinter.W)
createToolTip(smartUVProjectWidget, 'Use Smart UV project instead of unwrap')

orthographicCamera = tkinter.IntVar()
orthographicCamera.set(1)
orthographicCameraWidget = tkinter.Checkbutton(miscFrame, text="Orthographic camera", variable=orthographicCamera)
orthographicCameraWidget.grid(column=1, row=9, sticky=tkinter.W)
createToolTip(orthographicCameraWidget, 'Use orthographic camera')

cameraAngleStartLabel = ttk.Label(miscFrame, text="Camera angle start")
cameraAngleStartLabel.grid(column=2, row=9, sticky='W')
cameraAngleStart = tkinter.StringVar()
cameraAngleStart.set(0)
cameraAngleStartEntry = ttk.Entry(miscFrame, width=3, textvariable=cameraAngleStart)
cameraAngleStartEntry.grid(column=3, row=9, sticky='W')
createToolTip(cameraAngleStartEntry, 'Camera angle start')

before = tkinter.IntVar()
before.set(1)
beforeWidget = tkinter.Checkbutton(miscFrame, text="Render before", variable=before)
beforeWidget.grid(column=4, row=9, sticky=tkinter.W)
createToolTip(beforeWidget, 'Render before')

stdout = tkinter.IntVar()
stdout.set(0)
stdoutWidget = tkinter.Checkbutton(miscFrame, text="Blender output", variable=stdout)
stdoutWidget.grid(column=0, row=10, sticky=tkinter.W)
createToolTip(stdoutWidget, 'Log blender standard output')

stderr = tkinter.IntVar()
stderr.set(0)
stderrWidget = tkinter.Checkbutton(miscFrame, text="Blender error", variable=stderr)
stderrWidget.grid(column=1, row=10, sticky=tkinter.W)
createToolTip(stderrWidget, 'Log blender standard error')

def advancedOption():
    if (advanced.get()):
        blenderEntry.grid()
        browseBlender.grid()
        smartUVProjectWidget.grid()
        orthographicCameraWidget.grid()
        cameraAngleStartLabel.grid()
        cameraAngleStartEntry.grid()
        beforeWidget.grid()
        stdoutWidget.grid()
        stderrWidget.grid()
    else:
        blenderEntry.grid_remove()
        browseBlender.grid_remove()
        smartUVProjectWidget.grid_remove()
        orthographicCameraWidget.grid_remove()
        cameraAngleStartLabel.grid_remove()
        cameraAngleStartEntry.grid_remove()
        beforeWidget.grid_remove()
        stdoutWidget.grid_remove()
        stderrWidget.grid_remove()

advanced = tkinter.IntVar()
advancedWidget = tkinter.Checkbutton(miscFrame, text="Advanced", variable=advanced)
advancedWidget.grid(column=0, row=6, sticky=tkinter.W)
createToolTip(advancedWidget, 'Advanced option')

for child in miscFrame.winfo_children():
    child.grid_configure(padx=8, pady=4)

advanced.trace("w", lambda name, index, mode: advancedOption())
advanced.set(0)
#======================
# Start GUI
#======================
win.mainloop()
