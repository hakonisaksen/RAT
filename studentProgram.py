import PySimpleGUI as sg

layout = [[sg.T("")],
    [sg.T(""),sg.T(""),sg.T(""),sg.Text("Write your team number: "),sg.Input(size=(2,1), key='-INPUT1-')],
    [sg.T("")],
    [sg.T(""),sg.T(""),sg.T(""),sg.T(""), sg.Button('Join Unit',size=(20,4))],
    [sg.T("")],
    [sg.Text("Time remaining in current part: 15:00", font=("Helvetica", 10), justification='center', key='-TEXT-')],
    [sg.T("")],
    [sg.T(""),sg.T(""),sg.T(""),sg.T(""), sg.Button('Request help',size=(20,4))],
    [sg.T("")],
    [sg.T("Mark when finished")],    
    [sg.T(""),sg.T(""),sg.Checkbox('Induvidual RAT', enable_events=True, key='-CHECKBOX1-')],
    [sg.T(""),sg.T(""),sg.Checkbox('Team RAT', enable_events=True, key='-CHECKBOX2-')],
    [sg.T(""),sg.T(""),sg.Checkbox('Unit Part 1', enable_events=True, key='-CHECKBOX3-')],
    [sg.T(""),sg.T(""),sg.Checkbox('Unit Part 2', enable_events=True, key='-CHECKBOX4-')],
    [sg.T("")],
    [sg.T(""),sg.T(""),sg.T(""),sg.T(""),sg.T(""),sg.T(""),sg.T(""),sg.T("Progress bar")],
    [sg.T(""),sg.T(""),sg.ProgressBar(10, orientation='h', size=(20, 20), key='-PROGRESSBAR-')]]

window = sg.Window('Multiple Checkboxes and Progress Bar', layout)
# Add MQTT code for retreiving number of minutes in disposal from TA
minutes = 10
seconds = 0
# Denne skal startes når manager starter Uniten
while True:
    # Wait for 1 second before updating the time again
    event, values = window.read(timeout=1000)
    window['-TEXT-'].update(f"Time remaining in current part: {minutes:02d}:{seconds:02d}")    
    # If the timer has run out, break out of the loop and close the window
    if minutes == 0 and seconds == 0:
        break    
    if event == sg.WIN_CLOSED:
        break  
    
    # Decrement the time by 1 second
    seconds -= 1
    if seconds < 0:
        minutes -= 1
        seconds = 59

    progress = 0

    if values['-CHECKBOX1-']:
        progress += 1
    if values['-CHECKBOX2-']:
        progress += 1
    if values['-CHECKBOX3-']:
        progress += 1
    if values['-CHECKBOX4-']:
        progress += 1
    
    # Add MQTT code for sending help signal to TAs
    if event == 'Request help':
        print("Help Requested")
    # Add MQTT code for sending progress info (progress variabe)
    window['-PROGRESSBAR-'].update_bar(progress)

window.close()
