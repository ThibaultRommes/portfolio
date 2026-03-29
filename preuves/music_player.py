# IMPORTATIONS
import subprocess
import ipywidgets as widgets
import glob

# INTERFACE GRAPHIQUE
    # bouton

button = widgets.Button(
    description='Play',
    disabled=False,
    button_style='primary',
    icon='check',
    
)

    # cases cochables

checkbox1 = widgets.Checkbox(
    value=False,
    description='Pochette',
    disabled=False,
    indent=False,
    
)

checkbox2 = widgets.Checkbox(
    value=False,
    description='Métadonnées',
    disabled=False,
    indent=False,
    
)

checkbox3 = widgets.Checkbox(
    value=False,
    description='Représentation visuelle',
    disabled=False,
    indent=False,
    
)

    # fréquence

slider1 = widgets.IntSlider(
    value=44100,
    min=8000,
    max=96000,
    step=100,
    description='Fréquence :',
    disabled=False,
    continuous_update=False,
    orientation='horizontal',
    readout=True,
    readout_format='d'
)


slider2 = widgets.SelectionSlider(
    options=[8, 16, 24, 32],
    value=16,
    description='Profondeur :',
    continuous_update=False,
    orientation='horizontal',
    readout=True
)

    # basses
slider_bass = widgets.FloatSlider(
    value=0, 
    min=-24.0, 
    max=12.0, 
    step=0.1, 
    description='Basses', 
    orientation='vertical', 
    continuous_update=False, 
    layout=widgets.Layout(height='150px')
)

    # médiums
slider_mid = widgets.FloatSlider(
    value=0, 
    min=-24.0, 
    max=12.0, 
    step=0.1, 
    description='Mids', 
    orientation='vertical', 
    continuous_update=False, 
    layout=widgets.Layout(height='150px')
)

    # aigus
slider_treble = widgets.FloatSlider(
    value=0, 
    min=-24.0, 
    max=12.0, 
    step=0.1, 
    description='Aigus', 
    orientation='vertical', 
    continuous_update=False, 
    layout=widgets.Layout(height='150px')
)



# RECHERCHE DES FICHIERS AUDIOS ET IMAGES

listmusic = glob.glob('*.mp3') + glob.glob('*.wav') + glob.glob('*.flac')
listmusic.sort()





# LISTER LES FICHIERS

list1 = widgets.Dropdown(
    options=listmusic,
    description='Fichiers audio :',
    disabled=False,
    style={'description_width': 'initial'}
)


# PROGRAMMES
    # lire fichier audio :
out = widgets.Output()

def play(bouton):
    
    path = list1.value
    freq = slider1.value
    bits = slider2.value


    # Valeurs Egaliseur
    val_bass = slider_bass.value
    val_mid = slider_mid.value
    val_treble = slider_treble.value
    
    mapping_bits = {
        8: 'U8',
        16: 'S16LE',
        24: 'S24LE',
        32: 'S32LE'
    }
    format_gst = mapping_bits[bits]
    
    image = path.rsplit('.', 1)[0]
    jpg = image + ".jpg"
    png = image + ".png"
    
    if glob.glob(jpg):
        path_img = jpg
    elif glob.glob(png):
        path_img = png
    
        
    cmd = f'gst-launch-1.0 filesrc location="{path}" ! decodebin ! audioconvert '
    cmd_eq = f' ! equalizer-3bands band0={val_bass} band1={val_mid} band2={val_treble} '
    cmd1 = f' filesrc location="{path_img}" ! decodebin ! imagefreeze ! videoconvert ! autovideosink'
    cmd2 = f'gst-discoverer-1.0 "{path}"'
    cmd3 = f' filesrc location="{path}" ! decodebin ! audioconvert ! wavescope ! videoconvert ! autovideosink'
    cmd4 = f' ! audioresample ! audioconvert ! audio/x-raw,rate={freq},format={format_gst} ! autoaudiosink'
    
    out.clear_output()
    
    with out:

        cmd = cmd + cmd_eq + cmd4
        
        if checkbox1.value == True : # pochette
            cmd = cmd + cmd1

    
        if checkbox2.value == True : # métadonnées
            print("MÉTADONNÉES :")
            cmd_meta = subprocess.check_output(cmd2, shell=True)
            print(cmd_meta.decode('utf-8'))
        
        
        if checkbox3.value == True : # représentation visuelle
            cmd = cmd + cmd3
         
    
    subprocess.run(cmd, shell=True)
    
button.on_click(play)





# AFFICHAGE INTERFACE---------------------------------------------------------------


interfacelist = widgets.HBox([list1])
interfaceslider = widgets.HBox([slider1, slider2])
interface_eq = widgets.HBox([slider_bass, slider_mid, slider_treble])
interfacecheckbox = widgets.HBox([checkbox1, checkbox2, checkbox3], layout=widgets.Layout(display='flex',padding='20px'))
interfacebutton = widgets.HBox([button], layout=widgets.Layout(display='flex'))

interface = widgets.VBox([interfacelist,interface_eq,interfaceslider, interfacecheckbox, interfacebutton, out],layout=widgets.Layout(
        border='solid 2px black',
        padding='40px',
        width='90%',
        align_items='center'
    )
)

display(interface)




