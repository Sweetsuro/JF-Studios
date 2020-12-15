# JF-Studios
Project Description
-----------
The name of my project is JF Studio, which is short for Jellyfish Studio. 
JF Studio is a DAW (digital audio workstation) which allows users to produce 
audio files. Aside from some standard functionalities, such as being able to 
play, record, create new tracks, delete old tracks, import files, and export 
your final mix, JF Studio includes being able to equalize (to some extent), 
compress, and volume balance audio files. 


How to Run the Project
-----------
The user should run the term_project.py file in an editor, making sure that 
the song.py file is also present in the same directory. Additionally, the 
folder “SongFiles” is where audio files/final exports are stored, and should 
also be present in the same directory.


External Libraries
-----------
* pyaudio
* pydub
* numpy


Shortcut Commands
-----------
N/A 


Features (Key Presses)
-----------
Up
* Scrolls up tracks to see any tracks hidden after scrolling down. This key will not work if the top most track is visible.

Down
* Scrolls down tracks to see any tracks that are hidden by the volume balancer. Once the bottom most track is visible, this key will not work.

Left
* Scrolls backwards in time by half a second. Capped at the start position, or 00:00:00.

Right		
* Scrolls forward in time by half a second. 
	

Features (UI)
-----------
Selector		
* Blue line with a triangle on top.	
* Enables you to play a song from any location, and indicates what portion of the song is playing. Do not change its location while songs are playing. Clicking within the track sections (after the “New Track” labels, above the Master volume interface, and below the import/export/new track buttons) enables you to change the location of the selector. Clicking in the region of the “New Track” labels (the left labels, not to be confused with the ones in the volume balancer interface) resets the position of the selector to the very beginning. The rightmost silver arrow allows the user to go to the next waveform section in time (impacts all tracks).

Import
* Manilla colored folder with an orange arrow pointing into it. Initialized to start in the “SongFiles” directory. 
* Works via file explorer to find songs in .wav format. Can only be used if an empty track is available.
						
Export
* Manilla colored folder with an orange arrow pointing outside of it. Next to the import button.
* Creates a mixdown of whatever state all of your songs are in. The final creation can be found in the SongFiles directory.

Play
* Circle with a black triangle inside. Located in the slate grey section.
* Plays every song or soloed songs from wherever location the selector is. Only click this button if songs are currently not playing.

Record
* Circle with a red circle inside. Located in the slate grey section.
* Records the user’s input mic until the stop button is pressed. Saves recording to “SongFiles” directory with a filename prompted to the user. Adds recording to the next available track. Can only be used if an empty track is available.

Stop
* Circle with a black square inside. Located in the slate grey section.
* Stops playback/recording. Only click this button if songs are playing or a user is recording.

Volume Balancer
* Bottom, underneath the slate grey section. The location of the “Master” and all other tracks.
* Dragging the sliders enables users to increase/decrease the volume for respective tracks. As these sliders are very precarious, you must move your mouse slowly, so that it remains inside of the respective slider while being dragged. The “Master” volume track changes the volume of all tracks.

Rename Tracks
* Volume Balancer. 
* The track names present in the interface, when clicked, may be changed. Type normally after clicking. The “Backspace”, “Space”, “Shift”, and “Caps Lock” keys work as expected. Click “Enter” once finished renaming.

Time Labels
* Time stamp in the slate grey region. Also used to mark locations every half second. 
* The user cannot interact with these beyond as explained in the Selector + Key Presses sections.

Solo
* Small buttoned labelled with an “S”. Present for every track.
* When clicked, the play button will only play that track. If multiple solo buttons are clicked, the play button will play these tracks as a group. Click the solo button again to disable solo for that track. Only click the solo button when playback/recording is not in progress.

New Tracks
* Plus button located at the top, next to the export button.
* Adds a new track to the interface. You may have at maximum 10 tracks at any given moment.

Delete Tracks
* Small red button with an x inside. Located in the volume balancer interface on every track.
* Clicking the button deletes the track and any song present on that track.

FX Manager
* Small button labelled with an “FX”. Present for every track. 
* Provides an interface for filters that may be applied on the specific track (compressor, low pass, high pass, band pass). Enabled only when a song is present on the respective track. All filters are irreversible.

Compressor
* Button labelled compressor in the FX Manager.
* A compressor runs by using a ‘threshold’, ‘ratio’, ‘attack’, and ‘delay’ (delay is also commonly referred to as the release). A compressor reduces the dynamic range of the overall signal. To apply the filter, click the green checkmark. To cancel, click the red x.
* Threshold
** This indicates how loud the signal must be before compression is applied (in dB). Default value is -20.0 db.
* Ratio 
** This indicates how much compression is used. For example, if the compression ratio is set to 4:1 (as in the default settings by inputting 4), the input signal will have to cross the threshold by 4 dB for the output volume to increase by 1dB. Default value is 4 (represents 1:4).
* Attack 
** This refers to how quickly the compressor starts to work. Default value is 5 milliseconds.
* Delay
** This refers to how fast the compressor stops after dipping below the threshold. Default value is 100 milliseconds.

Low Pass Filter
* Button labelled low pass filter in the FX Manager.
* Clicking anywhere in the graph results in a change in cutoff frequency (x-axis). A model is shown to represent what will happen to the audio. A low pass filter attenuates (reduces the volume of) anything past the cutoff frequency. Something fairly standard to use is around 10k hz (default value), but for a noticeable difference, try 3k hz.

High Pass Filter
* Button labelled high pass filter in the FX Manager.
* Clicking anywhere in the graph results in a change in cutoff frequency (x-axis). A model is shown to represent what will happen to the audio. A high pass filter attenuates anything before the cutoff frequency. Something fairly standard to use is around 200 hz (default value), but for a noticeable difference, try 1k hz.

Band Pass Filter
* Button labelled band pass filter in the FX Manager.
* Dragging purple circles to the left and right in the graph results in a change in either low cutoff frequency or high cutoff frequency, depending on which circle is dragged (x-axis). Be gentle with your dragging movements. A model is shown to represent what will happen to the audio. A band pass filter attenuates anything before the low cutoff frequency and attenuates anything above the high cutoff frequency. Default values of 200 hz and 10k hz are given.
