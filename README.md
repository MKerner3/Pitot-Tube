# Pitot-Tube
Collection of files/programs used to design a Pitot Tube.

### Arduino folder: ### 
Folder used for arduino programs that get uploaded to the pitot probe. 

 * PitotTube_ADC calculates velocity from pressure transducer voltage readings, and outputs it to the serial monitor.
 * The ADS1255-ADS1256 folder is a requirement for PitotTube_ADC, so include/set up the library in your arduino IDE.


### Python files ###

 * data_reader.py continously reads serial bus values and plots them in real time. This will also do post processing on the signal to filter out any noise that the probe picks up.

 * fftandfilter.ipynp is a Jupyter notebook playground to test fourier transforms and butterworth filters on a fixed dataset.

 * test.py is a python file to test real time fourier transforms and butterworth filters on a predefined signal, as well as any other post processing calculations, before it is implemented in data_reader.py .


#### Usage ####

* fftandfilter.ipynp : Run the blocks in the notebook with a python environment, play around with new functionality to be implemented in other files.

* test.py : Run the test file in a python environment. The tube does not have to be connected for the script to work as it doesn't use the probe data. Currently, the number of data points will be printed to the console, which will cap at 30,000 (+1 before the data structure gets popped left). Hit 'Ctrl' to stop collecting data. This will then plot all data against time, the fourier transform of the data currently in the data structure, and a fourier transform of data that has been filtered.

* PitotTube_ADC : Open the arduino IDE and upload the .ino file to your arduino, ADS, and pitot tube + pressure sensor setup. Verify readings are being sent to the serial monitor.

* data_reader.py: Run the test file in a python environment, with the pitot tube connected to your computer. Serial data from the arduino will be read and stored in a data structure (a linked list/deque). Will perform fourier transforms with each new data point collected and will show filtered data when data stops collecting.



## Roadmap ##

* Develop initial pitot-static probe setup using amazon transducer and pitot probe. [May 2023]
* CAD a mount for the pitot-static probe + transducer to be tested in the LTWT [June 2023]
* CAD a dual configuration mount for a low frequency and high frequency transducer test using cheap transducers and pitot-static probes. [Aug 2023]
* Test dual configuration for low frequency and high frequency transducer in the LTWT [WIP]
* Use Machine Learning algorithms to predict the settling time of a low frequency pitot-static probe with data from the high frequency pitot-static probe [Backlog]
* Miniaturize the pitot-static probe to have a 0.5mm outer diameter. [WIP]
* CAD a pitot-static tube rake to mount miniaturized probes [Aug 2023]
* Test pitot-static probes with a high frequency transducer configuration and low frequency configurations (Kulite transducers) [Backlog]
* Test pitot-static probes with a single high frequency transducer (Kulite) and multiple low frequency transducers (amazon) [Backlog]
* Use Machine learning algorithms to predict settling times from both tests with the pressure rake. [Backlog]

